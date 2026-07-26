import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../models/food_item.dart';
import '../models/chat_message.dart';
import '../providers/chat_provider.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Entry point: opens the chat bottom sheet
// ─────────────────────────────────────────────────────────────────────────────

void showNutritionChat(
  BuildContext context,
  FoodItem food,
  String lang, {
  String? prefill,
}) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _ChatSheetWrapper(food: food, lang: lang, prefill: prefill),
  );
}

class _ChatSheetWrapper extends ConsumerWidget {
  final FoodItem food;
  final String lang;
  final String? prefill;
  const _ChatSheetWrapper({required this.food, required this.lang, this.prefill});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DraggableScrollableSheet(
      initialChildSize: 0.72,
      minChildSize: 0.45,
      maxChildSize: 0.96,
      expand: false,
      snap: true,
      snapSizes: const [0.55, 0.72, 0.96],
      builder: (ctx, scrollCtrl) => _NutritionChatSheet(
        food: food,
        lang: lang,
        scrollController: scrollCtrl,
        prefill: prefill,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Main sheet widget
// ─────────────────────────────────────────────────────────────────────────────

class _NutritionChatSheet extends ConsumerStatefulWidget {
  final FoodItem food;
  final String lang;
  final ScrollController scrollController;
  final String? prefill;

  const _NutritionChatSheet({
    required this.food,
    required this.lang,
    required this.scrollController,
    this.prefill,
  });

  @override
  ConsumerState<_NutritionChatSheet> createState() =>
      _NutritionChatSheetState();
}

class _NutritionChatSheetState extends ConsumerState<_NutritionChatSheet> {
  final _textCtrl = TextEditingController();
  final _msgListCtrl = ScrollController();
  int _prevMsgCount = 0;

  @override
  void initState() {
    super.initState();
    if (widget.prefill != null && widget.prefill!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        ref.read(chatProvider(widget.food).notifier).sendMessage(widget.prefill!);
        _scrollToBottom();
      });
    }
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    _msgListCtrl.dispose();
    super.dispose();
  }

  void _send() {
    final text = _textCtrl.text.trim();
    if (text.isEmpty) return;
    _textCtrl.clear();
    ref.read(chatProvider(widget.food).notifier).sendMessage(text);
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_msgListCtrl.hasClients) {
        _msgListCtrl.animateTo(
          _msgListCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final bn = widget.lang == 'bn';
    final chat = ref.watch(chatProvider(widget.food));

    // Auto-scroll when new messages arrive
    if (chat.messages.length != _prevMsgCount) {
      _prevMsgCount = chat.messages.length;
      _scrollToBottom();
    }

    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Drag handle
          _DragHandle(isDark: isDark),

          // Header
          _ChatHeader(food: widget.food, bn: bn, isDark: isDark),

          const Divider(height: 1),

          // Message list
          Expanded(
            child: chat.messages.isEmpty && !chat.isStreaming
                ? _WelcomeState(food: widget.food, bn: bn, onChip: (q) {
                    ref
                        .read(chatProvider(widget.food).notifier)
                        .sendMessage(q);
                    _scrollToBottom();
                  })
                : _MessageList(
                    chat: chat,
                    food: widget.food,
                    bn: bn,
                    scrollController: _msgListCtrl,
                    onRegeneratePressed: () => ref
                        .read(chatProvider(widget.food).notifier)
                        .regenerate(),
                  ),
          ),

          // Error banner
          if (chat.error != null) _ErrorBanner(message: chat.error!, bn: bn),

          // Suggestion chips (after first exchange)
          if (chat.hasMessages && !chat.isStreaming)
            _SuggestionChips(
              bn: bn,
              onChip: (q) {
                ref.read(chatProvider(widget.food).notifier).sendMessage(q);
                _scrollToBottom();
              },
            ),

          const Divider(height: 1),

          // Input area
          _InputArea(
            controller: _textCtrl,
            bn: bn,
            isStreaming: chat.isStreaming,
            onSend: _send,
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Drag handle
// ─────────────────────────────────────────────────────────────────────────────

class _DragHandle extends StatelessWidget {
  final bool isDark;
  const _DragHandle({required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 40,
      height: 4,
      margin: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        color: isDark ? Colors.white24 : Colors.black12,
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Header
// ─────────────────────────────────────────────────────────────────────────────

class _ChatHeader extends ConsumerWidget {
  final FoodItem food;
  final bool bn;
  final bool isDark;
  const _ChatHeader(
      {required this.food, required this.bn, required this.isDark});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final displayName =
        bn && food.nameBn != null && food.nameBn!.isNotEmpty
            ? food.nameBn!
            : food.name;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 8, 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.auto_awesome, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  bn ? 'AI নিউট্রিশন সহকারী' : 'AI Nutrition Assistant',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.w700),
                ),
                Text(
                  displayName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF7C3AED),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          // Clear button
          Consumer(builder: (ctx, r, _) {
            final hasMessages = r.watch(
                chatProvider(food).select((s) => s.hasMessages));
            if (!hasMessages) return const SizedBox.shrink();
            return IconButton(
              icon: const Icon(Icons.delete_sweep_outlined, size: 22),
              tooltip: bn ? 'চ্যাট মুছুন' : 'Clear chat',
              onPressed: () => showDialog(
                context: ctx,
                builder: (d) => AlertDialog(
                  title: Text(bn ? 'চ্যাট মুছুন?' : 'Clear chat?'),
                  content: Text(bn
                      ? 'সব কথোপকথন মুছে যাবে।'
                      : 'All messages will be deleted.'),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(d),
                        child: Text(bn ? 'বাতিল' : 'Cancel')),
                    FilledButton(
                      onPressed: () {
                        r.read(chatProvider(food).notifier).clearConversation();
                        Navigator.pop(d);
                      },
                      style: FilledButton.styleFrom(
                          backgroundColor: Colors.red),
                      child: Text(bn ? 'মুছুন' : 'Clear'),
                    ),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Welcome / empty state
// ─────────────────────────────────────────────────────────────────────────────

class _WelcomeState extends StatelessWidget {
  final FoodItem food;
  final bool bn;
  final void Function(String) onChip;
  const _WelcomeState(
      {required this.food, required this.bn, required this.onChip});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final displayName =
        bn && food.nameBn != null && food.nameBn!.isNotEmpty
            ? food.nameBn!
            : food.name;

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
      child: Column(
        children: [
          // Illustration
          Container(
            padding: const EdgeInsets.all(20),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.auto_awesome,
                size: 40, color: Colors.white),
          ),
          const SizedBox(height: 16),
          Text(
            bn
                ? '"$displayName" সম্পর্কে কিছু জানতে চান?'
                : 'Ask me anything about "$displayName"',
            textAlign: TextAlign.center,
            style: theme.textTheme.titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            bn
                ? 'ডায়াবেটিস, ওজন কমানো, পুষ্টি, বিকল্প খাবার — সব জিজ্ঞেস করুন।'
                : 'Ask about health conditions, nutrition, weight loss, alternatives, and more.',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: Colors.grey.shade600, height: 1.4),
          ),
          const SizedBox(height: 20),
          _SuggestionChips(bn: bn, onChip: onChip, fullGrid: true),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Message list
// ─────────────────────────────────────────────────────────────────────────────

class _MessageList extends StatelessWidget {
  final ChatState chat;
  final FoodItem food;
  final bool bn;
  final ScrollController scrollController;
  final VoidCallback onRegeneratePressed;

  const _MessageList({
    required this.chat,
    required this.food,
    required this.bn,
    required this.scrollController,
    required this.onRegeneratePressed,
  });

  @override
  Widget build(BuildContext context) {
    final allItems = [
      ...chat.messages,
      if (chat.isStreaming || chat.streamingText.isNotEmpty) null, // streaming slot
    ];

    return ListView.builder(
      controller: scrollController,
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
      itemCount: allItems.length,
      itemBuilder: (ctx, i) {
        final msg = allItems[i];
        if (msg == null) {
          // Streaming bubble
          return _ChatBubble.streaming(
            text: chat.streamingText,
            bn: bn,
          );
        }
        final isLast = i == allItems.length - 1;
        return _ChatBubble(
          message: msg,
          bn: bn,
          showRegenerate: isLast &&
              msg.role == MessageRole.assistant &&
              !chat.isStreaming,
          onRegenerate: onRegeneratePressed,
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Individual chat bubble
// ─────────────────────────────────────────────────────────────────────────────

class _ChatBubble extends StatelessWidget {
  final ChatMessage? message;
  final String bn_; // workaround: named param
  final bool isStreamingBubble;
  final String streamingText;
  final bool showRegenerate;
  final VoidCallback? onRegenerate;

  const _ChatBubble({
    required this.message,
    required bool bn,
    this.showRegenerate = false,
    this.onRegenerate,
  })  : bn_ = bn ? 'bn' : 'en',
        isStreamingBubble = false,
        streamingText = '';

  const _ChatBubble.streaming({
    required String text,
    required bool bn,
  })  : message = null,
        bn_ = bn ? 'bn' : 'en',
        isStreamingBubble = true,
        streamingText = text,
        showRegenerate = false,
        onRegenerate = null;

  bool get _bn => bn_ == 'bn';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final isUser = !isStreamingBubble && message!.role == MessageRole.user;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            // AI avatar
            Container(
              width: 30,
              height: 30,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.auto_awesome,
                  color: Colors.white, size: 14),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                _buildBubbleContent(context, theme, isDark, isUser),
                const SizedBox(height: 3),
                _buildMeta(context, theme, isUser),
              ],
            ),
          ),
          if (isUser) const SizedBox(width: 4),
        ],
      ),
    );
  }

  Widget _buildBubbleContent(
      BuildContext ctx, ThemeData theme, bool isDark, bool isUser) {
    if (isStreamingBubble) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E2D3D) : Colors.grey.shade100,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(18),
            topRight: Radius.circular(18),
            bottomLeft: Radius.circular(4),
            bottomRight: Radius.circular(18),
          ),
        ),
        child: streamingText.isEmpty
            ? _TypingIndicator()
            : _MarkdownBubble(
                text: streamingText,
                isDark: isDark,
                isStreaming: true,
              ),
      );
    }

    if (isUser) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(18),
            topRight: Radius.circular(18),
            bottomLeft: Radius.circular(18),
            bottomRight: Radius.circular(4),
          ),
        ),
        child: Text(
          message!.content,
          style: const TextStyle(
              color: Colors.white, fontSize: 14.5, height: 1.4),
        ),
      );
    }

    // AI response
    return GestureDetector(
      onLongPress: () {
        Clipboard.setData(ClipboardData(text: message!.content));
        ScaffoldMessenger.of(ctx).showSnackBar(
          SnackBar(
            content: Text(_bn ? 'কপি হয়েছে' : 'Copied to clipboard'),
            duration: const Duration(seconds: 1),
            behavior: SnackBarBehavior.floating,
          ),
        );
      },
      child: Container(
        padding: const EdgeInsets.fromLTRB(14, 10, 10, 10),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E2D3D) : Colors.grey.shade100,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(18),
            bottomLeft: Radius.circular(18),
            bottomRight: Radius.circular(18),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _MarkdownBubble(text: message!.content, isDark: isDark),
            if (showRegenerate)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _ActionChip(
                      icon: Icons.copy_outlined,
                      label: _bn ? 'কপি' : 'Copy',
                      onTap: () {
                        Clipboard.setData(
                            ClipboardData(text: message!.content));
                        ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(
                          content:
                              Text(_bn ? 'কপি হয়েছে' : 'Copied'),
                          duration: const Duration(seconds: 1),
                          behavior: SnackBarBehavior.floating,
                        ));
                      },
                    ),
                    const SizedBox(width: 6),
                    _ActionChip(
                      icon: Icons.refresh_rounded,
                      label: _bn ? 'আবার তৈরি' : 'Regenerate',
                      onTap: onRegenerate,
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMeta(BuildContext ctx, ThemeData theme, bool isUser) {
    if (isStreamingBubble) return const SizedBox.shrink();
    final time = DateFormat('h:mm a').format(message!.timestamp);
    return Padding(
      padding: EdgeInsets.only(left: isUser ? 0 : 38, right: isUser ? 4 : 0),
      child: Text(
        time,
        style: TextStyle(fontSize: 10.5, color: Colors.grey.shade500),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Markdown renderer
// ─────────────────────────────────────────────────────────────────────────────

class _MarkdownBubble extends StatelessWidget {
  final String text;
  final bool isDark;
  final bool isStreaming;

  const _MarkdownBubble({
    required this.text,
    required this.isDark,
    this.isStreaming = false,
  });

  @override
  Widget build(BuildContext context) {
    final baseStyle = TextStyle(
      fontSize: 14.5,
      height: 1.45,
      color: isDark ? Colors.white.withValues(alpha: 0.87) : Colors.black87,
    );

    final displayText = isStreaming ? '$text▋' : text;

    return MarkdownBody(
      data: displayText,
      selectable: true,
      styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
        p: baseStyle,
        strong:
            baseStyle.copyWith(fontWeight: FontWeight.w700),
        em: baseStyle.copyWith(fontStyle: FontStyle.italic),
        code: baseStyle.copyWith(
          fontFamily: 'monospace',
          fontSize: 13,
          backgroundColor:
              isDark ? Colors.white12 : Colors.black.withValues(alpha: 0.07),
        ),
        codeblockDecoration: BoxDecoration(
          color: isDark ? Colors.black26 : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(8),
        ),
        listBullet: baseStyle,
        blockquote: baseStyle.copyWith(
            color: isDark ? Colors.white54 : Colors.black45),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Typing indicator (animated dots)
// ─────────────────────────────────────────────────────────────────────────────

class _TypingIndicator extends StatefulWidget {
  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (i) {
            final phase = (_ctrl.value - i * 0.2).clamp(0.0, 1.0);
            final opacity = (math.sin(phase * math.pi)).clamp(0.2, 1.0);
            return Container(
              width: 7,
              height: 7,
              margin: const EdgeInsets.symmetric(horizontal: 2),
              decoration: BoxDecoration(
                color: const Color(0xFF7C3AED).withValues(alpha: opacity),
                shape: BoxShape.circle,
              ),
            );
          }),
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Suggestion chips
// ─────────────────────────────────────────────────────────────────────────────

class _SuggestionChips extends StatelessWidget {
  final bool bn;
  final void Function(String) onChip;
  final bool fullGrid;

  const _SuggestionChips({
    required this.bn,
    required this.onChip,
    this.fullGrid = false,
  });

  static const _suggestionsEn = [
    'Is this healthy?',
    'Is this good for weight loss?',
    'High in protein?',
    'Can diabetics eat this?',
    'Is this safe for pregnancy?',
    'Good for kids?',
    'Post-gym food?',
    'What are the benefits?',
    'Healthier alternatives?',
    'Can I eat this daily?',
    'Is this keto friendly?',
    'Gluten free?',
  ];

  static const _suggestionsBn = [
    'এটা কি স্বাস্থ্যকর?',
    'ওজন কমাতে কি ভালো?',
    'প্রোটিন বেশি?',
    'ডায়াবেটিস রোগীরা খেতে পারবেন?',
    'গর্ভাবস্থায় নিরাপদ?',
    'শিশুদের জন্য ভালো?',
    'ব্যায়ামের পরে খাওয়া যাবে?',
    'এর উপকারিতা কী?',
    'স্বাস্থ্যকর বিকল্প কী?',
    'প্রতিদিন খাওয়া যাবে?',
    'কিটো ডায়েটে চলে?',
    'গ্লুটেন মুক্ত?',
  ];

  @override
  Widget build(BuildContext context) {
    final suggestions = bn ? _suggestionsBn : _suggestionsEn;

    if (fullGrid) {
      return Wrap(
        spacing: 8,
        runSpacing: 8,
        children: suggestions
            .map((s) => _Chip(label: s, onTap: () => onChip(s)))
            .toList(),
      );
    }

    return SizedBox(
      height: 38,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.fromLTRB(12, 4, 12, 4),
        itemCount: suggestions.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) =>
            _Chip(label: suggestions[i], onTap: () => onChip(suggestions[i])),
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _Chip({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isDark
              ? const Color(0xFF7C3AED).withValues(alpha: 0.15)
              : const Color(0xFF7C3AED).withValues(alpha: 0.09),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: const Color(0xFF7C3AED).withValues(alpha: 0.35),
          ),
        ),
        child: Text(
          label,
          style: const TextStyle(
            fontSize: 12.5,
            color: Color(0xFF7C3AED),
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Error banner
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorBanner extends StatelessWidget {
  final String message;
  final bool bn;
  const _ErrorBanner({required this.message, required this.bn});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(12, 4, 12, 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.red.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded,
              size: 16, color: Colors.red),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(fontSize: 12.5, color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Input area
// ─────────────────────────────────────────────────────────────────────────────

class _InputArea extends StatelessWidget {
  final TextEditingController controller;
  final bool bn;
  final bool isStreaming;
  final VoidCallback onSend;

  const _InputArea({
    required this.controller,
    required this.bn,
    required this.isStreaming,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 10,
        bottom: MediaQuery.of(context).viewInsets.bottom + 12,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E2D3D) : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                    color: isDark ? Colors.white12 : Colors.grey.shade300),
              ),
              child: TextField(
                controller: controller,
                maxLines: 5,
                minLines: 1,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => isStreaming ? null : onSend(),
                decoration: InputDecoration(
                  hintText: bn
                      ? 'প্রশ্ন লিখুন…'
                      : 'Ask a nutrition question…',
                  hintStyle:
                      TextStyle(color: Colors.grey.shade500, fontSize: 14),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 10),
                ),
                style: const TextStyle(fontSize: 14.5),
              ),
            ),
          ),
          const SizedBox(width: 8),
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            decoration: BoxDecoration(
              gradient: isStreaming
                  ? const LinearGradient(
                      colors: [Colors.grey, Colors.grey])
                  : const LinearGradient(
                      colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
              shape: BoxShape.circle,
            ),
            child: IconButton(
              onPressed: isStreaming ? null : onSend,
              icon: isStreaming
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.send_rounded,
                      color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Small action chip (copy / regenerate)
// ─────────────────────────────────────────────────────────────────────────────

class _ActionChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  const _ActionChip(
      {required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.grey.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 13, color: Colors.grey.shade600),
            const SizedBox(width: 4),
            Text(label,
                style: TextStyle(
                    fontSize: 11.5,
                    color: Colors.grey.shade600,
                    fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}
