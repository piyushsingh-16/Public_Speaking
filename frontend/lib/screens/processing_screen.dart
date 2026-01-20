import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../services/evaluation_provider.dart';
import 'results/results_router.dart';

class ProcessingScreen extends StatefulWidget {
  final File audioFile;
  final int studentAge;
  final String? studentName;
  final String? topic;

  const ProcessingScreen({
    super.key,
    required this.audioFile,
    required this.studentAge,
    this.studentName,
    this.topic,
  });

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen>
    with TickerProviderStateMixin {
  late AnimationController _rotationController;

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();

    // Start processing
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startProcessing();
    });
  }

  @override
  void dispose() {
    _rotationController.dispose();
    super.dispose();
  }

  Future<void> _startProcessing() async {
    final provider = context.read<EvaluationProvider>();

    final success = await provider.submitAudio(
      audioFile: widget.audioFile,
      studentAge: widget.studentAge,
      studentName: widget.studentName,
      topic: widget.topic,
    );

    if (mounted) {
      if (success && (provider.result != null || provider.childPresentation != null)) {
        // Use ResultsRouter to navigate to age-appropriate results screen
        ResultsRouter.navigate(
          context,
          childPresentation: provider.childPresentation,
          rawResult: provider.result,
        );
      } else {
        // Show error
        _showErrorDialog(provider.errorMessage ?? 'Something went wrong');
      }
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.error_outline, color: Colors.red[400]),
            const SizedBox(width: 8),
            const Text('Oops!'),
          ],
        ),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Go back to recording screen
              context.read<EvaluationProvider>().reset();
            },
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              const Color(0xFF6C63FF).withValues(alpha: 0.1),
              Colors.white,
              const Color(0xFFE8F5E9).withValues(alpha: 0.5),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Animated stars
                Stack(
                  alignment: Alignment.center,
                  children: [
                    RotationTransition(
                      turns: _rotationController,
                      child: Container(
                        width: 180,
                        height: 180,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: SweepGradient(
                            colors: [
                              const Color(0xFF6C63FF).withValues(alpha: 0.3),
                              const Color(0xFFFFD700).withValues(alpha: 0.3),
                              const Color(0xFF4CAF50).withValues(alpha: 0.3),
                              const Color(0xFF6C63FF).withValues(alpha: 0.3),
                            ],
                          ),
                        ),
                      ),
                    ),
                    Container(
                      width: 140,
                      height: 140,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white,
                      ),
                      child: const Icon(
                        Icons.auto_awesome,
                        size: 60,
                        color: Color(0xFF6C63FF),
                      ),
                    )
                        .animate(
                          onPlay: (controller) => controller.repeat(),
                        )
                        .scale(
                          begin: const Offset(1, 1),
                          end: const Offset(1.1, 1.1),
                          duration: 1000.ms,
                        )
                        .then()
                        .scale(
                          begin: const Offset(1.1, 1.1),
                          end: const Offset(1, 1),
                          duration: 1000.ms,
                        ),
                  ],
                ),
                const SizedBox(height: 48),

                // Progress message
                Consumer<EvaluationProvider>(
                  builder: (context, provider, _) {
                    return Column(
                      children: [
                        Text(
                          provider.progressMessage,
                          style:
                              Theme.of(context).textTheme.titleLarge?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: const Color(0xFF6C63FF),
                                  ),
                          textAlign: TextAlign.center,
                        )
                            .animate(
                              key: ValueKey(provider.progressMessage),
                            )
                            .fadeIn(duration: 300.ms)
                            .slideY(begin: 0.2, end: 0),
                        const SizedBox(height: 16),
                        _buildProgressIndicator(provider.state),
                      ],
                    );
                  },
                ),

                const SizedBox(height: 48),

                // Fun messages
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 32),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.05),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Consumer<EvaluationProvider>(
                    builder: (context, provider, _) {
                      return Text(
                        _getFunMessage(provider.state),
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                        textAlign: TextAlign.center,
                      );
                    },
                  ),
                )
                    .animate()
                    .fadeIn(delay: 500.ms, duration: 600.ms)
                    .slideY(begin: 0.3, end: 0),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProgressIndicator(EvaluationState state) {
    final steps = [
      ('Upload', EvaluationState.submitting),
      ('Prepare', EvaluationState.preprocessing),
      ('Listen', EvaluationState.transcribing),
      ('Analyze', EvaluationState.analyzing),
    ];

    int currentIndex = 0;
    for (int i = 0; i < steps.length; i++) {
      if (state == steps[i].$2) {
        currentIndex = i;
        break;
      }
      if (state == EvaluationState.completed) {
        currentIndex = steps.length;
      }
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(steps.length, (index) {
        final isCompleted = index < currentIndex;
        final isCurrent = index == currentIndex;

        return Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isCompleted
                    ? Colors.green
                    : isCurrent
                        ? const Color(0xFF6C63FF)
                        : Colors.grey[300],
              ),
              child: Center(
                child: isCompleted
                    ? const Icon(Icons.check, color: Colors.white, size: 18)
                    : isCurrent
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(
                            '${index + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
              ),
            ),
            if (index < steps.length - 1)
              Container(
                width: 30,
                height: 3,
                color: isCompleted ? Colors.green : Colors.grey[300],
              ),
          ],
        );
      }),
    );
  }

  String _getFunMessage(EvaluationState state) {
    switch (state) {
      case EvaluationState.submitting:
        return 'Sending your amazing speech to our magical evaluator!';
      case EvaluationState.preprocessing:
        return 'Getting your audio ready for analysis...';
      case EvaluationState.transcribing:
        return 'Our smart helper is carefully listening to every word you said!';
      case EvaluationState.analyzing:
        return 'Almost there! We\'re calculating your superstar scores!';
      default:
        return 'Working on something special for you...';
    }
  }
}
