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
};
