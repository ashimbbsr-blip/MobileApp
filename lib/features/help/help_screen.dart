import 'package:flutter/material.dart';
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
            title: 'What is Infinite Nutrition Tracker?',
            isDark: isDark,
            children: const [
              _Bullet(
                'A bilingual (English + Bengali) nutrition tracker that works fully offline — no internet needed for your daily logging.',
              ),
              _Bullet(
                'Log every meal, track calories and macros (protein, carbs, fat), and see weekly trends in the History tab.',
              ),
              _Bullet(
                'Powered by a 5,000-item local database covering Indian, Bengali, and Odia foods — plus USDA\'s global database for international items.',
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
              _Bullet('Local tab (offline): 5,000 Indian & Bengali foods. Type English or Bengali — autocomplete suggestions appear as you type.'),
              _Bullet('Category chips (rice, dal, fish…) instantly browse all items in that group.'),
              _Bullet('USDA tab (online): Search millions of global foods from the US Dept. of Agriculture database. Requires an internet connection. No account or API key needed — this is handled automatically.'),
              _Bullet('My Foods tab: Create custom entries for home-cooked dishes with your own calorie values.'),
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
            icon: Icons.notifications_outlined,
            title: 'Meal Reminders',
            isDark: isDark,
            children: const [
              _Bullet('By default, the app sends a reminder at 6:00 PM to log your breakfast and dinner if you haven\'t done so yet.'),
              _Bullet('To change the time or turn reminders off: Settings → Meal Reminders.'),
              _Bullet('Once both breakfast and dinner are logged for the day, the reminder is automatically moved to the next day.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.bolt_outlined,
            title: 'Energy Balance',
            isDark: isDark,
            children: const [
              _Bullet('The Energy Balance card on the Home tab compares your daily calorie intake against your personalised TDEE (Total Daily Energy Expenditure).'),
              _Bullet('It shows your daily surplus or deficit in kcal, along with equivalent activities — like how many minutes of walking, running, or cycling that represents.'),
              _Bullet('The 7-Day History tab shows a weekly energy balance chart so you can spot trends at a glance.'),
              _Bullet('All values are approximate and for guidance only — always consult a professional for medical advice.'),
            ],
          ),
          const SizedBox(height: 12),
          _Section(
            icon: Icons.lightbulb_outline_rounded,
            title: 'Tips',
            isDark: isDark,
            children: const [
              _Bullet('Set your profile (weight, height, age, activity) for accurate calorie targets and energy balance calculations.'),
              _Bullet('Log water and beverages too — they count toward your daily goals.'),
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

