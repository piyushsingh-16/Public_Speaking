import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'api_service.dart';
import '../models/evaluation_result.dart';
import '../models/child_presentation.dart';

enum EvaluationState {
  idle,
  submitting,
  preprocessing,
  transcribing,
  analyzing,
  completed,
  error,
}

class EvaluationProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  EvaluationState _state = EvaluationState.idle;
  EvaluationResult? _result;
  ChildPresentation? _childPresentation;
  String? _errorMessage;
  String? _jobId;
  String _progressMessage = '';

  EvaluationState get state => _state;
  EvaluationResult? get result => _result;
  ChildPresentation? get childPresentation => _childPresentation;
  String? get errorMessage => _errorMessage;
  String get progressMessage => _progressMessage;

  Future<bool> submitAudio({
    required File audioFile,
    required int studentAge,
    String? studentName,
    String? topic,
  }) async {
    try {
      _state = EvaluationState.submitting;
      _progressMessage = 'Uploading your speech...';
      _errorMessage = null;
      notifyListeners();

      // Submit the audio file
      _jobId = await _apiService.submitEvaluation(
        audioFile: audioFile,
        studentAge: studentAge,
        studentName: studentName,
        topic: topic,
      );

      // Start polling for results
      await _pollForResults();

      return _state == EvaluationState.completed;
    } catch (e) {
      _state = EvaluationState.error;
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<void> _pollForResults() async {
    if (_jobId == null) return;

    const pollInterval = Duration(seconds: 2);
    const maxAttempts = 120; // 4 minutes max

    for (int attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        final status = await _apiService.getJobStatus(_jobId!);

        // Update state based on job status
        switch (status.status) {
          case 'pending':
            _state = EvaluationState.submitting;
            _progressMessage = 'Waiting in queue...';
            break;
          case 'preprocessing':
            _state = EvaluationState.preprocessing;
            _progressMessage = 'Preparing your audio...';
            break;
          case 'extracting_features':
            _state = EvaluationState.preprocessing;
            _progressMessage = 'Analyzing your voice...';
            break;
          case 'transcribing':
            _state = EvaluationState.transcribing;
            _progressMessage = 'Listening to your speech...';
            break;
          case 'analyzing':
            _state = EvaluationState.analyzing;
            _progressMessage = 'Analyzing your performance...';
            break;
          case 'completed':
            _state = EvaluationState.completed;
            _result = status.result;
            _childPresentation = status.childPresentation;
            _progressMessage = 'Done!';
            notifyListeners();
            return;
          case 'failed':
            _state = EvaluationState.error;
            _errorMessage = status.error ?? 'Something went wrong';
            notifyListeners();
            return;
        }

        notifyListeners();
        await Future.delayed(pollInterval);
      } catch (e) {
        _state = EvaluationState.error;
        _errorMessage = 'Connection error: $e';
        notifyListeners();
        return;
      }
    }

    // Timeout
    _state = EvaluationState.error;
    _errorMessage = 'Processing took too long. Please try again.';
    notifyListeners();
  }

  void reset() {
    _state = EvaluationState.idle;
    _result = null;
    _childPresentation = null;
    _errorMessage = null;
    _jobId = null;
    _progressMessage = '';
    notifyListeners();
  }

  Future<bool> checkServerHealth() async {
    return await _apiService.checkHealth();
  }
}
