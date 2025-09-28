export interface MedicalRecordData {
    patient_info: {
        full_name: string;
        birthday: string;
        gender: string;
        occupation: string;
        nationality: string;
        address: string;
    };

    medical_history: {
        chief_complaint: string;
        medical_history: string;
        past_medical_history: string;
        current_medications: string;
        allergies: string;
        family_medical_history: string;
    };

    social_information: {
        alcohol_consumption: string;
        smoking_habit: string;
        latest_alcohol_smoking_intake?: string;
        living_situation: string;
        daily_activity_independence: string;
        recent_travel_history: string;
    };

    obstetric_gynecological_history?: {
        menstruation_status: string | '';
        menstrual_cycle: string | '';
        recent_sexual_activity: boolean | null;
    };
}

// Request body expected by the backend
export interface AddMedicalRecordRequest {
    user_id: string; // UUID as string
    data: MedicalRecordData; // your full form data
}

// Minimal response per backend (you can expand later)
export interface AddMedicalRecordResponse {
    message: boolean;
    record_id: string;
    created_at: string;
    updated_at: string;
}

export interface getCurrentRecordRequest {
    user_id: string;
    record_id: string;
}

export interface GetCurrentRecordResponse {
    user_id: string;
    record_id: string;
    data: MedicalRecordData;
    created_at: string;
    updated_at: string;
}
