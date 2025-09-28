// Legacy API for creating a chat session from a medical record submission.
// Updated to avoid coupling with a Pinia store.

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
): Promise<{ message: string; session_id: string }> {
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
        console.log('Medical record submitted successfully.');
        // Return session id to the caller instead of mutating a store here.
        return data;
    } catch (error) {
        console.error('Error submitting medical record:', error);
        throw error;
    }
}
