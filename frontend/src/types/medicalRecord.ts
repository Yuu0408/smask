export interface MedicalRecord {
  patient_info: {
    full_name: string;
    birthday: string; // ISO format from Python (e.g. "2002-10-31")
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
    alcohol_consumption?: string;
    smoking_habit?: string;
    living_situation?: string;
    daily_activity_independence?: string;
    recent_travel_history?: string;
  };
  obstetric_gynecological_history?: {
    menstruation_status?: string;
    menstrual_cycle?: string;
    recent_sexual_activity?: boolean;
  };
}
