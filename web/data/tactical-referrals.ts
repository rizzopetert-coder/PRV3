/**
 * HRdiagnostic.com-only: per-section OneDigital referral mapping for the
 * Tactical & Compliance question module. Every section carries "HR
 * Consulting" in addition to its specific specialty/specialties, per
 * Pete's explicit mapping (2026-09-24). Keyed by question_set_id, matching
 * tactical-compliance-questions.json's own field -- not per-question,
 * since referral maps to the section, not the individual question.
 *
 * The core PRV3 diagnostic's own referral logic (routing to Principal
 * Resolution service tiers, resolution-family.ts) is untouched -- this is
 * a separate, hostname-gated lookup with no relationship to that system.
 *
 * NOTE: this mirrors the referral field added to a working copy of
 * tactical-compliance-questions.json (not yet committed to the repo --
 * see the accompanying report on why). If that JSON's own referral field
 * is ever treated as the source of truth instead, this file should be
 * regenerated from it rather than hand-maintained in two places.
 */

export const TACTICAL_REFERRALS: Record<string, string[]> = {
  "TC-HR_POLICIES": ["HR Consulting", "HR Compliance Consulting"],
  "TC-HIRING_ONBOARDING": ["HR Consulting", "Talent Acquisition", "Recruiting"],
  "TC-PAYROLL": ["HR Consulting", "Managed Payroll"],
  "TC-COMP_COMPLIANCE": ["HR Consulting", "Compensation Consulting"],
  "TC-BENEFITS": [
    "HR Consulting",
    "Retirement & Wealth Management Consulting",
    "Employee Benefits Consulting",
  ],
  "TC-LEAVE_MANAGEMENT": ["HR Consulting", "Leave Management"],
  "TC-SAFETY": [
    "HR Consulting",
    "Property & Casualty Insurance Consulting",
    "HR Compliance Consulting",
  ],
  "TC-RECORDS": ["HR Consulting", "HR Compliance Consulting"],
  "TC-TECHNOLOGY": ["HR Consulting", "HR Technology Consulting"],
  "TC-PERFORMANCE_MGMT": [
    "HR Consulting",
    "Employee Development/Coaching/Performance Management",
    "Learning & Development Consulting",
  ],
};

export function getTacticalReferrals(questionSetId: string): string[] {
  return TACTICAL_REFERRALS[questionSetId] ?? ["HR Consulting"];
}
