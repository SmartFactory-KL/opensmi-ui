<script setup lang="ts">
import {
    BugIcon,
    MessageCircleCodeIcon,
    MessageCircleIcon,
    MessageCircleWarningIcon,
    TriangleAlert,
} from "@lucide/vue";
</script>

<template>
    <div
        class="flex flex-row justify-end items-center gap-x-2 border-2 border-slate-500 rounded-md px-2 py-1 bg-slate-200 cursor-pointer"
    >
        <div class="text-blue-600 flex flex-col justify-center items-center">
            <MessageCircleIcon :size="24" class="fill-blue-500">
            </MessageCircleIcon>
            <span class="text-xs"> 482 </span>
        </div>
        <div class="text-amber-600 flex flex-col justify-center items-center">
            <TriangleAlert :size="24" class="fill-amber-400"></TriangleAlert>
            <span class="text-xs"> 32 </span>
        </div>
        <div class="text-red-600 flex flex-col justify-center items-center">
            <BugIcon :size="24" class="fill-red-400"></BugIcon>
            <span class="text-xs"> 4 </span>
        </div>
    </div>
</template>
