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

  double get calories => foodItem.calories * (quantityG / foodItem.servingSize);
  double get proteinG => foodItem.proteinG * (quantityG / foodItem.servingSize);
  double get carbsG => foodItem.carbsG * (quantityG / foodItem.servingSize);
  double get fatG => foodItem.fatG * (quantityG / foodItem.servingSize);
  double get fiberG => foodItem.fiberG * (quantityG / foodItem.servingSize);
  double get alcoholG => (foodItem.alcoholG ?? 0) * (quantityG / foodItem.servingSize);
  double get sodiumMg => (foodItem.sodiumMg ?? 0) * (quantityG / foodItem.servingSize);
}
