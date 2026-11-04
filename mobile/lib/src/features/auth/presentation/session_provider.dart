import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/network/api_client.dart';
import '../data/auth_repository.dart';
import '../domain/auth_user.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.watch(apiClientProvider),
    const FlutterSecureStorage(),
  );
});

final sessionProvider =
    AsyncNotifierProvider<SessionNotifier, AuthUser?>(SessionNotifier.new);

class SessionNotifier extends AsyncNotifier<AuthUser?> {
  AuthRepository get _repository => ref.read(authRepositoryProvider);

  @override
  Future<AuthUser?> build() => _repository.restoreSession();

  Future<String?> readToken() => _repository.readToken();

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => _repository.login(email: email, password: password),
    );
  }

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) {
    return _repository.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
    );
  }

  Future<void> loginWithGoogle() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.loginWithGoogle());
  }

  Future<void> updateProfile({
    required String firstName,
    required String lastName,
    required String phone,
    required String address,
  }) async {
    state = await AsyncValue.guard(
      () => _repository.updateProfile(
        firstName: firstName,
        lastName: lastName,
        phone: phone,
        address: address,
      ),
    );
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AsyncData(null);
  }
}
