<script setup lang="ts">
import type { VariantData } from "@/types/OPCTypes";
import { PlusIcon, XIcon } from "@lucide/vue";
import { computed } from "vue";
import IconButton from "@/components/IconButton.vue";
import ValueInputArrayLevel from "./ValueInputArrayLevel.vue";
import ValueInputScalar from "./ValueInputScalar.vue";
import { defaultScalar } from "./ValueInputUtils";
import type { VariableModifier } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    modifiers?: VariableModifier[];
}>();

const variant = defineModel<VariantData>({ required: true });

// The backend only sends `dimensions` for arrays with 2+ dimensions.
const dimensions = computed<number[] | null>(() => {
    const dims = variant.value.dimensions;
    return dims && dims.length > 1 ? [...dims] : null;
});

const items = computed<unknown[]>(() => {
    const val = variant.value.value;
    return Array.isArray(val) ? val : [];
});

function setItems(value: unknown[]) {
    variant.value = { ...variant.value, value } as VariantData;
}

function setItem(index: number, value: unknown) {
    const next = [...items.value];
    next[index] = value;
    setItems(next);
}

function addItem() {
    setItems([...items.value, defaultScalar(variant.value.type)]);
}

function removeItem(index: number) {
    setItems(items.value.filter((_, i) => i !== index));
}
</script>

<template>
    <div class="flex flex-col gap-1 max-w-full">
        <!-- multi-dimensional: the shape is fixed, so elements can only be edited -->
        <div v-if="dimensions" class="overflow-x-auto">
            <ValueInputArrayLevel
                :model-value="items"
                :type="variant.type"
                :modifiers="modifiers"
                :dimensions="dimensions"
                @update:model-value="setItems"
            />
        </div>

        <!-- one-dimensional: elements can be added and removed -->
        <template v-else>
            <div
                v-for="(item, i) in items"
                :key="i"
                class="flex flex-row items-center gap-1"
            >
                <XIcon
                    @click="removeItem(i)"
                    class="size-6 cursor-pointer active:scale-90"
                ></XIcon>
                <div class="w-6">
                    <span class="w-6 text-right text-xs text-stone-500">{{
                        i
                    }}</span>
                </div>
                <ValueInputScalar
                    :type="variant.type"
                    :model-value="item"
                    :modifiers="modifiers"
                    @update:model-value="setItem(i, $event)"
                />
            </div>
            <div class="flex flex-row justify-center items-center">
                <PlusIcon @click="addItem"></PlusIcon>
            </div>
        </template>

        <span class="text-xs text-stone-500">
            {{ dimensions ? dimensions.join(" × ") : `${items.length} items` }}
        </span>
    </div>
</template>
