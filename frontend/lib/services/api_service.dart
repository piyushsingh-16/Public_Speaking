import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../models/evaluation_result.dart';

class ApiService {
  // Change this to your server URL
  static const String baseUrl =
      'http://10.0.5.189:8000'; // Android emulator localhost
  // Use 'http://localhost:8000' for iOS simulator
  // Use your actual IP for physical devices (e.g., 'http://192.168.1.100:8000')

  /// Submit audio for evaluation
  Future<String> submitEvaluation({
    required File audioFile,
    required int studentAge,
    String? studentName,
    String? topic,
  }) async {
    final uri = Uri.parse('$baseUrl/evaluate');

    final request = http.MultipartRequest('POST', uri);

    // Add the audio file
    final mimeType = _getMimeType(audioFile.path);
    request.files.add(
      await http.MultipartFile.fromPath(
        'audio_file',
        audioFile.path,
        contentType: MediaType.parse(mimeType),
      ),
    );

    // Add form fields
    request.fields['student_age'] = studentAge.toString();
    if (studentName != null && studentName.isNotEmpty) {
      request.fields['student_name'] = studentName;
    }
    if (topic != null && topic.isNotEmpty) {
      request.fields['topic'] = topic;
    }

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 202) {
      final data = json.decode(response.body);
      return data['job_id'];
    } else {
      throw ApiException('Failed to submit evaluation: ${response.body}');
    }
  }

  /// Poll for job status and results
  Future<JobStatus> getJobStatus(String jobId) async {
    final uri = Uri.parse('$baseUrl/jobs/$jobId');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return JobStatus.fromJson(data);
    } else if (response.statusCode == 404) {
      throw ApiException('Job not found');
    } else {
      throw ApiException('Failed to get job status: ${response.body}');
    }
  }

  /// Submit audio path for evaluation (for server-side files)
  Future<String> submitEvaluationByPath({
    required String audioPath,
    required int studentAge,
    String? studentName,
    String? topic,
  }) async {
    final uri = Uri.parse('$baseUrl/evaluate/path');

    final body = {'audio_path': audioPath, 'student_age': studentAge};

    if (studentName != null && studentName.isNotEmpty) {
      body['student_name'] = studentName;
    }
    if (topic != null && topic.isNotEmpty) {
      body['topic'] = topic;
    }

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode(body),
    );

    if (response.statusCode == 202) {
      final data = json.decode(response.body);
      return data['job_id'];
    } else {
      throw ApiException('Failed to submit evaluation: ${response.body}');
    }
  }

  /// Check server health
  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await http.get(uri).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  String _getMimeType(String path) {
    final ext = path.split('.').last.toLowerCase();
    switch (ext) {
      case 'mp3':
        return 'audio/mpeg';
      case 'wav':
        return 'audio/wav';
      case 'm4a':
        return 'audio/m4a';
      case 'ogg':
        return 'audio/ogg';
      case 'flac':
        return 'audio/flac';
      case 'webm':
        return 'audio/webm';
      default:
        return 'audio/mpeg';
    }
  }
}

class JobStatus {
  final String jobId;
  final String status;
  final String? message;
  final String? progress;
  final EvaluationResult? result;
  final String? error;

  JobStatus({
    required this.jobId,
    required this.status,
    this.message,
    this.progress,
    this.result,
    this.error,
  });

  factory JobStatus.fromJson(Map<String, dynamic> json) {
    return JobStatus(
      jobId: json['job_id'] ?? '',
      status: json['status'] ?? 'unknown',
      message: json['message'],
      progress: json['progress'],
      result: json['result'] != null
          ? EvaluationResult.fromJson(json['result'])
          : null,
      error: json['error'],
    );
  }

  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isPending => status == 'pending';
  bool get isProcessing =>
      status == 'preprocessing' ||
      status == 'transcribing' ||
      status == 'analyzing';
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
