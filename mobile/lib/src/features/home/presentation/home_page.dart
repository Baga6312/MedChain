import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/presentation/session_provider.dart';
import '../../dashboard/data/dashboard_repository.dart';
import '../../../shared/network/api_client.dart';
import '../../../shared/theme/theme_provider.dart';
import '../../../shared/config/api_config.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>(
  (ref) => DashboardRepository(ref.watch(apiClientProvider)),
);

final episodesProvider = FutureProvider.autoDispose<List<TreatmentEpisode>>(
  (ref) => ref.watch(dashboardRepositoryProvider).episodes(),
);

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  final _timelines = <int, AsyncValue<TreatmentTimeline>>{};
  final _selectedPhases = <int, int>{};

  Future<void> _toggleTimeline(int episodeId) async {
    if (_timelines[episodeId] != null) {
      setState(() {
        _timelines.remove(episodeId);
        _selectedPhases.remove(episodeId);
      });
      return;
    }
    setState(() => _timelines[episodeId] = const AsyncLoading());
    try {
      final timeline =
          await ref.read(dashboardRepositoryProvider).timeline(episodeId);
      if (mounted) {
        setState(() => _timelines[episodeId] = AsyncData(timeline));
      }
    } catch (error, stackTrace) {
      if (mounted) {
        setState(
          () => _timelines[episodeId] = AsyncError(error, stackTrace),
        );
      }
    }
  }

  Future<void> _changeStatus(int episodeId, String status) async {
    try {
      await ref.read(dashboardRepositoryProvider).changeStatus(episodeId, status);
      ref.invalidate(episodesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Treatment updated.')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Unable to update treatment.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(sessionProvider).valueOrNull;
    final episodes = ref.watch(episodesProvider);
    final isDoctor = user?.role == 'doctor';

    return Scaffold(
      appBar: AppBar(
        title: Text(isDoctor ? 'Doctor space' : 'Patient space'),
        actions: [
          IconButton(
            tooltip: Theme.of(context).brightness == Brightness.dark
                ? 'Use light theme'
                : 'Use dark theme',
            onPressed: () => ref.read(themeModeProvider.notifier).toggle(),
            icon: Icon(
              Theme.of(context).brightness == Brightness.dark
                  ? Icons.light_mode
                  : Icons.dark_mode,
            ),
          ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => ref.read(sessionProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            UserAccountsDrawerHeader(
              accountName: Text(user?.displayName ?? 'MedChain user'),
              accountEmail: Text(user?.email ?? ''),
              currentAccountPicture: _UserAvatar(user?.avatarUrl ?? '', user?.displayName ?? ''),
            ),
            ListTile(
              leading: const Icon(Icons.medical_information_outlined),
              title: Text(isDoctor ? 'My patients' : 'My treatments'),
              selected: true,
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('My profile'),
              onTap: () {
                Navigator.pop(context);
                context.pushNamed('profile');
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Sign out'),
              onTap: () => ref.read(sessionProvider.notifier).logout(),
            ),
          ],
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(episodesProvider),
        child: episodes.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => ListView(
            children: [
              Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  'Unable to load treatments. Pull to retry.',
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            ],
          ),
          data: (items) => items.isEmpty
              ? ListView(
                  children: const [
                    SizedBox(height: 180),
                    Center(child: Text('No treatments associated yet.')),
                  ],
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Text(
                      'Hello, ${user?.displayName ?? 'there'}',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isDoctor
                          ? 'Follow your patients and their treatment progress.'
                          : 'Follow your treatment progress and care team.',
                    ),
                    const SizedBox(height: 20),
                    ...items.map((episode) => _EpisodeCard(
                          episode: episode,
                          isDoctor: isDoctor,
                          timeline: _timelines[episode.id],
                          selectedPhase: _selectedPhases[episode.id],
                          onToggleTimeline: () => _toggleTimeline(episode.id),
                          onSelectPhase: (phaseId) => setState(
                            () => _selectedPhases[episode.id] = phaseId,
                          ),
                          onChangeStatus: (status) =>
                              _changeStatus(episode.id, status),
                        )),
                  ],
                ),
        ),
      ),
    );
  }

}

class _UserAvatar extends StatelessWidget {
  const _UserAvatar(this.path, this.name);

  final String path;
  final String name;

  @override
  Widget build(BuildContext context) {
    final imageUrl = path.isEmpty
        ? null
        : path.startsWith('http')
            ? path
            : '${ApiConfig.baseUrl.replaceFirst('/api', '')}$path';
    return CircleAvatar(
      backgroundImage: imageUrl == null ? null : NetworkImage(imageUrl),
      child: imageUrl == null ? const Icon(Icons.person) : null,
    );
  }
}

class _EpisodeCard extends StatelessWidget {
  const _EpisodeCard({
    required this.episode,
    required this.isDoctor,
    required this.timeline,
    required this.selectedPhase,
    required this.onToggleTimeline,
    required this.onSelectPhase,
    required this.onChangeStatus,
  });

  final TreatmentEpisode episode;
  final bool isDoctor;
  final AsyncValue<TreatmentTimeline>? timeline;
  final int? selectedPhase;
  final VoidCallback onToggleTimeline;
  final ValueChanged<int> onSelectPhase;
  final ValueChanged<String> onChangeStatus;

  @override
  Widget build(BuildContext context) {
    final statusLabel = {
      'requested': 'Requested',
      'active': 'In progress',
      'abandoned': 'Abandoned',
      'completed': 'Completed',
    }[episode.status] ?? episode.status;
    final person = isDoctor ? episode.patientName : episode.doctorName;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  episode.status == 'active'
                      ? Icons.check_circle_outline
                      : Icons.person_outline,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(person, style: Theme.of(context).textTheme.titleMedium),
                      Text('${episode.reason.isEmpty ? 'Treatment' : episode.reason} · $statusLabel'),
                    ],
                  ),
                ),
                IconButton(
                  tooltip: 'Treatment timeline',
                  onPressed: onToggleTimeline,
                  icon: Icon(
                    timeline == null ? Icons.expand_more : Icons.expand_less,
                  ),
                ),
              ],
            ),
            if (isDoctor && episode.status == 'requested')
              TextButton(
                onPressed: () => onChangeStatus('active'),
                child: const Text('Activate'),
              ),
            if (isDoctor && episode.status == 'active')
              TextButton(
                onPressed: () => onChangeStatus('completed'),
                child: const Text('Complete'),
              ),
            if (!isDoctor &&
                (episode.status == 'requested' || episode.status == 'active'))
              TextButton(
                onPressed: () => onChangeStatus('abandoned'),
                child: const Text('Abandon treatment'),
              ),
            if (timeline != null) _TimelineDetails(
                timeline: timeline!,
                selectedPhase: selectedPhase,
                onSelectPhase: onSelectPhase,
              ),
          ],
        ),
      ),
    );
  }
}

class _TimelineDetails extends StatelessWidget {
  const _TimelineDetails({
    required this.timeline,
    required this.selectedPhase,
    required this.onSelectPhase,
  });

  final AsyncValue<TreatmentTimeline> timeline;
  final int? selectedPhase;
  final ValueChanged<int> onSelectPhase;

  @override
  Widget build(BuildContext context) {
    return timeline.when(
      loading: () => const Padding(
        padding: EdgeInsets.all(16),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => const Text('Unable to load this timeline.'),
      data: (data) {
        if (data.phases.isEmpty) {
          return const Padding(
            padding: EdgeInsets.only(top: 12),
            child: Text('No phases yet.'),
          );
        }
        final phase = data.phases.firstWhere(
          (item) => item.id == selectedPhase,
          orElse: () => data.phases.first,
        );
        final events =
            data.events.where((event) => event.phaseId == phase.id).toList();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Divider(height: 24),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (var index = 0; index < data.phases.length; index++) ...[
                    _PhaseNode(
                      phase: data.phases[index],
                      selected: data.phases[index].id == phase.id,
                      onTap: () => onSelectPhase(data.phases[index].id),
                    ),
                    if (index < data.phases.length - 1)
                      Container(
                        width: 28,
                        height: 2,
                        color: data.phases[index].status == 'completed'
                            ? Colors.green
                            : Theme.of(context).colorScheme.outlineVariant,
                      ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Step ${phase.sequence} — ${phase.name}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            Chip(label: Text(phase.status)),
            if (phase.summary.isNotEmpty) Text(phase.summary),
            if (phase.failureReason != null)
              Text(
                'Failure: ${phase.failureReason}',
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            const SizedBox(height: 8),
            if (events.isEmpty)
              const Text('No events for this step.')
            else
              ...events.map(
                (event) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.event_note_outlined),
                  title: Text('${event.type}: ${event.title}'),
                  subtitle: Text(
                    event.result.isEmpty
                        ? event.description
                        : '${event.description}\nResult: ${event.result}',
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}

class _PhaseNode extends StatelessWidget {
  const _PhaseNode({
    required this.phase,
    required this.selected,
    required this.onTap,
  });

  final TreatmentPhase phase;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = phase.status == 'completed'
        ? Colors.green
        : phase.status == 'failed'
            ? Theme.of(context).colorScheme.error
            : Theme.of(context).colorScheme.primary;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 104,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: selected ? color.withValues(alpha: 0.12) : null,
          border: Border.all(color: selected ? color : Colors.transparent),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(
              phase.status == 'completed'
                  ? Icons.check_circle
                  : phase.status == 'failed'
                      ? Icons.flag
                      : Icons.circle_outlined,
              color: color,
            ),
            Text('${phase.sequence}. ${phase.name}', textAlign: TextAlign.center),
            Text(phase.status, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}
