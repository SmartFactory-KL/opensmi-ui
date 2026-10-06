<script setup lang="ts">
import { onMounted, onUnmounted, reactive } from "vue";

const time = reactive({
    hours: "0",
    minutes: "0",
    seconds: "0",
});

let now = new Date();
let intervalHandle: number;

function updateTime() {
    now = new Date();
    time.hours = now.getHours().toString().padStart(2, "0");
    time.minutes = now.getMinutes().toString().padStart(2, "0");
    time.seconds = now.getSeconds().toString().padStart(2, "0");
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
    <div>{{ time.hours }}:{{ time.minutes }}:{{ time.seconds }}</div>
</template>
