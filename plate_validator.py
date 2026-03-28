import re  # Library for Regular Expression matching
import json  # Library for loading regional patterns from JSON
import sys  # Library for system-level operations
from rich.console import Console  # UI Library for professional output
from rich.panel import Panel  # UI component for bordered boxes
from rich.table import Table  # UI component for displaying the state menu

console = Console() # Initialize the console

class PatternRegistry:
    """Handles loading and retrieving plate formats from external JSON data."""
    def __init__(self, filepath="data/patterns.json"):
        try:
            with open(filepath, "r") as f:
                self.patterns = json.load(f)
        except FileNotFoundError:
            self.patterns = {}

    def get_format(self, region_code):
        """Retrieves the specific dictionary for a given region code."""
        return self.patterns.get(region_code.upper())
        
class ValidatorEngine:
    """The logic engine that performs the RegEx validation."""
    def validate(self, plate_text, region_data):
        """Matches the input against the stored RegEx pattern."""
        pattern = region_data['pattern']
        # Clean the input: uppercase and remove spaces/dashes
        clean_plate = plate_text.replace(" ", "").replace("-", "").upper()
        
        if re.match(pattern, clean_plate):
            return True, clean_plate
        return False, clean_plate

class PlateValidatorApp:
    """The Orchestrator that connects the UI, Registry, and Engine."""
    def __init__(self):
        self.registry = PatternRegistry()
        self.engine = ValidatorEngine()

    def run(self):
        console.print("[bold cyan]🏎️  License Plate Validator[/bold cyan]")
        region = "US_CA" # Defaulting to CA for Step 1
        region_data = self.registry.get_format(region)
        
        safe, word = self.security.is_appropriate(cleaned)
        if not safe:
            console.print(f"[bold red]REJECTED:[/bold red] Contains restricted word '{word}'")

        plate_input = input(f"\nEnter {region_data['region_name']} Plate (or 'q' to quit): ")
        if plate_input.lower() == 'q': sys.exit()

        is_valid, cleaned = self.engine.validate(plate_input, region_data)

        if is_valid:
            console.print(Panel(f"[bold green]VALID:[/bold green] {cleaned}\nMatches: {region_data['description']}", border_style="green"))
        else:
            console.print(Panel(f"[bold red]INVALID:[/bold red] {cleaned}\nExpected: {region_data['example']}", border_style="red"))

class SecurityValidator:
    """Handles content filtering and safety checks for license plates."""
    def __init__(self):
        # A small sample blacklist; in a real system, this would be an external file
        self.blacklist = ["BAD", "HELL", "UGLY"] 

    def is_appropriate(self, plate_text):
        """Checks if the plate contains any blacklisted offensive substrings."""
        for word in self.blacklist:
            if word in plate_text.upper():
                return False, word
        return True, None

if __name__ == "__main__":
    app = PlateValidatorApp()
    while True:
        app.run()
