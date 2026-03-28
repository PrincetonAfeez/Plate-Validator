import re  # Library for Regular Expression matching to verify plate formats
import json  # Library for parsing the external JSON pattern database
import sys  # Library for system-level operations like safe exiting
from rich.console import Console  # Rich library tool for professional terminal output
from rich.panel import Panel  # Rich component for displaying info in bordered boxes
from rich.table import Table  # Rich component for rendering structured data tables

console = Console()  # Initializing the global Rich console instance

class PatternRegistry:
    """Handles the retrieval of regional plate standards from external data."""
    def __init__(self, filepath="data/patterns.json"):
        """Initializes the registry by loading patterns from a JSON file."""
        try:
            with open(filepath, "r") as f:  # Attempting to open the pattern database
                self.patterns = json.load(f)  # Parsing JSON data into a dictionary
        except FileNotFoundError:  # Error handling if the data file is missing
            self.patterns = {}  # Initializing as empty to avoid downstream crashes

    def get_format(self, region_code):
        """Returns the format dictionary for a specific state code (e.g., 'CA')."""
        return self.patterns.get(region_code.upper())  # Returning data for the uppercase code

class SecurityValidator:
    """Provides a safety layer to filter out offensive or restricted content."""
    def __init__(self):
        """Initializes the security layer with a restricted word list."""
        self.blacklist = ["BAD", "HELL", "UGLY", "CRAP", "BUM"]  # Internal safety list

    def is_appropriate(self, plate_text):
        """Scans the normalized plate text for restricted substrings."""
        normalized = plate_text.upper().replace(" ", "")  # Ensuring standard format for check
        for word in self.blacklist:  # Iterating through each blocked word
            if word in normalized:  # If a restricted word is found within the plate
                return False, word  # Rejecting the plate and returning the flagged word
        return True, None  # Passing the plate as safe

class ValidatorEngine:
    """The logic engine responsible for alphanumeric pattern matching."""
    def validate(self, plate_text, region_data):
        """Compares user input against the region's specific RegEx pattern."""
        pattern = region_data['pattern']  # Extracting the RegEx string
        # Cleaning the input for the engine: uppercase and strip non-alphanumerics
        clean_plate = re.sub(r'[^A-Z0-9]', '', plate_text.upper())
        
        if re.match(pattern, clean_plate):  # Performing the RegEx match
            return True, clean_plate  # Return success and the cleaned string
        return False, clean_plate  # Return failure and the cleaned string

    def get_failure_reason(self, plate, region_data):
        """Feature 4: Analyzes the string to explain exactly why validation failed."""
        pattern = region_data['pattern']
        if len(plate) != len(region_data['example']):
            return f"Length mismatch: Expected {len(region_data['example'])} characters."
        
        # Simple character-by-character analysis
        for i, char in enumerate(plate):
            # This is a simplified architect's logic for failure feedback
            if not re.match(pattern[i+1] if i+1 < len(pattern) else pattern, char):
                return f"Character '{char}' at position {i+1} does not match regional format."
        return "Unknown format error."

class PlateValidatorApp:
    """The System Orchestrator connecting UI, Data, Logic, and Security."""
    def __init__(self):
        """Bootstraps the application components."""
        self.registry = PatternRegistry()  # Loading the data registry
        self.engine = ValidatorEngine()  # Initializing the validation logic
        self.security = SecurityValidator()  # Initializing the security layer

    def display_menu(self):
        """Renders a formatted table of all 50 supported US States."""
        table = Table(title="📍 Region Registry", show_header=True, header_style="bold magenta")
        table.add_column("Code", style="cyan", justify="center")  # State abbreviations
        table.add_column("State Name", style="white")  # Full state names

        for code, info in sorted(self.registry.patterns.items()):  # Alphabetical iteration
            table.add_row(code, info['name'])  # Adding each state to the table
        
        console.print(table)  # Outputting the table to the console

    def display_result(self, is_valid, is_safe, cleaned, region_name, example, blocked=None):
        """Renders the final architectural report based on validation results."""
        if not is_safe:  # Content filter failure takes priority
            console.print(Panel(f"[bold red]REJECTED:[/bold red] '{cleaned}' contains restricted word: [yellow]{blocked}[/yellow]", title="Security Alert"))
        elif is_valid:  # Success state
            console.print(Panel(f"[bold green]VALID:[/bold green] {cleaned}\n[dim]Matches {region_name} standard format.[/dim]", border_style="green"))
        else:  # Format mismatch state
            console.print(Panel(f"[bold red]INVALID:[/bold red] {cleaned}\n[yellow]Expected Format:[/yellow] {example}", title=f"Format Error: {region_name}"))

    def run(self):
        """Main operational loop for the application."""
        console.print("\n[bold cyan]🏎️  License Plate Validator v1.2[/bold cyan]")
        console.print("[dim]Type 'L' for State List | 'Q' to Quit[/dim]")
        
        # Capture initial command or region code
        choice = input("\nEnter State Code: ").strip().upper()
        
        if choice == 'Q': sys.exit()  # Exit command
        if choice == 'L':  # List command
            self.display_menu()
            return  # Restart loop to allow input after viewing list
        
        region_data = self.registry.get_format(choice)  # Attempting to fetch region data
        
        if not region_data:  # Handling invalid state codes
            console.print("[bold red]Error:[/bold red] State code not found in registry.")
            return

        # Input phase for the actual license plate
        plate_input = input(f"Enter {region_data['name']} Plate: ").strip()
        
        # Processing phase: Running security and validation engines
        is_valid, cleaned = self.engine.validate(plate_input, region_data)
        is_safe, blocked_word = self.security.is_appropriate(cleaned)

        # Output phase: Rendering the result
        self.display_result(is_valid, is_safe, cleaned, region_data['name'], region_data['example'], blocked_word)

if __name__ == "__main__":
    app = PlateValidatorApp()  # Instantiating the app
    while True:  # Commencing the persistent operational loop
        app.run()