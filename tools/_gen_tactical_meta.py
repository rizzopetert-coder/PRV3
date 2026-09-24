import json

with open(r'C:\Users\rizzo\Downloads\tactical-compliance-questions-schema-compliant.json', encoding='utf-8') as f:
    data = json.load(f)


def ts_str(s: str) -> str:
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


lines = []
lines.append('/**')
lines.append(' * HRdiagnostic.com-only. Minimal per-question metadata that has NO home')
lines.append(' * in the Python engine -- "intent" is explicitly not a QuestionDefinition')
lines.append(' * field (confirmed with Pete), and question_set_id/section grouping is')
lines.append(" * frontend-only bookkeeping the engine has no concept of. Deliberately")
lines.append(" * does NOT duplicate question_text or option_text -- this codebase's own")
lines.append(" * established principle (get_question_copy()'s docstring, engine/main.py)")
lines.append(' * is that question copy is never hand-duplicated in TypeScript; that text')
lines.append(' * is fetched live via invokeQuestionCopy() at completion time instead.')
lines.append(' */')
lines.append('')
lines.append('export interface TacticalQuestionMeta {')
lines.append('  question_set_id: string;')
lines.append('  intent: string;')
lines.append('}')
lines.append('')
lines.append('export const TACTICAL_QUESTION_META: Record<string, TacticalQuestionMeta> = {')
for qset in data['question_sets']:
    qsid = qset['question_set_id']
    for q in qset['questions']:
        qid = q['question_id']
        intent = q['intent']
        lines.append(f'  {ts_str(qid)}: {{ question_set_id: {ts_str(qsid)}, intent: {ts_str(intent)} }},')
lines.append('};')
lines.append('')

out = '\n'.join(lines)
with open(r'C:\Users\rizzo\PRV3\web\data\tactical-question-meta.ts', 'w', encoding='utf-8') as f:
    f.write(out)
print('wrote, length', len(out))
