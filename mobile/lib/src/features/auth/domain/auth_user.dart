class AuthUser {
  const AuthUser({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.role,
    required this.phone,
    required this.address,
    required this.avatarUrl,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as int? ?? 0,
      email: json['email'] as String? ?? '',
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      role: json['role'] as String? ?? 'patient',
      phone: json['phone'] as String? ?? '',
      address: json['address'] as String? ?? '',
      avatarUrl: json['avatar_url'] as String? ?? '',
    );
  }

  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String role;
  final String phone;
  final String address;
  final String avatarUrl;

  String get displayName {
    final name = '$firstName $lastName'.trim();
    return name.isEmpty ? email : name;
  }
}
