from pydantic import BaseModel

class PatientInformation(BaseModel):
    full_name: str
    year_of_birth: str
    age: str
    gender: str
    occupation: str
    nationality: str