<script setup lang="ts">
import { ref } from "vue";
import { simplyGet } from "../../util/SimplyFetch";

let debugInformation = ref("Loading...");

async function loadDebugInformation() {
  try {
    const result = (await simplyGet("/api/server/debug/info")) as {
      [key: string]: string;
    };

    debugInformation.value = JSON.stringify(result, null, 2);
  } catch (e) {
    debugInformation.value = (e as Error).message;
  }
}

loadDebugInformation();
</script>

<template>
  <div class="p-4 flex flex-col justify-center items-center h-full w-full">
    <div class="text-gray-600 font-bold mb-4">VueModuleUI Configuration</div>
    <div class="text-xs text-gray-800 mb-4 w-80">
      This is the configuration that has been used on startup of this ModuleUI. 
      Please compare it to your actual config inputs and make sure they match.
    </div>
    <div>
      <textarea rows="20" cols="80" class="p-4 text-sm">{{ debugInformation }}</textarea>
    </div>
    <div class="text-sm text-pink-400 mt-4">
      Please always provide this information whenever you want to report a
      problem. Note that sensitive information is masked.
    </div>
  </div>
</template>

<style scoped></style>
