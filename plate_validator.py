import re  # Library for Regular Expression matching to verify plate formats
import json  # Library for parsing the external JSON pattern database
import sys  # Library for system-level operations like safe exiting
from rich.console import Console  # Rich library tool for professional terminal output
from rich.panel import Panel  # Rich component for displaying info in bordered boxes
from rich.table import Table  # Rich component for rendering structured data tables
import os  # Added for file path checks in logging
from rich.columns import Columns  # Added for rectangular vertical menu
import csv # Add to top of file

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
    """Handles content filtering and safety checks for license plates."""
    def __init__(self):
        """Initializes the security layer with a restricted word list."""
        # Standard restricted words
        self.blacklist = ["BAD", "HELL", "UGLY", "CRAP", "BUM", "SHIT", "FUCK"] 
        
        # Leetspeak mapping for normalization
        self.leet_map = {
            '4': 'A', '@': 'A',
            '8': 'B',
            '3': 'E',
            '1': 'I', '!': 'I', '|': 'I',
            '0': 'O',
            '5': 'S', '$': 'S',
            '7': 'T', '+': 'T'
        }

    def normalize_leet(self, text):
        """Translates leetspeak characters back to standard alphabet."""
        translated = text.upper()
        for char, replacement in self.leet_map.items():
            translated = translated.replace(char, replacement)
        return translated

    def is_appropriate(self, plate_text):
        """Scans the leet-normalized plate text for restricted substrings."""
        # First, normalize the plate to catch hidden words (e.g., B4D -> BAD)
        normalized = self.normalize_leet(plate_text).replace(" ", "").replace("-", "")
        
        for word in self.blacklist:
            if word in normalized:
                return False, word  # Returns False and the word that triggered the flag
        return True, None

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

    def suggest_correction(self, plate, region_data):
        """Feature 1: Suggests common alphanumeric swaps if validation fails."""
        # Common typos: 0 vs O, 1 vs I, 5 vs S
        swaps = {'0': 'O', 'O': '0', '1': 'I', 'I': '1', '5': 'S', 'S': '5'}
        for i, char in enumerate(plate):
            if char in swaps:
                candidate = list(plate)
                candidate[i] = swaps[char]
                if re.match(region_data['pattern'], "".join(candidate)):
                    return "".join(candidate)
        return None

class PlateValidatorApp:
    def __init__(self):
        self.registry = PatternRegistry()
        self.engine = ValidatorEngine()
        self.security = SecurityValidator()

    def display_menu(self):
        """Feature: Renders a vertical, rectangular menu of regions."""
        # Create a list of stylized panels for each state/country
        state_panels = [
            Panel(f"[bold cyan]{code}[/]\n[dim]{info['name']}[/]", expand=False, border_style="blue")
            for code, info in sorted(self.registry.patterns.items())
        ]
        # Display them in a rectangular column layout
        console.print(Columns(state_panels, equal=True, expand=True))

    def log_audit(self, entry):
        """Feature 6: Persists validation attempts to data/audit_log.json."""
        log_path = "data/audit_log.json"
        history = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                try: history = json.load(f)
                except: history = []
        
        history.append(entry)
        with open(log_path, "w") as f:
            json.dump(history[-10:], f, indent=4) # Keep last 10 for efficiency

    def display_history(self):
        """Feature 7: Reads and displays the audit log in a professional table."""
        log_path = "data/audit_log.json"
        
        if not os.path.exists(log_path):
            console.print("[yellow]No audit history found yet.[/yellow]")
            return

        with open(log_path, "r") as f:
            history = json.load(f)

        table = Table(title="📜 Recent Validation Audit", show_header=True, header_style="bold yellow")
        table.add_column("Region", justify="center", style="cyan")
        table.add_column("Plate", style="white")
        table.add_column("Status", justify="center")

        # Display the last 10 entries
        for entry in history[-10:]:
            status = "[green]PASS[/]" if entry['valid'] and entry['safe'] else "[red]FAIL[/]"
            table.add_row(entry['region'], entry['plate'], status)
        
        console.print(table)

    def run(self):
        """Updated loop to handle the History command."""
        console.print("\n[bold cyan]🏎️  License Plate Validator v1.2[/bold cyan]")
        console.print("[dim]Type 'L' List | 'H' History | 'Q' Quit[/dim]")
        
        choice = input("\nEnter State Code: ").strip().upper()
        
        if choice == 'Q': sys.exit()
        if choice == 'L':
            self.display_menu()
            return
        if choice == 'H': # <--- New History Trigger
            self.display_history()
            return
        
        region_data = self.registry.get_format(choice)
        
        if not region_data:
            console.print("[bold red]Error:[/bold red] State code not found.")
            return # <--- Execution stops here if the code is invalid

        plate_input = input(f"Enter {region_data['name']} Plate: ").strip()
        
        # --- Variables are defined ONLY here ---
        is_valid, cleaned = self.engine.validate(plate_input, region_data)
        
        # Security check now uses the leetspeak-aware normalization
        is_safe, blocked_word = self.security.is_appropriate(plate_input)

        # Logging and UI logic remains the same
        self.log_audit({"region": choice, "plate": cleaned, "valid": is_valid, "safe": is_safe})
    

        # Move the logging and display logic INSIDE this flow
        audit_data = {"plate": cleaned, "valid": is_valid, "region": choice, "safe": is_safe}
        self.log_audit(audit_data)

        if not is_safe:
            console.print(Panel(f"[bold red]REJECTED:[/bold red] Restricted word '{blocked_word}'", title="Security Alert"))
        elif is_valid:
            console.print(Panel(f"[bold green]VALID:[/bold green] {cleaned}", border_style="green"))
        else:
            reason = self.engine.get_failure_reason(cleaned, region_data)
            console.print(Panel(f"[bold red]INVALID:[/bold red] {cleaned}\n[yellow]Reason:[/yellow] {reason}", title="Format Error"))

    def process_bulk(self, file_path):
        """Feature 2: Processes a CSV of plates and exports results."""
        if not os.path.exists(file_path):
            console.print("[bold red]File not found.[/]")
            return

        with open(file_path, mode='r') as infile, open('data/results.csv', mode='w', newline='') as outfile:
            reader = csv.DictReader(infile) # Expects columns: 'region', 'plate'
            writer = csv.writer(outfile)
            writer.writerow(["Region", "Plate", "Status", "Safe"])

            for row in reader:
                region_data = self.registry.get_format(row['region'])
                is_valid, _ = self.engine.validate(row['plate'], region_data)
                is_safe, _ = self.security.is_appropriate(row['plate'])
                writer.writerow([row['region'], row['plate'], is_valid, is_safe])
        
        console.print("[bold green]Bulk processing complete. Results saved to data/results.csv[/]")

if __name__ == "__main__":
    app = PlateValidatorApp()  # Instantiating the app
    while True:  # Commencing the persistent operational loop
        app.run()