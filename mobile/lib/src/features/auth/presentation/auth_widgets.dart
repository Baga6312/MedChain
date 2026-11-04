import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/theme/theme_provider.dart';

class AuthShell extends ConsumerWidget {
  const AuthShell({required this.title, required this.subtitle, required this.child, super.key});

  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    return Scaffold(
      body: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDark
                    ? [const Color(0xFF082F49), theme.scaffoldBackgroundColor]
                    : [const Color(0xFFE0F2FE), theme.scaffoldBackgroundColor],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 28, 24, 36),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 430),
                  child: Card(
                    elevation: 8,
                    shadowColor: Colors.black26,
                    child: Padding(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 42,
                                height: 42,
                                alignment: Alignment.center,
                                decoration: BoxDecoration(
                                  color: theme.colorScheme.primary,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(Icons.health_and_safety, color: Colors.white),
                              ),
                              const SizedBox(width: 12),
                              Text('MedChain', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                              const Spacer(),
                              IconButton(
                                tooltip: isDark ? 'Light theme' : 'Dark theme',
                                onPressed: () => ref.read(themeModeProvider.notifier).toggle(),
                                icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
                              ),
                            ],
                          ),
                          const SizedBox(height: 32),
                          Text(title, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          Text(subtitle, style: theme.textTheme.bodyMedium),
                          const SizedBox(height: 24),
                          child,
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class GoogleButton extends StatelessWidget {
  const GoogleButton({required this.onPressed, required this.loading, super.key});

  final VoidCallback? onPressed;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: loading ? null : onPressed,
      icon: loading
          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
          : const SizedBox(
              width: 20,
              height: 20,
              child: CustomPaint(painter: _GoogleLogoPainter()),
            ),
      label: const Text('Continue with Google'),
    );
  }
}

class _GoogleLogoPainter extends CustomPainter {
  const _GoogleLogoPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final bounds = Rect.fromCircle(center: center, radius: size.width * .38);
    const strokeWidth = 3.5;
    final segments = [
      (const Color(0xFF4285F4), -0.5, 1.6),
      (const Color(0xFF34A853), 1.1, 1.05),
      (const Color(0xFFFBBC05), 2.15, 1.05),
      (const Color(0xFFEA4335), 3.2, 1.95),
    ];
    for (final (color, start, sweep) in segments) {
      canvas.drawArc(
        bounds,
        start,
        sweep,
        false,
        Paint()
          ..color = color
          ..style = PaintingStyle.stroke
          ..strokeWidth = strokeWidth
          ..strokeCap = StrokeCap.butt,
      );
    }
    canvas.drawLine(
      Offset(size.width * .52, size.height * .5),
      Offset(size.width * .92, size.height * .5),
      Paint()
        ..color = const Color(0xFF4285F4)
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

InputDecoration authInput(String label, IconData icon) => InputDecoration(
      labelText: label,
      prefixIcon: Icon(icon),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
    );

Future<void> showAuthError(BuildContext context, String message) {
  return showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Sign-in diagnostic'),
      content: SelectableText(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    ),
  );
}
