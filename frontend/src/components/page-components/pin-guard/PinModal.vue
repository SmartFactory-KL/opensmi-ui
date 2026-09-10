<script lang="ts" setup>
import { onMounted, onUnmounted } from "vue";
import { usePinGuardStore } from "../../../stores/PinStore";

const pinStore = usePinGuardStore();

const handleKeydown = (e: KeyboardEvent) => {
  // only handle if modal is visible
  if (pinStore.pinModalVisible != true) {
    return;
  }

  // numbers (top row + numpad)
  if (e.key >= "0" && e.key <= "9") {
    pinStore.addNumber(Number(e.key));
    return;
  }

  // backspace → remove last digit
  if (e.key === "Backspace") {
    pinStore.removeLast();
    return;
  }

  // escape → reset
  if (e.key === "Escape") {
    pinStore.resetPin();
    pinStore.hidePinModal();
    return;
  }

  // enter → submit
  if (e.key === "Enter") {
    pinStore.sendPin();
    return;
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});

async function requestLock() {
  await pinStore.sendLockRequest();
  pinStore.pinModalVisible = false;
}
</script>

<template>
  <div
    class="pin-modal-bg"
    v-if="pinStore.pinModalVisible"
    @click.self="pinStore.hidePinModal"
  >
    <div class="pin-modal">
      <div class="pin-modal-title">
        <div class="text-slate-900 text-lg">Enter PIN Code</div>
        <div
          @click="pinStore.hidePinModal()"
          class="hover:scale-105 cursor-pointer hover:text-secondary"
        >
          <i class="fa-solid fa-circle-xmark fa-2x"></i>
        </div>
      </div>
      <div class="pin-display">
        <div
          class="text-lg flex flex-row justify-center items-center h-full tracking-widest"
        >
          <i class="fa fa-circle" v-for="_ in pinStore.digits.length"></i>
        </div>
      </div>
      <div class="mt-2 mb-4 text-sm text-orange-600">
        {{ pinStore.pinFeedback }}
      </div>

      <div class="number-pad">
        <div
          class="pad-item bg-slate-900 text-slate-200"
          v-for="num in 9"
          @click="pinStore.addNumber(num)"
        >
          {{ num }}
        </div>
        <div
          class="pad-item bg-yellow-900 text-slate-200"
          @click="pinStore.resetPin()"
        >
          <i class="fa-solid fa-arrow-rotate-left"></i>
        </div>
        <div
          class="pad-item bg-slate-900 text-slate-200"
          @click="pinStore.addNumber(0)"
        >
          0
        </div>
        <div
          class="pad-item bg-green-900 text-slate-200"
          @click="pinStore.sendPin()"
        >
          <i class="fa-solid fa-check"></i>
        </div>
      </div>
      <hr class="my-4 border-slate-400" />
      <div class="flex justify-center">
        <!-- Lock button -->
        <button
          @click="requestLock"
          class="flex items-center gap-2 bg-purple-900 hover:bg-purple-700 text-slate-200 px-4 py-2 shadow-md transition-transform transform hover:scale-105 active:scale-95"
        >
          <i class="fa-solid fa-lock"></i>
          <span class="font-medium">Lock</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pin-modal-bg {
  @apply bg-slate-800 bg-opacity-60;
  position: fixed;
  width: 100vw;
  height: 100vh;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 40;
}

.pin-modal-title {
  @apply flex flex-row justify-between items-center;
}

.pin-display {
  @apply mt-2 mb-2 bg-slate-200;
  height: 4rem;
}

.pin-modal {
  @apply bg-slate-300 p-4 border-2 border-slate-950 flex flex-col justify-center items-stretch;
  position: fixed;
  left: calc(50vw - 10rem);
  top: 5rem;
  min-height: 20rem;
  width: 20rem;
  z-index: 100;
}

.number-pad {
  @apply flex flex-row flex-wrap justify-center items-start gap-4;
}

.pad-item {
  @apply basis-1/4 text-4xl  flex flex-row justify-center items-center cursor-pointer;
  height: 5rem;
  width: 6rem;
}

.pad-item:hover {
  scale: 1.05;
}

.pad-item:active {
  @apply bg-secondary;
}
</style>
