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
    <div class="p-8 space-y-8 overflow-auto">
        <div class="flex items-center gap-3">
            <ListTodo class="w-8 h-8 text-primary" />
            <h1 class="text-3xl font-bold tracking-tight">
                {{ t('todo.title') }}
            </h1>
        </div>
        <div v-if="loading" class="text-muted-foreground animate-pulse">
            {{ t('common.loading') }}
        </div>
        <div
            v-else-if="!todo || (todo && todo.items.length === 0)"
            class="text-muted-foreground"
        >
            <div class="flex flex-col items-center gap-3 py-10">
                <div class="text-base">{{ t('todo.noTasks') }}</div>
                <Button
                    variant="default"
                    @click="openDialog({ component: MedicalRecordDialog })"
                >
                    {{ t('todo.startConversation') }}
                </Button>
            </div>
        </div>
        <div v-else>
            <Card class="shadow-sm border-muted">
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
                            class="group flex items-start gap-3 rounded-md border border-transparent hover:border-muted p-3 transition-colors bg-card hover:bg-muted/30"
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
                                    class="font-medium text-foreground"
                                    :class="
                                        item.is_check
                                            ? 'line-through text-muted-foreground'
                                            : ''
                                    "
                                >
                                    {{ item.text }}
                                </p>
                            </div>
                        </li>
                    </ul>
                </CardContent>
            </Card>
        </div>
    </div>
</template>
