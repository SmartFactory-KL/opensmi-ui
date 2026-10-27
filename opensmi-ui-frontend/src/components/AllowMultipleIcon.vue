<script setup lang="ts">
import { CheckIcon, UsersIcon, XIcon } from "@lucide/vue";

defineProps<{
    allowsMultiple: boolean;
}>();
</script>

<template>
    <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        class="shrink-0"
        :class="allowsMultiple ? 'text-emerald-600' : 'text-gray-400'"
        role="img"
    >
        <title>
            {{
                allowsMultiple ? "Multi-User allowed" : "Multi-User not allowed"
            }}
        </title>

        <!-- Base icon fills the whole viewBox -->
        <UsersIcon :size="24" />

        <!-- Badge: white ring, colored disc, then the nested icon -->
        <circle cx="17.5" cy="17.5" r="6.5" fill="white" />
        <circle
            cx="17.5"
            cy="17.5"
            r="5"
            :fill="allowsMultiple ? '#10b981' : '#ef4444'"
        />
        <CheckIcon
            v-if="allowsMultiple"
            x="13.5"
            y="13.5"
            :size="8"
            :stroke-width="4"
            color="white"
        />
        <XIcon
            v-else
            x="13.5"
            y="13.5"
            :size="8"
            :stroke-width="4"
            color="white"
        />
    </svg>
</template>
