import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type { GetAllChatHistoryResponse } from '@/types/history';
import type { GetAllChatHistoryRequest } from '@/types/history';

const URL_PREFIX = '/v1/history';

export const useHistoryStore = defineStore('history', () => {
    async function getAllChatHistory(params?: GetAllChatHistoryRequest) {
        const response = await $backend.get<GetAllChatHistoryResponse>(
            URL_PREFIX,
            {
                params,
            }
        );

        return response.data;
    }
    return {
        getAllChatHistory,
    };
});
