<script setup lang="ts">
import { computed, ref } from "vue";
import { usePageStore } from "../../../stores/PageStore";

import VariablePlot from "./plot/VariablePlot.vue";

const IMAGE_B64_PREFIX: Record<string, string> = {
  ImageJPG: "data:image/jpeg;base64, ",
  ImagePNG: "data:image/png;base64, ",
  ImageBMP: "data:image/bmp;base64, ",
  ImageGIF: "data:image/gif;base64, ",
};

const props = defineProps<{
  remoteVariable: RemoteVariableDto;
}>();

const isClickableLink = computed(() => {
  if (
    props.remoteVariable?.dataContent &&
    typeof props.remoteVariable.dataContent.value.value == "string"
  ) {
    return props.remoteVariable.dataContent.value.value.startsWith("http");
  }

  return false;
});

const isPlotVisible = ref(false);

const imageBase64Prefix = computed(() => {
  switch (props.remoteVariable.remoteVariableType) {
    case "ImageJPG":
    case "ImageBMP":
    case "ImagePNG":
    case "ImageGIF":
      return IMAGE_B64_PREFIX[props.remoteVariable.remoteVariableType];
      break;
    default:
      return "";
  }
});

function togglePlot() {
  isPlotVisible.value = !isPlotVisible.value;
}

const pageStore = usePageStore();
</script>

<template>
  <div class="remote-variable mt-0.5">
    <div class="variable-content flex flex-col">
      <div
        v-if="remoteVariable.remoteVariableType.startsWith('Image')"
        class="min-h-6"
      >
        <img
          :src="imageBase64Prefix + remoteVariable.dataContent.value.value"
          style="max-width: 300px; max-height: 300px"
        />
      </div>
      <div
        class="flex flex-row justify-between items-center bg-gray-300 border border-gray-300 p-0.5"
        v-else
      >
        <div class="min-h-6">
          {{ remoteVariable.dataContent.value.value }}
          <span v-show="isClickableLink">
            <a
              :href="remoteVariable.dataContent.value.value"
              target="_blank"
              class="text-secondary hover:text-primary"
            >
              <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
          </span>
        </div>
        <div class="flex flex-row justify-end items-center gap-x-2">
          <div v-show="remoteVariable.unit?.length">
            | {{ remoteVariable.unit }}
          </div>
          <div>|</div>
          <div class="mr-1">
            <div
              @click="togglePlot()"
              class="flex flex-row justify-center items-center gap-x-1 cursor-pointer hover:scale-105 hover:text-secondary"
              :class="{
                'text-primary': !isPlotVisible,
                'text-purple-700': isPlotVisible,
              }"
            >
              <i class="fa-solid fa-chart-simple"></i>
              <i class="fa-solid fa-caret-up" v-show="isPlotVisible"></i>
              <i class="fa-solid fa-caret-down" v-show="!isPlotVisible"></i>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isPlotVisible">
        <VariablePlot
          :entity-id="remoteVariable.entityId"
          :initial-value="remoteVariable.dataContent.value.value"
          :initial-timestamp="
            remoteVariable.dataContent.timestamp
              ? new Date(remoteVariable.dataContent.timestamp).getTime() /
                1000.0
              : Date.now() / 1000.0
          "
        ></VariablePlot>
      </div>
      <span class="text-xs text-gray-500">
        {{ remoteVariable.name }}
        <span v-show="pageStore.showFlags.entityIds">
          | {{ remoteVariable.entityId }}</span
        >
        <span v-show="pageStore.showFlags.nodeIds">
          | {{ remoteVariable.nodeId }}</span
        >
        <span v-show="pageStore.showFlags.timestamps">
          |
          {{
            new Date(
              remoteVariable.dataContent.timestamp * 1000.0
            ).toLocaleString()
          }}
        </span>
      </span>
    </div>
    <div class="variable-children ml-4">
      <RemoteVariableDisplay
        v-for="remoteVariable of remoteVariable.children"
        :remote-variable="remoteVariable"
      ></RemoteVariableDisplay>
    </div>
  </div>
</template>

<style scoped></style>
