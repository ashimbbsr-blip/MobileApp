import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../models/food_item.dart';
import '../models/chat_message.dart';
import '../services/gemini_ai_provider.dart';
import '../services/prompt_builder.dart';

@immutable
class ChatState {
  final List<ChatMessage> messages;
  final bool isStreaming;
  final String streamingText;
  final String? error;

  const ChatState({
    this.messages = const [],
    this.isStreaming = false,
    this.streamingText = '',
    this.error,
  });

  bool get hasMessages => messages.isNotEmpty;

  /// All non-error messages suitable for the Gemini history array.
  List<ChatMessage> get historyForApi =>
      messages.where((m) => !m.isError).toList();

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? isStreaming,
    String? streamingText,
    String? error,
    bool clearError = false,
  }) =>
      ChatState(
        messages: messages ?? this.messages,
        isStreaming: isStreaming ?? this.isStreaming,
        streamingText: streamingText ?? this.streamingText,
        error: clearError ? null : (error ?? this.error),
      );
}

class ChatNotifier extends StateNotifier<ChatState> {
  final FoodItem _food;
  final GeminiAIProvider _provider;
  static const _uuid = Uuid();
  String? _lastUserMessage;

  ChatNotifier(this._food)
      : _provider = GeminiAIProvider(),
        super(const ChatState());

  /// Send a new user message and stream the AI response.
  Future<void> sendMessage(String text) async {
    final trimmed = text.trim();
    if (state.isStreaming || trimmed.isEmpty) return;
    _lastUserMessage = trimmed;
    await _doSend(trimmed);
  }

  /// Re-send the last user message (regenerate).
  Future<void> regenerate() async {
    if (state.isStreaming || _lastUserMessage == null) return;
    // Remove last assistant message if present so we don't duplicate
    final msgs = state.messages.toList();
    if (msgs.isNotEmpty && msgs.last.role == MessageRole.assistant) {
      msgs.removeLast();
    }
    state = state.copyWith(messages: msgs, clearError: true);
    await _doSend(_lastUserMessage!);
  }

  Future<void> _doSend(String userText) async {
    final userMsg = ChatMessage(
      id: _uuid.v4(),
      role: MessageRole.user,
      content: userText,
      timestamp: DateTime.now(),
    );

    // Snapshot history before adding the new user message
    final historyBeforeThisMessage = state.historyForApi;

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamingText: '',
      clearError: true,
    );

    try {
      final systemPrompt = PromptBuilder.build(_food, userText);
      final stream = _provider.streamResponse(
        systemPrompt: systemPrompt,
        history: historyBeforeThisMessage,
        userMessage: userText,
      );

      final buf = StringBuffer();
      await for (final chunk in stream) {
        if (!mounted) return;
        buf.write(chunk);
        state = state.copyWith(
          streamingText: buf.toString(),
          isStreaming: true,
        );
      }

      if (!mounted) return;
      final finalText = buf.toString().trim();
      if (finalText.isEmpty) {
        throw const ChatAIException('No response received. Please try again.');
      }

      final assistantMsg = ChatMessage(
        id: _uuid.v4(),
        role: MessageRole.assistant,
        content: finalText,
        timestamp: DateTime.now(),
      );

      state = state.copyWith(
        messages: [...state.messages, assistantMsg],
        isStreaming: false,
        streamingText: '',
      );
    } catch (e) {
      if (!mounted) return;
      state = state.copyWith(
        isStreaming: false,
        streamingText: '',
        error: e.toString(),
      );
    }
  }

  void clearConversation() {
    _lastUserMessage = null;
    state = const ChatState();
  }

  @override
  void dispose() {
    _provider.dispose();
    super.dispose();
  }
}

/// Scoped per-food: each FoodItem gets its own isolated chat history.
final chatProvider =
    StateNotifierProvider.family<ChatNotifier, ChatState, FoodItem>(
  (ref, food) => ChatNotifier(food),
);
