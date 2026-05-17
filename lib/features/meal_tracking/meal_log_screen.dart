import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/meal_entry.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../dashboard/providers/dashboard_provider.dart';

class MealLogScreen extends ConsumerWidget {
  const MealLogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(mealProvider);
    final l10n = ref.watch(appStringsProvider);

    final mealTypes = [
      ('breakfast', l10n.breakfast, Icons.wb_sunny_outlined),
      ('lunch', l10n.lunch, Icons.lunch_dining_outlined),
      ('dinner', l10n.dinner, Icons.dinner_dining_outlined),
      ('snack', l10n.snack, Icons.cookie_outlined),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.meals),
        actions: [
          IconButton(
            icon: const Icon(Icons.camera_alt_outlined),
            onPressed: () => context.push('/camera', extra: 'snack'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ...mealTypes.map((m) => _MealSection(
            mealType: m.$1,
            label: m.$2,
            icon: m.$3,
            entries: state.forType(m.$1),
          )),
          const SizedBox(height: 80),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/meals/add', extra: 'snack'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: Text(l10n.addFood),
      ),
    );
  }
}

class _MealSection extends ConsumerWidget {
  final String mealType, label;
  final IconData icon;
  final List<MealEntry> entries;

  const _MealSection({
    required this.mealType, required this.label,
    required this.icon, required this.entries,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final totalCals = entries.fold<double>(0, (sum, e) => sum + e.calories);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        children: [
          ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: AppColors.primary),
            ),
            title: Text(label, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
            subtitle: totalCals > 0
                ? Text('${totalCals.toStringAsFixed(0)} kcal', style: TextStyle(color: AppColors.calories))
                : Text(l10n.tapToAdd, style: Theme.of(context).textTheme.bodySmall),
            trailing: IconButton(
              icon: const Icon(Icons.add_circle, color: AppColors.primary),
              onPressed: () => context.push('/meals/add', extra: mealType),
            ),
          ),
          if (entries.isNotEmpty) ...[
            const Divider(height: 1),
            ...entries.map((e) => _EntryTile(entry: e)),
          ],
        ],
      ),
    );
  }
}

class _EntryTile extends ConsumerWidget {
  final MealEntry entry;

  const _EntryTile({required this.entry});

  void _showEditSheet(BuildContext context, WidgetRef ref) {
    final qtyController = TextEditingController(text: entry.quantityG.toStringAsFixed(0));
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Consumer(
        builder: (ctx2, ref2, _) {
          final l10n = ref2.watch(appStringsProvider);
          return Padding(
            padding: EdgeInsets.only(
              left: 24, right: 24, top: 24,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.foodItem.name,
                  style: Theme.of(ctx2).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  '${entry.calories.toStringAsFixed(0)} kcal per ${entry.quantityG.toStringAsFixed(0)}g',
                  style: Theme.of(ctx2).textTheme.bodySmall?.copyWith(color: AppColors.calories),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: qtyController,
                  keyboardType: TextInputType.number,
                  autofocus: true,
                  decoration: InputDecoration(
                    labelText: l10n.quantity,
                    suffix: const Text('g'),
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          Navigator.pop(ctx);
                          await ref2.read(mealProvider.notifier).deleteEntry(entry.id);
                          ref2.read(dashboardProvider.notifier).refresh();
                        },
                        icon: const Icon(Icons.delete_outline, color: Colors.red),
                        label: Text(l10n.delete, style: const TextStyle(color: Colors.red)),
                        style: OutlinedButton.styleFrom(side: const BorderSide(color: Colors.red)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () async {
                          final qty = double.tryParse(qtyController.text);
                          Navigator.pop(ctx);
                          if (qty != null && qty > 0) {
                            await ref2.read(mealProvider.notifier).updateQuantity(entry, qty);
                            ref2.read(dashboardProvider.notifier).refresh();
                          }
                        },
                        child: Text(l10n.update),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Dismissible(
      key: Key(entry.id),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 16),
        color: Colors.red.shade400,
        child: const Icon(Icons.delete_outline, color: Colors.white),
      ),
      onDismissed: (_) async {
        await ref.read(mealProvider.notifier).deleteEntry(entry.id);
        ref.read(dashboardProvider.notifier).refresh();
      },
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        title: Text(
          entry.foodItem.name,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '${entry.quantityG.toStringAsFixed(0)}g | P: ${entry.proteinG.toStringAsFixed(1)}g | C: ${entry.carbsG.toStringAsFixed(1)}g | F: ${entry.fatG.toStringAsFixed(1)}g',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${entry.calories.toStringAsFixed(0)} kcal',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.calories,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(width: 4),
            const Icon(Icons.edit_outlined, size: 16, color: Colors.grey),
          ],
        ),
        onTap: () => _showEditSheet(context, ref),
      ),
    );
  }
}

