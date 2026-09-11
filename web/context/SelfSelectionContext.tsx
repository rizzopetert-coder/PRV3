'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface SelfSelectionState {
  selectedStateIds: Set<string>;
  selectedSignatureIds: Set<string>;
  // 'assembly' | signatureId | null
  activeSheet: string | null;
  // Live rendered height (px) of AssemblyPanel's mobile Drawer.Trigger,
  // measured via ResizeObserver. Used by the Phase 2 transition bar to
  // offset its own bottom position so the two fixed bars stack instead
  // of overlapping. 0 when the trigger isn't rendered (desktop, or
  // AssemblyPanel unmounted).
  assemblyTriggerHeight: number;
}

interface SelfSelectionActions {
  toggleState: (stateId: string, signatureId: string) => void;
  toggleSignature: (signatureId: string, stateIds: string[]) => void;
  setActiveSheet: (sheet: string | null) => void;
  setAssemblyTriggerHeight: (height: number) => void;
  clearAll: () => void;
}

type SelfSelectionContextValue = SelfSelectionState & SelfSelectionActions;

const SelfSelectionContext = createContext<SelfSelectionContextValue | null>(null);

export function SelfSelectionProvider({ children }: { children: ReactNode }) {
  const [selectedStateIds, setSelectedStateIds] = useState<Set<string>>(new Set());
  const [selectedSignatureIds, setSelectedSignatureIds] = useState<Set<string>>(new Set());
  const [activeSheet, setActiveSheetState] = useState<string | null>(null);
  const [assemblyTriggerHeight, setAssemblyTriggerHeightState] = useState<number>(0);

  const toggleState = useCallback((stateId: string, signatureId: string) => {
    setSelectedStateIds(prev => {
      const next = new Set(prev);
      if (next.has(stateId)) {
        next.delete(stateId);
      } else {
        next.add(stateId);
      }
      return next;
    });
    // If deselecting, remove signature-level cluster selection
    setSelectedSignatureIds(prev => {
      const next = new Set(prev);
      next.delete(signatureId);
      return next;
    });
  }, []);

  const toggleSignature = useCallback((signatureId: string, stateIds: string[]) => {
    setSelectedSignatureIds(prev => {
      const next = new Set(prev);
      if (next.has(signatureId)) {
        next.delete(signatureId);
        setSelectedStateIds(prevStates => {
          const nextStates = new Set(prevStates);
          stateIds.forEach(id => nextStates.delete(id));
          return nextStates;
        });
      } else {
        next.add(signatureId);
        setSelectedStateIds(prevStates => {
          const nextStates = new Set(prevStates);
          stateIds.forEach(id => nextStates.add(id));
          return nextStates;
        });
      }
      return next;
    });
  }, []);

  const setActiveSheet = useCallback((sheet: string | null) => {
    setActiveSheetState(sheet);
  }, []);

  const setAssemblyTriggerHeight = useCallback((height: number) => {
    setAssemblyTriggerHeightState(height);
  }, []);

  const clearAll = useCallback(() => {
    setSelectedStateIds(new Set());
    setSelectedSignatureIds(new Set());
    setActiveSheetState(null);
  }, []);

  return (
    <SelfSelectionContext.Provider value={{
      selectedStateIds,
      selectedSignatureIds,
      activeSheet,
      assemblyTriggerHeight,
      toggleState,
      toggleSignature,
      setActiveSheet,
      setAssemblyTriggerHeight,
      clearAll,
    }}>
      {children}
    </SelfSelectionContext.Provider>
  );
}

export function useSelfSelection() {
  const ctx = useContext(SelfSelectionContext);
  if (!ctx) throw new Error('useSelfSelection must be used within SelfSelectionProvider');
  return ctx;
}
