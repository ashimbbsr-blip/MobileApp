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
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            gradient: AppColors.primaryGradient,
            borderRadius: BorderRadius.circular(size * 0.25),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withOpacity(0.4),
                blurRadius: 20,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Icon(
            Icons.favorite,
            color: Colors.white,
            size: size * 0.5,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'Infinity Health Tracker',
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
