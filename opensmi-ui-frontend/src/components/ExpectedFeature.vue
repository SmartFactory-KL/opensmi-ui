<script setup lang="ts">
import { Info } from "@lucide/vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import FeatureErrorWrapper from "@/components/FeatureErrorWrapper.vue";
import { computed } from "vue";

const props = defineProps<{
    expectedFeature: FeatureNode | undefined | null;
    expectedFeatureType?: string;
    optional?: boolean;
}>();

defineSlots<{
    default(props: { resolvedFeature: FeatureNode }): unknown;
}>();

const isFeatureOk = computed(() => {
    return (
        props.expectedFeature !== null && props.expectedFeature !== undefined
    );
});
</script>

<template>
    <FeatureErrorWrapper
        v-if="isFeatureOk"
        :feature="expectedFeature!"
        v-slot="{ feature: resolvedFeature }"
    >
        <slot :resolved-feature="resolvedFeature"></slot>
    </FeatureErrorWrapper>
    <div
        v-else-if="!optional"
        role="status"
        class="flex w-fit min-w-0 max-w-xs items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 py-0.5 pl-1.5 pr-2 text-xs leading-snug text-slate-600"
    >
        <span
            class="flex size-8 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sky-600"
        >
            <Info class="size-6" aria-hidden="true" />
        </span>
        <span
            class="flex min-w-0 flex-col items-center justify-around gap-y-2 wrap-break-word py-2"
            v-show="!isFeatureOk"
        >
            <div>Missing Feature</div>
            <div
                v-if="expectedFeatureType?.length"
                class="rounded-full bg-amber-700 px-2 py-0.5 text-slate-100"
            >
                {{ expectedFeatureType }}
            </div>
        </span>
    </div>
</template>
