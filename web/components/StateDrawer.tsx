"use client";

import { Drawer } from "vaul";
import { useSelfSelection } from "@/context/SelfSelectionContext";
import { getStatesForSignature } from "@/data/taxonomy";
import type { Signature } from "@/data/taxonomy";

interface StateDrawerProps {
  signature: Signature;
}

export function StateDrawer({ signature }: StateDrawerProps) {
  const { activeSheet, setActiveSheet, selectedStateIds, toggleState } =
    useSelfSelection();
  const isOpen = activeSheet === signature.id;
  const states = getStatesForSignature(signature.id);

  return (
    <>
      {/* Desktop panel — slides in from right */}
      <div
        className={`hidden md:block fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 z-40 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex justify-between items-center p-4 border-b border-gray-100">
          <span className="font-display text-base font-semibold text-gray-900">
            {signature.name}
          </span>
          <button
            onClick={() => setActiveSheet(null)}
            className="text-gray-400 hover:text-gray-900 transition-colors"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        <div className="overflow-y-auto h-full pb-24 p-4 space-y-3">
          {states.map((state) => {
            const isSelected = selectedStateIds.has(state.id);
            return (
              <button
                key={state.id}
                onClick={() => toggleState(state.id, signature.id)}
                className={`w-full text-left p-3 rounded border transition-all duration-150 ${
                  isSelected
                    ? "border-gray-900 bg-gray-50 font-semibold text-gray-900"
                    : "border-gray-200 text-gray-500 hover:border-gray-400 hover:text-gray-700"
                }`}
              >
                <span className="font-display text-sm block mb-1">
                  {state.name}
                </span>
                <span className="font-ui text-xs text-gray-500 font-normal">
                  {state.description}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Mobile — Vaul bottom sheet */}
      <Drawer.Root
        open={isOpen}
        onOpenChange={(open) => setActiveSheet(open ? signature.id : null)}
      >
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/30 z-40 md:hidden" />
          <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl max-h-[80vh] flex flex-col md:hidden">
            <Drawer.Title className="sr-only">{signature.name}</Drawer.Title>
            <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-2 flex-shrink-0" />
            <div className="flex justify-between items-center px-4 pb-3 border-b border-gray-100 flex-shrink-0">
              <span className="font-display text-base font-semibold text-gray-900">
                {signature.name}
              </span>
            </div>
            <div className="overflow-y-auto p-4 space-y-3 pb-8">
              {states.map((state) => {
                const isSelected = selectedStateIds.has(state.id);
                return (
                  <button
                    key={state.id}
                    onClick={() => toggleState(state.id, signature.id)}
                    className={`w-full text-left p-3 rounded border transition-all duration-150 ${
                      isSelected
                        ? "border-gray-900 bg-gray-50 font-semibold text-gray-900"
                        : "border-gray-200 text-gray-500"
                    }`}
                  >
                    <span className="font-display text-sm block mb-1">
                      {state.name}
                    </span>
                    <span className="font-ui text-xs text-gray-500 font-normal">
                      {state.description}
                    </span>
                  </button>
                );
              })}
            </div>
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>
    </>
  );
}
