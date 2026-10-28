<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { Info, CircleCheck, TriangleAlert, CircleX, X, Pin } from "@lucide/vue";
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

// Once the user clicks/taps the toast it stays until the X is clicked.
const pinned = ref(false);

let timer: ReturnType<typeof setTimeout> | undefined = undefined;

const styles: Record<
    ToastClass,
    {
        icon: typeof Info;
        iconClass: string;
        accentClass: string;
        label: string;
    }
> = {
    info: {
        icon: Info,
        iconClass: "text-sky-600",
        accentClass: "border-stone-200 border-l-sky-500",
        label: "Information",
    },
    success: {
        icon: CircleCheck,
        iconClass: "text-emerald-600",
        accentClass: "border-stone-200 border-l-emerald-500",
        label: "Success",
    },
    warning: {
        icon: TriangleAlert,
        iconClass: "text-amber-600",
        accentClass: "border-stone-200 border-l-amber-500",
        label: "Warning",
    },
    error: {
        icon: CircleX,
        iconClass: "text-rose-600",
        accentClass: "border-stone-200 border-l-rose-500",
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

    if (pinned.value || duration.value <= 0) {
        return;
    }

    timer = setTimeout(() => {
        // Guard against a pin that happened right before the timer fired.
        if (!pinned.value) {
            emit("close", props.toast.id);
        }
    }, duration.value);
}

function pin() {
    if (pinned.value) return;
    pinned.value = true;
    stopTimer();
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
        class="group relative w-full overflow-hidden shadow-lg bg-white border border-l-4 text-gray-800 transition-shadow"
        :class="[appearance.accentClass]"
        @click="pin"
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
                <div class="flex items-center gap-2">
                    <p
                        class="text-[11px] font-semibold uppercase tracking-wider text-gray-500"
                    >
                        {{ appearance.label }}
                    </p>

                    <span
                        v-if="pinned"
                        class="inline-flex items-center gap-1 bg-gray-200 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-gray-700"
                    >
                        <Pin
                            :size="10"
                            :stroke-width="2.5"
                            aria-hidden="true"
                        />
                        Pinned
                    </span>
                </div>

                <p
                    class="mt-1 whitespace-pre-wrap wrap-break-words text-sm leading-5"
                >
                    {{ toast.msg }}
                </p>
            </div>

            <button
                type="button"
                class="-mr-1 -mt-1 inline-flex size-7 shrink-0 items-center justify-center text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                :aria-label="`Close ${appearance.label.toLowerCase()} notification`"
                @click.stop="close"
            >
                <X :size="16" :stroke-width="2" aria-hidden="true" />
            </button>
        </div>
    </div>
</template>
