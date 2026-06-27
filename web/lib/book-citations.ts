export interface BookCitation {
  id: string;
  text: string;
  source: string;
  url?: string;
  urlStatus: "verified" | "unverified";
  severity?: number;
}

export const bookCitations: Record<string, BookCitation> = {
  "HC-007": {
    id: "HC-007",
    text: "Google's Project Aristotle study of 180 teams found psychological safety — the ability to speak freely without fear of consequence — to be the top predictor of team effectiveness across every metric studied.",
    source: "Google",
    url: "https://rework.withgoogle.com/guides/understanding-team-effectiveness/steps/introduction/",
    urlStatus: "verified",
    severity: 5,
  },
  "HC-068": {
    id: "HC-068",
    text: "Edmondson's foundational 1999 study establishing team psychological safety — the shared belief that interpersonal risk-taking is safe — as a direct predictor of learning behavior and team performance.",
    source: "Administrative Science Quarterly",
    url: "https://journals.sagepub.com/doi/10.2307/2666999",
    urlStatus: "verified",
    severity: 1,
  },
  "HC-070": {
    id: "HC-070",
    text: "Edmondson and Kerrissey (2025) correct six persistent misconceptions about psychological safety, including the dangerous conflation of safety with comfort and the idea that safe teams avoid hard truths.",
    source: "Harvard Business Review",
    url: "https://hbr.org/2025/05/what-people-get-wrong-about-psychological-safety",
    urlStatus: "verified",
    severity: 2,
  },
  "HC-071": {
    id: "HC-071",
    text: "Five-year study of strategy execution finding that fewer than 10% of companies achieve all strategic objectives, with broken cross-functional coordination as the primary failure point — not a flawed strategy.",
    source: "Harvard Business Review",
    url: "https://hbr.org/2015/03/why-strategy-execution-unravels-and-what-to-do-about-it",
    urlStatus: "verified",
    severity: 3,
  },
  "HC-110": {
    id: "HC-110",
    text: "Gallup research showing employees who receive daily feedback are 3.6x more likely to feel motivated to do outstanding work, and 80% of employees who received meaningful feedback in the past week describe themselves as fully engaged.",
    source: "Gallup",
    url: "https://www.gallup.com/workplace/357764/fast-feedback-fuels-performance.aspx",
    urlStatus: "verified",
    severity: 2,
  },
  "HC-103": {
    id: "HC-103",
    text: "Keltner's research on power and social cognition finds that elevated status systematically impairs the neural processes underlying social attentiveness — people with power become less accurate at reading emotions, less likely to take others' perspectives, and less responsive to social feedback over time.",
    source: "Keltner, Dacher. The Power Paradox. Penguin Press, 2016.",
    urlStatus: "verified",
    severity: 3,
  },
  "HC-ROSS-1977": {
    id: "HC-ROSS-1977",
    text: "The Fundamental Attribution Error describes the pervasive cognitive bias wherein observers systematically overemphasize dispositional traits and underestimate situational or structural influences when diagnosing the causes of failure.",
    source: "Ross, L. (1977). The Intuitive Psychologist and His Shortcomings: Distortions in the Attribution Process. Advances in Experimental Social Psychology, 10, 173-220.",
    url: "https://www.sciencedirect.com/science/article/pii/S006526010860357X",
    urlStatus: "verified",
    severity: 1,
  },
  "HC-GREEN-1979": {
    id: "HC-GREEN-1979",
    text: "The two-stage attributional model of leadership establishes that supervisors systematically misattribute poor subordinate performance to internal traits rather than external conditions, leading to punitive behavioral interventions rather than structural corrections.",
    source: "Green, S. G., & Mitchell, T. R. (1979). Attributional Processes of Leaders in Leader-Subordinate Interactions. Organizational Behavior and Human Performance, 23(3), 429-458.",
    url: "https://www.sciencedirect.com/science/article/pii/0030507379900084",
    urlStatus: "verified",
    severity: 1,
  },
  "HC-SWIFT-2013": {
    id: "HC-SWIFT-2013",
    text: "Even highly experienced professionals suffer from correspondence bias in evaluation, systematically failing to discount performance advantages conferred by favorable situational and structural environments.",
    source: "Swift, S. A., Moore, D. A., Sharek, Z. S., & Gino, F. (2013). Inflated Applicants: Attribution Errors in Performance Evaluation by Professionals. PLoS ONE, 8(7), e69258.",
    url: "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0069258",
    urlStatus: "verified",
    severity: 2,
  },
  "HC-REASON-1990": {
    id: "HC-REASON-1990",
    text: "The Swiss Cheese Model demonstrates that visible 'active failures' by individuals are merely symptoms; the true root causes of systemic failure are 'latent conditions' — dormant structural weaknesses embedded in organizational architecture by management decisions.",
    source: "Reason, J. (2000). Human error: models and management. BMJ, 320(7237), 768-770.",
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC1070929/",
    urlStatus: "verified",
    severity: 1,
  },
  "HC-SENGE-1990": {
    id: "HC-SENGE-1990",
    text: "The 'Shifting the Burden' systems archetype illustrates how applying rapid symptomatic solutions temporarily reduces visible distress but diverts resources away from fundamental structural fixes, eventually eroding the organization's capacity for systemic resolution.",
    source: "Senge, P. M. (1990). The Fifth Discipline: The Art and Practice of the Learning Organization. Doubleday/Currency.",
    url: "https://thesystemsthinker.com/shifting-the-burden-moving-beyond-a-reactive-orientation/",
    urlStatus: "verified",
    severity: 2,
  },
  "HC-HUGHES-2011": {
    id: "HC-HUGHES-2011",
    text: "The widely repeated statistic that 70% of organizational change initiatives fail is an unsupported narrative lacking valid, reliable empirical evidence at its source — traced to an explicitly unscientific 1993 estimate, then repeated without verification.",
    source: "Hughes, M. (2011). Do 70 Per Cent of All Organizational Change Initiatives Really Fail? Journal of Change Management, 11(4), 451-464.",
    url: "https://doi.org/10.1080/14697017.2011.630506",
    urlStatus: "verified",
    severity: 1,
  },
  "HC-DEWAAL-2026": {
    id: "HC-DEWAAL-2026",
    text: "An integrative evidence synthesis of failure-rate claims in improvement and transformation initiatives finds reported rates vary widely and are not comparable unless definitions, denominators, and time horizons are specified — most repetition of a ~70% figure traces to secondary citation rather than recalculated rates.",
    source: "de Waal, A. (2026). Beyond the 70% myth: What do we actually know about failure rates in improvement and transformation initiatives?",
    url: "https://scindeks-clanci.ceon.rs/data/pdf/2334-9638/8888/2334-96388800002D.pdf",
    urlStatus: "verified",
    severity: 2,
  },
  "HC-SAKS-2006": {
    id: "HC-SAKS-2006",
    text: "Longitudinal evaluation of training transfer demonstrates a steep behavioral regression to baseline when unsupported by environmental conditions: 62% of learned behaviors are applied immediately, decaying to 44% at six months, and dropping to 34% at one year.",
    source: "Saks, A. M., & Belcourt, M. (2006). An investigation of training activities and transfer of training in organizations. Human Resource Management, 45(4), 629-648.",
    url: "https://onlinelibrary.wiley.com/doi/abs/10.1002/hrm.20135",
    urlStatus: "verified",
    severity: 2,
  },
};
