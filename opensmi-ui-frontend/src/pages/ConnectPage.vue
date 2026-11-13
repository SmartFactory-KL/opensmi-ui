<script setup lang="ts">
import { computed, ref } from "vue";
import {
    EyeIcon,
    EyeOffIcon,
    KeyRoundIcon,
    LinkIcon,
    LockKeyholeIcon,
    LockKeyholeOpenIcon,
    LogInIcon,
    LogOutIcon,
    MessageSquareWarningIcon,
    RotateCcwIcon,
    ShieldCheckIcon,
    Trash2Icon,
    UserIcon,
} from "@lucide/vue";
import { usePinGuardStore } from "@/stores/PinGuardStore";
import IconButton from "@/components/IconButton.vue";
import { useServerStore } from "@/stores/ServerSessionStore";
import { usePageStore } from "@/stores/PageStore";
import ServerStateIndicator from "@/navigation/ServerStateIndicator.vue";
import { useModelStore } from "@/stores/ModelStore";

const serverStore = useServerStore();
const pinGuardStore = usePinGuardStore();
const pageStore = usePageStore();

const showPassword = ref(false);
const isLocked = computed(() => pinGuardStore.isLocked);

const canEdit = computed(() => !isLocked.value && serverStore.isDisconnected);

function requestConnect() {
    serverStore.requestConnect();
}

function requestDisconnect() {
    serverStore.requestDisconnect();
}
</script>

<template>
    <main class="min-h-full bg-slate-50">
        <div class="mx-auto max-w-5xl px-6 py-10 lg:px-8">
            <!-- Header -->
            <header class="mb-8">
                <h1
                    class="text-3xl font-semibold tracking-tight text-slate-900"
                >
                    Connect to Server
                </h1>
            </header>

            <!-- PinGuard -->
            <div
                v-show="pinGuardStore.state.isLocked"
                class="mb-6 flex flex-row justify-between items-center gap-4 rounded-xl border border-violet-200 bg-violet-50 p-4 text-violet-800"
            >
                <div class="flex flex-row justify-start items-start gap-4">
                    <div
                        class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-violet-100"
                    >
                        <LockKeyholeIcon :size="24" />
                    </div>

                    <div>
                        <p class="font-medium">PinGuard is active</p>
                        <p class="mt-1 text-sm text-violet-600">
                            Unlock PinGuard to modify the server connection
                            settings.
                        </p>
                    </div>
                </div>

                <div>
                    <IconButton
                        class="bg-violet-900 text-white hover:bg-violet-800"
                    >
                        <LockKeyholeOpenIcon :size="16" />
                        Unlock
                    </IconButton>
                </div>
            </div>

            <!-- Main Connect Card -->
            <div class="grid gap-6 lg:grid-cols-[1fr_320px]">
                <!-- Connection settings -->
                <section
                    class="overflow-hidden border border-slate-200 bg-white shadow-sm place-self-stretch self-start"
                >
                    <div class="border-b border-slate-100 px-6 py-5">
                        <div class="flex items-center gap-3">
                            <div
                                class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600"
                            >
                                <LinkIcon :size="18" />
                            </div>

                            <div>
                                <h2 class="font-medium text-slate-900">
                                    Connection settings
                                </h2>
                                <p class="text-sm text-slate-500">
                                    Configure the OPC UA endpoint and
                                    credentials.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-5 p-6">
                        <!-- Server URL -->
                        <div>
                            <label
                                for="server-url"
                                class="mb-2 block text-sm font-medium text-slate-700"
                            >
                                Server URL
                            </label>

                            <div class="relative">
                                <LinkIcon
                                    :size="17"
                                    class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                />

                                <input
                                    id="server-url"
                                    :disabled="!canEdit"
                                    type="text"
                                    v-model="serverStore.userInput.serverUrl"
                                    placeholder="opc.tcp://localhost:4840"
                                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
                                />
                            </div>
                        </div>

                        <!-- Username -->
                        <div>
                            <label
                                for="username"
                                class="mb-2 block text-sm font-medium text-slate-700"
                            >
                                Username
                            </label>

                            <div class="relative">
                                <UserIcon
                                    :size="17"
                                    class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                />

                                <input
                                    id="username"
                                    :disabled="!canEdit"
                                    type="text"
                                    v-model="serverStore.userInput.username"
                                    autocomplete="username"
                                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
                                />
                            </div>
                        </div>

                        <!-- Password -->
                        <div>
                            <label
                                for="password"
                                class="mb-2 block text-sm font-medium text-slate-700"
                            >
                                Password
                            </label>

                            <div class="relative">
                                <KeyRoundIcon
                                    :size="17"
                                    class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                />

                                <input
                                    id="password"
                                    :disabled="!canEdit"
                                    :type="showPassword ? 'text' : 'password'"
                                    v-model="serverStore.userInput.password"
                                    autocomplete="current-password"
                                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-10 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
                                />

                                <button
                                    type="button"
                                    :disabled="!canEdit"
                                    @click="showPassword = !showPassword"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                                >
                                    <EyeOffIcon
                                        v-if="showPassword"
                                        :size="17"
                                    />
                                    <EyeIcon v-else :size="17" />
                                </button>
                            </div>
                        </div>

                        <!-- Server Request Error -->
                        <div
                            class="flex flex-row justify-start items-start border border-red-500 bg-red-50 gap-3 p-4 rounded-md text-slate-700"
                            v-show="serverStore.requestData.error !== null"
                        >
                            <MessageSquareWarningIcon
                                :size="24"
                            ></MessageSquareWarningIcon>
                            {{ serverStore.requestData.error }}
                        </div>

                        <!-- Actions -->
                        <div
                            class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5"
                        >
                            <IconButton
                                :disabled="!canEdit"
                                class="border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                                @click="serverStore.applyPageDefaults()"
                            >
                                <RotateCcwIcon :size="16" />
                                Use Server Defaults
                            </IconButton>

                            <div class="flex gap-2">
                                <IconButton
                                    class="border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                                    :disabled="isLocked"
                                    @click="requestDisconnect"
                                >
                                    <LogOutIcon :size="16" />
                                    Disconnect
                                </IconButton>

                                <IconButton
                                    class="bg-slate-900 hover:bg-slate-800 text-white"
                                    :disabled="isLocked"
                                    @click="requestConnect"
                                >
                                    <LogInIcon :size="16" />
                                    Connect
                                </IconButton>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Status -->
                <aside class="space-y-4">
                    <!-- Current state -->
                    <section class="shadow-sm">
                        <ServerStateIndicator
                            class="p-5"
                        ></ServerStateIndicator>
                    </section>

                    <!-- Model State -->
                    Model State: {{ useModelStore().state }}

                    <!-- Local data -->
                    <section
                        class="flex flex-col gap-y-2 border border-slate-200 bg-white p-5 shadow-sm"
                    >
                        <h2 class="font-medium text-slate-900">
                            Local connection data
                        </h2>

                        <p class="text-sm leading-5 text-slate-500">
                            The last successful connection is stored locally for
                            convenience.
                        </p>

                        <IconButton
                            class="text-slate-600 border border-slate-600 hover:text-red-600"
                            @click="pageStore.clearLocalConnectionData()"
                        >
                            <Trash2Icon :size="16" />
                            Clear Local Connection Data
                        </IconButton>
                    </section>
                </aside>
            </div>

            <!-- Connection info -->
            <section
                v-if="serverStore.isConnected"
                class="border border-slate-200 bg-white p-5 shadow-sm mt-10"
            >
                <div class="mb-4 flex items-center gap-2">
                    <ShieldCheckIcon :size="17" class="text-emerald-500" />
                    <h2 class="font-medium text-slate-900">Connection Info</h2>
                </div>

                <dl class="space-y-3 text-sm">
                    <div>
                        <dt class="text-xs text-slate-400">Server URL</dt>
                        <dd class="mt-1 break-all font-mono text-slate-700">
                            {{ serverStore.sessionData.url }}
                        </dd>
                    </div>

                    <div>
                        <dt class="text-xs text-slate-400">Username</dt>
                        <dd class="mt-1 text-slate-700">
                            {{ serverStore.sessionData.username }}
                        </dd>
                    </div>

                    <div>
                        <dt class="text-xs text-slate-400">Application URI</dt>
                        <dd class="mt-1 break-all font-mono text-slate-700">
                            {{ serverStore.sessionData.applicationUri }}
                        </dd>
                    </div>

                    <div>
                        <dt class="text-xs text-slate-400">Product URI</dt>
                        <dd class="mt-1 break-all font-mono text-slate-700">
                            {{ serverStore.sessionData.productUri }}
                        </dd>
                    </div>

                    <div class="border-t border-slate-100 pt-3">
                        <dt
                            class="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400"
                        >
                            Client Settings
                        </dt>

                        <div class="space-y-2">
                            <div class="flex justify-between gap-4">
                                <dt class="text-slate-500">Auto Reconnect</dt>
                                <dd class="text-slate-700">
                                    {{
                                        serverStore.sessionData.settings
                                            .autoReconnect
                                            ? "Yes"
                                            : "No"
                                    }}
                                </dd>
                            </div>

                            <div class="flex justify-between gap-4">
                                <dt class="text-slate-500">
                                    Reconnect Max Delay
                                </dt>
                                <dd class="text-slate-700">
                                    {{
                                        serverStore.sessionData.settings
                                            .reconnectMaxDelay
                                    }}
                                    s
                                </dd>
                            </div>

                            <div class="flex justify-between gap-4">
                                <dt class="text-slate-500">
                                    Reconnect Request Timeout
                                </dt>
                                <dd class="text-slate-700">
                                    {{
                                        serverStore.sessionData.settings
                                            .reconnectRequestTimeout
                                    }}
                                    s
                                </dd>
                            </div>

                            <div class="flex justify-between gap-4">
                                <dt class="text-slate-500">Request Timeout</dt>
                                <dd class="text-slate-700">
                                    {{
                                        serverStore.sessionData.settings.timeout
                                    }}
                                    s
                                </dd>
                            </div>

                            <div class="flex justify-between gap-4">
                                <dt class="text-slate-500">
                                    Watchdog Interval
                                </dt>
                                <dd class="text-slate-700">
                                    {{
                                        serverStore.sessionData.settings
                                            .watchdogInterval
                                    }}
                                    s
                                </dd>
                            </div>
                        </div>
                    </div>
                </dl>
            </section>
        </div>

        <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
        <div class="on-screen-placeholder" style="height: 25vh"></div>
    </main>
</template>
