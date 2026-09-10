<script setup lang="ts">
import { computed } from "vue";

interface Props {
  lockingModule: LockingModuleDto;
  serverUserName: string;
  enableTitle?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  enableTitle: false,
});

const isLockedByUser = computed(() => {
  return (
    props.lockingModule.isLocked == true &&
    props.lockingModule.lockingUser == props.serverUserName
  );
});

const isLockedByOthers = computed(() => {
  return (
    props.lockingModule.isLocked == true &&
    props.lockingModule.lockingUser != props.serverUserName
  );
});

const isLocked = computed(() => {
  return props.lockingModule.isLocked == true;
});

const lockTitleString = computed(() => {
  if (isLockedByUser.value) {
    return "Locked by " + props.lockingModule.lockingUser;
  } else if (isLockedByOthers.value) {
    return "Locked by " + props.lockingModule.lockingUser;
  } else {
    return "Not locked";
  }
});
</script>

<template>
  <div class="flex flex-col">
    <div
      class="locking-display"
      :title="'Locking by UI disabled! ' + lockTitleString"
    >
      <i class="fa-solid fa-key"></i>
      <i
        class="fa-solid fa-lock-open"
        v-show="!isLocked"
        :class="{ 'animate-spin': lockingModule.isLockPending }"
      ></i>
      <i
        class="fa-solid fa-lock"
        :class="{
          'text-green-400': isLockedByUser,
          'text-yellow-400': isLockedByOthers,
          'animate-spin': lockingModule.isLockPending,
        }"
        v-show="isLocked"
      ></i>

      <i
        class="fa-solid fa-user-lock text-green-400"
        v-show="isLockedByUser"
      ></i>
      <i
        class="fa-solid fa-plane-lock text-yellow-400"
        v-show="isLockedByOthers"
      ></i>
      <i class="fa-solid fa-circle-notch fa-2xs" v-show="!isLocked"></i>
    </div>
    <div v-if="enableTitle == true" class="text-base flex flex-col">
      {{ lockTitleString }}
    </div>
  </div>
</template>

<style scoped>
.locking-display {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  column-gap: 0.5rem;
  opacity: 0.6;
}
</style>
