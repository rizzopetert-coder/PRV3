export type BookContentType = "memo" | "methodology" | "case_pattern";
export type BookVoice = "standard" | "from_the_author";

export interface BookPiece {
  id: string;
  slug: string;
  contentType: BookContentType;
  voice: BookVoice;
  title: string;
  teaser: string;
  signatureId?: string;
  citationIds?: string[];
  author: "Principal Resolution";
  status: "draft" | "published";
}

export const bookManifest: BookPiece[] = [
  // populated in content migration pass
];
