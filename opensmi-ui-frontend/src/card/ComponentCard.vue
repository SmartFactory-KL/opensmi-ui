<script setup lang="ts">
import SquareStateIndicator from "@/components/SquareStateIndicator.vue";
import type { ComponentEntityDto } from "@/types/ModuleTypes";
import { Box, CircleCheck, Gauge, Package, Wrench } from "@lucide/vue";

const props = defineProps<{
    component: ComponentEntityDto;
}>();

const component = props.component;

const formatDate = (value: Date | string | null | undefined) => {
    if (!value) return "—";

    return new Date(value).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    });
};

const accessLevel = (level: number | null | undefined) => {
    if (level == null) return "—";
    return String(level);
};

const hasItems = (value: unknown[] | undefined) => Boolean(value?.length);

const lockLabel = component.data.lock?.isLocked ? "Locked" : "Unlocked";
</script>

<template>
    <article
        class="w-full max-w-4xl overflow-hidden rounded-xl border border-slate-200 bg-white text-slate-900 shadow-sm"
    >
        <!-- Header -->
        <header class="border-b border-slate-200 px-6 py-5">
            <div class="flex items-start justify-between gap-6">
                <div class="flex min-w-0 items-center gap-4">
                    <div
                        class="flex size-11 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-600"
                    >
                        <SquareStateIndicator
                            class="h-12 w-12"
                            :state="component.data.currentState"
                            :square-only="true"
                        ></SquareStateIndicator>
                    </div>

                    <div class="min-w-0">
                        <div class="flex items-center gap-2">
                            <h2 class="truncate text-lg font-semibold">
                                {{ component.data.name }}
                            </h2>

                            <div
                                class="flex shrink-0 items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium"
                                :class="
                                    component.data.currentState
                                        ? 'bg-emerald-50 text-emerald-700'
                                        : 'bg-slate-100 text-slate-500'
                                "
                            >
                                <span
                                    class="size-1.5 rounded-full bg-current"
                                />
                                {{ component.data.currentState || "Unknown" }}
                            </div>
                        </div>

                        <p
                            class="mt-1 truncate font-mono text-xs text-slate-400"
                        >
                            {{ component.data.uaNodeId }}
                        </p>
                    </div>
                </div>
            </div>
        </header>

        <!-- Details -->
        <section class="border-t border-slate-200 px-6 py-5">
            <div class="flex flex-row flex-wrap gap-4">
                <!-- Skills -->
                <div>
                    <div class="flex items-center gap-2 text-sm font-medium">
                        <Gauge :size="15" class="text-slate-400" />
                        {{ component.data.skillSet?.length || 0 }} Skill(s)
                    </div>
                </div>

                <!-- Methods -->
                <div>
                    <div class="flex items-center gap-2 text-sm font-medium">
                        <Wrench :size="15" class="text-slate-400" />
                        {{ component.data.methodSet?.length || 0 }} Method(s)
                    </div>
                </div>

                <!-- Resources -->
                <div>
                    <div class="flex items-center gap-2 text-sm font-medium">
                        <Package :size="15" class="text-slate-400" />
                        {{ component.data.resources?.length || 0 }} Resources
                    </div>
                </div>

                <!-- Components -->
                <div>
                    <div class="flex items-center gap-2 text-sm font-medium">
                        <Box :size="15" class="text-slate-400" />
                        {{ component.data.components?.length || 0 }} Components
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer
            class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-slate-50/70 px-6 py-3"
        >
            <div class="flex items-center gap-4 text-xs text-slate-400">
                <span>
                    {{ component.data.identification?.length }} Identification
                    Values
                </span>
                <span>
                    {{ component.data.monitoring?.length }} Monitoring Values
                </span>
                <span>
                    {{ component.data.attributes?.length }} Attributes
                </span>
                <span>
                    {{ component.data.parameterSet?.length }} Parameters
                </span>
            </div>

            <div class="flex items-center gap-1.5 text-xs text-slate-400">
                <CircleCheck :size="13" />
                OPC UA
            </div>
        </footer>
    </article>
</template>
