import 'package:hive/hive.dart';

part 'food_item.g.dart';

@HiveType(typeId: 1)
class FoodItem extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String name;

  @HiveField(2)
  String? brand;

  @HiveField(3)
  double servingSize; // in grams

  @HiveField(4)
  String servingUnit;

  @HiveField(5)
  double calories;

  @HiveField(6)
  double proteinG;

  @HiveField(7)
  double carbsG;

  @HiveField(8)
  double fatG;

  @HiveField(9)
  double fiberG;

  @HiveField(10)
  double? vitaminAMcg;

  @HiveField(11)
  double? vitaminCMg;

  @HiveField(12)
  double? vitaminDMcg;

  @HiveField(13)
  double? calciumMg;

  @HiveField(14)
  double? ironMg;

  @HiveField(15)
  double? potassiumMg;

  @HiveField(16)
  double? magnesiumMg;

  @HiveField(17)
  double? zincMg;

  @HiveField(18)
  String? usdaFdcId;

  @HiveField(19)
  bool isCustom;

  FoodItem({
    required this.id,
    required this.name,
    this.brand,
    required this.servingSize,
    required this.servingUnit,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    this.vitaminAMcg,
    this.vitaminCMg,
    this.vitaminDMcg,
    this.calciumMg,
    this.ironMg,
    this.potassiumMg,
    this.magnesiumMg,
    this.zincMg,
    this.usdaFdcId,
    this.isCustom = false,
  });

  FoodItem scaledTo(double grams) {
    final factor = grams / servingSize;
    return FoodItem(
      id: id,
      name: name,
      brand: brand,
      servingSize: grams,
      servingUnit: servingUnit,
      calories: calories * factor,
      proteinG: proteinG * factor,
      carbsG: carbsG * factor,
      fatG: fatG * factor,
      fiberG: fiberG * factor,
      vitaminAMcg: vitaminAMcg != null ? vitaminAMcg! * factor : null,
      vitaminCMg: vitaminCMg != null ? vitaminCMg! * factor : null,
      vitaminDMcg: vitaminDMcg != null ? vitaminDMcg! * factor : null,
      calciumMg: calciumMg != null ? calciumMg! * factor : null,
      ironMg: ironMg != null ? ironMg! * factor : null,
      potassiumMg: potassiumMg != null ? potassiumMg! * factor : null,
      magnesiumMg: magnesiumMg != null ? magnesiumMg! * factor : null,
      zincMg: zincMg != null ? zincMg! * factor : null,
      usdaFdcId: usdaFdcId,
      isCustom: isCustom,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'brand': brand,
    'servingSize': servingSize,
    'servingUnit': servingUnit,
    'calories': calories,
    'proteinG': proteinG,
    'carbsG': carbsG,
    'fatG': fatG,
    'fiberG': fiberG,
    'usdaFdcId': usdaFdcId,
    'isCustom': isCustom,
  };
}
