import '../models/chat_message.dart';

/// Abstract AI provider interface — swap Gemini for OpenAI/Claude/Groq
/// without touching the UI by creating a new implementation of this class.
abstract class AIProvider {
  /// Streams partial text chunks as the model generates its response.
  Stream<String> streamResponse({
    required String systemPrompt,
    required List<ChatMessage> history,
    required String userMessage,
  });

  void dispose();
}
