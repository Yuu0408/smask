<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';

const route = useRoute();
const { user } = storeToRefs(useAuthStore());
const contact = useContactStore();

const messages = ref<
    { id: string; role: 'doctor' | 'patient'; content: string }[]
>([]);
const sending = ref(false);
const bottomRef = ref<HTMLDivElement | null>(null);

function roleForMessage(mRole: 'doctor' | 'patient') {
    const selfRole = user.value?.role === 'doctor' ? 'doctor' : 'patient';
    return mRole === selfRole ? 'human' : 'ai';
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

onMounted(load);
</script>

<template>
    <div class="flex-1 overflow-y-auto">
        <div class="mx-auto w-full max-w-2xl px-4 pb-24 pt-6">
            <ChatMessage
                v-for="m in messages"
                :key="m.id"
                :role="roleForMessage(m.role)"
                :content="m.content"
            />
        </div>
        <div ref="bottomRef"></div>
    </div>
    <div
        class="sticky bottom-0 w-full bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
        <div class="mx-auto w-full max-w-2xl px-4 pb-3">
            <ChatInput :loading="sending" @send="handleSend" />
        </div>
    </div>
</template>
