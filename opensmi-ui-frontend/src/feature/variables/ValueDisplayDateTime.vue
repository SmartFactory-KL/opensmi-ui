<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
    value: string; // ISO 8601, UTC
}>();

const date = computed(() => new Date(props.value));
const isValid = computed(() => !Number.isNaN(date.value.getTime()));

const formatted = computed(() =>
    isValid.value
        ? new Intl.DateTimeFormat(undefined, {
              dateStyle: "medium",
              timeStyle: "medium",
          }).format(date.value)
        : props.value,
);
</script>

<template>
    <time
        class="tabular-nums"
        :datetime="isValid ? value : undefined"
        :title="value"
    >
        {{ formatted }}
    </time>
</template>
