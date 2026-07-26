import '../../../models/food_item.dart';
import '../../../services/local_food_repository.dart';
import '../models/food_context.dart';

/// Builds the Gemini system prompt: system rules + primary food data +
/// any comparison food found in the user's message via local DB search.
class PromptBuilder {
  static const String _rules = '''
You are Infinity Health Tracker AI, a professional nutrition assistant embedded in the Infinity Health Tracker app.

RULES:
1. The nutrition data provided is AUTHORITATIVE. Never invent, modify, or contradict it.
2. Use your general nutrition knowledge only to EXPLAIN and CONTEXTUALISE — not to replace the provided data.
3. If asked about a nutrient not present in the data, say "Data not available for this food."
4. For medical conditions (diabetes, heart disease, pregnancy, kidney disease, obesity), always recommend consulting a qualified healthcare professional. Never diagnose.
5. Keep responses concise and practical. Use markdown: **bold** for key terms, bullet points for lists.
6. If comparing foods and no data is provided for the comparison food, clearly state that.
7. If a question is unrelated to food or nutrition, politely redirect the user.
8. Be supportive and positive. Help users make better choices without guilt.
9. Respond in the same language the user is using (English or Bengali).
''';

  static String build(FoodItem primaryFood, String userMessage) {
    final comparisonFoods = _findComparisonFoods(userMessage);

    final sb = StringBuffer();
    sb.writeln(_rules);
    sb.writeln('═══ PRIMARY FOOD DATA ═══');
    sb.writeln(FoodContext(primaryFood).toPromptString());

    for (final cf in comparisonFoods) {
      sb.writeln('\n═══ COMPARISON FOOD FROM APP DATABASE ═══');
      sb.writeln(FoodContext(cf).toPromptString());
    }

    return sb.toString();
  }

  static List<FoodItem> _findComparisonFoods(String userMessage) {
    // Extract likely food names from comparison-intent phrases
    final patterns = [
      RegExp(r'compare\s+(?:with|to)\s+(.+?)(?:\?|$)', caseSensitive: false),
      RegExp(r'\bvs\.?\s+(.+?)(?:\?|$)', caseSensitive: false),
      RegExp(r'versus\s+(.+?)(?:\?|$)', caseSensitive: false),
      RegExp(r'than\s+(.+?)(?:\?|$)', caseSensitive: false),
      RegExp(r'compared\s+(?:with|to)\s+(.+?)(?:\?|$)', caseSensitive: false),
      RegExp(r'like\s+(.+?)(?:\?|$)', caseSensitive: false),
    ];

    final found = <FoodItem>[];
    final seen = <String>{};

    for (final pattern in patterns) {
      final match = pattern.firstMatch(userMessage);
      if (match == null) continue;
      final query = match.group(1)?.trim() ?? '';
      if (query.length < 3) continue;
      final results = LocalFoodRepository.search(query, limit: 1);
      if (results.isNotEmpty && !seen.contains(results.first.id)) {
        seen.add(results.first.id);
        found.add(results.first);
      }
    }

    return found;
  }
}
