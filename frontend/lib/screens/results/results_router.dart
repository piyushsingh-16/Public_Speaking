import 'package:flutter/material.dart';
import '../../models/child_presentation.dart';
import '../../models/evaluation_result.dart';
import 'pre_primary_results_screen.dart';
import 'lower_primary_results_screen.dart';
import 'upper_primary_results_screen.dart';
import 'detailed_results_screen.dart';

/// Routes to the appropriate results screen based on age group.
/// This factory determines which UI to show based on the child_presentation data.
class ResultsRouter {
  /// Navigate to the appropriate results screen based on age group
  static void navigate(
    BuildContext context, {
    required ChildPresentation? childPresentation,
    required EvaluationResult? rawResult,
  }) {
    Widget screen;

    if (childPresentation != null) {
      switch (childPresentation.ageGroup) {
        case 'pre_primary':
          screen = PrePrimaryResultsScreen(
            presentation: childPresentation as PrePrimaryPresentation,
          );
          break;
        case 'lower_primary':
          screen = LowerPrimaryResultsScreen(
            presentation: childPresentation as LowerPrimaryPresentation,
          );
          break;
        case 'upper_primary':
          screen = UpperPrimaryResultsScreen(
            presentation: childPresentation as UpperPrimaryPresentation,
          );
          break;
        case 'middle':
        case 'secondary':
        default:
          // Use detailed screen with raw result
          if (rawResult != null) {
            screen = DetailedResultsScreen(result: rawResult);
          } else {
            _showErrorAndReturn(context);
            return;
          }
          break;
      }
    } else if (rawResult != null) {
      // Fallback to detailed if no child presentation
      screen = DetailedResultsScreen(result: rawResult);
    } else {
      _showErrorAndReturn(context);
      return;
    }

    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) => screen,
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(
            opacity: animation,
            child: ScaleTransition(
              scale: Tween<double>(begin: 0.95, end: 1.0).animate(
                CurvedAnimation(parent: animation, curve: Curves.easeOutCubic),
              ),
              child: child,
            ),
          );
        },
        transitionDuration: const Duration(milliseconds: 600),
      ),
    );
  }

  /// Show error and return to previous screen
  static void _showErrorAndReturn(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Oops!'),
        content: const Text('Something went wrong. Please try again.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop();
            },
            child: const Text('Go Back'),
          ),
        ],
      ),
    );
  }

  /// Get the appropriate screen widget (for testing or direct use)
  static Widget getScreen({
    required ChildPresentation? childPresentation,
    required EvaluationResult? rawResult,
  }) {
    if (childPresentation != null) {
      switch (childPresentation.ageGroup) {
        case 'pre_primary':
          return PrePrimaryResultsScreen(
            presentation: childPresentation as PrePrimaryPresentation,
          );
        case 'lower_primary':
          return LowerPrimaryResultsScreen(
            presentation: childPresentation as LowerPrimaryPresentation,
          );
        case 'upper_primary':
          return UpperPrimaryResultsScreen(
            presentation: childPresentation as UpperPrimaryPresentation,
          );
        case 'middle':
        case 'secondary':
        default:
          if (rawResult != null) {
            return DetailedResultsScreen(result: rawResult);
          }
      }
    }

    if (rawResult != null) {
      return DetailedResultsScreen(result: rawResult);
    }

    // Fallback error screen
    return const _ErrorScreen();
  }
}

/// Error screen shown when no valid data is available
class _ErrorScreen extends StatelessWidget {
  const _ErrorScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.sentiment_dissatisfied_rounded,
                size: 80,
                color: Colors.grey.shade400,
              ),
              const SizedBox(height: 24),
              Text(
                'Oops!',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade700,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Something went wrong.\nPlease try recording again.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.arrow_back),
                label: const Text('Go Back'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
