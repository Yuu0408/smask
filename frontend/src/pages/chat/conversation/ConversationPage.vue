<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { useChatStore } from '@/stores/chat';
// import ChatMultipleChoice from '@/components/ChatMultipleChoices.vue';
import { storeToRefs } from 'pinia';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import type { Conversation, Message } from '@/types/message';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import type { ChatStage } from '@/types/chat';

const chatStore = useChatStore();
const { openDialog } = useDialog();

const { user } = storeToRefs(useAuthStore());
const { t } = useI18n();

const multipleChoices = ref<string[]>([]);
const userId = computed(() => user.value?.id ?? '');
const recordId = computed(() => user.value?.currentRecordId ?? '');

console.log(
    'ConversationPage userId:',
    userId.value,
    'recordId:',
    recordId.value
);

const conversations = ref<Conversation[]>([]);

const activeId = ref('1');
const sending = ref(false);
const currentStage = ref<ChatStage | null>(null);
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
    currentStage.value = null;
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
            pending: false,
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

const bottomRef = ref<HTMLDivElement | null>(null);

async function handleSend(text: string) {
    if (!text.trim() || !activeConversation.value) return;
    // Hide any quick replies as soon as user sends a message
    multipleChoices.value = [];
    const conv = activeConversation.value;

    // push human message
    conv.messages.push({
        id: crypto.randomUUID(),
        role: 'human',
        content: text,
    });

    // push placeholder AI message
    const aiPlaceholderId = crypto.randomUUID();
    const placeholderText = stagePlaceholder(currentStage.value);
    conv.messages.push({
        id: aiPlaceholderId,
        role: 'ai',
        content: placeholderText,
        pending: true,
    });
    await nextTick();
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' });

    sending.value = true;
    try {
        const res = await chatStore.sendChatMessage({
            user_id: userId.value,
            record_id: recordId.value,
            message: text,
        });

        // find the placeholder and replace content
        const idx = conv.messages.findIndex((m) => m.id === aiPlaceholderId);
        if (idx !== -1) {
            conv.messages[idx].content = res.data.message;
            conv.messages[idx].pending = false;
        }

        // update multiple choices if any
        multipleChoices.value = res.data.multiple_choices ?? [];
        currentStage.value = res.data.decision ?? currentStage.value;
    } finally {
        sending.value = false;
        await nextTick();
        bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
    }
}

function onChoice(choice: string) {
    handleSend(choice);
    multipleChoices.value = []; // hide choices after selection
}

onMounted(async () => {
    await loadHistory();
    await nextTick(); // wait until messages are rendered
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

const stagePlaceholderKeys: Record<ChatStage, string> = {
    FORM_CLARIFICATION: 'chat.placeholder.stage.formClarification',
    BASIC_QUESTIONING: 'chat.placeholder.stage.basicQuestioning',
    REASONING: 'chat.placeholder.stage.reasoning',
    RULE_OUT: 'chat.placeholder.stage.ruleOut',
    CLOSING: 'chat.placeholder.stage.closing',
    NEXT_STEP: 'chat.placeholder.stage.closing',
    LEGACY_DIAGNOSIS: 'chat.placeholder.stage.legacyDiagnosis',
};

function stagePlaceholder(stage: ChatStage | null) {
    const waitingText = t('chat.placeholder.waiting');
    const loadingText = t('chat.placeholder.loading');
    const baseFallback =
        (waitingText &&
            waitingText !== 'chat.placeholder.waiting' &&
            waitingText) ||
        (loadingText &&
            loadingText !== 'chat.placeholder.loading' &&
            loadingText) ||
        'AI is preparing your response...';
    if (!stage) return baseFallback;
    const key = stagePlaceholderKeys[stage];
    if (!key) return baseFallback;
    const localized = t(key);
    // vue-i18n returns the key itself if missing; guard to keep a friendly fallback.
    return !localized || localized === key ? baseFallback : localized;
}
</script>

<template>
    <div
        class="flex min-h-[calc(100vh-4rem)] h-[calc(100vh-4rem)] flex-col overflow-hidden"
    >
        <div
            v-if="showEmpty"
            class="flex flex-1 items-center justify-center p-10"
        >
            <div
                class="relative overflow-hidden rounded-3xl border border-primary/20 bg-gradient-to-br from-white via-primary/5 to-accent/10 p-10 text-center shadow-xl shadow-primary/10 backdrop-blur"
            >
                <div
                    class="pointer-events-none absolute -left-10 top-0 size-40 rounded-full bg-primary/15 blur-3xl"
                />
                <div
                    class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-primary"
                >
                    {{ t('sidebar.header.app.name') }}
                    <span class="text-muted-foreground">AI</span>
                </div>
                <div class="mt-4 text-2xl font-semibold">
                    {{ t('chat.empty.noConversation') }}
                </div>
                <div class="mt-2 text-sm text-muted-foreground max-w-md">
                    {{ t('chat.empty.startQuestion') }}
                </div>
                <Button
                    class="mt-6 rounded-xl px-6 shadow-lg shadow-primary/20"
                    @click="openDialog({ component: MedicalRecordDialog })"
                    >{{ t('chat.empty.newChat') }}</Button
                >
            </div>
        </div>

        <div v-else class="flex flex-1 flex-col overflow-hidden min-h-0">
            <div class="relative flex-1 overflow-hidden min-h-0">
                <div
                    class="pointer-events-none absolute inset-0 opacity-60"
                    aria-hidden="true"
                >
                    <div
                        class="absolute -left-16 top-10 size-80 rounded-full bg-primary/15 blur-3xl"
                    />
                    <div
                        class="absolute right-0 bottom-10 size-72 rounded-full bg-accent/20 blur-3xl"
                    />
                </div>
                <div class="relative h-full w-full px-0 py-0 min-h-0 flex">
                    <section
                        class="relative grid h-full min-h-full flex-1 grid-rows-[1fr_auto] overflow-hidden rounded-none border-0 bg-white/90 shadow-lg shadow-primary/10 backdrop-blur"
                    >
                        <div
                            class="relative min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4"
                        >
                            <ChatMessage
                                v-for="m in activeConversation?.messages || []"
                                :key="m.id"
                                :role="m.role"
                                :content="m.content"
                                :pending="m.pending"
                            />
                            <div ref="bottomRef" class="h-4"></div>
                        </div>

                        <div class="relative px-4 pb-3 pt-3 bg-transparent">
                            <div
                                v-if="multipleChoices.length"
                                class="pointer-events-none absolute inset-x-0 top-0 h-8 bg-gradient-to-b from-transparent via-white/70 to-white opacity-90"
                                aria-hidden="true"
                            />
                            <div
                                v-if="multipleChoices.length"
                                class="relative z-10 grid gap-2"
                                :class="
                                    multipleChoices.length > 2
                                        ? 'grid-cols-2'
                                        : 'grid-cols-1'
                                "
                            >
                                <div
                                    class="absolute -left-1 -top-6 text-primary"
                                >
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        class="size-5"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                        stroke-width="1.8"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    >
                                        <path
                                            d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
                                        />
                                        <path d="M20 3v4" />
                                        <path d="M22 5h-4" />
                                        <path d="M4 17v2" />
                                        <path d="M5 18H3" />
                                    </svg>
                                </div>
                                <button
                                    v-for="idea in multipleChoices"
                                    :key="idea"
                                    type="button"
                                    class="rounded-xl border border-primary/15 bg-gradient-to-r from-primary/5 via-white to-accent/10 px-3 py-2 text-left text-sm font-medium text-primary shadow-sm transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md hover:bg-primary hover:text-primary-foreground hover:bg-none"
                                    @click="onChoice(idea)"
                                >
                                    {{ idea }}
                                </button>
                            </div>

                            <div class="mt-3">
                                <ChatInput
                                    :loading="sending"
                                    @send="handleSend"
                                />
                                <p
                                    class="mt-2 text-center text-[10px] text-muted-foreground"
                                    v-html="t('chat.input.hint')"
                                ></p>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    </div>
</template>
