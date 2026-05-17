class Validators {
  static String? validateAge(String? value) {
    if (value == null || value.isEmpty) return 'Required';
    final age = int.tryParse(value);
    if (age == null) return 'Invalid number';
    if (age < 10 || age > 100) return '10–100 years';
    return null;
  }

  static String? validateHeight(String? value) {
    if (value == null || value.isEmpty) return 'Required';
    final height = double.tryParse(value);
    if (height == null) return 'Invalid number';
    if (height < 100 || height > 250) return '100–250 cm';
    return null;
  }

  static String? validateWeight(String? value) {
    if (value == null || value.isEmpty) return 'Required';
    final weight = double.tryParse(value);
    if (weight == null) return 'Invalid number';
    if (weight < 25 || weight > 300) return '25–300 kg';
    return null;
  }

  static String? validateRequired(String? value) {
    if (value == null || value.isEmpty) return 'Required';
    return null;
  }
}
