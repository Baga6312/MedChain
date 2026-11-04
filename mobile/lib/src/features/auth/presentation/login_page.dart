import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/auth_repository.dart';
import 'session_provider.dart';
import 'auth_widgets.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    FocusScope.of(context).unfocus();
    await ref.read(sessionProvider.notifier).login(
          email: _emailController.text,
          password: _passwordController.text,
        );
    if (!mounted) {
      return;
    }
    final error = ref.read(sessionProvider).error;
    if (error != null) {
      final message = error is AuthException
          ? error.message
          : 'Unable to sign in. Please try again.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
      return;
    }
    context.goNamed('home');
  }

  Future<void> _googleSignIn() async {
    await ref.read(sessionProvider.notifier).loginWithGoogle();
    if (!mounted) return;
    final error = ref.read(sessionProvider).error;
    if (error != null) {
    await showAuthError(
      context,
      error is AuthException ? error.message : 'Google sign-in failed.',
    );
    return;
    }
    context.goNamed('home');
  }

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(sessionProvider);
    final isLoading = session.isLoading;
    final error = session.error;
    final errorMessage = error is AuthException
        ? error.message
        : error == null
            ? null
            : 'Unable to sign in. Please try again.';
    return AuthShell(
      title: 'Welcome back',
      subtitle: 'Sign in to securely access your healthcare journey.',
      child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: authInput('Email', Icons.email_outlined),
                  validator: (value) =>
                      value == null || !value.contains('@') ? 'Enter a valid email.' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: authInput('Password', Icons.lock_outline),
                  validator: (value) =>
                      value == null || value.isEmpty ? 'Enter your password.' : null,
                ),
                if (errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    errorMessage,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: isLoading ? null : _submit,
                  child: isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Sign in'),
                ),
                const SizedBox(height: 12),
                GoogleButton(onPressed: _googleSignIn, loading: isLoading),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => context.goNamed('register'),
                  child: const Text('Create an account'),
                ),
              ],
            ),
          ),
    );
  }
}
