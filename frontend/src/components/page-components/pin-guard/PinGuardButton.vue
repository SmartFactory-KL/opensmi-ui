<script lang="ts" setup>
import { usePinGuardStore } from "../../../stores/PinStore";

const pinStore = usePinGuardStore();
</script>

<template>
  <div class="pin-guard-button">
    <div
      v-if="!pinStore.pinState.isEnabled"
      title="PinGuard is disabled"
      class="flex flex-col justify-center items-center"
    >
      <span class="fa-stack opacity-30">
        <i class="fa-solid fa-shield fa-stack-2x"></i>
        <i
          class="fa-solid fa-power-off fa-stack-1x text-gray-400 opacity-70"
          v-show="!pinStore.pinState.isEnabled"
        ></i>
      </span>
    </div>
    <div
      v-else
      class="flex flex-col justify-center items-center"
      @click="pinStore.pinModalVisible = !pinStore.pinModalVisible"
    >
      <span
        class="shield fa-stack hover:scale-105 cursor-pointer"
        :class="{
          'is-locked': pinStore.pinState.isLocked,
          'is-unlocked': !pinStore.pinState.isLocked,
        }"
      >
        <i class="fa fa-stack">
          <i class="fa-solid fa-shield fa-stack-2x"></i>
          <i
            v-show="pinStore.pinState.isLocked"
            class="fa-solid text-purple-800 fa-lock fa-stack-1x"
          ></i>
          <i
            v-show="!pinStore.pinState.isLocked"
            class="fa-solid text-green-600 fa-check fa-stack-1x"
          ></i>
        </i>
      </span>
    </div>
  </div>
</template>

<style scoped>
.shield.is-locked {
  @apply text-purple-500;
}

.shield.is-unlocked {
  @apply text-green-500;
}
</style>
