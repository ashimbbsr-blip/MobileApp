import 'package:hive/hive.dart';
import 'food_item.dart';

part 'meal_entry.g.dart';

@HiveType(typeId: 2)
class MealEntry extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String mealType; // 'breakfast', 'lunch', 'dinner', 'snack'

  @HiveField(2)
  FoodItem foodItem;

  @HiveField(3)
  double quantityG;

  @HiveField(4)
  DateTime loggedAt;

  @HiveField(5)
  String dateKey; // 'yyyy_mm_dd'

  MealEntry({
    required this.id,
    required this.mealType,
    required this.foodItem,
    required this.quantityG,
    required this.loggedAt,
    required this.dateKey,
  });

  FoodItem get scaledFood => foodItem.scaledTo(quantityG);

  double get _factor => foodItem.servingSize > 0 ? quantityG / foodItem.servingSize : 0.0;
  double get calories => foodItem.calories * _factor;
  double get proteinG => foodItem.proteinG * _factor;
  double get carbsG => foodItem.carbsG * _factor;
  double get fatG => foodItem.fatG * _factor;
  double get fiberG => foodItem.fiberG * _factor;
  double get alcoholG => (foodItem.alcoholG ?? 0) * _factor;
  double get sodiumMg => (foodItem.sodiumMg ?? 0) * _factor;
}
