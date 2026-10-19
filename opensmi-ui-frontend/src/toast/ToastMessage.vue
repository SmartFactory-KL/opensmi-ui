<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { Info, CircleCheck, TriangleAlert, CircleX, X } from "@lucide/vue";
import type { ToastClass, ToastMessage } from "@/toast/Toaster";

const props = defineProps<{
    toast: ToastMessage & { id: number };
}>();

const emit = defineEmits<{
    close: [id: number];
}>();

const DEFAULT_DELAY = 750;

const duration = computed(() =>
    Math.max(0, props.toast.settings.delayMS ?? DEFAULT_DELAY),
);

const remaining = ref(duration.value);
const isPaused = ref(false);

let timer: ReturnType<typeof setTimeout> | undefined = undefined;

const styles: Record<
    ToastClass,
    {
        icon: typeof Info;
        iconClass: string;
        accentClass: string;
        progressClass: string;
        label: string;
    }
> = {
    info: {
        icon: Info,
        iconClass: "text-sky-600",
        accentClass: "border-l-sky-500",
        progressClass: "bg-sky-500",
        label: "Information",
    },
    success: {
        icon: CircleCheck,
        iconClass: "text-emerald-600",
        accentClass: "border-l-emerald-500",
        progressClass: "bg-emerald-500",
        label: "Success",
    },
    warning: {
        icon: TriangleAlert,
        iconClass: "text-amber-600",
        accentClass: "border-l-amber-500",
        progressClass: "bg-amber-500",
        label: "Warning",
    },
    error: {
        icon: CircleX,
        iconClass: "text-rose-600",
        accentClass: "border-l-rose-500",
        progressClass: "bg-rose-500",
        label: "Error",
    },
};

const appearance = computed(() => styles[props.toast.toastClass]);

function stopTimer() {
    if (timer !== undefined) {
        clearTimeout(timer);
        timer = undefined;
    }
}

function startTimer() {
    stopTimer();

    if (isPaused.value || duration.value <= 0) {
        return;
    }

    if (remaining.value <= 0) {
        emit("close", props.toast.id);
        return;
    }

    timer = setTimeout(() => {
        remaining.value = 0;
        emit("close", props.toast.id);
    }, remaining.value);
}

function close() {
    stopTimer();
    emit("close", props.toast.id);
}

onMounted(startTimer);
onBeforeUnmount(stopTimer);
</script>

<template>
    <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        class="group relative w-full overflow-hidden border border-l-4 border-l-transparent border-gray-200 bg-white text-gray-800"
        :class="appearance.accentClass"
    >
        <div class="flex items-start gap-3 px-4 py-3.5">
            <component
                :is="appearance.icon"
                :size="20"
                :stroke-width="1.8"
                class="mt-0.5 shrink-0"
                :class="appearance.iconClass"
                aria-hidden="true"
            />

            <div class="min-w-0 flex-1">
                <p
                    class="text-[11px] font-semibold uppercase tracking-wider text-gray-500"
                >
                    {{ appearance.label }}
                </p>

                <p
                    class="mt-1 whitespace-pre-wrap wrap-break-words text-sm leading-5"
                >
                    {{ toast.msg }}
                </p>
            </div>

            <button
                v-if="toast.settings.closable"
                type="button"
                class="-mr-1 -mt-1 inline-flex size-7 shrink-0 items-center justify-center text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                :aria-label="`Close ${appearance.label.toLowerCase()} notification`"
                @click="close"
            >
                <X :size="16" :stroke-width="2" aria-hidden="true" />
            </button>
        </div>
    </div>
</template>
