import { signatures } from "@/data/taxonomy";

export function buildInterpretationPrompt(
  states: { name: string; signatureId: string }[]
): string {
  const signatureNames: Record<string, string> = Object.fromEntries(
    signatures.map((s) => [s.id, s.name])
  );

  const grouped: Record<string, string[]> = {};
  for (const { name, signatureId } of states) {
    const sigName = signatureNames[signatureId] ?? signatureId;
    if (!grouped[sigName]) grouped[sigName] = [];
    grouped[sigName].push(name);
  }

  const stateList = Object.entries(grouped)
    .map(([sig, names]) => `${sig}: ${names.join(", ")}`)
    .join("\n");

  return `You are describing an organizational condition pattern. A leader has identified the following conditions as present in their organization:

${stateList}

In 2 to 3 sentences, describe what these conditions produce together and what that costs the organization. State the pattern first, then the cost. Plain, direct language only. Do not use the words emerging, entrenched, or endemic. Do not name any specific service or professional intervention. Do not use prescriptive language.`;
}
