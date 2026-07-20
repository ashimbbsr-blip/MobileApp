import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../services/api_key_service.dart';
import '../../theme/app_colors.dart';
import 'providers/food_scan_provider.dart';

/// Body of the "Scan" tab inside AddFoodScreen: take/pick a meal photo and
/// jump to the scan-review flow.
class ScanTab extends ConsumerWidget {
  final String lang;
  final bool isDark;
  final String mealType;

  const ScanTab({
    super.key,
    required this.lang,
    required this.isDark,
    required this.mealType,
  });

  Future<void> _startScan(
      BuildContext context, WidgetRef ref, ImageSource source) async {
    final notifier = ref.read(foodScanProvider.notifier);
    final ok = await notifier.pickImage(source);
    if (!context.mounted) return;
    if (!ok) {
      // pickImage sets an error state when no API key is configured.
      if (ref.read(foodScanProvider).errorKind == ScanErrorKind.noApiKey) {
        context.push('/meals/scan-review', extra: mealType);
      }
      return;
    }
    notifier.analyze(); // fire and navigate; review screen shows progress
    context.push('/meals/scan-review', extra: mealType);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bn = lang == 'bn';
    final hasKey = ApiKeyService.instance.hasGeminiKey;

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Banner
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppColors.primary.withValues(alpha: isDark ? 0.25 : 0.14),
                  AppColors.secondary.withValues(alpha: isDark ? 0.18 : 0.10),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(
              children: [
                const Icon(Icons.photo_camera_rounded,
                    size: 44, color: AppColors.primary),
                const SizedBox(height: 10),
                Text(
                  bn ? 'ছবি তুলে খাবার লগ করুন' : 'Log food from a photo',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      fontSize: 17, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 6),
                Text(
                  bn
                      ? 'আপনার প্লেটের ছবি তুলুন — AI খাবার চিনে ক্যালরি ও পরিমাণ অনুমান করবে। যোগ করার আগে আপনি সব যাচাই করতে পারবেন।'
                      : 'Snap your plate — AI recognizes the dishes and suggests portions & calories. You review everything before it\'s logged.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: 12.5,
                      height: 1.4,
                      color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: () => _startScan(context, ref, ImageSource.camera),
            icon: const Icon(Icons.photo_camera_outlined),
            label: Text(bn ? 'ছবি তুলুন' : 'Take Photo'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.primary,
              minimumSize: const Size.fromHeight(52),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => _startScan(context, ref, ImageSource.gallery),
            icon: const Icon(Icons.photo_library_outlined),
            label: Text(bn ? 'গ্যালারি থেকে বাছুন' : 'Choose from Gallery'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(52),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
            ),
          ),
          const SizedBox(height: 20),
          if (!hasKey)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(Icons.key_rounded,
                      size: 20, color: Colors.amber.shade800),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      bn
                          ? 'ফটো স্ক্যানের জন্য একটি ফ্রি Gemini API কী প্রয়োজন। সেটিংসে যোগ করুন।'
                          : 'Photo scan needs a free Gemini API key. Add one in Settings.',
                      style: const TextStyle(fontSize: 12.5),
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.push('/settings'),
                    child: Text(bn ? 'সেটিংস' : 'Settings'),
                  ),
                ],
              ),
            )
          else
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.wifi_rounded, size: 14, color: Colors.grey.shade500),
                const SizedBox(width: 6),
                Text(
                  bn
                      ? 'ইন্টারনেট সংযোগ প্রয়োজন'
                      : 'Requires an internet connection',
                  style:
                      TextStyle(fontSize: 11.5, color: Colors.grey.shade500),
                ),
              ],
            ),
        ],
      ),
    );
  }
}
