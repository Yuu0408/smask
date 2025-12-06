<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useHistoryStore } from '@/stores/history';
import { useRouter } from 'vue-router';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import type { ChatHistoryPreview } from '@/types/history';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
} from '@/components/ui/card';
import { useI18n } from 'vue-i18n';
import { History as HistoryIcon, Clock3 } from 'lucide-vue-next';

const { user } = storeToRefs(useAuthStore());
const { t, locale } = useI18n();
const historyStore = useHistoryStore();
const router = useRouter();
const { openDialog } = useDialog();

const userId = computed(() => user.value?.id ?? '');

const histories = ref<ChatHistoryPreview[]>([]);

onMounted(async () => {
    const res = await historyStore.getAllChatHistory({
        user_id: userId.value,
    });
    histories.value = res.histories;
});

function openHistory(sessionId: string) {
    if (user.value) {
        user.value.currentRecordId = sessionId;
    }
    router.push(`/chat/conversation`);
}

function formatDateTime(dateStr?: string | null): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (Number.isNaN(date.getTime())) return '';
    const loc = locale.value === 'vi' ? 'vi-VN' : 'en-US';
    return date.toLocaleString(loc, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

const totalHistories = computed(() => histories.value.length);
const latestHistory = computed(() => {
    if (!histories.value.length) return null as ChatHistoryPreview | null;
    return histories.value.reduce((latest, current) =>
        new Date(current.updatedAt) > new Date(latest.updatedAt)
            ? current
            : latest
    );
});
const latestUpdated = computed(() =>
    latestHistory.value ? formatDateTime(latestHistory.value.updatedAt) : ''
);
const latestComplaint = computed(() =>
    latestHistory.value
        ? latestHistory.value.chiefComplaint ||
          latestHistory.value.lastMessage ||
          t('history.noMessagesYet')
        : ''
);

const currentRecordId = computed(() => user.value?.currentRecordId ?? '');

function isCurrentConversation(sessionId: string) {
    return !!currentRecordId.value && currentRecordId.value === sessionId;
}
</script>

<template>
    <div
        class="flex min-h-[calc(100vh-4rem)] h-[calc(100vh-4rem)] flex-col overflow-hidden"
    >
        <div class="relative flex-1 min-h-0 overflow-hidden">
            <div
                class="pointer-events-none absolute inset-0 opacity-70"
                aria-hidden="true"
            >
                <div
                    class="absolute -left-16 top-0 size-96 rounded-full bg-primary/15 blur-3xl"
                />
                <div
                    class="absolute right-[-4rem] bottom-0 size-72 rounded-full bg-accent/20 blur-3xl"
                />
            </div>
            <div class="relative h-full w-full flex flex-col overflow-hidden">
                <div class="flex-1 overflow-y-auto">
                    <div
                        class="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-8"
                    >
                        <header
                            class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between"
                        >
                            <div class="space-y-2">
                                <div
                                    class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary"
                                >
                                    <HistoryIcon class="size-4" />
                                    {{ t('history.title') }}
                                </div>
                                <div class="space-y-1">
                                    <h1
                                        class="text-3xl font-bold tracking-tight text-foreground"
                                    >
                                        {{ t('history.title') }}
                                    </h1>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('history.subtitle') }}
                                    </p>
                                </div>
                            </div>
                            <div class="flex flex-wrap gap-3">
                                <Button
                                    variant="outline"
                                    class="rounded-xl"
                                    @click="
                                        openDialog({
                                            component: MedicalRecordDialog,
                                        })
                                    "
                                >
                                    {{ t('todo.startConversation') }}
                                </Button>
                            </div>
                        </header>

                        <div class="grid gap-4 md:grid-cols-3">
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-1">
                                    <CardTitle class="text-base font-semibold">
                                        {{ t('history.stats.total') }}
                                    </CardTitle>
                                    <CardDescription class="text-sm">
                                        {{ t('history.title') }}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div class="text-3xl font-bold">
                                        {{ totalHistories }}
                                    </div>
                                </CardContent>
                            </Card>
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-1">
                                    <CardTitle class="text-base font-semibold">
                                        {{ t('history.stats.latest') }}
                                    </CardTitle>
                                    <CardDescription class="text-sm">
                                        {{ t('history.lastActivity') }}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div
                                        class="text-lg font-semibold text-foreground"
                                    >
                                        {{
                                            latestUpdated ||
                                            t('history.noMessagesYet')
                                        }}
                                    </div>
                                </CardContent>
                            </Card>
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-1">
                                    <CardTitle class="text-base font-semibold">
                                        {{ t('history.stats.active') }}
                                    </CardTitle>
                                    <CardDescription class="text-sm">
                                        {{ t('medicalRecord.chiefComplaint') }}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div
                                        class="text-sm font-medium text-foreground line-clamp-2"
                                    >
                                        {{
                                            latestComplaint ||
                                            t('history.noMessagesYet')
                                        }}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        <div
                            v-if="!histories.length"
                            class="text-muted-foreground"
                        >
                            <div
                                class="relative overflow-hidden rounded-3xl border border-primary/15 bg-white/80 p-10 text-center shadow-lg shadow-primary/20 backdrop-blur"
                            >
                                <div
                                    class="pointer-events-none absolute inset-0 opacity-40"
                                    aria-hidden="true"
                                >
                                    <div
                                        class="absolute -left-12 top-0 size-72 rounded-full bg-primary/10 blur-3xl"
                                    />
                                    <div
                                        class="absolute right-0 bottom-0 size-64 rounded-full bg-accent/10 blur-3xl"
                                    />
                                </div>
                                <div class="relative space-y-4">
                                    <p class="text-base font-medium">
                                        {{ t('history.empty') }}
                                    </p>
                                    <Button
                                        variant="default"
                                        class="rounded-xl shadow-md shadow-primary/20"
                                        @click="
                                            openDialog({
                                                component: MedicalRecordDialog,
                                            })
                                        "
                                    >
                                        {{ t('todo.startConversation') }}
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div
                            v-else
                            class="grid gap-4 md:grid-cols-2 lg:grid-cols-2"
                        >
                            <Card
                                v-for="history in histories"
                                :key="history.sessionId"
                                class="group cursor-pointer overflow-hidden border border-primary/10 bg-white/90 shadow-lg shadow-primary/10 transition hover:-translate-y-1 hover:shadow-xl"
                                @click="openHistory(history.sessionId)"
                            >
                                <CardHeader class="space-y-2">
                                    <div
                                        class="flex items-center justify-between gap-3"
                                    >
                                        <CardTitle
                                            class="text-base font-semibold text-foreground line-clamp-1"
                                        >
                                            {{
                                                history.chiefComplaint ||
                                                history.lastMessage ||
                                                t('history.noMessagesYet')
                                            }}
                                        </CardTitle>
                                        <span
                                            v-if="
                                                isCurrentConversation(
                                                    history.sessionId
                                                )
                                            "
                                            class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-primary"
                                        >
                                            {{ t('history.currentChat') }}
                                        </span>
                                    </div>
                                    <CardDescription
                                        class="flex items-center gap-2 text-xs text-muted-foreground"
                                    >
                                        <Clock3 class="size-4" />
                                        {{ formatDateTime(history.updatedAt) }}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p
                                        class="text-sm text-muted-foreground line-clamp-2"
                                    >
                                        {{
                                            history.lastMessage ||
                                            t('history.noMessagesYet')
                                        }}
                                    </p>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
