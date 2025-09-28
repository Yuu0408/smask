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
import { History as HistoryIcon } from 'lucide-vue-next';

const { user } = storeToRefs(useAuthStore());
const { t } = useI18n();
const historyStore = useHistoryStore();
const router = useRouter();
const { openDialog } = useDialog();

const userId = computed(() => user.value?.id ?? '');

const histories = ref<ChatHistoryPreview[]>([]);

onMounted(async () => {
    console.log('HistoryPage userId:', userId.value);
    const res = await historyStore.getAllChatHistory({
        user_id: userId.value,
    });

    console.log('histories:', res);
    histories.value = res.histories;
});

function openHistory(sessionId: string) {
    // Set the current record in auth store so ConversationPage picks it up
    if (user.value) {
        user.value.currentRecordId = sessionId;
    }
    router.push(`/chat/conversation`);
}
</script>

<template>
    <div class="p-8 space-y-8 overflow-auto">
        <div class="flex items-center gap-3">
            <HistoryIcon class="w-8 h-8 text-primary" />
            <h1 class="text-3xl font-bold tracking-tight">
                {{ t('history.title') }}
            </h1>
        </div>

        <div v-if="!histories.length" class="text-muted-foreground">
            <div class="flex flex-col items-center gap-3 py-10">
                <div class="text-base">{{ t('history.empty') }}</div>
                <Button
                    variant="default"
                    @click="openDialog({ component: MedicalRecordDialog })"
                >
                    {{ t('todo.startConversation') }}
                </Button>
            </div>
        </div>

        <div v-else class="grid gap-3">
            <Card
                v-for="history in histories"
                :key="history.sessionId"
                class="cursor-pointer hover:shadow-md transition"
                @click="openHistory(history.sessionId)"
            >
                <CardHeader>
                    <!-- Title now shows the chief complaint from the medical record -->
                    <CardTitle class="text-base font-medium truncate">
                        {{
                            history.chiefComplaint ||
                            history.lastMessage ||
                            t('history.noMessagesYet')
                        }}
                    </CardTitle>
                    <CardDescription>
                        {{ t('history.lastActivity') }}
                        {{ new Date(history.updatedAt).toLocaleString() }}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <p class="text-sm text-muted-foreground line-clamp-2">
                        {{ history.lastMessage }}
                    </p>
                </CardContent>
            </Card>
        </div>
    </div>
</template>
