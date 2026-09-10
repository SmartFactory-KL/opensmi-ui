<script setup lang="ts">
import { usePageStore } from "../../../stores/PageStore";
import BlueButton from "../../BlueButton.vue";
import WritableRemoteVariableInput from "./WritableRemoteVariableInput.vue";
import WritableRemoteVariableValueDisplay from "./WritableRemoteVariableValueDisplay.vue";

const props = defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();

const emit = defineEmits<{
  (e: "write-request", remoteVariable: RemoteVariableDto): void;
}>();

function handleOnEnterKeyUp() {
  if (props.enableWrites) {
    emit("write-request", props.remoteVariable);
  }
}

const pageStore = usePageStore();
</script>

<template>
  <div class="remote-variable mt-0.5">
    <div class="variable-content flex flex-col border border-secondary">
      <div
        class="text-base text-gray-500 flex flex-col justify-start items-center"
      >
        {{ remoteVariable.name }}
        <span class="text-xs" v-show="pageStore.showFlags.nodeIds">
          | {{ remoteVariable.nodeId }}
        </span>
      </div>
      <div class="flex flex-row justify-between items-center p-1">
        <div class="flex flex-row basis-1/2 justify-center">
          <div class="parameter-input" @keyup.enter="handleOnEnterKeyUp">
            <WritableRemoteVariableInput
              :remote-variable="remoteVariable"
              :enable-writes="enableWrites"
            ></WritableRemoteVariableInput>
          </div>
        </div>
        <div>
          <BlueButton
            @click="$emit('write-request', remoteVariable)"
            :disabled="!enableWrites"
            tabindex="-1"
            style="
              width: 4rem;
              padding-left: 0.4rem !important;
              padding-right: 0.4rem !important;
            "
          >
            <span class="text-sm"
              >Set <i class="fa-solid fa-angle-right fa-sm"></i
            ></span>
          </BlueButton>
        </div>
        <WritableRemoteVariableValueDisplay :remote-variable="remoteVariable"></WritableRemoteVariableValueDisplay>
      </div>
    </div>
    <div class="variable-children ml-4">
      <WritableRemoteVariableDisplay
        v-for="remoteVariable of remoteVariable.children"
        :remote-variable="remoteVariable"
        :enable-writes="enableWrites"
        @write-request="$emit('write-request', $event)"
      ></WritableRemoteVariableDisplay>
    </div>
  </div>
</template>

<style scoped>
.remote-variable {
  flex-basis: calc(33% - 5rem);
  min-width: 30rem;
}

.parameter-input {
  max-width: 9rem;
}

.parameter-value {
  width: 9rem;
}
</style>
