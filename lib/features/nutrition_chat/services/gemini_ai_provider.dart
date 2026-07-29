import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show debugPrint;

import '../../../core/constants/app_constants.dart';
import '../../../services/api_key_service.dart';
import '../models/chat_message.dart';
import 'ai_provider.dart';

class ChatAIException implements Exception {
  final String message;
  final bool isKeyError;
  final bool isOffline;
  final bool isRateLimit;

  const ChatAIException(
    this.message, {
    this.isKeyError = false,
    this.isOffline = false,
    this.isRateLimit = false,
  });

  @override
  String toString() => message;
}

/// Gemini implementation of [AIProvider] using SSE streaming.
class GeminiAIProvider implements AIProvider {
  final Dio _dio;

  GeminiAIProvider()
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.geminiBaseUrl,
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 90),
        ));

  @override
  Stream<String> streamResponse({
    required String systemPrompt,
    required List<ChatMessage> history,
    required String userMessage,
  }) async* {
    final key = ApiKeyService.instance.activeGeminiKey;
    if (key.isEmpty) {
      throw const ChatAIException(
        'No Gemini API key configured. Add one in Settings.',
        isKeyError: true,
      );
    }

    // Build Gemini-format conversation history
    final contents = <Map<String, dynamic>>[];
    for (final msg in history) {
      if (msg.isError) continue;
      contents.add({
        'role': msg.role == MessageRole.user ? 'user' : 'model',
        'parts': [
          {'text': msg.content}
        ],
      });
    }
    contents.add({
      'role': 'user',
      'parts': [
        {'text': userMessage}
      ],
    });

    final payload = {
      'system_instruction': {
        'parts': [
          {'text': systemPrompt}
        ],
      },
      'contents': contents,
      'generationConfig': {
        'temperature': 0.7,
        'maxOutputTokens': 1024,
        'topP': 0.9,
      },
    };

    try {
      final response = await _dio.post<ResponseBody>(
        '/models/${AppConstants.geminiModel}:streamGenerateContent',
        queryParameters: {'key': key, 'alt': 'sse'},
        data: payload,
        options: Options(responseType: ResponseType.stream),
      );

      final lineBuf = StringBuffer();

      await for (final chunk in response.data!.stream) {
        lineBuf.write(utf8.decode(chunk, allowMalformed: true));

        // Process all complete newline-terminated lines
        String remaining = lineBuf.toString();
        while (remaining.contains('\n')) {
          final idx = remaining.indexOf('\n');
          final line = remaining.substring(0, idx).trim();
          remaining = remaining.substring(idx + 1);

          if (line.startsWith('data: ')) {
            final jsonStr = line.substring(6).trim();
            if (jsonStr.isEmpty) continue;
            try {
              final data = json.decode(jsonStr) as Map<String, dynamic>;
              final text =
                  data['candidates']?[0]?['content']?['parts']?[0]?['text'];
              if (text is String && text.isNotEmpty) {
                yield text;
              }
            } catch (e) {
              debugPrint('[GeminiAIProvider] parse error: $e');
            }
          }
        }

        lineBuf.clear();
        lineBuf.write(remaining);
      }
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  ChatAIException _mapError(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return const ChatAIException(
        'No internet connection. AI requires an internet connection.',
        isOffline: true,
      );
    }
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return const ChatAIException('Request timed out. Please try again.');
    }
    final status = e.response?.statusCode;
    if (status == 429) {
      return const ChatAIException(
        'Too many requests. Please wait a moment and try again.',
        isRateLimit: true,
      );
    }
    if (status == 400 || status == 401 || status == 403) {
      return const ChatAIException(
        'API key error. Check your Gemini API key in Settings.',
        isKeyError: true,
      );
    }
    return ChatAIException(
        'AI error (HTTP ${status ?? 'unknown'}). Please try again.');
  }

  @override
  void dispose() => _dio.close(force: true);
}
