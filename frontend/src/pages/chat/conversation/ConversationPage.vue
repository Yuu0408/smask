<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useChatStore } from '@/stores/chat';
// import ChatMultipleChoice from '@/components/ChatMultipleChoices.vue';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import type { Conversation, Message } from '@/types/message';

const chatStore = useChatStore();
const userStore = useUserStore();

const { user } = storeToRefs(userStore);

const multipleChoices = ref<string[]>([]);
const userId = ref(user.value.id);
const recordId = ref(user.value.currentRecordId);

console.log(
    'ConversationPage userId:',
    userId.value,
    'recordId:',
    recordId.value
);

const conversations = ref<Conversation[]>([]);

const activeId = ref('1');
const sending = ref(false);
const activeConversation = computed(() =>
    conversations.value.find((c) => c.id === activeId.value)
);

async function loadHistory() {
    sending.value = true;
    try {
        const res = await chatStore.getChatHistory({
            user_id: userId.value,
            record_id: recordId.value,
        });
        // Map backend -> UI Message[]
        const messages: Message[] = (res?.history ?? []).map((h) => ({
            id: h.id ?? crypto.randomUUID(),
            role: h.role, // 'ai' | 'human' (matches your UI types)
            content: h.content,
            // created_at is available as h.created_at if you need it later
        }));

        // If an active conversation exists, replace its messages; otherwise create one.
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

        // Reset multiple choice suggestions based on last message if your API returns them elsewhere
        multipleChoices.value = [];
    } catch (err) {
        console.error('Failed to load history:', err);
    } finally {
        sending.value = false;
    }
}

// function handleChoice(choice: string) {
//     handleSend(choice);
// }

async function handleSend(text: string) {
    if (!text.trim() || !activeConversation.value) return;
    const conv = activeConversation.value;
    conv.messages.push({
        id: crypto.randomUUID(),
        role: 'human',
        content: text,
    });

    sending.value = true;
    try {
        // Simulated assistant reply
        await new Promise((r) => setTimeout(r, 600));
        const res = await chatStore.sendChatMessage({
            user_id: userId.value,
            record_id: recordId.value,
            message: text,
        });
        const ai_response = res.data.message;
        conv.messages.push({
            id: crypto.randomUUID(),
            role: 'ai',
            content: ai_response,
        });
        multipleChoices.value = res.data.multiple_choices ?? [];
    } finally {
        sending.value = false;
    }
}

onMounted(() => {
    loadHistory();
});
</script>

<template>
    <!-- Full width scroll host -->
    <div class="flex-1 overflow-y-auto">
        <div class="mx-auto w-full max-w-2xl px-4 pb-24 pt-6">
            <ChatMessage
                v-for="m in activeConversation?.messages || []"
                :key="m.id"
                :role="m.role"
                :content="m.content"
            />
        </div>
    </div>

    <!-- Sticky input at bottom; centered column -->
    <div
        class="sticky bottom-0 w-full border-t bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
        <div class="mx-auto w-full max-w-2xl px-4 py-3">
            <ChatInput :loading="sending" @send="handleSend" />
            <p class="mt-2 text-center text-[10px] text-muted-foreground">
                Press <kbd class="rounded border px-1">Enter</kbd> to send •
                <kbd class="rounded border px-1">Shift</kbd>+<kbd
                    class="rounded border px-1"
                    >Enter</kbd
                >
                for newline
            </p>
        </div>
    </div>
</template>
