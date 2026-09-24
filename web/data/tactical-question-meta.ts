/**
 * hr-dx.com-only. Minimal per-question metadata that has NO home
 * in the Python engine -- "intent" is explicitly not a QuestionDefinition
 * field (confirmed with Pete), and question_set_id/section grouping is
 * frontend-only bookkeeping the engine has no concept of. Deliberately
 * does NOT duplicate question_text or option_text -- this codebase's own
 * established principle (get_question_copy()'s docstring, engine/main.py)
 * is that question copy is never hand-duplicated in TypeScript; that text
 * is fetched live via invokeQuestionCopy() at completion time instead.
 */

export interface TacticalQuestionMeta {
  question_set_id: string;
  intent: string;
}

export const TACTICAL_QUESTION_META: Record<string, TacticalQuestionMeta> = {
  "TC-HRPOL-01": { question_set_id: "TC-HR_POLICIES", intent: "Distinguishes cosmetic maintenance from genuine review. A handbook updated only in formatting is effectively unreviewed." },
  "TC-HRPOL-02": { question_set_id: "TC-HR_POLICIES", intent: "Tests whether policy exists as an enforceable record or as an artifact nobody can prove anyone read." },
  "TC-HRPOL-03": { question_set_id: "TC-HR_POLICIES", intent: "Surfaces the gap between stated policy and lived practice -- often the first place liability hides." },
  "TC-HRPOL-04": { question_set_id: "TC-HR_POLICIES", intent: "Tests whether policy maintenance is a defined process or something that happens reactively, usually after an incident." },
  "TC-HIRE-01": { question_set_id: "TC-HIRING_ONBOARDING", intent: "Inconsistent interviewing is where disparate-impact exposure usually starts, long before anyone files a complaint." },
  "TC-HIRE-02": { question_set_id: "TC-HIRING_ONBOARDING", intent: "An undocumented adjudication process is defensible until the first time it isn't -- usually when two similar findings get two different outcomes." },
  "TC-HIRE-03": { question_set_id: "TC-HIRING_ONBOARDING", intent: "Onboarding that lives in one person's head doesn't survive that person's vacation, let alone their departure." },
  "TC-HIRE-04": { question_set_id: "TC-HIRING_ONBOARDING", intent: "I-9 completeness is one of the few compliance items with a hard audit trigger and no grace period once asked." },
  "TC-PAY-01": { question_set_id: "TC-PAYROLL", intent: "Misclassification usually isn't a decision, it's an accumulation -- a role evolves and nobody revisits the exemption." },
  "TC-PAY-02": { question_set_id: "TC-PAYROLL", intent: "Tests whether timekeeping is a system or a habit." },
  "TC-PAY-03": { question_set_id: "TC-PAYROLL", intent: "A review step that exists on paper but doesn't function as a real check is functionally the same as no review." },
  "TC-PAY-04": { question_set_id: "TC-PAYROLL", intent: "Vendors handle the mechanics, not the liability -- the employer is still the responsible party if a state's specific disclosure requirements aren't met." },
  "TC-COMPC-01": { question_set_id: "TC-COMP_COMPLIANCE", intent: "A pay range that doesn't match reality is worse than no range at all once someone compares the posting to their offer." },
  "TC-COMPC-02": { question_set_id: "TC-COMP_COMPLIANCE", intent: "Most pay equity gaps aren't the result of a decision -- they're the accumulated effect of individually reasonable ones." },
  "TC-COMPC-03": { question_set_id: "TC-COMP_COMPLIANCE", intent: "Remote work quietly multiplied the number of wage floors an employer has to track -- this is where it's most often missed." },
  "TC-COMPC-04": { question_set_id: "TC-COMP_COMPLIANCE", intent: "An undocumented philosophy isn't a philosophy, it's a set of precedents nobody wrote down." },
  "TC-BEN-01": { question_set_id: "TC-BENEFITS", intent: "Same pattern as payroll vendors: the broker executes, the employer remains the party of record if something wasn't sent." },
  "TC-BEN-02": { question_set_id: "TC-BENEFITS", intent: "COBRA notice failures are one of the more litigated benefits gaps, and proof of timely notice is the entire defense." },
  "TC-BEN-03": { question_set_id: "TC-BENEFITS", intent: "ACA obligations change with headcount and coverage offers -- a process that isn't re-evaluated annually eventually falls out of compliance quietly." },
  "TC-BEN-04": { question_set_id: "TC-BENEFITS", intent: "Confusion at the point of use is where benefits complaints turn into claims." },
  "TC-LEAVE-01": { question_set_id: "TC-LEAVE_MANAGEMENT", intent: "Case-by-case leave handling is where similarly situated employees end up treated differently -- which is exactly what creates exposure." },
  "TC-LEAVE-02": { question_set_id: "TC-LEAVE_MANAGEMENT", intent: "Intermittent leave is the hardest leave type to administer cleanly, and the gap between policy and practice shows up here first." },
  "TC-LEAVE-03": { question_set_id: "TC-LEAVE_MANAGEMENT", intent: "An interactive process that isn't consistent isn't really a process -- it's a set of individual judgment calls with the employer's name on them." },
  "TC-LEAVE-04": { question_set_id: "TC-LEAVE_MANAGEMENT", intent: "An undocumented return can leave open questions about what was actually cleared, restored, or agreed to." },
  "TC-SAFE-01": { question_set_id: "TC-SAFETY", intent: "Recordkeeping requirements shift with headcount and industry classification -- a process set up once and left alone tends to drift out of compliance." },
  "TC-SAFE-02": { question_set_id: "TC-SAFETY", intent: "The first hour after an incident is where documentation quality is set -- and where most reconstruction problems start." },
  "TC-SAFE-03": { question_set_id: "TC-SAFETY", intent: "A safety policy nobody has revisited is a policy nobody can say is still accurate." },
  "TC-SAFE-04": { question_set_id: "TC-SAFETY", intent: "A policy that isn't known can't be relied on as a defense -- it has to actually be communicated to function as one." },
  "TC-REC-01": { question_set_id: "TC-RECORDS", intent: "Indefinite retention isn't caution, it's its own liability -- old records are discoverable too." },
  "TC-REC-02": { question_set_id: "TC-RECORDS", intent: "Broad access to personnel files is one of the more overlooked exposure points -- it's rarely tested until there's a dispute about who saw what." },
  "TC-REC-03": { question_set_id: "TC-RECORDS", intent: "Several states have specific timelines for this request -- not having a ready answer is itself the gap." },
  "TC-REC-04": { question_set_id: "TC-RECORDS", intent: "Commingled records are a common, quietly persistent compliance gap -- it's rarely intentional, just never corrected." },
  "TC-TECH-01": { question_set_id: "TC-TECHNOLOGY", intent: "Manual reconciliation is where errors enter and where nobody notices until the numbers stop matching." },
  "TC-TECH-02": { question_set_id: "TC-TECHNOLOGY", intent: "An undefined source of truth means the error gets discovered at the worst possible moment -- usually when someone's paycheck is wrong." },
  "TC-TECH-03": { question_set_id: "TC-TECHNOLOGY", intent: "Default broad access is the most common gap between what a system is capable of restricting and what's actually been configured." },
  "TC-TECH-04": { question_set_id: "TC-TECHNOLOGY", intent: "Access that isn't promptly removed is a liability that grows quietly the longer it's overlooked." },
  "TC-PERF-01": { question_set_id: "TC-PERFORMANCE_MGMT", intent: "Inconsistent review cadence across managers is a pattern that becomes visible -- and legally relevant -- the moment two similar situations get compared." },
  "TC-PERF-02": { question_set_id: "TC-PERFORMANCE_MGMT", intent: "Documentation built after a decision reads differently than documentation built alongside one -- and it's usually easy to tell which is which." },
  "TC-PERF-03": { question_set_id: "TC-PERFORMANCE_MGMT", intent: "A mismatch between stated ratings and actual outcomes is one of the more common things that surfaces in a discrimination claim review." },
  "TC-PERF-04": { question_set_id: "TC-PERFORMANCE_MGMT", intent: "Ad hoc PIPs create inconsistency in both content and follow-through -- which undermines their value as either a coaching tool or a legal record." },
};
