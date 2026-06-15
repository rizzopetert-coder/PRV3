"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { states as allStates } from "@/data/taxonomy";
import type { Signature } from "@/data/taxonomy";

interface SignatureCardProps {
  signature: Signature;
  isSelected: boolean;
  isExpanded: boolean;
  selectedStateIds: string[];
  onSelect: () => void;
  onToggleExpand: () => void;
  onSelectState: (stateId: string) => void;
}

export default function SignatureCard({
  signature,
  isSelected,
  isExpanded,
  selectedStateIds,
  onSelect,
  onToggleExpand,
  onSelectState,
}: SignatureCardProps) {
  const cardStates = allStates.filter((s) =>
    signature.stateIds.includes(s.id)
  );
  return (
    <Collapsible.Root open={isExpanded} onOpenChange={onToggleExpand}>
      <div
        className={`rounded-xl border bg-white transition-colors ${
          isSelected ? "border-gray-900" : "border-gray-200"
        }`}
      >
        {/* Card header */}
        <div className="px-5 pt-5 pb-4">
          <button
            onClick={onSelect}
            className="w-full text-left"
          >
            <span className="text-base font-semibold text-gray-900">
              {signature.name}
            </span>
          </button>

          <p className="text-sm text-gray-500 mt-1.5 leading-relaxed">
            {signature.description}
          </p>

          {/* Count affordance / collapse trigger */}
          <Collapsible.Trigger asChild>
            <button className="mt-3 text-xs text-gray-400 hover:text-gray-600 transition-colors">
              {isExpanded ? "Hide conditions" : "Show conditions"}
            </button>
          </Collapsible.Trigger>
        </div>

        {/* State list */}
        <Collapsible.Content>
          <ul className="px-3 pb-3 space-y-1.5">
            {cardStates.map((state) => {
              const isStateSelected = selectedStateIds.includes(state.id);
              return (
                <li key={state.id}>
                  <button
                    onClick={() => onSelectState(state.id)}
                    className={`w-full text-left rounded-lg px-3 py-2.5 transition-colors ${
                      isStateSelected
                        ? "border border-gray-900"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <span
                      className={`block text-sm ${
                        isStateSelected
                          ? "font-semibold text-gray-900"
                          : "text-gray-400"
                      }`}
                    >
                      {state.name}
                    </span>
                    <span
                      className={`block text-xs mt-0.5 leading-relaxed ${
                        isStateSelected ? "text-gray-500" : "text-gray-400"
                      }`}
                    >
                      {state.description}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </Collapsible.Content>
      </div>
    </Collapsible.Root>
  );
}
