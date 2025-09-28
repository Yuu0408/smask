export interface User {
    id: string;
    currentRecordId: string;
    username?: string;
    is_active?: boolean;
    role?: 'patient' | 'doctor';
}
