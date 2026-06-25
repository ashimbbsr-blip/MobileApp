import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/weight_entry.dart';
import '../../../storage/hive_storage.dart';
import '../../profile/providers/profile_provider.dart';

class WeightState {
  final List<WeightEntry> history; // ascending by date
  final bool saving;

  const WeightState({this.history = const [], this.saving = false});

  WeightState copyWith({List<WeightEntry>? history, bool? saving}) =>
      WeightState(history: history ?? this.history, saving: saving ?? this.saving);

  WeightEntry? get latest => history.isEmpty ? null : history.last;
  WeightEntry? get first => history.isEmpty ? null : history.first;

  /// Net change across the recorded history (kg). Positive = gain.
  double get netChange =>
      history.length >= 2 ? history.last.weightKg - history.first.weightKg : 0;
}

class WeightNotifier extends StateNotifier<WeightState> {
  final Ref ref;
  WeightNotifier(this.ref) : super(const WeightState()) {
    _load();
  }

  void _load() {
    state = state.copyWith(history: HiveStorage.getWeightHistory());
  }

  void refresh() => _load();

  /// Log (or update) a weight for a given day and keep the profile's current
  /// weight in sync.
  Future<bool> logWeight(double weightKg, {DateTime? when}) async {
    if (weightKg <= 0 || weightKg > 600) return false;
    state = state.copyWith(saving: true);
    final profile = HiveStorage.getUserProfile();
    final heightCm = profile?.heightCm ?? 170;
    final date = when ?? DateTime.now();
    final dateKey =
        '${date.year}_${date.month.toString().padLeft(2, '0')}_${date.day.toString().padLeft(2, '0')}';

    await HiveStorage.saveWeightEntry(WeightEntry(
      id: dateKey,
      recordedAt: date,
      weightKg: weightKg,
      heightCm: heightCm,
    ));

    // Keep current profile weight aligned with the most recent measurement.
    if (profile != null && _isTodayOrLater(date)) {
      await HiveStorage.saveUserProfile(profile.copyWith(weightKg: weightKg));
      ref.read(profileProvider.notifier).refresh();
    }

    _load();
    state = state.copyWith(saving: false);
    return true;
  }

  Future<void> deleteEntry(String dateKey) async {
    await HiveStorage.deleteWeightEntry(dateKey);
    _load();
  }

  bool _isTodayOrLater(DateTime d) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    return !DateTime(d.year, d.month, d.day).isBefore(today);
  }
}

final weightProvider =
    StateNotifierProvider<WeightNotifier, WeightState>((ref) => WeightNotifier(ref));
