```vue
<script setup lang="ts">
import type { RemoteVariableDto } from "@/types/ModuleTypes";

defineProps<{
    items: RemoteVariableDto[];
    label?: string | undefined;
}>();
</script>

<template>
    <div
        class="border border-amber-100 bg-white p-1 shadow-sm flex flex-col gap-y-1"
    >
        <div class="text-amber-500 uppercase text-xs">
            {{ label }}
        </div>
        <div v-show="items?.length == 0" class="text-gray-500 text-xs italic">
            - empty -
        </div>
        <div
            v-for="variable in items"
            :key="variable.name"
            class="p-0.5 text-sm"
        >
            <div class="flex flex-col items-start justify-between">
                <span
                    class="break-all rounded bg-gray-100 font-mono text-xs text-stone-800"
                >
                    {{ variable.value }}
                </span>

                <span class="text-xs text-slate-500">
                    {{ variable.name }}
                </span>
            </div>

            <div
                v-if="variable.children?.length"
                class="mt-3 border-l-2 border-gray-200 pl-3"
            >
                <VariableTreeFeature :items="variable.children" />
            </div>
        </div>
    </div>
</template>
```
