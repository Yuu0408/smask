export interface User {
    id: string;
    currentRecordId: string;
    username?: string;
    is_active?: boolean;
    role?: 'patient' | 'doctor';
    address?: string;
    facility?: string;
    metadata?: {
        address?: string;
        facility?: string;
        [key: string]: any;
    };
}
