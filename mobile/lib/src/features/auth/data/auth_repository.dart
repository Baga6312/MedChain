import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../domain/auth_user.dart';

class AuthException implements Exception {
  const AuthException(this.message);

  final String message;
}

class AuthRepository {
  const AuthRepository(this._client, this._storage);

  static const _tokenKey = 'medchain_access_token';

  final Dio _client;
  final FlutterSecureStorage _storage;

  Future<AuthUser?> restoreSession() async {
    final token = await _storage.read(key: _tokenKey);
    if (token == null || token.isEmpty) {
      return null;
    }

    try {
      return await currentUser();
    } on AuthException {
      await logout();
      return null;
    }
  }

  Future<String?> readToken() => _storage.read(key: _tokenKey);

  Future<AuthUser> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post<Map<String, dynamic>>(
        '/auth/login/',
        data: {'email': email.trim(), 'password': password},
      );
      final token = response.data?['access'] as String?;
      if (token == null || token.isEmpty) {
        throw const AuthException('The server did not return a session token.');
      }
      await _storage.write(key: _tokenKey, value: token);
      return await currentUser();
    } on AuthException {
      rethrow;
    } on DioException catch (error) {
      throw AuthException(_messageFrom(error));
    }
  }

  Future<AuthUser> loginWithGoogle() async {
    final serverClientId = const String.fromEnvironment('GOOGLE_SERVER_CLIENT_ID');
    debugPrint(
      'MedChain Google OAuth: starting; '
      'server client configured=${serverClientId.isNotEmpty}, '
      'client suffix=${serverClientId.length > 12 ? serverClientId.substring(serverClientId.length - 12) : 'none'}',
    );
    if (serverClientId.isEmpty) {
      debugPrint('MedChain Google OAuth: missing GOOGLE_SERVER_CLIENT_ID');
      throw const AuthException(
        'Google Sign-In is not configured. Add GOOGLE_SERVER_CLIENT_ID.',
      );
    }
    final googleSignIn = GoogleSignIn(serverClientId: serverClientId);
    GoogleSignInAccount? account;
    try {
      account = await googleSignIn.signIn();
      debugPrint(
        'MedChain Google OAuth: Android sign-in returned '
        '${account == null ? 'no account (cancelled)' : 'an account'}',
      );
    } on PlatformException catch (error) {
      debugPrint(
        'MedChain Google OAuth: Android sign-in failed; '
        'code=${error.code}, message=${error.message}',
      );
      throw AuthException(
        'Google sign-in failed (${error.code}): '
        '${error.message ?? 'Android OAuth configuration is invalid.'}',
      );
    }
    if (account == null) {
      throw const AuthException('Google Sign-In was cancelled.');
    }
    GoogleSignInAuthentication authentication;
    try {
      authentication = await account.authentication;
      debugPrint(
        'MedChain Google OAuth: token response received; '
        'id token present=${authentication.idToken?.isNotEmpty == true}',
      );
    } on PlatformException catch (error) {
      debugPrint(
        'MedChain Google OAuth: token retrieval failed; '
        'code=${error.code}, message=${error.message}',
      );
      throw AuthException(
        'Google token retrieval failed (${error.code}): '
        '${error.message ?? 'Google did not return an ID token.'}',
      );
    }
    final idToken = authentication.idToken;
    if (idToken == null || idToken.isEmpty) {
      throw const AuthException('Google did not return an ID token.');
    }
    try {
      debugPrint('MedChain Google OAuth: exchanging ID token with backend');
      final response = await _client.post<Map<String, dynamic>>(
        '/auth/google/mobile/',
        data: {'id_token': idToken},
      );
      final token = response.data?['access'] as String?;
      if (token == null || token.isEmpty) {
        throw const AuthException('The server did not return a session token.');
      }
      await _storage.write(key: _tokenKey, value: token);
      debugPrint('MedChain Google OAuth: backend session created');
      return await currentUser();
    } on AuthException {
      rethrow;
    } on DioException catch (error) {
      debugPrint(
        'MedChain Google OAuth: backend exchange failed; '
        'status=${error.response?.statusCode}, type=${error.type}',
      );
      throw AuthException(_messageFrom(error));
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    try {
      await _client.post<void>(
        '/auth/register/',
        data: {
          'email': email.trim(),
          'password': password,
          'first_name': firstName.trim(),
          'last_name': lastName.trim(),
        },
      );
    } on DioException catch (error) {
      throw AuthException(_messageFrom(error));
    }
  }

  Future<AuthUser> currentUser() async {
    try {
      final response = await _client.get<Map<String, dynamic>>('/auth/me/');
      return AuthUser.fromJson(response.data ?? <String, dynamic>{});
    } on DioException catch (error) {
      throw AuthException(_messageFrom(error));
    }
  }

  Future<AuthUser> updateProfile({
      required String firstName,
      required String lastName,
      required String phone,
      required String address,
    }) async {
      try {
        final response = await _client.patch<Map<String, dynamic>>(
          '/auth/profile/',
          data: {
            'first_name': firstName.trim(),
            'last_name': lastName.trim(),
            'phone': phone.trim(),
            'address': address.trim(),
          },
        );
        return AuthUser.fromJson(response.data ?? <String, dynamic>{});
      } on DioException catch (error) {
        throw AuthException(_messageFrom(error));
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: _tokenKey);
    try {
      await GoogleSignIn().signOut();
    } on PlatformException catch (error) {
      debugPrint(
        'MedChain Google OAuth: local logout completed, '
        'Google sign-out failed; code=${error.code}, message=${error.message}',
      );
    }
  }

  String _messageFrom(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is String && detail.isNotEmpty) {
        return 'HTTP ${error.response?.statusCode ?? 'error'}: $detail';
      }
      final password = data['password'];
      if (password is List && password.isNotEmpty) {
        return 'HTTP ${error.response?.statusCode ?? 'error'}: '
            '${password.first}';
      }
    }
    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout) {
      return 'Unable to connect to the MedChain server.';
    }
    final status = error.response?.statusCode;
    return status == null
        ? 'Unable to reach the authentication server.'
        : 'Authentication request failed (HTTP $status).';
  }
}
