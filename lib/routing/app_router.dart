import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/hive_storage.dart';
import '../features/splash/splash_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/legal/legal_acceptance_screen.dart';
import '../features/legal/legal_content_screen.dart';
import '../features/legal/legal_content.dart';
import '../features/dashboard/dashboard_screen.dart';
import '../features/food_search/food_search_screen.dart';
import '../features/food_search/food_detail_screen.dart';
import '../features/meal_tracking/meal_log_screen.dart';
import '../features/meal_tracking/add_food_screen.dart';
import '../features/micronutrients/micronutrient_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/history/history_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/help/help_screen.dart';
import '../models/food_item.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/legal',
        builder: (context, state) => const LegalAcceptanceScreen(),
        routes: [
          GoRoute(
            path: 'terms',
            builder: (context, state) =>
                const LegalContentScreen(type: LegalDocType.terms),
          ),
          GoRoute(
            path: 'privacy',
            builder: (context, state) =>
                const LegalContentScreen(type: LegalDocType.privacy),
          ),
          GoRoute(
            path: 'health',
            builder: (context, state) =>
                const LegalContentScreen(type: LegalDocType.health),
          ),
        ],
      ),
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/food-search',
            builder: (context, state) => const FoodSearchScreen(),
            routes: [
              GoRoute(
                path: 'detail',
                builder: (context, state) {
                  final food = state.extra as FoodItem?;
                  if (food == null) return const Scaffold(body: SizedBox.shrink());
                  return FoodDetailScreen(foodItem: food);
                },
              ),
            ],
          ),
          GoRoute(
            path: '/meals',
            builder: (context, state) => const MealLogScreen(),
            routes: [
              GoRoute(
                path: 'add',
                builder: (context, state) {
                  final mealType = state.extra as String? ?? 'snack';
                  return AddFoodScreen(mealType: mealType);
                },
              ),
            ],
          ),
          GoRoute(
            path: '/history',
            builder: (context, state) => const HistoryScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/micronutrients',
        builder: (context, state) => const MicronutrientScreen(),
      ),
      GoRoute(
        path: '/help',
        builder: (context, state) => const HelpScreen(),
      ),
    ],
    redirect: (context, state) {
      final location = state.matchedLocation;

      // Splash always renders — it performs its own navigation
      if (location == '/splash') return null;

      // Legal gate: must accept before anything else
      final legalOk =
          HiveStorage.isLegalAccepted && !HiveStorage.needsPolicyReAcceptance;
      final isLegalRoute = location.startsWith('/legal');

      if (!legalOk) {
        // Allow navigation within the /legal subtree; redirect everything else
        return isLegalRoute ? null : '/legal';
      }

      // Legal is accepted — legal routes still accessible (from settings)
      if (isLegalRoute) return null;

      // Onboarding gate
      if (!HiveStorage.isOnboardingDone) return '/onboarding';

      return null;
    },
  );
});

class MainShell extends StatelessWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  static const _routes = [
    '/dashboard',
    '/food-search',
    '/meals',
    '/history',
    '/settings',
  ];

  static int _indexForLocation(String location) {
    for (int i = 0; i < _routes.length; i++) {
      if (location.startsWith(_routes[i])) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    final currentIndex = _indexForLocation(location);

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) => context.go(_routes[index]),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.search_outlined), selectedIcon: Icon(Icons.search), label: 'Search'),
          NavigationDestination(icon: Icon(Icons.restaurant_outlined), selectedIcon: Icon(Icons.restaurant), label: 'Meals'),
          NavigationDestination(icon: Icon(Icons.bar_chart_outlined), selectedIcon: Icon(Icons.bar_chart), label: 'History'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: 'Settings'),
        ],
        height: 65,
        labelBehavior: NavigationDestinationLabelBehavior.onlyShowSelected,
      ),
    );
  }
}
