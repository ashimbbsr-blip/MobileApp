import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../theme/app_colors.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Help & Guide'),
        centerTitle: false,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _Section(
            icon: Icons.info_outline_rounded,
            title: 'What is Infinite Health Tracker?',
            isDark: isDark,
            children: const [
              _Bullet(
                'A bilingual (English + Bengali) nutrition tracker that works fully offline — no internet needed for your daily logging.',
              ),
              _Bullet(
                'Log every meal, track calories and macros (protein, carbs, fat), and see weekly trends in the History tab.',
              ),
              _Bullet(
                'Powered by a 1,377-item local database covering Indian, Bengali, Odia, and Bangladeshi foods — plus USDA\'s global database for international items.',
              ),
              _Bullet(
                'Smart recommendations appear on your dashboard after you log your first meal of the day.',
              ),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.restaurant_menu_rounded,
            title: 'How to Log a Meal',
            isDark: isDark,
            children: const [
              _Step(n: 1, text: 'Tap Meals (bottom nav) → + button next to any meal type.'),
              _Step(n: 2, text: 'Search the food by name (try in Bengali too!). Tap a result to open its detail.'),
              _Step(n: 3, text: 'Adjust serving size, pick a meal type, and tap Add.'),
              _Step(n: 4, text: 'Your daily totals and recommendations update instantly on the Home tab.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.dinner_dining_rounded,
            title: 'Planning a Healthy Dinner',
            isDark: isDark,
            children: const [
              _Bullet('Aim for dinner to be ~30 % of your daily calorie target (e.g. ~600 kcal on a 2000 kcal goal).'),
              _Bullet('Balance plate: ½ vegetables, ¼ protein (fish / chicken / dal / paneer), ¼ carbs (rice / roti).'),
              _Bullet('Avoid heavy fried items close to bedtime — steamed or boiled preparations digest faster.'),
              _Bullet('A small salad or raita adds micronutrients without many calories.'),
              _Bullet('Eat at least 2 hours before sleeping for better digestion.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.search_rounded,
            title: 'Searching Foods',
            isDark: isDark,
            children: const [
              _Bullet('Local tab (offline): 1,377 Indian / Bengali / Odia foods. Type English or Bengali — autocomplete suggestions appear after 1 character.'),
              _Bullet('Category chips (rice, dal, fish…) instantly browse all items in that group.'),
              _Bullet('USDA tab (online): Search millions of global foods from the US Dept. of Agriculture database. Requires internet.'),
              _Bullet('My Foods tab: Create custom entries for home-cooked dishes with your own calorie values.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.vpn_key_outlined,
            title: 'Getting a Free USDA API Key',
            isDark: isDark,
            children: [
              const _Bullet(
                'The USDA tab works with a DEMO key (limited to ~30 requests/hour). For unlimited access, get a free API key in under a minute:',
              ),
              const _Step(n: 1, text: 'Visit fdc.nal.usda.gov/api-key-signup.html (link below).'),
              const _Step(n: 2, text: 'Enter your name and email — no payment required.'),
              const _Step(n: 3, text: 'Check your inbox for the key (arrives in seconds).'),
              const _Step(n: 4, text: 'In this app: Settings → USDA API Key → Add Key → paste it.'),
              _LinkButton(
                label: 'Get Free USDA API Key',
                url: 'https://fdc.nal.usda.gov/api-key-signup.html',
              ),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.bar_chart_rounded,
            title: 'History & Analytics',
            isDark: isDark,
            children: const [
              _Bullet('History tab shows a 7-day calorie trend bar chart and macro breakdown for any past date.'),
              _Bullet('Tap any bar to jump to that day\'s full meal log.'),
              _Bullet('Export your data as CSV or JSON from Settings → Data Export.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.lightbulb_outline_rounded,
            title: 'Tips',
            isDark: isDark,
            children: const [
              _Bullet('Set your profile (weight, height, age, activity) for accurate calorie targets.'),
              _Bullet('Log water and beverages too — they count toward your daily energy.'),
              _Bullet('The app works completely offline — your data never leaves your phone.'),
              _Bullet('Switch language to Bengali (Settings → Language) for Bengali food names and tips.'),
            ],
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

// ── Section ───────────────────────────────────────────────────────────────────

class _Section extends StatelessWidget {
  final IconData icon;
  final String title;
  final List<Widget> children;
  final bool isDark;

  const _Section({
    required this.icon,
    required this.title,
    required this.children,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: AppColors.primary, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    title,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _Bullet extends StatelessWidget {
  final String text;
  const _Bullet(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 5),
            child: Icon(Icons.circle, size: 5, color: AppColors.primary),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(text, style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.45)),
          ),
        ],
      ),
    );
  }
}

class _Step extends StatelessWidget {
  final int n;
  final String text;
  const _Step({required this.n, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                '$n',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primary,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(text, style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.45)),
          ),
        ],
      ),
    );
  }
}

class _LinkButton extends StatelessWidget {
  final String label;
  final String url;
  const _LinkButton({required this.label, required this.url});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: OutlinedButton.icon(
        onPressed: () async {
          final uri = Uri.parse(url);
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri, mode: LaunchMode.externalApplication);
          }
        },
        icon: const Icon(Icons.open_in_browser_outlined, size: 16),
        label: Text(label, style: const TextStyle(fontSize: 13)),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: const BorderSide(color: AppColors.primary),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      ),
    );
  }
}
