import { defineStore } from "pinia";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { useModelStore } from "@/stores/ModelStore";
import { getFeatureName, getFeatureType } from "@/dashboard/featureUtils";

export type DashboardLayout = "rows" | "columns" | "grid";
export type DashboardGridSize = "small" | "medium" | "large";
export type DashboardSortKey = "name" | "type";
export type DashboardSortDirection = "asc" | "desc";

const STORAGE_KEY = "dashboard-state-v1";

interface PersistedState {
  elementIds: string[];
  layout: DashboardLayout;
  gridSize: DashboardGridSize;
}

function loadPersisted(): Partial<PersistedState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Partial<PersistedState>) : {};
  } catch {
    return {};
  }
}

export const useDashboardStore = defineStore("dashboard", {
  state: (): PersistedState => {
    const saved = loadPersisted();
    return {
      elementIds: Array.isArray(saved.elementIds) ? saved.elementIds : [],
      layout: saved.layout ?? "grid",
      gridSize: saved.gridSize ?? "medium",
    };
  },
  getters: {
    /** Dashboard elements resolved against the current model. IDs that
     *  don't exist (yet) in the model are skipped, not deleted. */
    elements(state): FeatureNode[] {
      const modelStore = useModelStore();
      return state.elementIds
        .map((id) => modelStore.entityIdFeatureNodeMap.get(id))
        .filter((f): f is FeatureNode => !!f);
    },
  },
  actions: {
    persist() {
      try {
        const data: PersistedState = {
          elementIds: this.elementIds,
          layout: this.layout,
          gridSize: this.gridSize,
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn("Could not persist dashboard state", e);
      }
    },
    clear() {
      this.elementIds = [];
      this.persist();
    },
    addElement(element: FeatureNode) {
      if (this.elementIds.includes(element.entityId)) return;
      this.elementIds.push(element.entityId);
      this.persist();
    },
    removeElement(entityId: string) {
      this.elementIds = this.elementIds.filter((id) => id !== entityId);
      this.persist();
    },
    /** Moves an element by `offset` positions among the visible elements. */
    moveElement(entityId: string, offset: number) {
      const visible = this.elements.map((e) => e.entityId);
      const from = visible.indexOf(entityId);
      const fromId = visible[from];
      const toId = visible[from + offset];
      if (fromId === undefined || toId === undefined) return;

      const a = this.elementIds.indexOf(fromId);
      const b = this.elementIds.indexOf(toId);
      if (a < 0 || b < 0) return;

      // remove the element and re-insert it at the target's position
      this.elementIds.splice(a, 1);
      this.elementIds.splice(b, 0, fromId);
      this.persist();
    },
    sortElements(key: DashboardSortKey, direction: DashboardSortDirection) {
      const factor = direction === "asc" ? 1 : -1;
      const sorted = [...this.elements].sort((a, b) => {
        const primary =
          key === "type"
            ? getFeatureType(a).localeCompare(getFeatureType(b))
            : 0;
        // use name as tiebreaker so type-sorting is stable and readable
        return (
          factor *
          (primary || getFeatureName(a).localeCompare(getFeatureName(b)))
        );
      });

      const sortedIds = sorted.map((e) => e.entityId);
      const sortedSet = new Set(sortedIds);
      const unresolved = this.elementIds.filter((id) => !sortedSet.has(id));
      this.elementIds = [...sortedIds, ...unresolved];
      this.persist();
    },
    setLayout(layout: DashboardLayout) {
      this.layout = layout;
      this.persist();
    },
    setGridSize(size: DashboardGridSize) {
      this.gridSize = size;
      this.persist();
    },
  },
});
