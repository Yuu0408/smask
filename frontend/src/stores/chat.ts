import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type {
    MedicalRecordData,
    AddMedicalRecordRequest,
    AddMedicalRecordResponse,
} from '@/types/medical-record';
import type {
    getChatHistoryRequest,
    GetChatHistoryResponse,
    sendChatMessageRequest,
    sendChatMessageResponse,
} from '@/types/chat';

const URL_PREFIX = '/v1/chat';

export const useChatStore = defineStore('chat', () => {
    async function createNewRecord(userId: string, form: MedicalRecordData) {
        const payload: AddMedicalRecordRequest = {
            user_id: userId,
            data: form,
        };

        return await $backend.post<AddMedicalRecordResponse>(
            `${URL_PREFIX}/new-record`,
            payload
        );
    }

    async function sendChatMessage(payload: sendChatMessageRequest) {
        return await $backend.post<sendChatMessageResponse>(
            `${URL_PREFIX}/chat`,
            payload
        );
    }

    async function getChatHistory(params?: getChatHistoryRequest) {
        const response = await $backend.get<GetChatHistoryResponse>(
            URL_PREFIX,
            {
                params: params,
            }
        );

        return response.data;
    }

    return {
        createNewRecord,
        sendChatMessage,
        getChatHistory,
    };
});
