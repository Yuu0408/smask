import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type {
    SendContactRequest,
    SendContactResponse,
    ListPatientsResponse,
    ContactDetailResponse,
    ContactMessagesResponse,
    ContactMessageRequest,
    MyDoctorsResponse,
} from '@/types/contact';

const URL_PREFIX = '/v1/contact';

export const useContactStore = defineStore('contact', () => {
    async function sendContact(payload: SendContactRequest) {
        return await $backend.post<SendContactResponse>(
            `${URL_PREFIX}/send`,
            payload
        );
    }
    async function listPatients(doctorId: string) {
        const res = await $backend.get<ListPatientsResponse>(
            `${URL_PREFIX}/patients`,
            { params: { doctor_id: doctorId } }
        );
        return res.data;
    }
    async function getContactDetail(contactId: string) {
        const res = await $backend.get<ContactDetailResponse>(
            `${URL_PREFIX}/detail`,
            { params: { contact_id: contactId } }
        );
        return res.data;
    }
    async function getMessages(contactId: string) {
        const res = await $backend.get<ContactMessagesResponse>(
            `${URL_PREFIX}/messages`,
            { params: { contact_id: contactId } }
        );
        return res.data;
    }
    async function sendMessage(payload: ContactMessageRequest) {
        return await $backend.post(`${URL_PREFIX}/message`, payload);
    }
    async function listMyDoctors(patientId: string) {
        const res = await $backend.get<MyDoctorsResponse>(
            `${URL_PREFIX}/my-doctors`,
            { params: { patient_id: patientId } }
        );
        return res.data;
    }
    return {
        sendContact,
        listPatients,
        getContactDetail,
        getMessages,
        sendMessage,
        listMyDoctors,
    };
});
