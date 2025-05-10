from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class MedicalRecord(BaseModel):
    class PatientInformation(BaseModel):
        full_name: str = Field(..., description="Full name of the patient.")
        birthday: date = Field(..., description="Birthday of the patient.")
        gender: str = Field(..., description="Gender of the patient.")
        occupation: str = Field(..., description="Occupation of the patient.")
        nationality: str = Field(..., description="Nationality of the patient.")
        address: str = Field(..., description="Address of patient")
    
    class MedicalHistory(BaseModel):
        chief_complaint: str = Field(..., description="Main reason for the patient's visit.")
        medical_history: str = Field(..., description="Description of symptom progression.")
        past_medical_history: str = Field(..., description="Previous illnesses and medical conditions.")
        current_medications: str = Field(default_factory=list, description="medications the patient is currently taking.")
        allergies: str = Field(default_factory=list, description="allergies the patient has.")
        family_medical_history: str = Field(..., description="Medical conditions present in the patient's family.")
    
    class SocialInformation(BaseModel):
        alcohol_consumption: Optional[str] = Field(None, description="Does the patient consume alcohol? If so, how frequently and how much?")
        smoking_habit: Optional[str] = Field(None, description="Does the patient smoke? If so, how many cigarettes per day and for how long?")
        living_situation: Optional[str] = Field(None, description="Does the patient live alone or with others?")
        daily_activity_independence: Optional[str] = Field(None, description="Can the patient independently perform daily activities, or do they require assistance?")
        recent_travel_history: Optional[str] = Field(None, description="Has the patient traveled internationally recently?")
    
    class ObstetricGynecologicalHistory(BaseModel):
        menstruation_status: Optional[str] = Field(None, description="Is the patient currently menstruating, or has menopause occurred?")
        menstrual_cycle: Optional[str] = Field(None, description="Are the patient’s menstrual cycles regular or irregular?")
        recent_sexual_activity: Optional[bool] = Field(None, description="Has the patient had sexual activity recently?")
    
    patient_info: PatientInformation = Field(..., description="Basic patient information including name, age, gender, and occupation.")
    medical_history: MedicalHistory = Field(..., description="Medical details including symptoms, past medical conditions, and medications.")
    social_information: SocialInformation = Field(..., description="Social history including lifestyle habits and recent travel history.")
    obstetric_gynecological_history: Optional[ObstetricGynecologicalHistory] = Field(None, description="Relevant history for female patients regarding menstruation and reproductive health.")

