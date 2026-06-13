"use client";

import { Drawer } from "vaul";
import { uiCopy } from "@/data/taxonomy";
import type { State } from "@/data/taxonomy";

interface AssemblyPanelProps {
  selectedStates: State[];
  onRemove: (stateId: string) => void;
}

function AssemblyList({ selectedStates, onRemove }: AssemblyPanelProps) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-4">
        {uiCopy.assemblyTitle}
      </p>
      {selectedStates.length === 0 ? (
        <p className="text-sm text-gray-400 leading-relaxed">
          {uiCopy.assemblyEmpty}
        </p>
      ) : (
        <ul className="space-y-0 divide-y divide-gray-100">
          {selectedStates.map((state) => (
            <li
              key={state.id}
              className="flex items-start justify-between gap-3 py-2.5 first:pt-0"
            >
              <span className="text-sm text-gray-900 leading-snug">
                {state.name}
              </span>
              <button
                onClick={() => onRemove(state.id)}
                className="text-xs text-gray-400 hover:text-gray-700 transition-colors shrink-0 mt-0.5"
              >
                Remove
              </button>
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
      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-l border-gray-200 bg-white sticky top-0 h-screen overflow-y-auto">
        <div className="p-6">
          <AssemblyList selectedStates={selectedStates} onRemove={onRemove} />
        </div>
      </aside>

      {/* Mobile — Vaul bottom sheet */}
      <div className="md:hidden">
        <Drawer.Root>
          <Drawer.Trigger asChild>
            <button className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 px-5 py-4 flex items-center justify-between text-sm font-medium text-gray-900">
              <span>
                {count > 0
                  ? `${count} ${count === 1 ? "condition" : "conditions"} selected`
                  : uiCopy.assemblyEmpty}
              </span>
              <span className="text-gray-400 text-xs">View</span>
            </button>
          </Drawer.Trigger>
          <Drawer.Portal>
            <Drawer.Overlay className="fixed inset-0 z-40 bg-black/30" />
            <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl border-t border-gray-200 flex flex-col max-h-[80vh]">
              <Drawer.Title className="sr-only">
                {uiCopy.assemblyTitle}
              </Drawer.Title>
              {/* Drag handle */}
              <div className="flex justify-center pt-3 pb-1 shrink-0">
                <div className="w-10 h-1 rounded-full bg-gray-300" />
              </div>
              <div className="overflow-y-auto px-5 pt-4 pb-10">
                <AssemblyList
                  selectedStates={selectedStates}
                  onRemove={onRemove}
                />
              </div>
            </Drawer.Content>
          </Drawer.Portal>
        </Drawer.Root>
      </div>
    </>
  );
}
