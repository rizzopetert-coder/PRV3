"use client";

import { useState } from "react";

type FormState = "idle" | "submitting" | "success" | "error";

interface FormData {
  name: string;
  email: string;
  organization: string;
  message: string;
  website: string;
}

const EMPTY: FormData = {
  name: "",
  email: "",
  organization: "",
  message: "",
  website: "",
};

function isEmailShaped(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export default function AskPage() {
  const [formState, setFormState] = useState<FormState>("idle");
  const [form, setForm] = useState<FormData>(EMPTY);
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [serverError, setServerError] = useState<string | null>(null);

  function update(field: keyof FormData) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm((f) => ({ ...f, [field]: e.target.value }));
      if (fieldErrors[field]) {
        setFieldErrors((errs) => ({ ...errs, [field]: undefined }));
      }
    };
  }

  function validate(): boolean {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.name.trim()) errs.name = "Name is required.";
    if (!form.email.trim()) {
      errs.email = "Email is required.";
    } else if (!isEmailShaped(form.email.trim())) {
      errs.email = "Check that email address.";
    }
    if (!form.message.trim()) errs.message = "This field is required.";
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setFormState("submitting");
    setServerError(null);
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setFormState("success");
      } else {
        setFormState("error");
        setServerError("Something went wrong. Try again.");
      }
    } catch {
      setFormState("error");
      setServerError("Something went wrong. Try again.");
    }
  }

  if (formState === "success") {
    return (
      <main className="max-w-2xl mx-auto px-6 py-16">
        <p className="font-display text-2xl text-charcoal mb-4">Got it.</p>
        <p className="font-ui text-base text-gray-500">
          Message received. Expect to hear back within a couple of days.
        </p>
      </main>
    );
  }

  const disabled = formState === "submitting";

  const inputClass =
    "w-full bg-paper border border-charcoal px-3 py-2 font-ui text-sm text-charcoal focus:outline-none focus:border-slate focus:ring-1 focus:ring-slate disabled:opacity-60";

  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-2">Just Ask.</h1>
      <p className="font-ui text-base text-gray-500 mb-10">
        If you already know what you&apos;re dealing with, say it here.
      </p>

      <form onSubmit={handleSubmit} noValidate className="space-y-6">

        {/* Honeypot — real off-screen input, invisible to humans */}
        <div style={{ position: "absolute", left: "-9999px", top: "auto", width: "1px", height: "1px", overflow: "hidden" }} aria-hidden="true">
          <label htmlFor="website">Website</label>
          <input
            id="website"
            name="website"
            type="text"
            tabIndex={-1}
            autoComplete="off"
            value={form.website}
            onChange={update("website")}
          />
        </div>

        <div>
          <label htmlFor="name" className="block font-ui text-sm text-charcoal mb-1">
            Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            autoComplete="name"
            disabled={disabled}
            value={form.name}
            onChange={update("name")}
            className={inputClass}
          />
          {fieldErrors.name && (
            <p className="font-ui text-xs text-red-600 mt-1">{fieldErrors.name}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block font-ui text-sm text-charcoal mb-1">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            disabled={disabled}
            value={form.email}
            onChange={update("email")}
            className={inputClass}
          />
          {fieldErrors.email && (
            <p className="font-ui text-xs text-red-600 mt-1">{fieldErrors.email}</p>
          )}
        </div>

        <div>
          <label htmlFor="organization" className="block font-ui text-sm text-charcoal mb-1">
            Organization{" "}
            <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <input
            id="organization"
            name="organization"
            type="text"
            autoComplete="organization"
            disabled={disabled}
            value={form.organization}
            onChange={update("organization")}
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="message" className="block font-ui text-sm text-charcoal mb-1">
            What&apos;s going on?
          </label>
          <textarea
            id="message"
            name="message"
            rows={7}
            disabled={disabled}
            value={form.message}
            onChange={update("message")}
            className={`${inputClass} resize-y`}
          />
          {fieldErrors.message && (
            <p className="font-ui text-xs text-red-600 mt-1">{fieldErrors.message}</p>
          )}
        </div>

        {serverError && (
          <p className="font-ui text-sm text-red-600">{serverError}</p>
        )}

        <button
          type="submit"
          disabled={disabled}
          className="bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 hover:bg-gray-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {disabled ? "Sending…" : "Send"}
        </button>

      </form>
    </main>
  );
}
