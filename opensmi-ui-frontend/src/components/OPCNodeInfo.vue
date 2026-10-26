<script setup lang="ts">
import { computed, ref } from "vue";
import {
    BoxIcon,
    BracesIcon,
    CheckIcon,
    CircleIcon,
    CopyIcon,
    DatabaseIcon,
    FolderIcon,
    NetworkIcon,
    ShapesIcon,
    ZapIcon,
    type LucideIcon,
} from "@lucide/vue";
import type { NodeIdData, OPCNode } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    node: OPCNode;
}>();

const classIcons: Record<string, LucideIcon> = {
    Object: BoxIcon,
    Variable: BracesIcon,
    Method: ZapIcon,
    View: FolderIcon,
    ObjectType: ShapesIcon,
    VariableType: ShapesIcon,
    ReferenceType: NetworkIcon,
    DataType: DatabaseIcon,
};

const classIcon = computed(
    () => classIcons[props.node.nodeClass] ?? CircleIcon,
);

const typePrefix: Record<string, string> = {
    Numeric: "i",
    TwoByte: "i",
    FourByte: "i",
    String: "s",
    Guid: "g",
    ByteString: "b",
};

// Standard OPC UA textual form, e.g. ns=1;s=SarahRobot
function formatNodeId(id: NodeIdData | string | null): string | null {
    if (id === null) return null;
    if (typeof id === "string") return id;

    const prefix = typePrefix[id.identifierType] ?? "?";
    const ns = id.namespaceIndex === 0 ? "" : `ns=${id.namespaceIndex};`;
    return `${ns}${prefix}=${id.identifier}`;
}

const nodeIdText = computed(() => formatNodeId(props.node.nodeId) ?? "");

const references = computed(() => [
    {
        label: "Type definition",
        value: formatNodeId(props.node.typeDefinitionId),
    },
    {
        label: "Reference type",
        value: formatNodeId(props.node.referenceTypeId),
    },
]);

const facts = computed(() => [
    {
        label: "Browse name",
        value: `${props.node.browseName.namespaceIndex}:${props.node.browseName.name}`,
    },
    {
        label: "Namespace",
        value: String(props.node.nodeId.namespaceIndex),
    },
    {
        label: "Identifier type",
        value: props.node.nodeId.identifierType,
    },
]);

const attributeEntries = computed(() => Object.entries(props.node.attributes));
const propertyEntries = computed(() => Object.entries(props.node.properties));

const copied = ref(false);

async function copyNodeId() {
    try {
        await navigator.clipboard.writeText(nodeIdText.value);
        copied.value = true;
        setTimeout(() => (copied.value = false), 1500);
    } catch (e) {
        console.error(e);
    }
}
</script>

<template>
    <article
        class="overflow-hidden rounded-lg border border-slate-200 bg-white text-slate-900 shadow-sm"
    >
        <!-- Header -->
        <header class="flex items-center gap-3 border-b border-slate-100 p-4">
            <div
                class="flex size-11 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600"
            >
                <component :is="classIcon" class="size-6" aria-hidden="true" />
            </div>

            <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                    <h3 class="truncate text-lg font-semibold leading-tight">
                        {{ node.displayName.text }}
                    </h3>
                    <span
                        class="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700"
                    >
                        {{ node.nodeClass }}
                    </span>
                    <span
                        class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500"
                    >
                        {{ node.displayName.locale ?? "no locale" }}
                    </span>
                </div>

                <div class="mt-1 flex items-center gap-1">
                    <code
                        class="truncate font-mono text-sm text-slate-500"
                        :title="nodeIdText"
                    >
                        {{ nodeIdText }}
                    </code>
                    <button
                        type="button"
                        class="rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 focus-visible:outline-2 focus-visible:outline-indigo-500"
                        :aria-label="copied ? 'Copied' : 'Copy node ID'"
                        :title="copied ? 'Copied' : 'Copy node ID'"
                        @click="copyNodeId"
                    >
                        <CheckIcon
                            v-if="copied"
                            class="size-3.5 text-emerald-600"
                        />
                        <CopyIcon v-else class="size-3.5" />
                    </button>
                </div>
            </div>
        </header>

        <!-- Quick facts -->
        <dl
            class="grid grid-cols-1 divide-y divide-slate-100 border-b border-slate-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0"
        >
            <div v-for="fact in facts" :key="fact.label" class="px-4 py-3">
                <dt class="text-xs uppercase tracking-wide text-slate-400">
                    {{ fact.label }}
                </dt>
                <dd class="mt-0.5 truncate text-sm font-medium text-slate-700">
                    {{ fact.value }}
                </dd>
            </div>
        </dl>

        <!-- References -->
        <dl
            class="grid grid-cols-1 divide-y divide-slate-100 border-b border-slate-100 bg-slate-50/60 sm:grid-cols-2 sm:divide-x sm:divide-y-0"
        >
            <div v-for="ref in references" :key="ref.label" class="px-4 py-3">
                <dt class="text-xs uppercase tracking-wide text-slate-400">
                    {{ ref.label }}
                </dt>
                <dd class="mt-0.5 truncate font-mono text-sm">
                    <span v-if="ref.value" class="text-slate-700">{{
                        ref.value
                    }}</span>
                    <span v-else class="font-sans text-slate-400">None</span>
                </dd>
            </div>
        </dl>

        <!-- Attributes & properties -->
        <div
            class="grid grid-cols-1 divide-y divide-slate-100 md:grid-cols-2 md:divide-x md:divide-y-0"
        >
            <section
                v-for="group in [
                    { title: 'Attributes', entries: attributeEntries },
                    { title: 'Properties', entries: propertyEntries },
                ]"
                :key="group.title"
                class="p-4"
            >
                <div class="mb-2 flex items-center justify-between">
                    <h4 class="text-sm font-semibold text-slate-700">
                        {{ group.title }}
                    </h4>
                    <span
                        class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500"
                    >
                        {{ group.entries.length }}
                    </span>
                </div>

                <dl v-if="group.entries.length" class="space-y-1.5 text-sm">
                    <div
                        v-for="[key, value] in group.entries"
                        :key="key"
                        class="flex items-baseline justify-between gap-4"
                    >
                        <dt class="shrink-0 text-slate-500">{{ key }}</dt>
                        <dd
                            class="min-w-0 break-all text-right font-mono text-slate-800"
                        >
                            {{ value }}
                        </dd>
                    </div>
                </dl>

                <p v-else class="text-sm text-slate-400">
                    No {{ group.title.toLowerCase() }}
                </p>
            </section>
        </div>
    </article>
</template>
