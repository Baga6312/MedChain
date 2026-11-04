import 'package:dio/dio.dart';

class TreatmentEpisode {
  const TreatmentEpisode({
    required this.id,
    required this.patientName,
    required this.doctorName,
    required this.status,
    required this.reason,
  });

  factory TreatmentEpisode.fromJson(Map<String, dynamic> json) {
    return TreatmentEpisode(
      id: json['id'] as int? ?? 0,
      patientName: json['patient_name'] as String? ?? 'Patient',
      doctorName: json['doctor_name'] as String? ?? 'Doctor',
      status: json['status'] as String? ?? 'requested',
      reason: json['reason'] as String? ?? '',
    );
  }

  final int id;
  final String patientName;
  final String doctorName;
  final String status;
  final String reason;
}

class TreatmentPhase {
  const TreatmentPhase({
    required this.id,
    required this.sequence,
    required this.name,
    required this.status,
    required this.summary,
    required this.failureReason,
  });

  factory TreatmentPhase.fromJson(Map<String, dynamic> json) {
    return TreatmentPhase(
      id: json['id'] as int? ?? 0,
      sequence: json['sequence_number'] as int? ?? 0,
      name: json['name'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      summary: json['summary'] as String? ?? '',
      failureReason: json['failure_reason'] as String?,
    );
  }

  final int id;
  final int sequence;
  final String name;
  final String status;
  final String summary;
  final String? failureReason;
}

class TreatmentEvent {
  const TreatmentEvent({
    required this.phaseId,
    required this.type,
    required this.title,
    required this.description,
    required this.result,
  });

  factory TreatmentEvent.fromJson(Map<String, dynamic> json) {
    return TreatmentEvent(
      phaseId: json['treatment_phase'] as int?,
      type: json['event_type'] as String? ?? 'note',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      result: json['result'] as String? ?? '',
    );
  }

  final int? phaseId;
  final String type;
  final String title;
  final String description;
  final String result;
}

class TreatmentTimeline {
  const TreatmentTimeline({
    required this.phases,
    required this.events,
  });

  factory TreatmentTimeline.fromJson(Map<String, dynamic> json) {
    final phases = (json['phases'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(TreatmentPhase.fromJson)
        .toList();
    final events = (json['events'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(TreatmentEvent.fromJson)
        .toList();
    return TreatmentTimeline(phases: phases, events: events);
  }

  final List<TreatmentPhase> phases;
  final List<TreatmentEvent> events;
}

class DashboardRepository {
  const DashboardRepository(this._client);

  final Dio _client;

  Future<List<TreatmentEpisode>> episodes() async {
    final response =
        await _client.get<List<dynamic>>('/treatment-episodes/');
    return (response.data ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(TreatmentEpisode.fromJson)
        .toList();
  }

  Future<TreatmentTimeline> timeline(int episodeId) async {
    final response = await _client
        .get<Map<String, dynamic>>('/treatment-episodes/$episodeId/timeline/');
    return TreatmentTimeline.fromJson(response.data ?? const {});
  }

  Future<void> changeStatus(int episodeId, String status) async {
    await _client.patch<void>(
      '/treatment-episodes/$episodeId/',
      data: {'status': status},
    );
  }
}

