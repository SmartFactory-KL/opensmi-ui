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
import type { OPCNode } from "@/types/NodeFeatureTypes";
import type { NodeIdData, QualifiedNameData } from "@/types/OPCTypes";

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
function formatNodeId(id: NodeIdData): string {
    const prefix = typePrefix[id.identifierType] ?? "?";
    const ns = id.namespaceIndex === 0 ? "" : `ns=${id.namespaceIndex};`;
    return `${ns}${prefix}=${id.identifier}`;
}

// Standard OPC UA textual form, e.g. 2:MachineryItemType
function formatQualifiedName(name: QualifiedNameData | null): string | null {
    if (!name) return null;
    return `${name.namespaceIndex}:${name.name}`;
}

const nodeIdText = computed(() => formatNodeId(props.node.nodeId));

const rows = computed(() => [
    {
        label: "Browse name",
        value: formatQualifiedName(props.node.browseName),
        mono: true,
    },
    {
        label: "Type",
        value: formatQualifiedName(props.node.opcType),
        mono: true,
    },
    {
        label: "Type definition",
        value: props.node.typeDefinition,
        mono: true,
    },
    {
        label: "Reference type",
        value: props.node.referenceTypeId,
        mono: true,
    },
    {
        label: "Namespace",
        value: String(props.node.nodeId.namespaceIndex),
        mono: true,
    },
    {
        label: "Identifier type",
        value: props.node.nodeId.identifierType,
        mono: false,
    },
]);

const groups = computed(() => [
    { title: "Attributes", entries: Object.entries(props.node.attributes) },
    { title: "Properties", entries: Object.entries(props.node.properties) },
]);

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
    <article class="border border-slate-300 bg-white text-slate-900">
        <!-- Header -->
        <header
            class="flex items-stretch border-b border-slate-300 bg-slate-50"
        >
            <div
                class="flex w-12 shrink-0 items-center justify-center bg-indigo-600 text-white"
            >
                <component :is="classIcon" class="size-5" aria-hidden="true" />
            </div>

            <div class="min-w-0 flex-1 px-3 py-2">
                <div class="flex items-center gap-2">
                    <h3
                        class="truncate text-sm font-semibold leading-tight text-slate-900"
                    >
                        {{ node.displayName.text }}
                    </h3>
                    <span
                        class="shrink-0 border border-indigo-200 bg-indigo-50 px-1.5 text-xs font-medium leading-5 text-indigo-700"
                    >
                        {{ node.nodeClass }}
                    </span>
                    <span
                        v-if="node.displayName.locale"
                        class="shrink-0 border border-slate-200 bg-white px-1.5 text-xs leading-5 text-slate-500"
                    >
                        {{ node.displayName.locale }}
                    </span>
                </div>

                <div class="mt-0.5 flex items-center gap-1">
                    <code
                        class="truncate font-mono text-xs text-slate-500"
                        :title="nodeIdText"
                    >
                        {{ nodeIdText }}
                    </code>
                    <button
                        type="button"
                        class="p-0.5 text-slate-400 hover:bg-slate-200 hover:text-slate-700 focus-visible:outline-2 focus-visible:outline-indigo-500"
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

        <!-- Identity: dense key/value grid -->
        <dl class="flex flex-col text-xs">
            <div
                v-for="row in rows"
                :key="row.label"
                class="flex items-baseline justify-between gap-3 border-b border-slate-200 px-3 py-1.5"
            >
                <dt class="shrink-0 text-slate-500">{{ row.label }}</dt>
                <dd
                    class="min-w-0 text-right font-medium text-xs text-slate-800"
                    :class="{ 'font-mono': row.mono }"
                >
                    <template v-if="row.value">{{ row.value }}</template>
                    <span v-else class="font-normal text-slate-400">none</span>
                </dd>
            </div>
        </dl>

        <!-- Attributes & properties -->
        <div class="grid grid-cols-1 md:grid-cols-2">
            <section
                v-for="group in groups"
                :key="group.title"
                class="min-w-0 border-b border-slate-300 last:border-b-0 md:border-b-0 md:border-r md:last:border-r-0"
            >
                <div
                    class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-3 py-1"
                >
                    <h4 class="text-xs font-semibold text-slate-700">
                        {{ group.title }}
                    </h4>
                    <span
                        class="min-w-5 bg-slate-200 px-1 text-center text-xs tabular-nums text-slate-600"
                    >
                        {{ group.entries.length }}
                    </span>
                </div>

                <dl v-if="group.entries.length" class="text-xs">
                    <div
                        v-for="[key, value] in group.entries"
                        :key="key"
                        class="flex items-baseline justify-between gap-4 px-3 py-1 odd:bg-white even:bg-slate-50/70"
                    >
                        <dt class="shrink-0 text-slate-500">{{ key }}</dt>
                        <dd
                            class="min-w-0 break-all text-right font-mono text-slate-800"
                        >
                            {{ value }}
                        </dd>
                    </div>
                </dl>

                <p v-else class="px-3 py-2 text-xs text-slate-400">
                    No {{ group.title.toLowerCase() }}
                </p>
            </section>
        </div>
    </article>
</template>
