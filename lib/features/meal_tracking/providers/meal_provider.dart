import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/meal_entry.dart';
import '../../../models/food_item.dart';
import '../../../storage/hive_storage.dart';
import '../../../services/notification_service.dart';
import '../../../core/utils/extensions.dart';
import 'package:uuid/uuid.dart';

class MealState {
  final List<MealEntry> entries;
  final String dateKey;
  final bool isLoading;

  const MealState({
    this.entries = const [],
    required this.dateKey,
    this.isLoading = false,
  });

  List<MealEntry> forType(String type) => entries.where((e) => e.mealType == type).toList();

  MealState copyWith({List<MealEntry>? entries, String? dateKey, bool? isLoading}) {
    return MealState(
      entries: entries ?? this.entries,
      dateKey: dateKey ?? this.dateKey,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class MealNotifier extends StateNotifier<MealState> {
  MealNotifier() : super(MealState(dateKey: DateTime.now().toLogKey())) {
    _load();
  }

  void _load() {
    final entries = HiveStorage.getMealsForDate(state.dateKey);
    state = state.copyWith(entries: entries);
  }

  void setDate(DateTime date) {
    state = state.copyWith(dateKey: date.toLogKey());
    _load();
  }

  Future<void> addFood(FoodItem food, String mealType, double quantityG) async {
    final entry = MealEntry(
      id: const Uuid().v4(),
      mealType: mealType,
      foodItem: food,
      quantityG: quantityG,
      loggedAt: DateTime.now(),
      dateKey: state.dateKey,
    );
    await HiveStorage.addMealEntry(entry);
    _load();
    // If today's log: check if both breakfast & dinner are done, reschedule
    final today = DateTime.now().toLogKey();
    if (state.dateKey == today) {
      await NotificationService.instance.checkMealsAndMaybeReschedule(today);
    }
  }

  Future<void> deleteEntry(String id) async {
    await HiveStorage.deleteMealEntry(id);
    _load();
  }

  Future<void> updateQuantity(MealEntry entry, double newQuantity) async {
    final updated = MealEntry(
      id: entry.id,
      mealType: entry.mealType,
      foodItem: entry.foodItem,
      quantityG: newQuantity,
      loggedAt: entry.loggedAt,
      dateKey: entry.dateKey,
    );
    await HiveStorage.updateMealEntry(updated);
    _load();
  }

  void refresh() => _load();
}

final mealProvider = StateNotifierProvider<MealNotifier, MealState>(
  (ref) => MealNotifier(),
);
