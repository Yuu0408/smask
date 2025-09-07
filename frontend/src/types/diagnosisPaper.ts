export interface PredictedDisease {
    name: string; // The name of the diagnosed or predicted disease
    supporting_evidence: string[]; // List of symptoms and diagnostic results supporting the diagnosis
    differentiating_factor?: string; // Key factor that differentiates this disease from others
    search_keywords: string[]; // List of questions to ask internet to confirm / reconsider the predicted disease
}

export interface Diagnosis {
    most_likely?: PredictedDisease; // Most strongly supported condition
    possible_diagnoses: PredictedDisease[]; // Up to 6 other plausible diagnoses
    rule_out: PredictedDisease[]; // Dangerous/serious conditions that must be ruled out
}

export interface FurtherTest {
    name: string; // Name of the test
    purpose: string; // Why the test is needed
    related_condition: string[]; // Conditions/symptoms the test addresses
    urgency?: string; // Urgency level: immediate, urgent, routine, etc.
}

export interface DiagnosisPaper {
    reasoning_process: string; // The reasoning process behind the diagnosis
    diagnosis: Diagnosis; // Categorized potential conditions
    further_test: FurtherTest[]; // Recommended further tests
}
