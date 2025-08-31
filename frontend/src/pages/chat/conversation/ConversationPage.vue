<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useChatStore } from '@/stores/chat';
import ChatWindow from '@/components/ChatWindow.vue';
import ChatInputBar from '@/components/ChatInputBar.vue';
import ChatMultipleChoice from '@/components/ChatMultipleChoices.vue';
import type { Message } from '@/types/message';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import { ScrollArea } from '@/components/ui/scroll-area';

const chatStore = useChatStore();
const userStore = useUserStore();

const { user } = storeToRefs(userStore);

const messages = ref<Message[]>([]);
const multipleChoices = ref<string[]>([]);

const userId = user.value.id;
const recordId = user.value.currentRecordId;

async function loadHistory() {
    const res = await chatStore.getChatHistory({
        user_id: userId,
        record_id: recordId,
    });
    // Map backend shape -> frontend Message type
    messages.value = res.history.map((h) => ({
        from: h.role === 'assistant' ? 'bot' : 'user',
        text: h.content,
    }));
}

async function handleSend(text: string) {
    // push optimistic user message
    messages.value.push({ from: 'user', text, isPlaceholder: false });

    // send to backend
    const res = await chatStore.sendChatMessage({
        user_id: userId,
        record_id: recordId,
        message: text,
    });

    // add bot response
    messages.value.push({ from: 'bot', text: res.data.response });
    multipleChoices.value = res.data.multiple_choices ?? [];
}

function handleChoice(choice: string) {
    handleSend(choice);
}

onMounted(() => {
    loadHistory();
});
</script>

<template>
    <div class="w-full max-w-2xl flex flex-col flex-1 min-h-[calc(100vh-64px)]">
        <ScrollArea class="flex-1">
            <ChatWindow :messages="messages" class="flex-1" />
        </ScrollArea>
        <ChatMultipleChoice
            v-if="multipleChoices.length"
            :choices="multipleChoices"
            @select="handleChoice"
        />

        <ChatInputBar :sidebarOpen="false" @send="handleSend" />
    </div>
</template>
