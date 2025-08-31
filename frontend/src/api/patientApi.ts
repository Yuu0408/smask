import { useUserStore } from '@/stores/userStore';

export interface MedicalRecordRequest {
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
        living_situation: string;
        daily_activity_independence: string;
        recent_travel_history: string;
    };

    obstetric_gynecological_history?: {
        menstruation_status: string;
        menstrual_cycle: string;
        recent_sexual_activity: boolean | null;
    };
}

export async function submitPatientInfo(
    medicalRecord: MedicalRecordRequest
): Promise<void> {
    try {
        const API_BASE = import.meta.env.VITE_API_BASE;
        const response = await fetch(`${API_BASE}/patient_info`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(medicalRecord),
        });

        if (!response.ok) {
            throw new Error(`Failed to submit: ${response.statusText}`);
        }

        const data = await response.json();
        const sessionId = data.session_id;
        console.log('Medical record submitted successfully.');

        const userStore = useUserStore();
        userStore.setSessionId(sessionId);
    } catch (error) {
        console.error('Error submitting medical record:', error);
        throw error;
    }
}
