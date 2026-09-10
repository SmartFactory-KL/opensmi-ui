<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from "vue";

const time = reactive({
  hours: "0",
  minutes: "0",
  seconds: "0",
  date: "",
  tDelta: 0,
  tDeltaLabel: "",
});

const showDelta = ref(false)

let now = new Date();
let intervalHandle: number;

function updateTime() {
  now = new Date();
  time.hours = now.getHours().toString().padStart(2, "0");
  time.minutes = now.getMinutes().toString().padStart(2, "0");
  time.seconds = now.getSeconds().toString().padStart(2, "0");

  time.date = now.toLocaleString(navigator.language, {
    weekday: "short",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

onMounted(() => {
  updateTime();
  intervalHandle = setInterval(updateTime, 500);
});

onUnmounted(() => {
  clearInterval(intervalHandle);
});
</script>

<template>
  <div class="container">
    <div class="clock">
      {{ time.hours }}:{{ time.minutes }}:{{ time.seconds }}
    </div>
    <div class="date" @click="showDelta = !showDelta">
      {{ time.date }}
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  width: 12rem;
  padding-left: 1rem;
  padding-right: 1rem;
}

.clock {
  font-family: monospace;
  height: 2rem;
  line-height: 2rem;
  font-size: 1.5rem;
}

.delta {
  font-size: 0.5rem;
}

.date {
  font-family: monospace;
  font-size: smaller;
}
</style>
