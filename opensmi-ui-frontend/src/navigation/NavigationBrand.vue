<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function goHome() {
    router.push("/");
}
</script>

<template>
    <div @click="goHome" class="cursor-pointer flex flex-row justify-center items-center ml-2 py-1">
        <img src="/src/assets/Logo_OpenSMI.svg"></img>
    </div>
</template>
