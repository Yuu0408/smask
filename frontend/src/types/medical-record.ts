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
        alcohol_consumption: string; // never | occasionally | frequently | daily
        alcohol_details?: {
            per_month_times?: number; // for occasionally
            per_week_times?: number; // for frequently
            per_time_ml?: number;     // for occasionally
            avg_per_day_ml?: number;  // for frequently or daily
            drink_type?: string;
        };
        smoking_habit: string; // never | used_to_quit | current
        smoking_details?: {
            start_age?: number;
            end_age?: number; // only for used_to_quit
            cigarettes_per_day?: number;
            years_smoked?: number; // computed client-side if possible
        };
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
