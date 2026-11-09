<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
    value: string; // Base64
    dataType?: string;
}>();

const PREVIEW_BYTES = 16;

const IMAGE_B64_PREFIX: Record<string, string> = {
    ImageJPG: "data:image/jpeg;base64, ",
    ImagePNG: "data:image/png;base64, ",
    ImageBMP: "data:image/bmp;base64, ",
    ImageGIF: "data:image/gif;base64, ",
};

const isImageType = computed(() => {
    if (props.dataType && props.dataType.length) {
        switch (props.dataType) {
            case "ImageJPG":
            case "ImagePNG":
            case "ImageBMP":
            case "ImageGIF":
                return true;
        }
    }

    return false;
});

const bytes = computed<number[] | null>(() => {
    try {
        return Array.from(atob(props.value), (c) => c.charCodeAt(0));
    } catch {
        return null; // not valid Base64
    }
});

const preview = computed(() => {
    if (!bytes.value) return props.value;
    const head = bytes.value
        .slice(0, PREVIEW_BYTES)
        .map((b) => b.toString(16).toUpperCase().padStart(2, "0"))
        .join(" ");
    return bytes.value.length > PREVIEW_BYTES ? head + " …" : head;
});
</script>

<template>
    <span
        v-if="bytes && bytes.length === 0"
        class="text-xs italic text-slate-400"
    >
        (empty)
    </span>
    <span v-else class="inline-flex flex-wrap items-baseline gap-x-2">
        <div v-if="isImageType">
            <img :src="IMAGE_B64_PREFIX[dataType!] + value" />
        </div>
        <span v-show="!isImageType" class="font-mono text-xs break-all" :title="value">
            {{ preview }}
        </span>
        <span v-if="bytes" class="text-xs text-slate-400">
            {{ bytes.length }} {{ bytes.length === 1 ? "byte" : "bytes" }}
        </span>
    </span>
</template>
