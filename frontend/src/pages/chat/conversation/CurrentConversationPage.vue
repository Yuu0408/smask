<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { useChatStore } from '@/stores/chat';
import { storeToRefs } from 'pinia';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import type { Conversation, Message } from '@/types/message';
import { useAuthStore } from '@/stores/auth';
import ChatMultipleChoices from '@/components/ChatMultipleChoices.vue';
import { useI18n } from 'vue-i18n';

const chatStore = useChatStore();
const { openDialog } = useDialog();

const { user } = storeToRefs(useAuthStore());
const { t } = useI18n();

const multipleChoices = ref<string[]>([]);
const userId = computed(() => user.value?.id ?? '');
const recordId = computed(() => user.value?.currentRecordId ?? '');

const conversations = ref<Conversation[]>([]);
const activeId = ref('1');
const sending = ref(false);

const activeConversation = computed(() =>
    conversations.value.find((c) => c.id === activeId.value)
);
const hasMessages = computed(
    () => (activeConversation.value?.messages?.length ?? 0) > 0
);
const showEmpty = computed(
    () => !recordId.value || (!sending.value && !hasMessages.value)
);

async function loadHistory() {
    sending.value = true;
    try {
        const res = await chatStore.getChatHistory({
            user_id: userId.value,
            record_id: recordId.value,
        });
        const messages: Message[] = (res?.history ?? []).map((h) => ({
            id: h.id ?? crypto.randomUUID(),
            role: h.role,
            content: h.content,
        }));

        const existing = activeConversation.value;
        if (existing) {
            existing.messages = messages;
        } else {
            const conv: Conversation = {
                id: recordId.value || crypto.randomUUID(),
                title: 'Conversation',
                messages,
            };
            conversations.value.push(conv);
            activeId.value = conv.id;
        }

        multipleChoices.value = [];
    } catch (err) {
        console.error('Failed to load history:', err);
    } finally {
        sending.value = false;
    }
}

const bottomRef = ref<HTMLDivElement | null>(null);

async function handleSend(text: string) {
    if (!text.trim() || !activeConversation.value) return;
    multipleChoices.value = [];
    const conv = activeConversation.value;

    if (text !== '###DIAGNOSIS###') {
        conv.messages.push({
            id: crypto.randomUUID(),
            role: 'human',
            content: text,
        });
    }
    const aiPlaceholderId = crypto.randomUUID();
    conv.messages.push({ id: aiPlaceholderId, role: 'ai', content: '' });

    await nextTick();
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' });

    sending.value = true;
    try {
        const res = await chatStore.sendChatMessage({
            user_id: userId.value,
            record_id: recordId.value,
            message: text,
        });
        const idx = conv.messages.findIndex((m) => m.id === aiPlaceholderId);
        if (idx !== -1) conv.messages[idx].content = res.data.message;

        if (res.data.decision === 'DIAGNOSIS') {
            handleSend('###DIAGNOSIS###');
        }
        multipleChoices.value = res.data.multiple_choices ?? [];
    } finally {
        sending.value = false;
        await nextTick();
        bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
    }
}

function onChoice(choice: string) {
    handleSend(choice);
    multipleChoices.value = [];
}

onMounted(async () => {
    await loadHistory();
    await nextTick();
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
});

watch(
    () => recordId.value,
    async (newId, oldId) => {
        if (newId && newId !== oldId) {
            conversations.value = [];
            activeId.value = '';
            await loadHistory();
            await nextTick();
            bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
        }
    }
);
</script>

<template>
    <!-- Empty state without chat controls -->
    <div v-if="showEmpty" class="flex-1 flex items-center justify-center p-8">
        <div class="text-center space-y-3">
            <div class="text-lg font-medium">
                {{ t('chat.empty.noConversation') }}
            </div>
            <div class="text-sm text-muted-foreground">
                {{ t('chat.empty.startQuestion') }}
            </div>
            <Button @click="openDialog({ component: MedicalRecordDialog })">{{
                t('chat.empty.newChat')
            }}</Button>
        </div>
    </div>

    <!-- Conversation view with full controls -->
    <template v-else>
        <div class="flex-1 overflow-y-auto">
            <div class="mx-auto w-full max-w-2xl px-4 pb-24 pt-6">
                <ChatMessage
                    v-for="m in activeConversation?.messages || []"
                    :key="m.id"
                    :role="m.role"
                    :content="m.content"
                />
            </div>
            <div ref="bottomRef"></div>
        </div>

        <div
            class="sticky bottom-0 w-full bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        >
            <div class="w-full flex justify-center mt-2">
                <ChatMultipleChoices
                    v-if="multipleChoices.length"
                    :choices="multipleChoices"
                    @select="onChoice"
                />
            </div>

            <div class="mx-auto w-full max-w-2xl px-4 pb-3">
                <ChatInput :loading="sending" @send="handleSend" />
                <p
                    class="mt-2 text-center text-[10px] text-muted-foreground"
                    v-html="t('chat.input.hint')"
                ></p>
            </div>
        </div>
    </template>
</template>
