<script lang="ts" setup>
import {
  NOTIFICATION_MAX_COUNT,
  UINotificationStatistic,
} from "../../../stores/NotificationStore";

defineProps<{
  statItem: UINotificationStatistic;
}>();
</script>

<template>
  <div
    class="flex flex-row justify-center items-center gap-x-2 font-mono text-xs w-24"
  >
    <slot></slot>
    <div class="flex flex-col justify-center items-start">
      <div>
        <i class="fa fa-list"></i>
        {{ statItem.total }}<span v-show="statItem.total >= NOTIFICATION_MAX_COUNT">+</span>
      </div>

      <div><i class="fa fa-arrow-down"></i>  {{ statItem.lastDelta }}</div>
    </div>
  </div>
</template>
