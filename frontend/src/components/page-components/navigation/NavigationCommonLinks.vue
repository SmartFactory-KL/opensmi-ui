<script setup lang="ts"></script>

<template>
  <div class="navigation-common">
    <RouterLink class="nav-item" to="/">
      <i class="fa-solid fa-house fa-2x"></i>
      <span>Home</span>
    </RouterLink>
    <RouterLink class="nav-item" to="/server">
      <i class="fa-solid fa-tower-observation fa-2x"></i>
      <span>Server</span>
    </RouterLink>

    <div>
      <RouterLink class="nav-item" to="/logs">
        <i class="fa-solid fa-rectangle-list fa-2x"></i>
        <span> Logs </span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.navigation-common {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.nav-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-left: 1rem;
  padding-right: 1rem;
}

.nav-item:hover {
  @apply bg-gray-400;
  scale: 1.05;
}

.nav-item.router-link-active {
  @apply text-white;
  @apply bg-primary;
}
</style>
