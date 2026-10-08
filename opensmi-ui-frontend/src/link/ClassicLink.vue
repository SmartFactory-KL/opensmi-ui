<script setup lang="ts">
import { useRouter } from "vue-router";

const props = defineProps<{
    to: string;
}>();

const router = useRouter();

function route() {
    router.push(props.to);
}
</script>

<template>
    <div @click="route()" class="cursor-pointer active:underline">
        <slot></slot>
    </div>
</template>
