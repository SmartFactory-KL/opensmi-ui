<script lang="ts" setup>
import TitleClock from "./TitleClock.vue";
import TitleBranding from "./TitleBranding.vue";
import TitleStateOverview from "./TitleStateOverview.vue";
import TitleSettings from "./TitleSettings.vue";
import PinGuardButton from "../pin-guard/PinGuardButton.vue";
import TitleLogStats from "./TitleLogStats.vue";
</script>

<template>
  <div class="main-title">
    <div class="title-left flex flex-row justify-end items-center gap-x-2">
      <TitleBranding></TitleBranding>
      <div class="divider"></div>
      <TitleClock></TitleClock>
    </div>
    <div class="title-center">
      <TitleLogStats></TitleLogStats>
    </div>
    <div class="title-right flex flex-row justify-end items-center gap-x-2">
      <PinGuardButton></PinGuardButton>
      <div class="divider"></div>

      <TitleStateOverview></TitleStateOverview>
      <TitleSettings></TitleSettings>
    </div>
  </div>
</template>

<style scoped>
.main-title {
  @apply bg-primary text-gray-100;
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  min-height: 4rem;

  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: space-between;
}

.title-left {
  display: flex;
  justify-content: flex-start;
  flex-basis: 0;
  flex-grow: 2;
}

.title-center {
  display: flex;
  justify-content: center;
  flex-basis: 0;
  flex-grow: 1;
}

.title-right {
  display: flex;
  justify-content: flex-end;
  flex-basis: 0;
  flex-grow: 2;
}

.divider {
  @apply bg-white;
  height: 70%;
  width: 0.1rem;
}
</style>
