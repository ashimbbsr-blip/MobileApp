import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';

class AppLogo extends StatelessWidget {
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
          'assets/images/healthtrackerlogo.png',
          width: size,
          height: size,
          fit: BoxFit.contain,
        ),
        const SizedBox(height: 12),
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
            ),
          ),
        ],
      ],
    );
  }
}
