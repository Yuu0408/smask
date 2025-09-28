import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type { sendChatMessageRequest } from '@/types/chat';

const URL_PREFIX = '/v1/chat';

export const useVoiceStore = defineStore('voice', () => {
    async function sendVoiceMessage(
        payload: sendChatMessageRequest
    ): Promise<{ text: string; audio: Blob }> {
        const response = await $backend.post(`${URL_PREFIX}/voice`, payload, {
            responseType: 'json',
        });
        const data = response.data as {
            text: string;
            audio_b64: string;
            content_type?: string;
        };
        const byteChars = atob(data.audio_b64);
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {
            byteNumbers[i] = byteChars.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {
            type: data.content_type || 'audio/mpeg',
        });
        return { text: data.text, audio: blob };
    }

    async function speakText(text: string): Promise<Blob> {
        const response = await $backend.post(
            `${URL_PREFIX}/tts`,
            { text },
            { responseType: 'blob' }
        );
        return response.data as Blob;
    }

    return { sendVoiceMessage, speakText };
});
