<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../../stores/MachineStore";
import { usePageStore } from "../../../../stores/PageStore";

import NotFoundNotice from "../../../NotFoundNotice.vue";
import SkillControlBoard from "../../skill/SkillControlBoard.vue";
import SkillLink from "../../skill/SkillLink.vue";
import MethodLink from "../../method/MethodLink.vue";
import StorageSlotDisplay from "./storage/StorageSlotDisplay.vue";

import { computed, reactive, watch } from "vue";
import { useServerStore } from "../../../../stores/ServerStore";
import NodeBreadcrumbContainer from "../../../NodeBreadcrumbContainer.vue";

const SETTINGS_KEY = "sf-module-ui-storage-quick-view-settings";

const ZOOM_MIN = 0.01;
const ZOOM_MAX = 2.0;

const route = useRoute();

const machineStore = useMachineStore();
const pageStore = usePageStore();
const serverStore = useServerStore();

const props = defineProps<{
  component: ComponentDto;
}>();

const quickViewSettings = reactive({
  itemsPerRow: 6,
  flipHorizontal: false,
  flipVertical: false,
  zoomLevel: 1.0,
});

function increaseZoomNumber() {
  if (quickViewSettings.zoomLevel + 0.1 > ZOOM_MAX) {
    quickViewSettings.zoomLevel = ZOOM_MAX;
  } else {
    quickViewSettings.zoomLevel =
      Math.round((quickViewSettings.zoomLevel + 0.1) * 100) / 100.0;
  }
}

function decreaseZoomNumber() {
  if (quickViewSettings.zoomLevel - 0.1 < ZOOM_MIN) {
    quickViewSettings.zoomLevel = ZOOM_MIN;
  } else {
    quickViewSettings.zoomLevel =
      Math.round((quickViewSettings.zoomLevel - 0.1) * 100) / 100.0;
  }
}

watch(quickViewSettings, function (newVal, _) {
  localStorage.setItem(
    SETTINGS_KEY + "[" + (component?.nodeId || "common") + "]",
    JSON.stringify(newVal),
  );
});

function readItemsPerRow() {
  const input = localStorage.getItem(
    SETTINGS_KEY + "[" + (component?.nodeId || "common") + "]",
  );
  if (input) {
    try {
      const jsonInput = JSON.parse(input);
      quickViewSettings.itemsPerRow = jsonInput.itemsPerRow;
      quickViewSettings.flipHorizontal = jsonInput.flipHorizontal;
      quickViewSettings.flipVertical = jsonInput.flipVertical;
      quickViewSettings.zoomLevel = jsonInput.zoomLevel;
    } catch (e) {
      console.warn("unable to parse json for storage quick view settings");
      console.warn(e);
    }
  }
}

const lockedByUs = computed(() => {
  if (!component) {
    return false;
  }
  const machine = machineStore.entityToParentMachineMap.get(component.entityId);

  if (!machine) {
    return false;
  }

  if (!machine.lockingModule.isLocked) {
    return false;
  }

  if (
    machine.lockingModule.lockingUser != serverStore.connectionData.username
  ) {
    return false;
  }

  return true;
});

const component = machineStore.componentEntityMap.get(
  route.params.componentEntityId as string,
);

const slotGrid = computed(() => {
  const grid = [] as ComponentDto[][];

  if (!component?.components.length) {
    return [];
  }

  for (
    let k = 0;
    k < component.components.length;
    k = k + quickViewSettings.itemsPerRow
  ) {
    grid[k] = component.components.slice(k, k + quickViewSettings.itemsPerRow);
    if (quickViewSettings.flipHorizontal === true) {
      grid[k].reverse();
    }
  }

  if (quickViewSettings.flipVertical === true) {
    grid.reverse();
  }

  return grid;
});

const freeStorageSlotCount = computed(() => {
  return (
    props.component.monitoring.find(
      (item) => item.name === "FreeStorageSlotCount",
    )?.dataContent.value.value ?? 0
  );
}); //

const storageSlotCount = computed(() => {
  return (
    props.component.attributes.find((item) => item.name === "StorageSlotCount")
      ?.dataContent.value.value ?? 0
  );
});

const slotUsagePercentage = computed(() => {
  if (storageSlotCount.value > 0) {
    return freeStorageSlotCount.value / storageSlotCount.value;
  }

  return 1.0;
});

readItemsPerRow();
</script>

<template>
  <div v-if="!component"><NotFoundNotice></NotFoundNotice></div>
  <div v-else class="m-8">
    <NodeBreadcrumbContainer
      :parent-node-id-list="component.parentNodeIdList"
      class="mb-2"
    ></NodeBreadcrumbContainer>
    <div class="title-line">
      <div class="title">
        <div
          class="text-gray-800 flex flex-row gap-x-4 justify-start items-center"
        >
          <div class="flex flex-col justify-start items-start">
            <div class="text-3xl flex flex-row justify-start items-center">
              <i class="fa-solid fa-toolbox fa-xs mr-1"></i> |
              {{ component.name }} |
              <span class="text-gray-500 text-sm mt-2 ml-4"
                >{{ Math.floor(slotUsagePercentage * 100) }} % free</span
              >
            </div>
            <div class="flex flex-col">
              <span class="text-sm" v-show="pageStore.showFlags.nodeIds">
                <span class="text-gray-400">NodeId</span> {{ component.nodeId }}
              </span>
              <span class="text-sm" v-show="pageStore.showFlags.entityIds">
                <span class="text-gray-400">EntityId</span>
                {{ component.entityId }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Type</span> {{ component.type }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <hr class="border-primary mt-1" />

    <div class="flex flex-row justify-around mt-2 mb-4">
      <div class="basis-1/4">
        <span
          v-show="!component.skillSet?.length"
          class="text-base text-gray-500"
        >
          No skills
        </span>
        <div v-show="component.skillSet?.length">
          <div class="mb-2 text-lg text-primary">Skillset</div>
          <div
            v-for="skill of component.skillSet"
            class="flex flex-row justify-start gap-x-4 items-center"
          >
            <SkillControlBoard
              :skill="skill"
              :show-as-tiny="true"
            ></SkillControlBoard>
            <SkillLink :skill="skill"></SkillLink>
          </div>
        </div>
      </div>

      <div class="basis-1/4">
        <span
          v-show="!component.methods?.length"
          class="text-base text-gray-500"
        >
          No methods
        </span>
        <div v-show="component.methods?.length">
          <div class="mb-2 text-lg text-primary">Methods</div>
          <div
            v-for="method of component.methods"
            class="flex flex-row justify-start gap-x-4 items-center"
          >
            <MethodLink :method="method"></MethodLink>
          </div>
        </div>
      </div>

      <div class="basis-1/3">
        <div class="mb-2 text-lg text-primary">Storage Quick View</div>
        <div class="flex flex-row justify-start items-center gap-x-4 h-8">
          <select v-model="quickViewSettings.itemsPerRow">
            <option v-for="idx in 15" :value="idx">{{ idx }}</option>
          </select>
          |
          <button
            class="border border-primary px-4 py-1 cursor-pointer hover:scale-105 active:scale-90"
            :class="{
              'text-green-600 bg-green-200': quickViewSettings.flipHorizontal,
            }"
            title="flip horizontally"
            @click="
              quickViewSettings.flipHorizontal =
                !quickViewSettings.flipHorizontal
            "
          >
            <i class="fa-solid fa-arrows-left-right"></i>
          </button>
          |
          <button
            class="border border-primary px-4 py-1 cursor-pointer hover:scale-105 active:scale-90"
            :class="{
              'text-green-600 bg-green-200': quickViewSettings.flipVertical,
            }"
            title="flip vertically"
            @click="
              quickViewSettings.flipVertical = !quickViewSettings.flipVertical
            "
          >
            <i class="fa-solid fa-arrows-up-down"></i>
          </button>
          |
          <div class="flex flex-row justify-start items-center gap-x-2">
            <div
              class="w-10 h-10 flex flex-row justify-center items-center cursor-pointer hover:scale-105"
              @click="decreaseZoomNumber()"
            >
              <i class="fa-solid fa-down-left-and-up-right-to-center fa-sm"></i>
            </div>
            <input
              type="range"
              min="0.1"
              max="2.0"
              step="0.05"
              v-model.number="quickViewSettings.zoomLevel"
            />
            <input
              type="text"
              v-model="quickViewSettings.zoomLevel"
              maxlength="5"
              class="w-16 border border-primary px-2 py-1"
            />
            <div
              class="w-10 h-10 flex flex-row justify-center items-center cursor-pointer hover:scale-105"
              @click="increaseZoomNumber()"
            >
              <i class="fa-solid fa-up-right-and-down-left-from-center fa-lg">
              </i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <hr class="border-primary" />

    <div
      class="flex flex-col justify-start items-start overflow-x-auto"
      :style="{ zoom: quickViewSettings.zoomLevel }"
    >
      <div
        class="flex justify-start items-start"
        :key="idx"
        v-for="(slotLine, idx) of slotGrid"
      >
        <StorageSlotDisplay
          :storage-slot="slot"
          :locked-by-us="lockedByUs"
          :key="slot.entityId"
          v-for="slot of slotLine"
        ></StorageSlotDisplay>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-line {
  @apply flex flex-row justify-between items-start;
}
</style>
