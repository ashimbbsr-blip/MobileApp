import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../storage/hive_storage.dart';
import '../../theme/app_colors.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final bool _isFirstInstall;
  late AnimationController _controller;
  late Animation<double> _imageFade;
  late Animation<double> _taglineFade;
  late Animation<Offset> _taglineSlide;

  @override
  void initState() {
    super.initState();
    _isFirstInstall = !HiveStorage.isOnboardingDone;

    if (_isFirstInstall) {
      // Full branded splash — only shown once on fresh install
      _controller = AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 1800),
      );
      _imageFade = Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(
            parent: _controller,
            curve: const Interval(0, 0.4, curve: Curves.easeOut)),
      );
      _taglineFade = Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.5, 1.0, curve: Curves.easeOut)),
      );
      _taglineSlide =
          Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero).animate(
        CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.5, 1.0, curve: Curves.easeOut)),
      );
      _controller.forward();
      _navigateAfter(const Duration(milliseconds: 2400));
    } else {
      // Returning user — minimal fast splash, just the logo
      _controller = AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 350),
      );
      _imageFade = Tween<double>(begin: 0, end: 1).animate(_controller);
      _taglineFade = _imageFade;
      _taglineSlide =
          Tween<Offset>(begin: Offset.zero, end: Offset.zero).animate(_controller);
      _controller.forward();
      _navigateAfter(const Duration(milliseconds: 450));
    }
  }

  Future<void> _navigateAfter(Duration delay) async {
    await Future.delayed(delay);
    if (!mounted) return;
    if (_isFirstInstall) {
      context.go('/onboarding');
    } else {
      context.go('/dashboard');
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isFirstInstall) {
      return _buildMinimalSplash(context);
    }
    return _buildFullSplash(context);
  }

  // ── Full splash (first install only) ────────────────────────────────────────
  Widget _buildFullSplash(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Scaffold(
      backgroundColor: const Color(0xFF0F1923),
      body: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Stack(
            fit: StackFit.expand,
            children: [
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
                          Colors.black.withValues(alpha: 0.72),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
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
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.primary.withValues(alpha: 0.9),
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

  // ── Minimal splash (returning users) ────────────────────────────────────────
  Widget _buildMinimalSplash(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1923),
      body: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) => FadeTransition(
          opacity: _imageFade,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Image.asset(
                  'assets/images/infinitehealthtrackerlogo.png',
                  height: 72,
                  fit: BoxFit.fitHeight,
                ),
                const SizedBox(height: 14),
                const Text(
                  'INFINITE NUTRITION TRACKER',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 2.0,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
