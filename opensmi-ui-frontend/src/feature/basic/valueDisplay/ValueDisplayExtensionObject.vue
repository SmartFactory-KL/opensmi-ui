<script setup lang="ts">
import type { ExtensionObjectData } from "@/types/OPCTypes";
import ValueDisplayRaw from "./ValueDisplayRaw.vue";
import ValueDisplayByteString from "./ValueDisplayBytes.vue";

defineProps<{
    value: ExtensionObjectData;
}>();

function isPrimitive(v: unknown): v is string | number | boolean | null {
    return v === null || typeof v !== "object";
}
</script>

<template>
    <div class="flex flex-col gap-1">
        <span
            v-if="value.typeName"
            class="w-fit rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-700"
        >
            {{ value.typeName }}
        </span>

        <!-- Decoded structure: one row per member -->
        <dl
            v-if="value.members"
            class="grid grid-cols-[max-content_1fr] gap-x-3 gap-y-0.5 text-sm"
        >
            <template v-for="(member, name) in value.members" :key="name">
                <dt class="text-slate-500">{{ name }}</dt>
                <dd class="min-w-0 wrap-break-word">
                    <template v-if="isPrimitive(member)">
                        {{ member ?? "-" }}
                    </template>
                    <ValueDisplayRaw v-else :value="member" />
                </dd>
            </template>
        </dl>

        <!-- Undecoded structure: raw bytes -->
        <ValueDisplayByteString v-else-if="value.body" :value="value.body" />
    </div>
</template>
