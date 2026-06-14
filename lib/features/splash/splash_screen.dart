import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../storage/hive_storage.dart';
import '../../theme/app_colors.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _imageFade;
  late Animation<double> _taglineFade;
  late Animation<Offset> _taglineSlide;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1800));

    // Front image fades in quickly
    _imageFade = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0, 0.4, curve: Curves.easeOut)),
    );

    // Tagline fades in and slides up after image appears
    _taglineFade = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.5, 1.0, curve: Curves.easeOut)),
    );
    _taglineSlide = Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.5, 1.0, curve: Curves.easeOut)),
    );

    _controller.forward();
    _navigate();
  }

  Future<void> _navigate() async {
    await Future.delayed(const Duration(milliseconds: 2400));
    if (!mounted) return;
    if (HiveStorage.isOnboardingDone) {
      context.go('/dashboard');
    } else {
      context.go('/onboarding');
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF0F1923),
      body: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Stack(
            fit: StackFit.expand,
            children: [
              // ── Full-screen front image ──────────────────────────────────
              FadeTransition(
                opacity: _imageFade,
                child: Image.asset(
                  'assets/images/frontimage.png',
                  width: size.width,
                  height: size.height,
                  fit: BoxFit.contain,
                  alignment: Alignment.center,
                ),
              ),

              // ── Bottom gradient for tagline readability ──────────────────
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                height: size.height * 0.35,
                child: FadeTransition(
                  opacity: _imageFade,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withValues(alpha:0.72),
                        ],
                      ),
                    ),
                  ),
                ),
              ),

              // ── Logo + tagline over the image ────────────────────────────
              Positioned(
                left: 24,
                right: 24,
                bottom: size.height * 0.12,
                child: FadeTransition(
                  opacity: _taglineFade,
                  child: SlideTransition(
                    position: _taglineSlide,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Image.asset(
                          'assets/images/infinitehealthtrackerlogo.png',
                          height: 56,
                          fit: BoxFit.fitHeight,
                        ),
                        const SizedBox(height: 10),
                        const Text(
                          'INFINITE NUTRITION TRACKER',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 2.0,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.primary.withValues(alpha:0.9),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'Better Health Every Day',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
