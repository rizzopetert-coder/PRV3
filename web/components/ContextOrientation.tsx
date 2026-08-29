"use client";

import { useId, useState } from "react";
import { Drawer } from "vaul";

// Site-wide contextual orientation affordance. Desktop: hover/focus resolves
// an anchored panel via the real, already-shipped [data-emphasis] utilities
// (globals.css, "receded"/"primary" -- untouched by this component). Mobile:
// tap opens a vaul bottom drawer, exact shape copied from book/toc/page.tsx's
// TermsGuide pattern (Drawer.Root/Portal/Overlay/Content/Title, sr-only
// title, open/onOpenChange to local state) -- not reinvented.
//
// Token discipline, enforced here and re-checked by grep before every commit
// that touches this file: never --color-rust, --urgency, or --urgency-text,
// in any form. Those are reserved exclusively for genuine Endemic-severity
// signaling elsewhere in the app (ConstellationField.tsx's
// severityAccentTokens()) -- this component has nothing to do with severity
// and must never borrow that color family, decoratively or otherwise.

export type OrientationVariant = "inline" | "floating" | "modal-drawer";

export interface ContextOrientationProps {
  variant: OrientationVariant;
  /** Stable id for this trigger -- used in aria-label and the drawer's sr-only title. */
  topic: string;
  title: string;
  /** One line, shown at the top of the resolved panel/drawer. */
  summary: string;
  /** Body copy. */
  details: string;
  /** Wrapper override for per-surface trigger placement (e.g. floating position). */
  className?: string;
}

function TriggerLabel({ title }: { title: string }) {
  return (
    <>
      <span aria-hidden className="inline-block w-4 h-4 rounded-full border border-line text-[10px] leading-[14px] text-center mr-1.5 align-middle">
        i
      </span>
      <span className="align-middle">{title}</span>
    </>
  );
}

function PanelBody({
  summary,
  details,
}: {
  summary: string;
  details: string;
}) {
  return (
    <>
      <p className="font-ui text-sm font-semibold text-ink mb-2">{summary}</p>
      <p className="font-ui text-sm text-oxide-text leading-relaxed">{details}</p>
    </>
  );
}

export default function ContextOrientation({
  variant,
  topic,
  title,
  summary,
  details,
  className,
}: ContextOrientationProps) {
  // Desktop resolve state (hover/focus for inline & floating; click for
  // modal-drawer, since a modal shouldn't open on a stray hover). Mobile
  // drawer state is fully independent -- resolved never drives `open` and
  // vice versa, matching the TermsGuide precedent's termsHovered/termsTapped
  // split exactly.
  const [resolved, setResolved] = useState(false);
  const [open, setOpen] = useState(false);
  const panelId = useId();

  const triggerCommon = {
    type: "button" as const,
    "aria-label": title,
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        // Desktop keyboard activation resolves the panel via focus already
        // firing onFocus below -- preventDefault here stops the space bar's
        // native scroll/click behavior from also firing, per the spec's
        // explicit accessibility requirement.
        e.preventDefault();
        if (variant === "modal-drawer") setResolved((cur) => !cur);
      }
    },
  };

  const triggerClass =
    "font-ui text-xs text-[color:var(--slate)] hover:text-hover-ink transition-colors";

  const panelSurfaceClass =
    variant === "floating" ? "bg-field-raise" : "bg-field";

  const desktopPanel = resolved && (
    <div
      id={panelId}
      data-emphasis="primary"
      className={
        variant === "modal-drawer"
          ? `hidden md:block fixed inset-0 z-40 flex items-center justify-center`
          : `hidden md:block absolute z-10 w-80 max-h-96 overflow-y-auto rounded-md border border-line p-4 shadow-lg ${panelSurfaceClass} ${
              variant === "floating" ? "bottom-full mb-2 right-0" : "top-full left-0"
            }`
      }
      onMouseLeave={variant !== "modal-drawer" ? () => setResolved(false) : undefined}
    >
      {variant === "modal-drawer" ? (
        <div
          className={`relative w-96 max-w-[90vw] max-h-[80vh] overflow-y-auto rounded-lg border border-line p-6 shadow-xl ${panelSurfaceClass}`}
        >
          <button
            type="button"
            aria-label="Close"
            onClick={() => setResolved(false)}
            className="absolute top-3 right-3 text-[color:var(--slate)] hover:text-hover-ink font-ui text-sm"
          >
            ×
          </button>
          <PanelBody summary={summary} details={details} />
        </div>
      ) : (
        <PanelBody summary={summary} details={details} />
      )}
    </div>
  );

  return (
    <div
      className={`${variant === "floating" ? "fixed z-30" : "relative inline-block"} ${
        className ?? ""
      }`}
      data-emphasis={resolved ? "primary" : "receded"}
    >
      <button
        {...triggerCommon}
        aria-describedby={resolved ? panelId : undefined}
        aria-haspopup={variant === "modal-drawer" ? "dialog" : undefined}
        aria-expanded={variant === "modal-drawer" ? resolved : resolved || open}
        className={`hidden md:inline-flex items-center ${triggerClass}`}
        onMouseEnter={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onFocus={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onBlur={variant !== "modal-drawer" ? () => setResolved(false) : undefined}
        onClick={variant === "modal-drawer" ? () => setResolved((cur) => !cur) : undefined}
      >
        <TriggerLabel title={title} />
      </button>
      {desktopPanel}

      {/* Mobile trigger + drawer -- every variant collapses to the same
          bottom-sheet pattern below md, per the spec: only desktop
          presentation differs between inline/floating/modal-drawer. */}
      <button
        type="button"
        aria-label={title}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen(true)}
        className={`md:hidden inline-flex items-center ${triggerClass}`}
      >
        <TriggerLabel title={title} />
      </button>

      <Drawer.Root open={open} onOpenChange={setOpen}>
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/30 z-40 md:hidden" />
          <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-field rounded-t-2xl max-h-[80vh] flex flex-col md:hidden">
            <Drawer.Title className="sr-only">{title}</Drawer.Title>
            <div className="w-10 h-1 bg-line-strong rounded-full mx-auto mt-3 mb-2 shrink-0" />
            <div className="overflow-y-auto p-4 pb-8" data-topic={topic}>
              <PanelBody summary={summary} details={details} />
            </div>
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>
    </div>
  );
}
