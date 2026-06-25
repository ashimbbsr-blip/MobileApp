import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/backup/archive_engine.dart';
import '../../services/backup/backup_schema.dart';
import '../../services/backup/backup_types.dart';
import '../../services/backup/import_service.dart';
import '../../services/backup/storage_stats_service.dart';
import '../../theme/app_colors.dart';
import 'providers/backup_provider.dart';

class BackupArchiveScreen extends ConsumerWidget {
  const BackupArchiveScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(backupControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Backup & Archive'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh',
            onPressed: state.busy
                ? null
                : () => ref.read(backupControllerProvider.notifier).load(),
          ),
        ],
      ),
      body: Stack(
        children: [
          if (state.loading && state.stats == null)
            const Center(child: CircularProgressIndicator())
          else
            RefreshIndicator(
              onRefresh: () =>
                  ref.read(backupControllerProvider.notifier).load(),
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 40),
                children: [
                  _BackupHealthBanner(stats: state.stats),
                  const SizedBox(height: 14),
                  _BackupRestoreSection(stats: state.stats),
                  const SizedBox(height: 12),
                  const _ExportSection(),
                  const SizedBox(height: 12),
                  _ArchiveSection(candidates: state.candidates),
                  const SizedBox(height: 12),
                  _StorageSection(stats: state.stats),
                  const SizedBox(height: 12),
                  _DataHealthSection(stats: state.stats),
                ],
              ),
            ),
          if (state.busy)
            _BusyOverlay(progress: state.progress, message: state.message),
        ],
      ),
    );
  }
}

// ── Backup Health Banner ──────────────────────────────────────────────────────

class _BackupHealthBanner extends StatelessWidget {
  final StorageStats? stats;
  const _BackupHealthBanner({required this.stats});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final last = stats?.lastBackupAt;
    final color = _statusColor(last);
    final icon = _statusIcon(last);
    final headline = _headline(last);
    final sub = _subline(last);
    final sizeText = stats != null && stats!.compressedBytes > 0
        ? StorageStats.formatBytes(stats!.compressedBytes)
        : null;

    return Card(
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: color.withValues(alpha: 0.4), width: 1.2),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 26),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    headline,
                    style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700, color: color),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    sub,
                    style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface
                            .withValues(alpha: 0.65)),
                  ),
                ],
              ),
            ),
            if (sizeText != null) ...[
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(sizeText,
                      style: theme.textTheme.labelLarge
                          ?.copyWith(fontWeight: FontWeight.w700)),
                  Text('backup size',
                      style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.5))),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _statusColor(DateTime? last) {
    if (last == null) return Colors.red;
    final days = DateTime.now().difference(last).inDays;
    if (days <= 7) return Colors.green;
    if (days <= 30) return Colors.orange;
    return Colors.red;
  }

  IconData _statusIcon(DateTime? last) {
    if (last == null) return Icons.warning_amber_rounded;
    final days = DateTime.now().difference(last).inDays;
    if (days <= 7) return Icons.verified_user_rounded;
    if (days <= 30) return Icons.shield_outlined;
    return Icons.warning_rounded;
  }

  String _headline(DateTime? last) {
    if (last == null) return 'No backup created yet';
    final days = DateTime.now().difference(last).inDays;
    if (days <= 7) return 'Data is protected';
    if (days <= 30) return 'Backup recommended';
    return 'Backup overdue';
  }

  String _subline(DateTime? last) {
    if (last == null) return 'Create a backup to protect your health journey.';
    final days = DateTime.now().difference(last).inDays;
    if (days == 0) return 'Backed up today — your data is safe.';
    if (days == 1) return 'Last backup: yesterday.';
    if (days <= 7) return 'Last backup: $days days ago.';
    if (days <= 30) return 'Last backup: $days days ago — back up soon.';
    return 'Last backup: $days days ago — your data is at risk!';
  }
}

// ── 1. Backup & Restore ───────────────────────────────────────────────────────

class _BackupRestoreSection extends ConsumerWidget {
  final StorageStats? stats;
  const _BackupRestoreSection({required this.stats});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lastBackup = stats?.lastBackupAt;
    return _SectionCard(
      icon: Icons.backup_outlined,
      title: 'Backup & Restore',
      subtitle: 'Compressed .iht file — works fully offline, no cloud needed',
      children: [
        _ActionTile(
          icon: Icons.save_alt_rounded,
          title: 'Create Backup',
          subtitle: lastBackup != null
              ? 'Last: ${_fmtDate(lastBackup)} · Share to Files, Drive or email'
              : 'Recommended — share to Files, Drive or email',
          color: AppColors.primary,
          onTap: () async {
            final outcome = await ref
                .read(backupControllerProvider.notifier)
                .createBackup();
            if (!context.mounted) return;
            _toast(
              context,
              outcome.success
                  ? 'Backup created & shared ✓'
                  : (outcome.error ?? 'Backup failed'),
              outcome.success,
            );
          },
        ),
        const Divider(height: 1),
        _ActionTile(
          icon: Icons.restore_rounded,
          title: 'Import / Restore',
          subtitle: 'Full replace or smart merge from an .iht backup file',
          color: Colors.teal,
          onTap: () => _startImport(context, ref),
        ),
      ],
    );
  }

  Future<void> _startImport(BuildContext context, WidgetRef ref) async {
    final picked = await ImportService.pickAndValidate();
    if (picked.validation == null) return;
    if (!context.mounted) return;
    final v = picked.validation!;
    if (!v.ok) {
      _toast(context, v.error ?? 'Invalid backup file', false);
      return;
    }
    final mode = await _chooseMode(context, v);
    if (mode == null || !context.mounted) return;
    final outcome = await ref
        .read(backupControllerProvider.notifier)
        .restore(v, mode);
    if (!context.mounted) return;
    if (outcome.success && outcome.mergeReport != null) {
      final r = outcome.mergeReport!;
      _toast(
          context,
          'Merged: +${r.totalAdded} added, ${r.totalSkipped} skipped ✓',
          true);
    } else {
      _toast(
        context,
        outcome.success
            ? 'Restore complete ✓'
            : (outcome.error ?? 'Restore failed'),
        outcome.success,
      );
    }
  }

  Future<ImportMode?> _chooseMode(
      BuildContext context, BackupValidation v) {
    final created =
        v.createdAt != null ? _fmtDate(v.createdAt!) : 'unknown date';
    return showDialog<ImportMode>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Choose restore mode'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _InfoRow('Created', created),
            _InfoRow('App version', v.appVersion),
            _InfoRow('Total records', '${v.totalRecords}'),
            const SizedBox(height: 14),
            const _ModeCard(
              icon: Icons.sync_alt_rounded,
              color: Colors.teal,
              title: 'Merge',
              description:
                  'Keeps your current data and adds non-duplicate records from this backup. Safe for combining history from multiple devices.',
            ),
            const SizedBox(height: 8),
            const _ModeCard(
              icon: Icons.delete_sweep_rounded,
              color: Colors.red,
              title: 'Replace',
              description:
                  'Wipes all current data and fully restores this backup. Use for new phone migration.',
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, ImportMode.merge),
            child: const Text('Merge'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, ImportMode.replace),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Replace'),
          ),
        ],
      ),
    );
  }
}

// ── 2. Export Reports ─────────────────────────────────────────────────────────

class _ExportSection extends ConsumerWidget {
  const _ExportSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return _SectionCard(
      icon: Icons.assessment_outlined,
      title: 'Export Reports',
      subtitle: 'Professional report for your nutritionist, doctor or trainer',
      children: [
        _ActionTile(
          icon: Icons.table_view_rounded,
          title: 'Excel Report (.xlsx)',
          subtitle:
              'Profile · Daily · Monthly · Yearly · Weight · Water · Health Insights',
          color: Colors.green.shade700,
          onTap: () async {
            final o = await ref
                .read(backupControllerProvider.notifier)
                .exportXlsx();
            if (!context.mounted) return;
            _toast(
              context,
              o.success ? 'Report exported ✓' : (o.error ?? 'Export failed'),
              o.success,
            );
          },
        ),
      ],
    );
  }
}

// ── 3. Archive Management ─────────────────────────────────────────────────────

class _ArchiveSection extends ConsumerWidget {
  final List<ArchiveCandidate> candidates;
  const _ArchiveSection({required this.candidates});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final actionable = candidates.where((c) => c.hasWork).toList();
    return _SectionCard(
      icon: Icons.inventory_2_outlined,
      title: 'Archive Management',
      subtitle: 'Compress old records — preserve trends, free storage',
      trailing: IconButton(
        icon: const Icon(Icons.info_outline, size: 18),
        tooltip: 'How archiving works',
        onPressed: () => _showInfo(context),
        padding: const EdgeInsets.all(8),
        constraints: const BoxConstraints(),
      ),
      children: [
        if (actionable.isEmpty)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
            child: Row(
              children: [
                Icon(Icons.check_circle_outline,
                    color: Colors.green.shade600, size: 18),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'Everything is up to date. Detailed records under 12 months are always kept in full.',
                    style: TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
          )
        else
          for (final c in actionable) ...[
            _ArchiveTile(candidate: c),
            if (c != actionable.last) const Divider(height: 1),
          ],
      ],
    );
  }

  void _showInfo(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('How archiving works'),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Archiving compresses old records to save storage '
                'while preserving your health journey. Your trends, '
                'progress and scores are never lost.',
              ),
              SizedBox(height: 16),
              _LevelCard(
                icon: Icons.looks_one_rounded,
                color: Colors.blue,
                label: 'Level 1 — After 12 months',
                desc:
                    'Individual meal logs → compact daily summaries. Calories, protein, water and score are preserved.',
              ),
              SizedBox(height: 8),
              _LevelCard(
                icon: Icons.looks_two_rounded,
                color: Colors.orange,
                label: 'Level 2 — After 24 months',
                desc:
                    'Daily summaries → monthly averages. Trends and consistency scores are kept.',
              ),
              SizedBox(height: 8),
              _LevelCard(
                icon: Icons.looks_3_rounded,
                color: Colors.red,
                label: 'Level 3 — After 5 years',
                desc:
                    'Monthly records → a single yearly entry. Key health metrics and weight change are retained.',
              ),
            ],
          ),
        ),
        actions: [
          FilledButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Got it')),
        ],
      ),
    );
  }
}

class _LevelCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  final String desc;
  const _LevelCard(
      {required this.icon,
      required this.color,
      required this.label,
      required this.desc});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label,
                  style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                      color: color)),
              Text(desc,
                  style: const TextStyle(fontSize: 12, height: 1.4)),
            ],
          ),
        ),
      ],
    );
  }
}

class _ArchiveTile extends ConsumerWidget {
  final ArchiveCandidate candidate;
  const _ArchiveTile({required this.candidate});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final color = _color(candidate.level);
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withValues(alpha: 0.12),
        child: Icon(Icons.compress_rounded, color: color, size: 20),
      ),
      title: Text(candidate.title,
          style:
              const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      subtitle: Text(
        '${candidate.description}\n'
        '≈ ${StorageStats.formatBytes(candidate.estimatedBytesSaved)} freed',
        style: const TextStyle(fontSize: 12, height: 1.4),
      ),
      isThreeLine: true,
      trailing: const Icon(Icons.chevron_right),
      onTap: () => _confirm(context, ref),
    );
  }

  Color _color(ArchiveLevel level) {
    switch (level) {
      case ArchiveLevel.level1:
        return Colors.blue;
      case ArchiveLevel.level2:
        return Colors.orange;
      case ArchiveLevel.level3:
        return Colors.red;
    }
  }

  Future<void> _confirm(BuildContext context, WidgetRef ref) async {
    final choice = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Archive & compress?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(candidate.description),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.storage, size: 16, color: Colors.grey),
                const SizedBox(width: 6),
                Text(
                  '≈ ${StorageStats.formatBytes(candidate.estimatedBytesSaved)} storage freed',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                    color: Colors.amber.withValues(alpha: 0.4)),
              ),
              child: const Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.info_outline,
                      size: 16, color: Colors.amber),
                  SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Trends and progress are preserved. Export a backup first to keep full-detail records.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Keep Detailed Data')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'export'),
            child: const Text('Export & Archive'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, 'archive'),
            child: const Text('Archive Only'),
          ),
        ],
      ),
    );
    if (choice == null || !context.mounted) return;
    final notifier = ref.read(backupControllerProvider.notifier);
    if (choice == 'export') {
      await notifier.createBackup();
      if (!context.mounted) return;
    }
    final outcome = await notifier.archive(candidate.level);
    if (!context.mounted) return;
    _toast(
      context,
      outcome.success
          ? 'Archived & compressed ✓'
          : (outcome.error ?? 'Archive failed'),
      outcome.success,
    );
  }
}

// ── 4. Storage Usage ──────────────────────────────────────────────────────────

class _StorageSection extends StatelessWidget {
  final StorageStats? stats;
  const _StorageSection({required this.stats});

  @override
  Widget build(BuildContext context) {
    final s = stats;
    final subtitle = s == null
        ? ''
        : '${StorageStats.formatBytes(s.rawBytes)} raw  →  '
            '${StorageStats.formatBytes(s.compressedBytes)} compressed';
    return _SectionCard(
      icon: Icons.sd_storage_outlined,
      title: 'Storage Usage',
      subtitle: subtitle,
      children: [
        if (s != null)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
            child: Column(
              children: [
                _StatRow('Uncompressed data size',
                    StorageStats.formatBytes(s.rawBytes)),
                _StatRow('Backup file size (.iht)',
                    StorageStats.formatBytes(s.compressedBytes)),
                _StatRow(
                  'Compression savings',
                  '${s.savingsPercent.toStringAsFixed(1)}%'
                  ' (${StorageStats.formatBytes(s.rawBytes - s.compressedBytes)} saved)',
                ),
                const SizedBox(height: 10),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: (s.savingsPercent / 100).clamp(0.0, 1.0),
                    minHeight: 10,
                    backgroundColor: AppColors.primary.withValues(alpha: 0.13),
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Compressed',
                        style: TextStyle(
                            fontSize: 11,
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600)),
                    Text('Uncompressed',
                        style: TextStyle(
                            fontSize: 11,
                            color:
                                AppColors.primary.withValues(alpha: 0.45))),
                  ],
                ),
              ],
            ),
          ),
      ],
    );
  }
}

// ── 5. Data Health ────────────────────────────────────────────────────────────

class _DataHealthSection extends StatelessWidget {
  final StorageStats? stats;
  const _DataHealthSection({required this.stats});

  @override
  Widget build(BuildContext context) {
    final s = stats;
    return _SectionCard(
      icon: Icons.health_and_safety_outlined,
      title: 'Data Health',
      subtitle: 'Record counts and last activity',
      children: [
        if (s != null)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
            child: Column(
              children: [
                _StatRow('Total records', '${s.totalRecords}',
                    bold: true),
                const Divider(height: 14, thickness: 0.5),
                _StatRow('Active food logs', '${s.mealCount}'),
                _StatRow('Custom foods', '${s.customFoodCount}'),
                _StatRow(
                    'Archived daily summaries', '${s.dailySummaryCount}'),
                _StatRow(
                    'Monthly summaries', '${s.monthlySummaryCount}'),
                _StatRow('Yearly summaries', '${s.yearlySummaryCount}'),
                _StatRow('Weight entries', '${s.weightCount}'),
                _StatRow('Water log days', '${s.waterCount}'),
                const Divider(height: 14, thickness: 0.5),
                _StatRow('Last backup', _fmtDate(s.lastBackupAt)),
                _StatRow('Last archive', _fmtDate(s.lastArchiveAt)),
              ],
            ),
          ),
      ],
    );
  }
}

// ── Shared widgets ────────────────────────────────────────────────────────────

class _SectionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Widget? trailing;
  final List<Widget> children;
  const _SectionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.trailing,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 8, 8),
            child: Row(
              children: [
                Icon(icon, color: AppColors.primary, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: theme.textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.w700)),
                      if (subtitle.isNotEmpty)
                        Text(
                          subtitle,
                          style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface
                                  .withValues(alpha: 0.6)),
                        ),
                    ],
                  ),
                ),
                if (trailing != null) trailing!,
              ],
            ),
          ),
          ...children,
        ],
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;
  const _ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withValues(alpha: 0.12),
        child: Icon(icon, color: color, size: 22),
      ),
      title: Text(title,
          style:
              const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}

class _StatRow extends StatelessWidget {
  final String label;
  final String value;
  final bool bold;
  const _StatRow(this.label, this.value, {this.bold = false});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color:
                  theme.colorScheme.onSurface.withValues(alpha: bold ? 1.0 : 0.7),
              fontWeight: bold ? FontWeight.w700 : FontWeight.normal,
            ),
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Text('$label: ',
              style: const TextStyle(
                  fontWeight: FontWeight.w600, fontSize: 13)),
          Expanded(
              child: Text(value,
                  style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}

class _ModeCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String description;
  const _ModeCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: color)),
                const SizedBox(height: 2),
                Text(description,
                    style: const TextStyle(fontSize: 12, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BusyOverlay extends StatelessWidget {
  final double progress;
  final String message;
  const _BusyOverlay({required this.progress, required this.message});

  @override
  Widget build(BuildContext context) {
    final pct = progress > 0 && progress < 1;
    return Positioned.fill(
      child: ColoredBox(
        color: Colors.black54,
        child: Center(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(28, 28, 28, 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 60,
                    height: 60,
                    child: CircularProgressIndicator(
                      value: pct ? progress : null,
                      strokeWidth: 3,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    message.isEmpty ? 'Working…' : message,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  if (pct) ...[
                    const SizedBox(height: 6),
                    Text(
                      '${(progress * 100).toInt()}%',
                      style: const TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w700,
                          fontSize: 13),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

String _fmtDate(DateTime? d) {
  if (d == null) return 'Never';
  final now = DateTime.now();
  final diff = now.difference(d).inDays;
  if (diff == 0) return 'Today';
  if (diff == 1) return 'Yesterday';
  return '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
}

void _toast(BuildContext context, String message, bool ok) {
  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: Text(message),
    backgroundColor: ok ? AppColors.primary : Colors.red,
    behavior: SnackBarBehavior.floating,
    margin: const EdgeInsets.all(16),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
  ));
}
