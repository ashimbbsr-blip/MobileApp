import 'package:hive/hive.dart';
part 'legal_acceptance.g.dart';

@HiveType(typeId: 4)
class LegalAcceptance {
  @HiveField(0)
  final DateTime acceptedAt;

  @HiveField(1)
  final String policyVersion;

  @HiveField(2)
  final String appVersion;

  @HiveField(3)
  final bool termsAccepted;

  @HiveField(4)
  final bool healthDisclaimerAccepted;

  const LegalAcceptance({
    required this.acceptedAt,
    required this.policyVersion,
    required this.appVersion,
    this.termsAccepted = true,
    this.healthDisclaimerAccepted = true,
  });
}
