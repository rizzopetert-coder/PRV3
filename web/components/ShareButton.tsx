"use client";

import { useState } from "react";

interface ShareButtonProps {
  sessionId: string;
  onShareCreated?: (shareKey: string, shareUrl: string) => void;
}

type ShareState = "idle" | "creating" | "ready" | "error";

export default function ShareButton({
  sessionId,
  onShareCreated,
}: ShareButtonProps) {
  const [shareState, setShareState] = useState<ShareState>("idle");
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  async function handleCreateShare() {
    if (shareState === "creating") return;
    setShareState("creating");

    try {
      const res = await fetch("/api/share/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId }),
      });

      if (!res.ok) {
        setShareState("error");
        return;
      }

      const data = (await res.json()) as {
        shareKey: string;
        shareUrl: string;
        expiresAt: string;
      };

      setShareUrl(data.shareUrl);
      setShareState("ready");
      onShareCreated?.(data.shareKey, data.shareUrl);
    } catch {
      setShareState("error");
    }
  }

  async function handleCopy() {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
  }

  if (shareState === "ready" && shareUrl) {
    return (
      <div>
        <p>{shareUrl}</p>
        <button onClick={handleCopy}>Copy link</button>
      </div>
    );
  }

  return (
    <button
      onClick={handleCreateShare}
      disabled={shareState === "creating"}
    >
      {shareState === "creating" ? "Creating link…" : "Share this report"}
      {shareState === "error" && " — try again"}
    </button>
  );
}
