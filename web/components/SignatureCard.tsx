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
  const selectedCount = cardStates.filter((s) =>
    selectedStateIds.includes(s.id)
  ).length;
  const unselectedCount = cardStates.length - selectedCount;

  return (
    <Collapsible.Root open={isExpanded} onOpenChange={onToggleExpand}>
      <div data-selected={isSelected}>
        <button onClick={onSelect}>
          <span>{signature.name}</span>
        </button>

        <p>{signature.description}</p>

        <Collapsible.Trigger asChild>
          <button>
            {isExpanded
              ? "Collapse"
              : `${unselectedCount} ${unselectedCount === 1 ? "condition" : "conditions"} inside`}
          </button>
        </Collapsible.Trigger>

        <Collapsible.Content>
          <ul>
            {cardStates.map((state) => {
              const isStateSelected = selectedStateIds.includes(state.id);
              return (
                <li key={state.id} data-selected={isStateSelected}>
                  <button onClick={() => onSelectState(state.id)}>
                    <span>{state.name}</span>
                    <p>{state.description}</p>
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
