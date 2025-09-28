import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type {
    MedicalRecordData,
    AddMedicalRecordRequest,
    AddMedicalRecordResponse,
} from '@/types/medical-record';
import { ref } from 'vue';
import type { User } from '@/types/user';

const URL_PREFIX = '/v1/user';
export const useUserStore = defineStore('user', () => {
    const user = ref<User>({
        id: ``,
        currentRecordId: ``,
    });
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

    return {
        user,
        createNewRecord,
    };
});
