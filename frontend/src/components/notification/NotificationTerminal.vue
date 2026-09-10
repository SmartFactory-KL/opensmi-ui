<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import { UINotification } from "../../stores/NotificationStore";

const props = defineProps<{
  notifications: UINotification[];
}>();

const stickToBottom = ref(true);
const terminalContainer = ref<HTMLElement | null>(null);

const BOTTOM_THRESHOLD = 20;

function handleScroll() {
  if (!terminalContainer.value) {
    return;
  }

  stickToBottom.value = isAtBottom(terminalContainer.value);
}

function isAtBottom(el: HTMLElement) {
  return el.scrollHeight - el.scrollTop - el.clientHeight < BOTTOM_THRESHOLD;
}

function scrollToBottom() {
  if (terminalContainer.value) {
    terminalContainer.value.scrollTop = terminalContainer.value.scrollHeight;
  }
}

watch(
  () => props.notifications.length,
  async () => {
    await nextTick();

    if (stickToBottom.value) {
      scrollToBottom();
    }
  },
);

onMounted(() => {
  scrollToBottom();
});
</script>

<template>
  <div
    ref="terminalContainer"
    class="h-full font-mono text-sm bg-slate-800 text-gray-100 p-4 m-0 overflow-y-auto"
    v-on:scroll="handleScroll"
  >
    <div v-for="notification in notifications">
      {{ notification.createTime }} | {{ notification.level }} |
      {{ notification.message }} | {{ notification.debugMessage }}
    </div>

    <div v-show="!notifications.length" class="text-gray-400 font-mono">
      no notifications to show
    </div>

    <button
      v-if="!stickToBottom"
      class="absolute bottom-4 right-6 bg-blue-800 text-slate-50 px-3 py-1 rounded text-lg hover:bg-blue-600"
      @click="
        scrollToBottom();
        stickToBottom = true;
      "
    >
      <i class="fa fa-arrow-down"></i> Show latest
    </button>
  </div>
</template>
