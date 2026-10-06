<script setup lang="ts">
import MainNavigation from "./navigation/MainNavigation.vue";
</script>

<template>
    <main class="main">
        <div>
            <MainNavigation></MainNavigation>
        </div>
        <div
            class="bg-red-50 overflow-x-auto overflow-y-scroll border-t-4 border-t-slate-500"
        >
            <RouterView :key="$route.fullPath"></RouterView>
            <div class="h-full">Dulli</div>
            <div class="h-full">Dulli</div>
            <div class="h-full">Dulli</div>
        </div>
    </main>
</template>

<style scoped>
.main {
    display: grid;
    height: 100vh;
    width: 100vw;
    grid-template-rows: 4rem 1fr;
    grid-template-columns: 1fr;
}
</style>
