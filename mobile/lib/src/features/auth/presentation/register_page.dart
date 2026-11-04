import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/auth_repository.dart';
import 'session_provider.dart';
import 'auth_widgets.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _firstName = TextEditingController();
  final _lastName = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _firstName.dispose();
    _lastName.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    FocusScope.of(context).unfocus();
    setState(() => _isSubmitting = true);
    try {
      await ref.read(sessionProvider.notifier).register(
            email: _email.text,
            password: _password.text,
            firstName: _firstName.text,
            lastName: _lastName.text,
          );
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Account created. You can now sign in.')),
      );
      context.goNamed('login');
    } on AuthException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message)),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }

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
    return AuthShell(
      title: 'Create your account',
      subtitle: 'Join MedChain and keep your care organized in one place.',
      child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _firstName,
                decoration: authInput('First name', Icons.person_outline),
                validator: _required,
              ),
              TextFormField(
                controller: _lastName,
                decoration: authInput('Last name', Icons.person_outline),
                validator: _required,
              ),
              TextFormField(
                controller: _email,
                keyboardType: TextInputType.emailAddress,
                decoration: authInput('Email', Icons.email_outlined),
                validator: (value) => value == null || !value.contains('@')
                    ? 'Enter a valid email.'
                    : null,
              ),
              TextFormField(
                controller: _password,
                obscureText: true,
                decoration: authInput('Password', Icons.lock_outline),
                validator: (value) => value == null || value.length < 8
                    ? 'Use at least 8 characters.'
                    : null,
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _isSubmitting ? null : _submit,
                child: _isSubmitting
                    ? const CircularProgressIndicator()
                    : const Text('Register'),
              ),
              const SizedBox(height: 12),
              GoogleButton(onPressed: _googleSignIn, loading: _isSubmitting),
              TextButton(
                onPressed: () => context.goNamed('login'),
                child: const Text('Already have an account? Sign in'),
              ),
            ],
          ),
        ),
    );
  }

  String? _required(String? value) =>
      value == null || value.trim().isEmpty ? 'This field is required.' : null;
}
