from dotenv import load_dotenv

load_dotenv()

from pprint import pprint
from graph.chains.conversation_chain import conversation_chain
from graph.chains.extraction_chain import extraction_chain
from graph.chains.diagnosis_chain import diagnosis_chain


def test_extraction_chain() -> None:
    medical_record = """
    {
  "medical_record": {
    "patient_info": {
      "full_name": "Yuu",
      "year_of_birth": 2003,
      "age": 21,
      "gender": "Male",
      "occupation": "University student",
      "nationality": "Unknown"
    },
    "medical_history": {
      "chief_complaint": "Itchy throat and small cough for 3 weeks.",
      "medical_history": "Symptoms started 5 days after a trip to Vietnam. Initially slight itchy throat, then painful throat, watery nose, and mucus in throat. Symptoms improved with penicillin, but itchy throat persists.",
      "past_medical_history": "No past medical history or chronic conditions.",
      "current_medications": [
        "Strepsils Cool"
      ],
      "allergies": [],
      "family_medical_history": "Family has no known medical conditions."
    },
    "social_information": {
      "alcohol_consumption": "Does not consume alcohol.",
      "smoking_habit": "Does not smoke, but exposed to secondhand smoke from neighbor.",
      "living_situation": "Lives with father.",
      "daily_activity_independence": "Performs daily activities independently.",
      "recent_travel_history": "Traveled to Vietnam for 20 days."
    }
  }
}    
"""

    generation = diagnosis_chain.invoke({"medical_record": medical_record}) 

    pprint(generation)
