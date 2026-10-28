<script setup lang="ts">
import ValueInputScalar from "./ValueInputScalar.vue";

// One level of a (possibly multi-dimensional) array. Recursive: every level
// except the last renders one child level per index.
const props = defineProps<{
    type: string;
    /** shape of this level and everything below it, e.g. [2, 3, 4] */
    dimensions: number[];
}>();
const model = defineModel<any[]>({ required: true });

function setAt(index: number, value: unknown) {
    const next = [...model.value];
    next[index] = value;
    model.value = next;
}
</script>

<template>
    <div v-if="props.dimensions.length <= 1" class="flex flex-row items-center gap-1">
        <ValueInputScalar
            v-for="(item, i) in model"
            :key="i"
            :type="props.type"
            :model-value="item"
            @update:model-value="setAt(i, $event)"
        />
    </div>
    <div v-else class="flex flex-col gap-1">
        <div v-for="(sub, i) in model" :key="i" class="flex flex-row items-start gap-1">
            <span class="w-6 pt-1 text-right text-xs text-stone-500">{{ i }}</span>
            <ValueInputArrayLevel
                :model-value="sub"
                :type="props.type"
                :dimensions="props.dimensions.slice(1)"
                @update:model-value="setAt(i, $event)"
            />
        </div>
    </div>
</template>
