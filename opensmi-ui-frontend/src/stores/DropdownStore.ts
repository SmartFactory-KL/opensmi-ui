import { defineStore } from "pinia";

export const useDropdownStore = defineStore("dropdown", {
  state: (): {
    isVisible: boolean;
  } => {
    return {
      isVisible: false,
    };
  },
  actions: {
    toggleDropdown() {
      this.isVisible = !this.isVisible;
    },
    closeDropdown() {
      this.isVisible = false;
    }
  },
});
