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
const userId = ref(user.value.id);
const recordId = ref(user.value.currentRecordId);

console.log(
    'ConversationPage userId:',
    userId.value,
    'recordId:',
    recordId.value
);
async function loadHistory() {
    const res = await chatStore.getChatHistory({
        user_id: userId.value,
        record_id: recordId.value,
    });
    // Map backend shape -> frontend Message type
    messages.value = res.history.map((h) => ({
        from: h.role,
        text: h.content,
    }));
}

async function handleSend(text: string) {
    // push optimistic user message
    messages.value.push({ from: 'human', text, isPlaceholder: false });

    // send to backend
    const res = await chatStore.sendChatMessage({
        user_id: userId.value,
        record_id: recordId.value,
        message: text,
    });

    // add bot response
    messages.value.push({ from: 'ai', text: res.data.message });
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
    <!-- Full width scroll host -->
    <div class="flex-1 min-h-0 overflow-auto">
        <!-- Centered content inside -->
        <div class="mx-auto flex h-full w-full max-w-2xl flex-col">
            <!-- Messages just fill available space in this column -->
            <ChatWindow :messages="messages" class="flex-1" />

            <ChatMultipleChoice
                v-if="multipleChoices.length"
                :choices="multipleChoices"
                @select="handleChoice"
            />
            <ChatInputBar :sidebarOpen="false" @send="handleSend" />
        </div>
    </div>
</template>
