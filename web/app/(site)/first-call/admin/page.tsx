import { cookies } from "next/headers";
import { Redis } from "@upstash/redis";
import AdminLoginForm from "./AdminLoginForm";
import { FIRST_CALL_SESSION_COOKIE, deriveFirstCallSessionToken } from "@/lib/first-call-admin-session";

// ---------------------------------------------------------------------------
// First Call submissions viewer, Pete-only. Gated by a single shared secret
// (FIRST_CALL_ADMIN_SECRET) via web/app/api/first-call/admin-login/route.ts
// -- no accounts, matching this project's solo-practice scale.
//
// redis.keys() chosen over scan() for this listing: neither had any prior
// precedent in this codebase (checked directly before picking). keys() is
// O(N) and blocking on the Redis side, which matters at high key-space
// volume -- not the case here (a solo practice's crisis intakes), so its
// single-call simplicity outweighs scan()'s cursor-iteration correctness
// benefit, which solves a scale problem this page doesn't have.
// ---------------------------------------------------------------------------

const redis = Redis.fromEnv();

interface CrisisIntakeRecord {
  id: string;
  organization_name: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string | null;
  crisis_categories: string[];
  description: string | null;
  submitted_at: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  safety: "Safety",
  financial: "Financial",
  personnel: "Personnel",
};

// Same defensive shape as web/lib/share-store.ts's getShareRecord() --
// @upstash/redis's automaticDeserialization means redis.get() normally
// returns the already-parsed object, not the raw string a generic type
// parameter might suggest. See that file's comment for the real bug this
// pattern was fixed to prevent (2026-09-16, double-JSON.parse on an
// already-parsed object).
async function getSubmissions(): Promise<CrisisIntakeRecord[]> {
  const keys = await redis.keys("crisis-intake:*");
  if (keys.length === 0) return [];
  const raws = await Promise.all(
    keys.map((key) => redis.get<string | CrisisIntakeRecord>(key))
  );
  const records = raws
    .filter((raw): raw is string | CrisisIntakeRecord => raw !== null && raw !== undefined)
    .map((raw) => (typeof raw === "string" ? (JSON.parse(raw) as CrisisIntakeRecord) : raw));
  return records.sort((a, b) => b.submitted_at.localeCompare(a.submitted_at));
}

export default async function FirstCallAdminPage() {
  const cookieStore = await cookies();
  const adminSecret = process.env.FIRST_CALL_ADMIN_SECRET ?? "";
  const sessionCookie = cookieStore.get(FIRST_CALL_SESSION_COOKIE)?.value;
  const isAuthed = adminSecret.length > 0 && sessionCookie === deriveFirstCallSessionToken(adminSecret);

  if (!isAuthed) {
    return <AdminLoginForm />;
  }

  const submissions = await getSubmissions();

  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-slate mb-2">First Call</p>
      <h1 className="font-display text-2xl text-charcoal mb-8">
        Recent submissions ({submissions.length})
      </h1>

      {submissions.length === 0 && (
        <p className="font-ui text-sm text-slate">No submissions yet.</p>
      )}

      <div className="space-y-6">
        {submissions.map((s) => (
          <div key={s.id} className="border border-gray-200 rounded-lg p-5">
            <div className="flex items-baseline justify-between mb-2">
              <h2 className="font-display text-lg text-charcoal">{s.organization_name}</h2>
              <span className="font-ui text-xs text-slate">
                {new Date(s.submitted_at).toLocaleString()}
              </span>
            </div>
            <p className="font-ui text-sm text-charcoal mb-1">
              {s.contact_name} · {s.contact_email}
              {s.contact_phone ? ` · ${s.contact_phone}` : ""}
            </p>
            <p className="font-ui text-xs text-slate uppercase tracking-wide mb-2">
              {s.crisis_categories.map((c) => CATEGORY_LABELS[c] ?? c).join(" · ")}
            </p>
            {s.description && (
              <p className="font-ui text-sm text-charcoal leading-relaxed">{s.description}</p>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
