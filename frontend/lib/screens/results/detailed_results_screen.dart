import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:provider/provider.dart';
import '../../models/evaluation_result.dart';
import '../../services/evaluation_provider.dart';
import '../../widgets/score_card.dart';
import '../../widgets/feedback_section.dart';
import '../recording_screen.dart';

/// Detailed results screen for ages 11+ (middle/secondary).
/// Shows full numerical scores, detailed analysis, and multiple improvement tips.
class DetailedResultsScreen extends StatefulWidget {
  final EvaluationResult result;

  const DetailedResultsScreen({super.key, required this.result});

  @override
  State<DetailedResultsScreen> createState() => _DetailedResultsScreenState();
}

class _DetailedResultsScreenState extends State<DetailedResultsScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scores = widget.result.scores;
    final analysis = widget.result.detailedAnalysis;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              _getScoreColor(scores.overall).withValues(alpha: 0.15),
              Colors.white,
            ],
          ),
        ),
        child: SafeArea(
          child: CustomScrollView(
            controller: _scrollController,
            slivers: [
              // Header with overall score
              SliverToBoxAdapter(
                child: _buildHeader(scores),
              ),

              // Score breakdown cards
              SliverToBoxAdapter(
                child: _buildScoreSection(scores, analysis),
              ),

              // Detailed feedback sections
              SliverToBoxAdapter(
                child: _buildDetailedFeedback(analysis),
              ),

              // Improvement suggestions
              SliverToBoxAdapter(
                child: _buildImprovementSection(),
              ),

              // Transcript section
              SliverToBoxAdapter(
                child: _buildTranscriptSection(),
              ),

              // Try again button
              SliverToBoxAdapter(
                child: _buildActionButtons(),
              ),

              const SliverToBoxAdapter(
                child: SizedBox(height: 40),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(Scores scores) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () => _goBack(),
                icon: const Icon(Icons.arrow_back_ios),
                color: Colors.grey[700],
              ),
              const Spacer(),
              Text(
                'Your Results',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const Spacer(),
              const SizedBox(width: 48),
            ],
          ),
          const SizedBox(height: 24),

          // Overall score circle
          CircularPercentIndicator(
            radius: 80,
            lineWidth: 12,
            percent: scores.overall / 100,
            center: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  scores.overall.toStringAsFixed(0),
                  style: TextStyle(
                    fontSize: 42,
                    fontWeight: FontWeight.bold,
                    color: _getScoreColor(scores.overall),
                  ),
                ),
                Text(
                  'out of 100',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            progressColor: _getScoreColor(scores.overall),
            backgroundColor: Colors.grey[200]!,
            circularStrokeCap: CircularStrokeCap.round,
            animation: true,
            animationDuration: 1500,
          )
              .animate()
              .fadeIn(duration: 600.ms)
              .scale(begin: const Offset(0.8, 0.8)),

          const SizedBox(height: 16),

          // Rating text
          Text(
            _getOverallRating(scores.overall),
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: _getScoreColor(scores.overall),
            ),
          ).animate().fadeIn(delay: 500.ms, duration: 600.ms),

          const SizedBox(height: 8),

          if (widget.result.metadata.studentName != null)
            Text(
              'Great job, ${widget.result.metadata.studentName}!',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ).animate().fadeIn(delay: 700.ms, duration: 600.ms),
        ],
      ),
    );
  }

  Widget _buildScoreSection(Scores scores, DetailedAnalysis analysis) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
            child: Text(
              'Score Breakdown',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.4,
            children: [
              ScoreCard(
                title: 'Clarity',
                score: scores.clarity,
                icon: Icons.record_voice_over,
                color: const Color(0xFF6C63FF),
                delay: 0,
              ),
              ScoreCard(
                title: 'Pace',
                score: scores.pace,
                icon: Icons.speed,
                color: const Color(0xFF4CAF50),
                delay: 100,
              ),
              ScoreCard(
                title: 'Pauses',
                score: scores.pauseManagement,
                icon: Icons.pause_circle_outline,
                color: const Color(0xFFFF9800),
                delay: 200,
              ),
              ScoreCard(
                title: 'Filler Words',
                score: scores.fillerReduction,
                icon: Icons.do_not_disturb_alt,
                color: const Color(0xFFE91E63),
                delay: 300,
              ),
              ScoreCard(
                title: 'Repetition',
                score: scores.repetitionControl,
                icon: Icons.repeat,
                color: const Color(0xFF00BCD4),
                delay: 400,
              ),
              ScoreCard(
                title: 'Structure',
                score: scores.structure,
                icon: Icons.account_tree,
                color: const Color(0xFF9C27B0),
                delay: 500,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDetailedFeedback(DetailedAnalysis analysis) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Detailed Feedback',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),

          // Clarity feedback
          FeedbackSection(
            title: 'Clarity',
            icon: Icons.record_voice_over,
            color: const Color(0xFF6C63FF),
            score: analysis.clarity.score,
            feedback: analysis.clarity.feedback,
            extraInfo:
                'Average confidence: ${(analysis.clarity.averageConfidence * 100).toStringAsFixed(0)}%',
            delay: 0,
          ),

          // Pace feedback
          FeedbackSection(
            title: 'Speaking Pace',
            icon: Icons.speed,
            color: const Color(0xFF4CAF50),
            score: analysis.pace.score,
            feedback: analysis.pace.feedback,
            extraInfo:
                '${analysis.pace.wordsPerMinute} words/minute (ideal: ${analysis.pace.idealRange})',
            delay: 100,
          ),

          // Pauses feedback
          FeedbackSection(
            title: 'Pause Management',
            icon: Icons.pause_circle_outline,
            color: const Color(0xFFFF9800),
            score: analysis.pauses.score,
            feedback: analysis.pauses.feedback,
            extraInfo:
                '${analysis.pauses.totalPauses} pauses (${analysis.pauses.longPauses} long)',
            delay: 200,
          ),

          // Fillers feedback
          FeedbackSection(
            title: 'Filler Words',
            icon: Icons.do_not_disturb_alt,
            color: const Color(0xFFE91E63),
            score: analysis.fillers.score,
            feedback: analysis.fillers.feedback,
            extraInfo: analysis.fillers.commonFillers.isNotEmpty
                ? 'Common fillers: ${analysis.fillers.commonFillers.map((f) => '"${f[0]}" (${f[1]}x)').join(', ')}'
                : 'No filler words detected!',
            delay: 300,
          ),

          // Structure feedback
          FeedbackSection(
            title: 'Speech Structure',
            icon: Icons.account_tree,
            color: const Color(0xFF9C27B0),
            score: analysis.structure.score,
            feedback: analysis.structure.feedback,
            extraInfo: _buildStructureInfo(analysis.structure),
            delay: 400,
          ),
        ],
      ),
    );
  }

  String _buildStructureInfo(StructureAnalysis structure) {
    final parts = <String>[];
    if (structure.hasIntroduction) parts.add('Introduction');
    if (structure.hasBody) parts.add('Body');
    if (structure.hasConclusion) parts.add('Conclusion');

    if (parts.isEmpty) return 'Speech structure needs work';
    return 'Found: ${parts.join(' + ')}';
  }

  Widget _buildImprovementSection() {
    final suggestions = widget.result.improvementSuggestions;
    if (suggestions.isEmpty) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFFFFE082).withValues(alpha: 0.3),
            const Color(0xFFFFD54F).withValues(alpha: 0.3),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(0xFFFFB300).withValues(alpha: 0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFB300).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.lightbulb,
                  color: Color(0xFFFF8F00),
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'Tips to Improve',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...suggestions.asMap().entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFB300),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Center(
                      child: Text(
                        '${entry.key + 1}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      entry.value,
                      style: TextStyle(
                        color: Colors.grey[800],
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            )
                .animate()
                .fadeIn(delay: Duration(milliseconds: 100 * entry.key))
                .slideX(begin: 0.1, end: 0);
          }),
        ],
      ),
    ).animate().fadeIn(delay: 800.ms, duration: 600.ms);
  }

  Widget _buildTranscriptSection() {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
          childrenPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
          leading: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF6C63FF).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.description_outlined,
              color: Color(0xFF6C63FF),
            ),
          ),
          title: const Text(
            'Your Transcript',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text(
            '${widget.result.transcript.wordCount} words',
            style: TextStyle(color: Colors.grey[600], fontSize: 12),
          ),
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                widget.result.transcript.fullText.isEmpty
                    ? 'No transcript available'
                    : widget.result.transcript.fullText,
                style: TextStyle(
                  color: Colors.grey[700],
                  height: 1.6,
                ),
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 1000.ms, duration: 600.ms);
  }

  Widget _buildActionButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: Column(
        children: [
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _goBack,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6C63FF),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.mic),
                  SizedBox(width: 8),
                  Text(
                    'Record Another Speech',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 1200.ms, duration: 600.ms);
  }

  void _goBack() {
    context.read<EvaluationProvider>().reset();
    Navigator.pushAndRemoveUntil(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) =>
            const RecordingScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(
            opacity: animation,
            child: child,
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
      (route) => false,
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return const Color(0xFF4CAF50);
    if (score >= 60) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }

  String _getOverallRating(double score) {
    if (score >= 90) return 'Superstar Speaker!';
    if (score >= 80) return 'Excellent Work!';
    if (score >= 70) return 'Great Job!';
    if (score >= 60) return 'Good Effort!';
    if (score >= 50) return 'Keep Practicing!';
    return 'Room to Grow!';
  }
}
