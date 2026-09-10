<script lang="ts" setup>
import { computed } from "vue";
import ComponentLink from "../../ComponentLink.vue";

import SkillControlBoard from "../../../skill/SkillControlBoard.vue";
import SkillLink from "../../../skill/SkillLink.vue";

const props = defineProps<{
  storageSlot: ComponentDto;
  lockedByUs: boolean;
}>();

const isSlotEmpty = computed(() => {
  return (
    props.storageSlot.monitoring.find((item) => item.name === "IsSlotEmpty")
      ?.dataContent.value.value ?? false
  );
});
const isCarrierEmpty = computed(() => {
  return (
    props.storageSlot.monitoring.find((item) => item.name === "IsCarrierEmpty")
      ?.dataContent.value.value ?? false
  );
});
const productType = computed(() => {
  const val =
    props.storageSlot.monitoring.find((item) => item.name === "ProductType")
      ?.dataContent.value.value ?? "";

  if (typeof val !== "string") {
    if (typeof val == "object") {
      if ("Identifier" in val) {
        return val["Identifier"] ?? "";
      }
    }

    return JSON.stringify(val);
  }

  return val;
});
const carrierType = computed(() => {
  const val =
    props.storageSlot.monitoring.find((item) => item.name === "CarrierType")
      ?.dataContent.value.value ?? "";

  if (typeof val !== "string") {
    if (typeof val == "object") {
      if ("Identifier" in val) {
        return val["Identifier"] ?? "";
      }
    }

    return JSON.stringify(val);
  }

  return val;
});
const productID = computed(() => {
  return (
    props.storageSlot.monitoring.find((item) => item.name === "ProductID")
      ?.dataContent.value.value ?? ""
  );
});
const carrierID = computed(() => {
  return (
    props.storageSlot.monitoring.find((item) => item.name === "CarrierID")
      ?.dataContent.value.value ?? ""
  );
});

const storeState = computed(() => {
  const val =
    props.storageSlot.monitoring.find((item) => item.name === "CurrentState")
      ?.dataContent.value.value ?? "";

  return val;
});

const productImage = computed(() => {
  if (isCarrierEmpty.value == true) {
    return "default";
  }

  return productType.value?.split(".").pop() ?? "default";
});

const carrierImage = computed(() => {
  if (isSlotEmpty.value == true) {
    return "default";
  }

  return carrierType.value?.split(".").pop() ?? "default";
});
</script>

<template>
  <div class="storage-slot-display" :class="['storage-' + storeState]">
    <div
      class="px-2 border-b border-gray-400 flex flex-row justify-between items-center"
      :title="storeState"
    >
      <ComponentLink :component="storageSlot"></ComponentLink>
      <div class="text-sm text-gray-400">
        <span :class="{ 'is-present': productID.length > 0 }">Product</span>
        |
        <span :class="{ 'is-present': carrierID.length > 0 }">Carrier</span>
      </div>
    </div>
    <div class="product-line">
      <div class="product-image">
        <img :src="'api/static/image/' + productImage" :alt="productImage" />
      </div>
      <span class="text-xs text-gray-400">
        {{ productID }}
      </span>
    </div>
    <hr class="border-primary" />
    <div class="carrier-line">
      <div class="carrier-image">
        <img :src="'api/static/image/' + carrierImage" :alt="carrierImage" />
      </div>
      <span class="text-xs text-gray-400">
        {{ carrierID }}
      </span>
    </div>
    <hr class="border-primary" />
    <div class="flex flex-col justify-start items-center mt-2 mb-2">
      <span
        v-show="!storageSlot.skillSet?.length"
        class="text-base text-gray-500"
      >
        No skills available
      </span>
      <div v-show="storageSlot.skillSet?.length">
        <div
          v-for="skill of storageSlot.skillSet"
          class="flex flex-row justify-start gap-x-4 items-center"
        >
          <SkillControlBoard
            :skill="skill"
            :show-as-tiny="true"
          ></SkillControlBoard>
          <SkillLink :skill="skill"></SkillLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.storage-slot-display {
  @apply border-2 border-gray-400;
  width: 18rem;
  min-width: 18rem;
}

.storage-0, .storage-Uninitialized {
  @apply bg-slate-200;
}

.storage-1, .storage-Empty {
  @apply bg-slate-200;
}

.storage-2, .storage-LoadedUnknown {
  @apply bg-pink-200;
}

.storage-3, .storage-LoadedKnown {
  @apply bg-green-200;
}

.storage-4, .storage-GetsLoaded {
  @apply bg-orange-200;
}

.storage-5, .storage-GetsEmptied {
  @apply bg-cyan-200;
}

.is-present {
  @apply text-green-600;
}

.product-line {
  @apply flex flex-col justify-between items-center;
  height: 10rem;
}

.product-line img {
  max-height: 8rem;
  max-width: 8rem;
}

.product-image {
  @apply flex flex-row justify-center items-center h-full;
}

.carrier-line {
  height: 7rem;
  @apply flex flex-col justify-between items-center;
}

.carrier-line img {
  max-height: 5rem;
  max-width: 12rem;
}

.carrier-image {
  @apply flex flex-row justify-center items-center h-full;
}
</style>
