<script setup lang="ts">
import { useToasterStore } from "@/stores/ToasterStore";
import ToastMessage from "./ToastMessage.vue";

const toasterStore = useToasterStore();

function dismissToast(id: number) {
    toasterStore.removeToast(id);
}
</script>

<template>
    <div
        class="pointer-events-none fixed bottom-4 right-4 z-100 flex w-[calc(100%-2rem)] max-w-sm flex-col gap-2 sm:bottom-6 sm:right-6"
        aria-label="Notifications"
    >
        <TransitionGroup
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="translate-x-3 opacity-0"
            enter-to-class="translate-x-0 opacity-100"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="translate-x-0 opacity-100"
            leave-to-class="translate-x-3 opacity-0"
            move-class="transition-transform duration-200"
        >
            <div
                v-for="toast in toasterStore.toasts"
                :key="toast.id"
                class="pointer-events-auto"
            >
                <ToastMessage :toast="toast" @close="dismissToast" />
            </div>
        </TransitionGroup>
    </div>
</template>
