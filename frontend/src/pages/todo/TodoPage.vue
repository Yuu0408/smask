<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useTodoStore } from '@/stores/todo';
import type {
    GetCurrentTodoResponse,
    UpdateTodoItemRequest,
} from '@/types/todo';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { ListTodo } from 'lucide-vue-next';
import { useI18n } from 'vue-i18n';

const { user } = storeToRefs(useAuthStore());
const { t } = useI18n();
const userId = computed(() => user.value?.id ?? '');
const recordId = computed(() => user.value?.currentRecordId ?? '');

const todoStore = useTodoStore();
const { openDialog } = useDialog();
const todo = ref<GetCurrentTodoResponse | null>(null);
const loading = ref(false);
const updatingIndex = ref<number | null>(null);

const completedCount = computed(
    () => todo.value?.items.filter((i) => i.is_check).length ?? 0
);
const pendingCount = computed(
    () => (todo.value?.items.length ?? 0) - completedCount.value
);
const completionPct = computed(() => {
    const total = todo.value?.items.length ?? 0;
    if (!total) return 0;
    return Math.round((completedCount.value / total) * 100);
});

onMounted(async () => {
    if (!userId.value) return;
    loading.value = true;
    try {
        todo.value = await todoStore.getCurrentTodo({
            user_id: userId.value,
            record_id: recordId.value || undefined,
        });
    } finally {
        loading.value = false;
    }
});

async function toggleItem(idx: number) {
    if (!todo.value || !userId.value) return;
    const current = todo.value.items[idx];
    updatingIndex.value = idx;
    try {
        const payload: UpdateTodoItemRequest = {
            user_id: userId.value,
            record_id: todo.value.record_id || undefined,
            index: idx,
            is_check: !current.is_check,
        };
        const updated = await todoStore.checkTodoItem(payload);
        todo.value = updated;
    } finally {
        updatingIndex.value = null;
    }
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
                ></div>
                <div
                    class="absolute right-[-4rem] bottom-0 size-72 rounded-full bg-accent/20 blur-3xl"
                ></div>
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
                                    <ListTodo class="size-4" />
                                    {{ t('todo.title') }}
                                </div>
                                <div class="space-y-1">
                                    <h1
                                        class="text-3xl font-bold tracking-tight text-foreground"
                                    >
                                        {{ t('todo.title') }}
                                    </h1>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('sidebar.todoList') }}
                                    </p>
                                </div>
                            </div>
                            <div class="flex flex-wrap gap-3">
                                <Button
                                    variant="outline"
                                    class="rounded-xl"
                                    @click="openDialog({ component: MedicalRecordDialog })"
                                >
                                    {{ t('todo.startConversation') }}
                                </Button>
                            </div>
                        </header>

                        <div v-if="loading" class="text-muted-foreground animate-pulse">
                            {{ t('common.loading') }}
                        </div>

                        <div
                            v-else-if="!todo || (todo && todo.items.length === 0)"
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
                                    ></div>
                                    <div
                                        class="absolute right-0 bottom-0 size-64 rounded-full bg-accent/10 blur-3xl"
                                    ></div>
                                </div>
                                <div class="relative space-y-4">
                                    <p class="text-base font-medium">
                                        {{ t('todo.noTasks') }}
                                    </p>
                                    <Button
                                        variant="default"
                                        class="rounded-xl shadow-md shadow-primary/20"
                                        @click="openDialog({ component: MedicalRecordDialog })"
                                    >
                                        {{ t('todo.startConversation') }}
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div v-else class="space-y-4">
                            <div class="grid gap-4 sm:grid-cols-3">
                                <Card class="shadow-lg shadow-primary/10">
                                    <CardHeader class="space-y-1">
                                        <CardTitle class="text-sm font-semibold text-muted-foreground">
                                            Pending
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div class="text-2xl font-bold text-foreground">
                                            {{ pendingCount }}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card class="shadow-lg shadow-primary/10">
                                    <CardHeader class="space-y-1">
                                        <CardTitle class="text-sm font-semibold text-muted-foreground">
                                            Completed
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div class="text-2xl font-bold text-foreground">
                                            {{ completedCount }}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card class="shadow-lg shadow-primary/10 sm:col-span-1">
                                    <CardHeader class="space-y-2">
                                        <CardTitle class="text-sm font-semibold text-muted-foreground">
                                            Completion
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div class="text-2xl font-bold text-foreground">
                                            {{ completionPct }}%
                                        </div>
                                        <div class="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
                                            <div
                                                class="h-full rounded-full bg-primary transition-all duration-500"
                                                :style="{ width: `${completionPct}%` }"
                                            ></div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            <Card class="shadow-lg shadow-primary/10 border-primary/10">
                                <CardHeader>
                                    <CardTitle class="flex items-center justify-between">
                                        <span class="text-xl">{{
                                            t('todo.upcomingActions')
                                        }}</span>
                                        <span class="text-sm text-muted-foreground"
                                            >{{ todo.items.length }} {{ t('todo.items') }}</span
                                        >
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ul class="space-y-3">
                                        <li
                                            v-for="(item, idx) in todo.items"
                                            :key="idx"
                                            class="group flex items-start gap-3 rounded-2xl border border-border/60 bg-white/80 p-3 shadow-sm transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg"
                                        >
                                            <input
                                                type="checkbox"
                                                class="mt-1 h-4 w-4 accent-emerald-600"
                                                :checked="item.is_check"
                                                :disabled="updatingIndex === idx"
                                                @change="toggleItem(idx)"
                                            />
                                            <div class="text-sm leading-6 flex-1">
                                                <p
                                                    class="font-medium text-foreground transition-colors"
                                                    :class="
                                                        item.is_check
                                                            ? 'line-through text-muted-foreground'
                                                            : ''
                                                    "
                                                >
                                                    {{ item.text }}
                                                </p>
                                                <p
                                                    v-if="item.is_check"
                                                    class="text-[11px] uppercase tracking-[0.14em] text-emerald-600"
                                                >
                                                    {{ t('common.done') || 'Completed' }}
                                                </p>
                                            </div>
                                        </li>
                                    </ul>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
