<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import { useI18n } from 'vue-i18n';

const route = useRoute();
const { user } = storeToRefs(useAuthStore());
const contact = useContactStore();
const { t } = useI18n();

const messages = ref<
    { id: string; role: 'doctor' | 'patient'; content: string }[]
>([]);
const sending = ref(false);
const bottomRef = ref<HTMLDivElement | null>(null);
const contactName = ref('');

function roleForMessage(mRole: 'doctor' | 'patient') {
    const selfRole = user.value?.role === 'doctor' ? 'doctor' : 'patient';
    return mRole === selfRole ? 'human' : 'ai';
}

const selfLabel = computed(() => user.value?.username || 'You');
const otherLabel = computed(() => {
    if (contactName.value) return contactName.value;
    return user.value?.role === 'doctor' ? 'Patient' : 'Doctor';
});

async function loadMeta() {
    if (!user.value?.id) return;
    const contactId = String(route.params.id);
    try {
        if (user.value.role === 'doctor') {
            const detail = await contact.getContactDetail(contactId);
            contactName.value =
                detail?.medical_record?.patient_info?.full_name ||
                detail?.patient_user_id ||
                '';
        } else {
            const res = await contact.listMyDoctors(user.value.id);
            const match = (res.doctors || []).find(
                (d) => d.contact_id === contactId
            );
            contactName.value = match?.username || '';
            if (!contactName.value) {
                const detail = await contact.getContactDetail(contactId);
                contactName.value = detail?.facility || '';
            }
        }
    } catch (err) {
        console.error('Failed to load contact meta', err);
    }
}

async function load() {
    const res = await contact.getMessages(String(route.params.id));
    messages.value = (res.messages || []).map((m) => ({
        id: m.id,
        role: m.role as 'doctor' | 'patient',
        content: m.content,
    }));
    await nextTick();
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
}

async function handleSend(text: string) {
    if (!text.trim() || !user.value?.id) return;
    sending.value = true;
    const selfRole = user.value?.role === 'doctor' ? 'doctor' : 'patient';
    const tmpId = crypto.randomUUID();
    messages.value.push({ id: tmpId, role: selfRole, content: text });
    try {
        await contact.sendMessage({
            contact_id: String(route.params.id),
            sender_id: user.value.id,
            content: text,
        });
    } finally {
        sending.value = false;
        await load();
    }
}

onMounted(async () => {
    await Promise.all([loadMeta(), load()]);
    await nextTick();
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' });
});
</script>

<template>
    <div
        class="flex min-h-[calc(100vh-4rem)] h-[calc(100vh-4rem)] flex-col overflow-hidden"
    >
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
                        class="relative min-h-0 flex-1 overflow-y-auto px-4 py-4"
                    >
                        <div class="mx-auto w-full max-w-3xl space-y-2">
                            <ChatMessage
                                v-for="m in messages"
                                :key="m.id"
                                :role="roleForMessage(m.role)"
                                :content="m.content"
                                :human-label="selfLabel"
                                :ai-label="otherLabel"
                            />
                            <div ref="bottomRef" class="h-4"></div>
                        </div>
                    </div>

                    <div class="relative px-4 pb-3 pt-3 bg-transparent">
                        <div class="mx-auto w-full max-w-3xl">
                            <ChatInput :loading="sending" @send="handleSend" />
                            <p
                                class="mt-2 text-center text-[10px] text-muted-foreground"
                            >
                                {{ t('contact.detail.startChatPrompt') }}
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>
</template>
