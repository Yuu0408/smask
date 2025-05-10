from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time

class Displayer:
    def __init__(self):
        self.console = Console()
    
    def display_diagnosis_response(self, diagnosis_response):
        self.console.print("\n[bold cyan]--- DIAGNOSIS RESULT ---[/bold cyan]")
        
        # Reasoning Process
        self.console.print("\n[bold]Reasoning Process:[/bold]", style="bold yellow")
        self.console.print(diagnosis_response.reasoning_process, style="italic white")
        
        # Diagnosis Table
        diagnosis = diagnosis_response.diagnosis
        table = Table(title="Diagnosis Summary", show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Type", style="bold cyan", justify="center")
        table.add_column("Name", style="bold yellow")
        table.add_column("Supporting Evidence", style="bold green")
        table.add_column("Differentiating Factor", style="bold red")
        
        def add_disease_row(category, disease):
            evidence = "\n".join(disease.supporting_evidence)
            diff_factor = disease.differentiating_factor if disease.differentiating_factor else "N/A"
            table.add_row(category, disease.name, evidence, diff_factor)
        
        if diagnosis.most_likely:
            add_disease_row("Most Likely", diagnosis.most_likely)
        
        for possible in diagnosis.possible_diagnoses:
            add_disease_row("Possible", possible)
        
        for rule_out in diagnosis.rule_out:
            add_disease_row("Rule Out", rule_out)
        
        self.console.print(table)
        
        # Further Tests
        if diagnosis_response.further_test:
            self.console.print("\n[bold]Further Tests Recommended:[/bold]", style="bold blue")
            for test in diagnosis_response.further_test:
                self.console.print(f"- {test}", style="italic white")
        
        # Further Questions
        # if diagnosis_response.further_question_to_ask:
        #     self.console.print("\n[bold]Further Questions to Ask the Patient:[/bold]", style="bold purple")
        #     for question in diagnosis_response.further_question_to_ask:
        #         self.console.print(f"- {question}", style="italic white")
    
    def display_extraction_response(self, response):
        self.console.print("\n[bold cyan]--- MEDICAL RECORD---[/bold cyan]")
        
        # Patient Information
        patient_info = response.patient_info
        self.console.print("\n[bold]Patient Information:[/bold]", style="bold yellow")
        self.console.print(f"Full Name: {patient_info.full_name}")
        self.console.print(f"Year of Birth: {patient_info.year_of_birth}")
        self.console.print(f"Age: {patient_info.age}")
        self.console.print(f"Gender: {patient_info.gender}")
        self.console.print(f"Occupation: {patient_info.occupation}")
        self.console.print(f"Nationality: {patient_info.nationality}")
        
        # Medical History Table
        medical_history = response.medical_history
        table = Table(title="Medical History", show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Category", style="bold cyan", justify="center")
        table.add_column("Details", style="bold white")
        
        table.add_row("Chief Complaint", medical_history.chief_complaint)
        table.add_row("History", medical_history.medical_history)
        table.add_row("Past Medical History", medical_history.past_medical_history)
        table.add_row("Current Medications", ", ".join(medical_history.current_medications) if medical_history.current_medications else "None")
        table.add_row("Allergies", ", ".join(medical_history.allergies) if medical_history.allergies else "None")
        table.add_row("Family Medical History", medical_history.family_medical_history)
        
        self.console.print(table)
        
        # Social Information Table
        social_info = response.social_information
        social_table = Table(title="Social Information", show_header=True, header_style="bold magenta", show_lines=True)
        social_table.add_column("Category", style="bold cyan", justify="center")
        social_table.add_column("Details", style="bold white")
        
        social_table.add_row("Alcohol Consumption", social_info.alcohol_consumption or "N/A")
        social_table.add_row("Smoking Habit", social_info.smoking_habit or "N/A")
        social_table.add_row("Living Situation", social_info.living_situation or "N/A")
        social_table.add_row("Daily Activity Independence", social_info.daily_activity_independence or "N/A")
        social_table.add_row("Recent Travel History", social_info.recent_travel_history or "N/A")
        
        self.console.print(social_table)
        
        # Obstetric & Gynecological History (if available)
        if response.obstetric_gynecological_history:
            obgyn = response.obstetric_gynecological_history
            self.console.print("\n[bold]Obstetric & Gynecological History:[/bold]", style="bold yellow")
            self.console.print(f"Menstruation Status: {obgyn.menstruation_status or 'N/A'}")
            self.console.print(f"Menstrual Cycle: {obgyn.menstrual_cycle or 'N/A'}")
            self.console.print(f"Recent Sexual Activity: {'Yes' if obgyn.recent_sexual_activity else 'No'}")

    def display_progress_bar(self, task_description: str):
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(task_description, total=100)
            
            while not progress.finished:
                progress.update(task, advance=10)
                time.sleep(0.3)  # Simulate progress delay