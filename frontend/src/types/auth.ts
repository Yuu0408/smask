export interface UserMetadata {
    [key: string]: string | number | boolean;
}

export interface loginRequest {
    username: string;
    password: string;
}

export interface registerRequest {
    username: string;
    password: string;
    role: 'patient' | 'doctor';
    metadata?: UserMetadata;
}
