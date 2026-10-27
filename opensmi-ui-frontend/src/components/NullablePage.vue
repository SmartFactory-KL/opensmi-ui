<script setup lang="ts" generic="T">
import { RabbitIcon } from "@lucide/vue";

defineProps<{
    item: T | null | undefined;
    entityId?: unknown;
    entityType?: unknown;
}>();

defineSlots<{
    default(props: { item: NonNullable<T> }): unknown;
}>();
</script>

<template>
    <main class="h-full">
        <section
            v-if="item === null || item === undefined"
            role="status"
            class="relative flex h-full min-h-[50vh] w-full select-none items-center justify-center overflow-hidden p-8 text-center"
        >
            <RabbitIcon
                aria-hidden="true"
                :stroke-width="0.75"
                class="pointer-events-none absolute size-[min(80vh,80vw)] max-w-none text-slate-200"
            />

            <div class="relative max-w-2xl">
                <h2
                    class="text-4xl font-semibold tracking-tight text-slate-600 sm:text-6xl"
                >
                    Nothing here but a rabbit
                </h2>

                <p class="mt-4 text-lg text-slate-500 sm:text-xl">
                    We couldn't find the item you were looking for. Make sure it
                    exists, or try refreshing the page.
                </p>

                <p
                    v-if="entityType && typeof entityType == 'string'"
                    class="mt-8 text-sm text-slate-400"
                >
                    Entity Type
                    <code
                        class="ml-1 select-text break-all rounded bg-slate-100 px-2 py-1 font-mono text-slate-500"
                    >
                        {{ entityType }}
                    </code>
                </p>

                <p
                    v-if="entityId && typeof entityId == 'string'"
                    class="mt-2 text-sm text-slate-400"
                >
                    Entity ID
                    <code
                        class="ml-1 select-text break-all rounded bg-slate-100 px-2 py-1 font-mono text-slate-500"
                    >
                        {{ entityId }}
                    </code>
                </p>
            </div>
        </section>

        <slot v-else :item="item as NonNullable<T>"></slot>
    </main>
</template>
