import type { DimensionKey } from "./book-manifest";

export const PUBLIC_DIMENSION_LABELS: Record<DimensionKey, { title: string; description: string }> = {
  aptitude: {
    title: "How the work actually gets done",
    description: "Skills, roles, and capacity — whether people can do what the job requires, and whether the structure around them lets them.",
  },
  authority: {
    title: "Who really has the power to decide",
    description: "Where decisions actually get made, versus where the org chart says they get made.",
  },
  alliance: {
    title: "How people work together",
    description: "Trust, coordination, and follow-through across teams — what happens at the handoffs.",
  },
  attitude: {
    title: "How people show up",
    description: "Candor, culture, and the unwritten rules people have learned to live by.",
  },
};
