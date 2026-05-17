import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import 'legal_content.dart';

class LegalContentScreen extends ConsumerWidget {
  final LegalDocType type;
  const LegalContentScreen({super.key, required this.type});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final lang = l10n.language;
    final sections = LegalContent.getSections(type, lang);
    final theme = Theme.of(context);

    String title;
    switch (type) {
      case LegalDocType.terms:
        title = l10n.legalTerms;
      case LegalDocType.privacy:
        title = l10n.legalPrivacy;
      case LegalDocType.health:
        title = l10n.legalHealth;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        centerTitle: false,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 40),
        itemCount: sections.length,
        itemBuilder: (context, i) {
          final section = sections[i];
          return _SectionCard(section: section, theme: theme, isFirst: i == 0);
        },
      ),
    );
  }
}

class _SectionCard extends StatefulWidget {
  final LegalSection section;
  final ThemeData theme;
  final bool isFirst;

  const _SectionCard({
    required this.section,
    required this.theme,
    required this.isFirst,
  });

  @override
  State<_SectionCard> createState() => _SectionCardState();
}

class _SectionCardState extends State<_SectionCard> {
  late bool _expanded;

  @override
  void initState() {
    super.initState();
    _expanded = widget.isFirst;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      clipBehavior: Clip.hardEdge,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      widget.section.heading,
                      style: widget.theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                  AnimatedRotation(
                    turns: _expanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 200),
                    child: const Icon(Icons.keyboard_arrow_down,
                        size: 20, color: AppColors.primary),
                  ),
                ],
              ),
            ),
          ),
          AnimatedCrossFade(
            firstChild: const SizedBox.shrink(),
            secondChild: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Divider(height: 1, indent: 16, endIndent: 16),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                  child: Text(
                    widget.section.body,
                    style: widget.theme.textTheme.bodySmall?.copyWith(
                      height: 1.7,
                      color: widget.theme.colorScheme.onSurface.withValues(alpha: 0.85),
                    ),
                  ),
                ),
              ],
            ),
            crossFadeState:
                _expanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 220),
          ),
        ],
      ),
    );
  }
}
