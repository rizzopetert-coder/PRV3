"use client";

import { Drawer } from "vaul";
import { uiCopy } from "@/data/taxonomy";
import type { State } from "@/data/taxonomy";

interface AssemblyPanelProps {
  selectedStates: State[];
  onRemove: (stateId: string) => void;
}

function AssemblyList({
  selectedStates,
  onRemove,
}: AssemblyPanelProps) {
  return (
    <div>
      <p>{uiCopy.assemblyTitle}</p>
      {selectedStates.length === 0 ? (
        <p>{uiCopy.assemblyEmpty}</p>
      ) : (
        <ul>
          {selectedStates.map((state) => (
            <li key={state.id}>
              <span>{state.name}</span>
              <button onClick={() => onRemove(state.id)}>Remove</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AssemblyPanel({
  selectedStates,
  onRemove,
}: AssemblyPanelProps) {
  const count = selectedStates.length;

  return (
    <>
      {/* Desktop — persistent sidebar */}
      <aside className="hidden md:block">
        <AssemblyList selectedStates={selectedStates} onRemove={onRemove} />
      </aside>

      {/* Mobile — Vaul bottom sheet */}
      <div className="md:hidden">
        <Drawer.Root>
          <Drawer.Trigger asChild>
            {/* Collapsed state: floating summary bar */}
            <button>
              {count > 0
                ? `${count} ${count === 1 ? "condition" : "conditions"} selected`
                : uiCopy.assemblyEmpty}
            </button>
          </Drawer.Trigger>
          <Drawer.Portal>
            <Drawer.Overlay />
            <Drawer.Content>
              <Drawer.Title className="sr-only">
                {uiCopy.assemblyTitle}
              </Drawer.Title>
              <AssemblyList
                selectedStates={selectedStates}
                onRemove={onRemove}
              />
            </Drawer.Content>
          </Drawer.Portal>
        </Drawer.Root>
      </div>
    </>
  );
}
