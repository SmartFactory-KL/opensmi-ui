<template>
  <div class="loader">
    <i class="fa-solid fa-robot fa-bounce fa-4x text-gray-400"></i>
    <span class="text-sm text-gray-400">
      Loading machine data...
    </span>
  </div>
</template>

<style scoped>
.loader {
  display: flex;
  flex-direction: column;
  row-gap: 2rem;
  justify-content: center;
  align-items: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 4rem;
  width: 15rem;
}

.fa-beat, .fa-bounce, .fa-fade, .fa-beat-fade, .fa-flip, .fa-pulse, .fa-shake, .fa-spin, .fa-spin-pulse
{
  animation-duration: 1s;
  animation-iteration-count: infinite;
}
</style>
