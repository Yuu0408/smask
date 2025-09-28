<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
import { Dialog } from '@/components/ui/dialog';
import DialogContent from '@/components/ui/dialog/DialogContent.vue';
import DialogHeader from '@/components/ui/dialog/DialogHeader.vue';
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue';
import { Button } from '@/components/ui/button';
import { Mic, Square } from 'lucide-vue-next';
import UserAvatar from '@/components/common/UserAvatar.vue';
import { useVoiceStore } from '@/stores/voice';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
    userId: string;
    recordId: string;
    initialMessage?: string;
}>();

const open = defineModel<boolean>();

const authStore = useAuthStore();
const { user } = storeToRefs(authStore);
const voiceStore = useVoiceStore();
const { locale, t } = useI18n();

const listening = ref(false);
const transcript = ref('');
const audioPlaying = ref(false);
const sending = ref(false);
const responseText = ref('');
let currentAudio: HTMLAudioElement | null = null;
let recognition: any | null = null;

const canUseSpeech = computed(
    () =>
        typeof window !== 'undefined' &&
        ((window as any).SpeechRecognition ||
            (window as any).webkitSpeechRecognition)
);

// Map current app locale to a suitable BCP-47 code for the recognizer
const speechLang = computed(() => {
    switch (locale.value) {
        case 'vi':
            return 'vi-VN';
        case 'en':
        default:
            return 'en-US';
    }
});

function initRecognition() {
    if (!canUseSpeech.value) return;
    const SR =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
    recognition = new SR();
    recognition.lang = speechLang.value;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = async (event: any) => {
        const result = event.results?.[0]?.[0]?.transcript || '';
        transcript.value = result;
        listening.value = false;
        if (result.trim()) {
            await sendTranscript(result.trim());
        }
    };

    recognition.onerror = () => {
        listening.value = false;
    };

    recognition.onend = () => {
        listening.value = false;
    };
}

async function sendTranscript(text: string) {
    sending.value = true;
    try {
        const payload = {
            user_id: props.userId,
            record_id: props.recordId,
            message: text,
        };
        const { text: aiText, audio } =
            await voiceStore.sendVoiceMessage(payload);
        responseText.value = aiText || '';
        await playBlob(audio);
    } catch (e) {
        console.error('Voice send/play failed', e);
    } finally {
        // Keep disabled until audio finished (handled by audioPlaying)
        sending.value = false;
    }
}

async function playBlob(blob: Blob) {
    // Stop any current audio
    try {
        currentAudio?.pause();
    } catch {}
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    currentAudio = audio;
    audioPlaying.value = true;
    audio.onended = () => {
        audioPlaying.value = false;
        URL.revokeObjectURL(url);
    };
    audio.onerror = () => {
        audioPlaying.value = false;
        URL.revokeObjectURL(url);
    };
    try {
        await audio.play();
    } catch (err) {
        // If autoplay is blocked, allow mic immediately
        audioPlaying.value = false;
        URL.revokeObjectURL(url);
        throw err;
    }
}

function startListening() {
    if (!recognition) return;
    if (audioPlaying.value) return; // wait until audio finishes
    if (sending.value) return; // wait until backend response completes
    try {
        transcript.value = '';
        listening.value = true;
        // Ensure language reflects current locale at start time
        recognition.lang = speechLang.value;
        recognition.start();
    } catch (e) {
        listening.value = false;
    }
}

function stopListening() {
    try {
        recognition?.stop();
    } catch {}
}

onMounted(() => {
    initRecognition();
    // Auto-play the initial AI message when available
    const initial = (props.initialMessage || '').trim();
    if (initial) {
        responseText.value = initial;
        voiceStore
            .speakText(initial)
            .then((blob) => playBlob(blob))
            .catch((e) => console.error('Auto TTS failed', e));
    }
});

// Update recognition language when app locale changes
watch(speechLang, (lng) => {
    if (recognition) {
        try {
            recognition.lang = lng;
        } catch {}
    }
});

onBeforeUnmount(() => {
    stopListening();
    recognition = null;
});
</script>

<template>
    <Dialog v-model:open="open">
        <DialogContent class="max-w-none w-screen h-screen rounded-none p-0">
            <div
                class="w-full h-full flex flex-col items-center justify-center gap-10 bg-background"
            >
                <DialogHeader class="sr-only">
                    <DialogTitle>{{ t('voice.title') }}</DialogTitle>
                </DialogHeader>

                <UserAvatar
                    :name="user?.username || 'User'"
                    class="size-40 rounded-full"
                />

                <div class="flex flex-col items-center gap-3 mt-10">
                    <Button
                        size="icon"
                        class="size-16 rounded-full"
                        :variant="listening ? 'default' : 'secondary'"
                        :disabled="!canUseSpeech || sending || audioPlaying"
                        @click="listening ? stopListening() : startListening()"
                    >
                        <Mic v-if="!listening" class="size-8" />
                        <Square v-else class="size-8" />
                    </Button>
                    <p class="text-sm text-muted-foreground">
                        {{
                            listening
                                ? t('voice.status.listening')
                                : sending
                                  ? t('common.loading')
                                  : audioPlaying
                                    ? t('voice.status.playing')
                                    : canUseSpeech
                                      ? t('voice.status.tapToSpeak')
                                      : t('voice.status.notSupported')
                        }}
                    </p>
                    <div class="flex flex-col gap-1 items-center">
                        <p
                            v-if="transcript"
                            class="text-center max-w-xl text-sm px-6 py-4"
                        >
                            <span class="font-medium text-muted-foreground"
                                >{{ t('voice.label.youSaid') }}:
                            </span>
                            "{{ transcript }}"
                        </p>
                        <p
                            v-if="responseText"
                            class="text-center max-w-xl text-sm px-6"
                        >
                            <span class="font-medium text-muted-foreground"
                                >{{ t('voice.label.assistantSaid') }}:
                            </span>
                            "{{ responseText }}"
                        </p>
                    </div>
                </div>
            </div>
        </DialogContent>
    </Dialog>
</template>
