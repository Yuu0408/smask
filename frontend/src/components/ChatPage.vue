<script setup lang="ts">
// Legacy ChatPage updated to use current stores and message shape
import ChatWindow from '@/components/ChatWindow.vue';
import ChatInputBar from '@/components/ChatInputBar.vue';
import ChatMultipleChoices from '@/components/ChatMultipleChoices.vue';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Message } from '@/types/message';
import { ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

defineProps<{ sidebarOpen: boolean }>();

const { t } = useI18n();
const chatStore = useChatStore();
const { user } = storeToRefs(useAuthStore());
const router = useRouter();

const messages = ref<Message[]>([]);
const multipleChoices = ref<string[]>([]);

const userId = computed(() => user.value?.id ?? '');
const recordId = computed(() => user.value?.currentRecordId ?? '');

const toastVisible = ref(false);
const filteredChoices = computed(() => {
    if (
        multipleChoices.value.length === 1 &&
        multipleChoices.value[0] === '%medical_record%'
    ) {
        toastVisible.value = true;
        return [];
    }
    return multipleChoices.value;
});

watch(toastVisible, (visible) => {
    if (visible) setTimeout(() => (toastVisible.value = false), 4000);
});

function goToDiagnosis() {
    router.push('/diagnosis');
    toastVisible.value = false;
}

async function sendMessage(text: string) {
    if (!userId.value || !recordId.value) {
        alert(t('chatPage.sessionNotInitialized'));
        return;
    }

    messages.value.push({
        id: crypto.randomUUID(),
        role: 'human',
        content: text,
    });
    const aiId = crypto.randomUUID();
    messages.value.push({ id: aiId, role: 'ai', content: '' });
    await nextTick();

    try {
        const res = await chatStore.sendChatMessage({
            user_id: userId.value,
            record_id: recordId.value,
            message: text,
        });
        const idx = messages.value.findIndex((m) => m.id === aiId);
        if (idx !== -1) messages.value[idx].content = res.data.message;
        multipleChoices.value = res.data.multiple_choices ?? [];
        if (res.data.decision === 'DIAGNOSIS') {
            // Optionally navigate or show toast
            toastVisible.value = true;
        }
    } catch (error) {
        console.error(error);
        const idx = messages.value.findIndex((m) => m.id === aiId);
        if (idx !== -1) messages.value[idx].content = t('chatPage.error');
    }
}

defineExpose({ sendMessage });
</script>

<template>
    <!-- Main centered container -->
    <div class="w-full max-w-2xl flex flex-col flex-1 min-h-[calc(100vh-64px)]">
        <ScrollArea class="flex-1">
            <ChatWindow :messages="messages" class="flex-1" />
        </ScrollArea>

        <!-- Animated toast -->
        <Transition name="fade">
            <div
                v-if="toastVisible"
                @click="goToDiagnosis"
                class="fixed top-20 right-4 z-40 bg-gray-100 dark:bg-zinc-700 text-black dark:text-white px-4 py-2 rounded-lg shadow-md cursor-pointer transition hover:bg-gray-200 dark:hover:bg-zinc-600"
            >
                📄 {{ t('chatPage.viewDiagnosis') }}
            </div>
        </Transition>

        <ChatMultipleChoices :choices="filteredChoices" @select="sendMessage" />
        <ChatInputBar @send="sendMessage" :sidebar-open="sidebarOpen" />
    </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
