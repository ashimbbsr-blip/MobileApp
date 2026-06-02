import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';

class AppLogo extends StatelessWidget {
  /// Height of the logo image. Width scales naturally with the 3:2 aspect ratio.
  final double size;
  final bool showTagline;
  final bool light;

  const AppLogo({super.key, this.size = 80, this.showTagline = true, this.light = false});

  @override
  Widget build(BuildContext context) {
    final textColor = light ? Colors.white : Theme.of(context).colorScheme.onSurface;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          'assets/images/infinitehealthtrackerlogo.png',
          height: size,
          fit: BoxFit.fitHeight,
        ),
        const SizedBox(height: 8),
        Text(
          'Infinite Health Tracker',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
            color: textColor,
          ),
          textAlign: TextAlign.center,
        ),
        if (showTagline) ...[
          const SizedBox(height: 4),
          Text(
            'Better Health Every Day',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: light ? Colors.white70 : AppColors.primary,
              fontWeight: FontWeight.w500,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ],
    );
  }
}
