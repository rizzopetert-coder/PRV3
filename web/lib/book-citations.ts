export interface BookCitation {
  id: string;
  text: string;
  source: string;
  url?: string;
  urlStatus: "verified" | "unverified";
  severity?: number;
}

export const bookCitations: Record<string, BookCitation> = {
  // populated in content migration pass
};
