"use client";

import { Drawer } from "vaul";
import { signatures, getStatesForSignature } from "@/data/taxonomy";
import { useSelfSelection } from "@/context/SelfSelectionContext";

function AssemblyList() {
  const { selectedStateIds, selectedSignatureIds } = useSelfSelection();

  const grouped = signatures
    .map((sig) => {
      const allStates = getStatesForSignature(sig.id);
      const selected = allStates.filter((s) => selectedStateIds.has(s.id));
      const unselected = allStates.filter(
        (s) => !selectedStateIds.has(s.id) && selectedSignatureIds.has(sig.id)
      );
      return { signature: sig, selected, unselected };
    })
    .filter((g) => g.selected.length > 0 || g.unselected.length > 0);

  if (grouped.length === 0) {
    return (
      <p className="text-sm text-gray-400 leading-relaxed">
        Select conditions to build your picture.
      </p>
    );
  }

  return (
    <div className="space-y-5">
      {grouped.map(({ signature, selected, unselected }) => (
        <div key={signature.id}>
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            {signature.name}
          </p>
          <ul className="space-y-0 divide-y divide-gray-100">
            {selected.map((state) => (
              <li key={state.id} className="py-2 first:pt-0">
                <span className="text-sm text-gray-900 leading-snug">
                  {state.name}
                </span>
              </li>
            ))}
            {unselected.map((state) => (
              <li key={state.id} className="py-2 first:pt-0">
                <span className="font-ui text-xs text-gray-300 leading-snug">
                  {state.name}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default function AssemblyPanel() {
  const { selectedStateIds, activeSheet, setActiveSheet } = useSelfSelection();
  const count = selectedStateIds.size;

  return (
    <>
      {/* Desktop — persistent sidebar */}
      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-l border-gray-200 bg-white sticky top-0 h-screen overflow-y-auto">
        <div className="p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-4">
            What you&apos;re carrying
          </p>
          <AssemblyList />
        </div>
      </aside>

      {/* Mobile — Vaul bottom sheet */}
      <div className="md:hidden">
        <Drawer.Root
          open={activeSheet === "assembly"}
          onOpenChange={(open) => setActiveSheet(open ? "assembly" : null)}
        >
          <Drawer.Trigger asChild>
            <button
              onClick={() => setActiveSheet("assembly")}
              className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 px-5 py-4 flex items-center justify-between text-sm font-medium text-gray-900"
            >
              <span>
                {count > 0
                  ? `${count} ${count === 1 ? "condition" : "conditions"} selected`
                  : "Select conditions to build your picture."}
              </span>
              <span className="text-gray-400 text-xs">View</span>
            </button>
          </Drawer.Trigger>
          <Drawer.Portal>
            <Drawer.Overlay className="fixed inset-0 z-40 bg-black/30" />
            <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl border-t border-gray-200 flex flex-col max-h-[80vh]">
              <Drawer.Title className="sr-only">What you&apos;re carrying</Drawer.Title>
              <div className="flex justify-center pt-3 pb-1 shrink-0">
                <div className="w-10 h-1 rounded-full bg-gray-300" />
              </div>
              <div className="overflow-y-auto px-5 pt-4 pb-10">
                <AssemblyList />
              </div>
            </Drawer.Content>
          </Drawer.Portal>
        </Drawer.Root>
      </div>
    </>
  );
}
