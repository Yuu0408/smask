export interface SendContactRequest {
    user_id: string;
    record_id: string;
    include_conversation: boolean;
    address: string;
    facility: string;
}
export interface SendContactResponse {
    ok: boolean;
    contact_id: string;
}

export interface PatientCard {
    contact_id: string;
    patient_user_id: string;
    full_name: string;
    age: number;
    address: string;
}
export interface ListPatientsResponse {
    patients: PatientCard[];
}

export interface ContactDetailResponse {
    contact_id: string;
    patient_user_id: string;
    record_id: string;
    address: string;
    facility: string;
    medical_record: any;
    diagnosis?: any;
    reasoning_process?: string;
    further_test?: {
        name: string;
        purpose: string;
        related_condition: string[];
        urgency?: string;
    }[];
    todos: { text: string; is_check: boolean }[];
    conversation?:
        | { id: string; role: string; content: string; created_at: string }[]
        | null;
}

export interface ContactMessageRequest {
    contact_id: string;
    sender_id: string;
    content: string;
}
export interface ContactMessage {
    id: string;
    role: 'doctor' | 'patient';
    content: string;
    created_at: string;
}
export interface ContactMessagesResponse {
    messages: ContactMessage[];
}
export interface MyDoctor {
    doctor_id: string;
    contact_id: string;
    username: string;
}
export interface MyDoctorsResponse {
    doctors: MyDoctor[];
}
