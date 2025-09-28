import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type {
    MedicalRecordData,
    AddMedicalRecordRequest,
    AddMedicalRecordResponse,
    getCurrentRecordRequest,
    GetCurrentRecordResponse,
} from '@/types/medical-record';

const URL_PREFIX = '/v1/record';

export const useChatStore = defineStore('record', () => {
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

    async function getCurrentRecord(params?: getCurrentRecordRequest) {
        const response = await $backend.get<GetCurrentRecordResponse>(
            URL_PREFIX,
            {
                params: params,
            }
        );

        return response.data;
    }

    return {
        createNewRecord,
        getCurrentRecord,
    };
});
