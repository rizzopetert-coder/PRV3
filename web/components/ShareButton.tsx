"use client";

import { useState } from "react";
import type { EnginePayload } from "@/lib/engine-client";

interface ShareButtonProps {
  selectedStateIds: string[];
  intake: EnginePayload["intake"];
}

type ShareState = "idle" | "creating" | "ready" | "error";

export default function ShareButton({ selectedStateIds, intake }: ShareButtonProps) {
  const [shareState, setShareState] = useState<ShareState>("idle");
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleCreateShare() {
    if (shareState === "creating") return;
    setShareState("creating");
    try {
      const res = await fetch("/api/share/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedStateIds, intake }),
      });
      if (!res.ok) {
        setShareState("error");
        return;
      }
      const data = (await res.json()) as {
        share_id: string;
        shareUrl: string;
        expiresAt: string;
      };
      setShareUrl(data.shareUrl);
      setShareState("ready");
    } catch {
      setShareState("error");
    }
  }

  async function handleCopy() {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (shareState === "error") {
    return (
      <div className="w-full">
        <p className="text-[13px] text-gray-400 mb-3">
          Something went wrong. Try again.
        </p>
        <button
          onClick={handleCreateShare}
          className="w-full border border-charcoal text-charcoal text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  if (shareState === "ready" && shareUrl) {
    return (
      <div className="w-full">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Shareable link
        </p>
        <div className="flex items-center gap-3 px-3 py-2.5 bg-paper border border-gray-200 rounded-lg">
          <p className="text-[13px] text-gray-600 flex-1 truncate">{shareUrl}</p>
          <button
            onClick={handleCopy}
            className="text-[13px] font-medium text-charcoal whitespace-nowrap hover:text-gray-500 transition-colors"
          >
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleCreateShare}
      disabled={shareState === "creating"}
      className="w-full bg-charcoal text-white text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {shareState === "creating" ? "Creating..." : "Create shareable version"}
    </button>
  );
}
