<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function goHome() {
  router.push("/");
}
</script>

<template>
  <div class="container">
    <img src="/src/assets/sflogowhite.png" class="image" @click="goHome"/>
    <div class="title">
      VueModuleUI
    </div>
  </div>
</template>

<style scoped>
.container {
  width: 18rem;
  height: 4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.image {
  height: 2.5rem;
  padding-top: 0.5rem;
  opacity: 0.8;
  cursor: pointer;
}

.image:hover {
  opacity: 1.0;
}

.title {
  font-size: small
}
</style>