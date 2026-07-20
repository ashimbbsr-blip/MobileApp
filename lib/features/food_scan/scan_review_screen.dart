import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../localization/strings_provider.dart';
import '../../models/food_item.dart';
import '../../services/local_food_repository.dart';
import '../../theme/app_colors.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';
import 'food_match_service.dart';
import 'providers/food_scan_provider.dart';

class ScanReviewScreen extends ConsumerStatefulWidget {
  final String initialMealType;
  const ScanReviewScreen({super.key, required this.initialMealType});

  @override
  ConsumerState<ScanReviewScreen> createState() => _ScanReviewScreenState();
}

class _ScanReviewScreenState extends ConsumerState<ScanReviewScreen> {
  late String _mealType;
  bool _adding = false;

  @override
  void initState() {
    super.initState();
    _mealType = widget.initialMealType;
  }

  Future<void> _confirmAdd() async {
    final scan = ref.read(foodScanProvider);
    if (scan.items.isEmpty || _adding) return;
    setState(() => _adding = true);
    for (final it in scan.items) {
      await ref
          .read(mealProvider.notifier)
          .addFood(it.selected, _mealType, it.grams);
    }
    if (!mounted) return;
    ref.read(dashboardProvider.notifier).refresh();
    final lang = ref.read(appStringsProvider).language;
    final n = scan.items.length;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(lang == 'bn'
            ? '$nটি খাবার যোগ হয়েছে!'
            : '$n item${n == 1 ? '' : 's'} added!'),
        backgroundColor: AppColors.primary,
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
    ref.read(foodScanProvider.notifier).reset();
    context.go('/meals');
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(appStringsProvider).language;
    final bn = lang == 'bn';
    final scan = ref.watch(foodScanProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(bn ? 'স্ক্যান ফলাফল' : 'Scan Results'),
      ),
      body: switch (scan.status) {
        ScanStatus.analyzing => _AnalyzingView(imagePath: scan.imagePath, bn: bn),
        ScanStatus.error => _ErrorView(
            kind: scan.errorKind ?? ScanErrorKind.generic,
            message: scan.errorMessage,
            bn: bn,
            onRetry: () => ref.read(foodScanProvider.notifier).analyze(),
          ),
        ScanStatus.review => _buildReview(scan, lang),
        ScanStatus.idle => const SizedBox.shrink(),
      },
      bottomNavigationBar:
          scan.status == ScanStatus.review && scan.items.isNotEmpty
              ? _buildBottomBar(scan, bn)
              : null,
    );
  }

  Widget _buildReview(FoodScanState scan, String lang) {
    final bn = lang == 'bn';
    final l10n = ref.watch(appStringsProvider);
    final mealTypes = {
      'breakfast': l10n.breakfast,
      'lunch': l10n.lunch,
      'dinner': l10n.dinner,
      'snack': l10n.snack,
    };

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        if (scan.imagePath != null)
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.file(
              File(scan.imagePath!),
              height: 160,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
        const SizedBox(height: 12),
        Text(
          bn ? 'কোন বেলার খাবার?' : 'Which meal?',
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 8,
          children: [
            for (final entry in mealTypes.entries)
              ChoiceChip(
                label: Text(entry.value),
                selected: _mealType == entry.key,
                onSelected: (_) => setState(() => _mealType = entry.key),
              ),
          ],
        ),
        const SizedBox(height: 12),
        Text(
          bn
              ? 'শনাক্ত করা খাবার (${scan.items.length})'
              : 'Detected foods (${scan.items.length})',
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        for (var i = 0; i < scan.items.length; i++)
          _ScannedItemCard(
            key: ObjectKey(scan.items[i]),
            item: scan.items[i],
            index: i,
            lang: lang,
            onChangeMatch: () => _showChangeMatchSheet(i, lang),
          ),
        if (scan.items.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 32),
            child: Center(
              child: Text(bn ? 'সব আইটেম মুছে ফেলা হয়েছে' : 'All items removed'),
            ),
          ),
      ],
    );
  }

  Widget _buildBottomBar(FoodScanState scan, bool bn) {
    final kcal = scan.totalKcal.round();
    final n = scan.items.length;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
        child: FilledButton(
          onPressed: _adding ? null : _confirmAdd,
          style: FilledButton.styleFrom(
            backgroundColor: AppColors.primary,
            minimumSize: const Size.fromHeight(52),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
          child: _adding
              ? const SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(
                      strokeWidth: 2.5, color: Colors.white),
                )
              : Text(
                  bn
                      ? '$nটি আইটেম যোগ করুন ($kcal ক্যালরি)'
                      : 'Add $n item${n == 1 ? '' : 's'} ($kcal kcal)',
                  style: const TextStyle(
                      fontSize: 15, fontWeight: FontWeight.w700),
                ),
        ),
      ),
    );
  }

  void _showChangeMatchSheet(int index, String lang) {
    final bn = lang == 'bn';
    final item = ref.read(foodScanProvider).items[index];
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetCtx) => _ChangeMatchSheet(
        bn: bn,
        lang: lang,
        item: item,
        onSelect: (food) {
          ref.read(foodScanProvider.notifier).replaceSelection(index, food);
          Navigator.of(sheetCtx).pop();
        },
        onUseAiEstimate: () {
          ref.read(foodScanProvider.notifier).useAiEstimate(index);
          Navigator.of(sheetCtx).pop();
        },
      ),
    );
  }
}

// ── Analyzing ────────────────────────────────────────────────────────────────

class _AnalyzingView extends StatelessWidget {
  final String? imagePath;
  final bool bn;
  const _AnalyzingView({required this.imagePath, required this.bn});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (imagePath != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.file(
                File(imagePath!),
                height: 180,
                width: 180,
                fit: BoxFit.cover,
              ),
            ),
          const SizedBox(height: 24),
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            bn ? 'আপনার খাবার বিশ্লেষণ হচ্ছে…' : 'Analyzing your food…',
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          Text(
            bn ? 'কয়েক সেকেন্ড লাগতে পারে' : 'This can take a few seconds',
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }
}

// ── Error ────────────────────────────────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  final ScanErrorKind kind;
  final String? message;
  final bool bn;
  final VoidCallback onRetry;
  const _ErrorView({
    required this.kind,
    required this.message,
    required this.bn,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final (icon, title, subtitle) = switch (kind) {
      ScanErrorKind.noApiKey => (
          Icons.key_off_rounded,
          bn ? 'API কী প্রয়োজন' : 'API key needed',
          bn
              ? 'ফটো স্ক্যানের জন্য সেটিংসে ফ্রি Gemini API কী যোগ করুন।'
              : 'Add a free Gemini API key in Settings to use photo scan.',
        ),
      ScanErrorKind.invalidKey => (
          Icons.key_off_rounded,
          bn ? 'API কী সমস্যা' : 'API key problem',
          bn
              ? 'Gemini API কী কাজ করছে না। সেটিংসে কী পরীক্ষা করুন।'
              : 'The Gemini API key is not working. Check it in Settings.',
        ),
      ScanErrorKind.offline => (
          Icons.wifi_off_rounded,
          bn ? 'ইন্টারনেট নেই' : 'No connection',
          bn
              ? 'ফটো স্ক্যানের জন্য ইন্টারনেট প্রয়োজন। সংযোগ পরীক্ষা করে আবার চেষ্টা করুন।'
              : 'Photo scan needs internet. Check your connection and retry.',
        ),
      ScanErrorKind.rateLimited => (
          Icons.hourglass_top_rounded,
          bn ? 'একটু অপেক্ষা করুন' : 'Please wait a minute',
          bn
              ? 'ফ্রি কোটা সাময়িকভাবে শেষ। এক মিনিট পরে আবার চেষ্টা করুন।'
              : 'Free quota briefly exceeded. Try again in a minute.',
        ),
      ScanErrorKind.nothingRecognized => (
          Icons.no_food_outlined,
          bn ? 'কোনো খাবার পাওয়া যায়নি' : 'No food recognized',
          bn
              ? 'ছবিতে খাবার শনাক্ত করা যায়নি। ভালো আলোতে কাছ থেকে আবার ছবি তুলুন।'
              : 'No food was detected in the photo. Try a closer shot in good light.',
        ),
      ScanErrorKind.generic => (
          Icons.error_outline_rounded,
          bn ? 'স্ক্যান ব্যর্থ হয়েছে' : 'Scan failed',
          message ?? (bn ? 'আবার চেষ্টা করুন।' : 'Please try again.'),
        ),
    };

    final showSettings =
        kind == ScanErrorKind.noApiKey || kind == ScanErrorKind.invalidKey;
    final showRetry = kind != ScanErrorKind.noApiKey;

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 56, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(title,
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (showRetry)
                  OutlinedButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh_rounded, size: 18),
                    label: Text(bn ? 'আবার চেষ্টা' : 'Retry'),
                  ),
                if (showRetry && showSettings) const SizedBox(width: 12),
                if (showSettings)
                  FilledButton.icon(
                    onPressed: () => context.push('/settings'),
                    icon: const Icon(Icons.settings_rounded, size: 18),
                    label: Text(bn ? 'সেটিংস খুলুন' : 'Open Settings'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ── Item card ────────────────────────────────────────────────────────────────

class _ScannedItemCard extends ConsumerStatefulWidget {
  final ScannedItemMatch item;
  final int index;
  final String lang;
  final VoidCallback onChangeMatch;

  const _ScannedItemCard({
    super.key,
    required this.item,
    required this.index,
    required this.lang,
    required this.onChangeMatch,
  });

  @override
  ConsumerState<_ScannedItemCard> createState() => _ScannedItemCardState();
}

class _ScannedItemCardState extends ConsumerState<_ScannedItemCard> {
  late final TextEditingController _gramsCtrl;

  @override
  void initState() {
    super.initState();
    _gramsCtrl =
        TextEditingController(text: widget.item.grams.round().toString());
  }

  @override
  void dispose() {
    _gramsCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bn = widget.lang == 'bn';
    final item = widget.item;
    final food = item.selected;
    final kcal = (food.calories * item.grams / food.servingSize).round();
    final confidence = (item.detected.confidence * 100).round();

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 8, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        food.displayName(widget.lang),
                        style: const TextStyle(
                            fontSize: 15, fontWeight: FontWeight.w700),
                      ),
                      if (item.detected.portionDescription.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: 2),
                          child: Text(
                            item.detected.portionDescription,
                            style: TextStyle(
                                fontSize: 12, color: Colors.grey.shade600),
                          ),
                        ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          _Badge(
                            label: item.isFallback
                                ? (bn ? 'AI অনুমান' : 'AI estimate')
                                : (bn ? 'মিলেছে' : 'Matched'),
                            color: item.isFallback
                                ? Colors.amber.shade700
                                : AppColors.primary,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '$confidence%',
                            style: TextStyle(
                                fontSize: 11, color: Colors.grey.shade600),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close_rounded, size: 20),
                  tooltip: bn ? 'বাদ দিন' : 'Remove',
                  onPressed: () => ref
                      .read(foodScanProvider.notifier)
                      .removeItem(widget.index),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                SizedBox(
                  width: 90,
                  child: TextField(
                    controller: _gramsCtrl,
                    keyboardType: TextInputType.number,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    decoration: InputDecoration(
                      isDense: true,
                      suffixText: 'g',
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 8),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                    onChanged: (v) {
                      final g = double.tryParse(v);
                      if (g != null && g > 0) {
                        ref
                            .read(foodScanProvider.notifier)
                            .updateGrams(widget.index, g);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  bn ? '$kcal ক্যালরি' : '$kcal kcal',
                  style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: AppColors.calories),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: widget.onChangeMatch,
                  icon: const Icon(Icons.swap_horiz_rounded, size: 18),
                  label: Text(bn ? 'পরিবর্তন' : 'Change'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style:
            TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: color),
      ),
    );
  }
}

// ── Change-match bottom sheet ────────────────────────────────────────────────

class _ChangeMatchSheet extends StatefulWidget {
  final bool bn;
  final String lang;
  final ScannedItemMatch item;
  final void Function(FoodItem) onSelect;
  final VoidCallback onUseAiEstimate;

  const _ChangeMatchSheet({
    required this.bn,
    required this.lang,
    required this.item,
    required this.onSelect,
    required this.onUseAiEstimate,
  });

  @override
  State<_ChangeMatchSheet> createState() => _ChangeMatchSheetState();
}

class _ChangeMatchSheetState extends State<_ChangeMatchSheet> {
  final _searchCtrl = TextEditingController();
  List<FoodItem> _searchResults = [];

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  void _onSearch(String q) {
    setState(() {
      _searchResults =
          q.trim().isEmpty ? [] : LocalFoodRepository.search(q, limit: 15);
    });
  }

  @override
  Widget build(BuildContext context) {
    final bn = widget.bn;
    final suggestions =
        _searchCtrl.text.trim().isEmpty ? widget.item.alternates : _searchResults;

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.65,
      maxChildSize: 0.9,
      builder: (context, scrollCtrl) => Padding(
        padding: EdgeInsets.only(
          left: 16,
          right: 16,
          top: 12,
          bottom: MediaQuery.of(context).viewInsets.bottom + 12,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade400,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              bn
                  ? '"${widget.item.detected.nameEn}" এর জন্য মিল বদলান'
                  : 'Change match for "${widget.item.detected.nameEn}"',
              style:
                  const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _searchCtrl,
              onChanged: _onSearch,
              decoration: InputDecoration(
                isDense: true,
                hintText: bn ? 'খাবার খুঁজুন…' : 'Search foods…',
                prefixIcon: const Icon(Icons.search_rounded, size: 20),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView(
                controller: scrollCtrl,
                children: [
                  ListTile(
                    dense: true,
                    leading:
                        Icon(Icons.auto_awesome, color: Colors.amber.shade700),
                    title: Text(bn ? 'AI অনুমান ব্যবহার করুন' : 'Use AI estimate'),
                    subtitle: Text(
                      '${widget.item.detected.kcal.round()} kcal · '
                      '${widget.item.detected.estimatedGrams.round()} g',
                      style: const TextStyle(fontSize: 12),
                    ),
                    onTap: widget.onUseAiEstimate,
                  ),
                  const Divider(height: 1),
                  for (final food in suggestions)
                    ListTile(
                      dense: true,
                      title: Text(food.displayName(widget.lang)),
                      subtitle: Text(
                        '${food.calories.round()} kcal / '
                        '${food.servingSize.round()} ${food.servingUnit}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      trailing: food.id == widget.item.selected.id
                          ? const Icon(Icons.check_rounded,
                              color: AppColors.primary)
                          : null,
                      onTap: () => widget.onSelect(food),
                    ),
                  if (suggestions.isEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 24),
                      child: Center(
                        child: Text(
                          bn ? 'কোনো ফলাফল নেই' : 'No results',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
