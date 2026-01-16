import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('App renders recording screen', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const PublicSpeakingApp());

    // Verify that the app title is displayed
    expect(find.text('Speech Star'), findsOneWidget);

    // Verify the subtitle is displayed
    expect(find.text('Become a speaking superstar!'), findsOneWidget);

    // Verify the record instruction is displayed
    expect(find.text('Tap to record'), findsOneWidget);
  });
}
