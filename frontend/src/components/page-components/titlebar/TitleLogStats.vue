<script lang="ts" setup>
import { useNotificationStore } from "../../../stores/NotificationStore";
import TitleLogStatsItem from "./TitleLogStatsItem.vue";

const notificationstore = useNotificationStore();
</script>

<template>
  <div
    class="flex flex-row justify-center items-center gap-x-6 cursor-pointer hover:scale-105 bg-slate-700 px-4 rounded-md my-2"
    @click="$router.push('/logs')"
  >
    <i class="fa-solid fa-rectangle-list fa-2xl"></i>

    <TitleLogStatsItem
      :stat-item="notificationstore.notificationStatistics.info"
      class="text-blue-200"
    ><i class="fa-solid fa-info-circle fa-2xl"></i></TitleLogStatsItem>
    <TitleLogStatsItem
      :stat-item="notificationstore.notificationStatistics.warning"
      class="text-amber-200"
    ><i class="fa-solid fa-warning fa-2xl"></i></TitleLogStatsItem>
    <TitleLogStatsItem
      :stat-item="notificationstore.notificationStatistics.error"
      class="text-red-200"
    ><i class="fa-solid fa-bug fa-2xl"></i></TitleLogStatsItem>
  </div>
</template>
