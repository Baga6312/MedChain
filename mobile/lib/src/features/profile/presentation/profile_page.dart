import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/data/auth_repository.dart';
import '../../auth/presentation/session_provider.dart';
import '../../../shared/config/api_config.dart';

class ProfilePage extends ConsumerStatefulWidget {
  const ProfilePage({super.key});

  @override
  ConsumerState<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends ConsumerState<ProfilePage> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _firstName;
  late final TextEditingController _lastName;
  late final TextEditingController _phone;
  late final TextEditingController _address;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final user = ref.read(sessionProvider).valueOrNull;
    _firstName = TextEditingController(text: user?.firstName);
    _lastName = TextEditingController(text: user?.lastName);
    _phone = TextEditingController(text: user?.phone);
    _address = TextEditingController(text: user?.address);
  }

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _phone.dispose();
    _address.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    await ref.read(sessionProvider.notifier).updateProfile(
          firstName: _firstName.text,
          lastName: _lastName.text,
          phone: _phone.text,
          address: _address.text,
        );
    if (!mounted) return;
    final error = ref.read(sessionProvider).error;
    setState(() => _saving = false);
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error is AuthException ? error.message : 'Unable to update profile.')),
      );
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profile updated.')),
    );
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(sessionProvider).valueOrNull;
    return Scaffold(
      appBar: AppBar(title: const Text('My profile')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Center(child: _ProfileAvatar(user?.avatarUrl ?? '', user?.displayName ?? '')),
            const SizedBox(height: 12),
            Center(child: Text(user?.email ?? '', style: Theme.of(context).textTheme.bodySmall)),
            const SizedBox(height: 24),
            TextFormField(controller: _firstName, decoration: const InputDecoration(labelText: 'First name'), validator: _required),
            const SizedBox(height: 12),
            TextFormField(controller: _lastName, decoration: const InputDecoration(labelText: 'Last name'), validator: _required),
            const SizedBox(height: 12),
            TextFormField(controller: _phone, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Phone')),
            const SizedBox(height: 12),
            TextFormField(controller: _address, decoration: const InputDecoration(labelText: 'Address')),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _saving ? null : _save,
              child: _saving ? const CircularProgressIndicator() : const Text('Save changes'),
            ),
          ],
        ),
      ),
    );
  }

  String? _required(String? value) =>
      value == null || value.trim().isEmpty ? 'This field is required.' : null;
}

class _ProfileAvatar extends StatelessWidget {
  const _ProfileAvatar(this.path, this.name);

  final String path;
  final String name;

  @override
  Widget build(BuildContext context) {
    final imageUrl = path.isEmpty
        ? null
        : path.startsWith('http')
            ? path
            : '${ApiConfig.baseUrl.replaceFirst('/api', '')}$path';
    return CircleAvatar(
      radius: 46,
      backgroundImage: imageUrl == null ? null : NetworkImage(imageUrl),
      child: imageUrl == null ? Text(name.isEmpty ? '?' : name.substring(0, 1).toUpperCase()) : null,
    );
  }
}
