import re  # Library for Regular Expression matching to verify plate formats
import json  # Library for parsing the external JSON pattern database
import sys  # Library for system-level operations like safe exiting
import os  # Library for file path and directory management
import csv  # Library for reading and writing CSV files for bulk processing
from rich.console import Console  # Rich library tool for professional terminal output
from rich.panel import Panel  # Rich component for displaying info in bordered boxes
from rich.table import Table  # Rich component for rendering structured data tables
from rich.columns import Columns  # Rich tool for the rectangular vertical menu layout

console = Console()  # Initializing the global Rich console instance for UI rendering

class PatternRegistry:
    """Handles the retrieval of regional plate standards from external data."""
    def __init__(self, filepath="data/patterns.json"):
        """Initializes the registry by loading patterns from a JSON file."""
        try: # Start safety block for file operations
            with open(filepath, "r") as f:  # Attempting to open the pattern database
                raw = json.load(f)
                if isinstance(raw, dict):
                    self.patterns = {
                        k: v
                        for k, v in raw.items()
                        if isinstance(k, str) and not k.startswith("_")
                    }
                else:
                    self.patterns = {}
        except (FileNotFoundError, json.JSONDecodeError):  # Missing or invalid JSON
            self.patterns = {}  # Initializing as empty to avoid downstream crashes

    def get_format(self, region_code):
        """Returns the format dictionary for a specific state code (e.g., 'CA')."""
        return self.patterns.get(region_code.upper())  # Returning data for the uppercase code

class SecurityValidator:
    """Handles content filtering and leetspeak-aware safety checks."""
    def __init__(self):
        """Initializes the security layer with a restricted word list and leet map."""
        self.blacklist = ["BAD", "HELL", "UGLY", "CRAP", "BUM", "SHIT", "FUCK"] # Blocked words
        self._short_word_allowed_parts = {
            "BUM": frozenset({"BUMBLE"}),
        }
        self.leet_map = { # Mapping symbols/numbers to letters to prevent filter bypass
            '4': 'A', '@': 'A', '8': 'B', '3': 'E', '1': 'I', 
            '!': 'I', '|': 'I', '0': 'O', '5': 'S', '$': 'S', '7': 'T', '+': 'T'
        }

    def normalize_leet(self, text):
        """Translates leetspeak characters back to standard alphabet letters."""
        translated = text.upper() # Work with uppercase for consistency
        for char, replacement in self.leet_map.items(): # Loop through the leet dictionary
            translated = translated.replace(char, replacement) # Swap symbol for letter
        return translated # Return the normalized string

    def is_appropriate(self, plate_text):
        """Scans leet-normalized text: long words use letter-boundary rules; short words use substring plus a small allowlist."""
        normalized = self.normalize_leet(plate_text).replace(" ", "").replace("-", "")
        parts = [p for p in re.split(r"[0-9]+", normalized) if p]
        for part in parts:
            for word in self.blacklist:
                wl = len(word)
                if wl >= 4:
                    strict = re.compile(r"(?<![A-Z])" + re.escape(word) + r"(?![A-Z])")
                    if strict.search(part):
                        return False, word
                    if word not in part:
                        continue
                    if part == word:
                        return False, word
                    if part.startswith(word) and len(part) == wl + 1:
                        continue
                    return False, word
                else:
                    if word in part:
                        allowed = self._short_word_allowed_parts.get(word)
                        if allowed and part in allowed:
                            continue
                        return False, word
        return True, None

class ValidatorEngine:
    """The logic engine responsible for alphanumeric pattern matching and feedback."""
    def validate(self, plate_text, region_data):
        """Compares user input against the region's specific RegEx pattern."""
        pattern = region_data['pattern']  # Extracting the RegEx string from data
        clean_plate = re.sub(r'[^A-Z0-9]', '', plate_text.upper()) # Remove non-alphanumerics
        if re.fullmatch(pattern, clean_plate):
            return True, clean_plate
        return False, clean_plate

    @staticmethod
    def _char_kind(ch):
        if ch.isdigit():
            return "digit"
        if ch.isalpha():
            return "letter"
        return "character"

    def get_failure_reason(self, plate, region_data):
        """Explains failure: length, first class/character mismatch vs example, or pattern-only mismatch."""
        example = region_data['example']
        clean_example = re.sub(r"[^A-Z0-9]", "", example.upper())
        desc = region_data.get('desc', "the required format")
        pattern = region_data['pattern']
        if len(plate) != len(clean_example):
            return f"Length mismatch: Expected {len(clean_example)} chars, got {len(plate)}."
        for i, (pc, ec) in enumerate(zip(plate, clean_example)):
            if self._char_kind(pc) != self._char_kind(ec):
                return (
                    f"Position {i + 1}: expected a {self._char_kind(ec)} (like '{ec}'), "
                    f"found '{pc}'."
                )
        for i, (pc, ec) in enumerate(zip(plate, clean_example)):
            if pc != ec:
                return f"Position {i + 1}: expected '{ec}', found '{pc}'."
        if not re.fullmatch(pattern, plate):
            return (
                f"Pattern mismatch: same length as example but does not match the rule ({desc})."
            )
        return f"Pattern mismatch: Format must be {desc}."

    def suggest_correction(self, plate, region_data):
        """Suggests common alphanumeric swaps (like 0 for O) if validation fails."""
        swaps = {'0': 'O', 'O': '0', '1': 'I', 'I': '1', '5': 'S', 'S': '5'} # Common typos
        for i, char in enumerate(plate): # Iterate through each character in the plate
            if char in swaps: # Check if the character is a common typo
                candidate = list(plate) # Convert string to list for mutability
                candidate[i] = swaps[char] # Swap the character
                if re.fullmatch(region_data['pattern'], "".join(candidate)):
                    return "".join(candidate) # Return the suggested fix
        return None # Return None if no simple fix is found

class AuditManager:
    """Handles persistence: logging attempts and reading history."""
    def __init__(self, log_path="data/audit_log.json"):
        """Sets the path for the JSON audit file."""
        self.log_path = log_path # Store the file path

    def log_attempt(self, entry):
        """Persists a single validation attempt to the JSON audit log."""
        history = self.get_all_logs() # Fetch existing logs
        history.append(entry) # Add new entry to the list
        if not os.path.exists("data"): os.makedirs("data") # Ensure data folder exists
        with open(self.log_path, "w") as f: # Open file for writing
            json.dump(history[-10:], f, indent=4) # Save only the last 10 entries

    def get_all_logs(self):
        """Reads all logs from the JSON file safely."""
        if not os.path.exists(self.log_path): return [] # Return empty list if no file
        with open(self.log_path, "r") as f:
            try:
                return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []

class UIManager:
    """Handles all terminal-based visual presentation logic."""
    @staticmethod
    def display_menu(patterns):
        """Renders the regions in a rectangular vertical column layout."""
        panels = [Panel(f"[bold cyan]{c}[/]\n[dim]{info['name']}[/]", expand=False) for c, info in sorted(patterns.items())]
        console.print(Columns(panels, equal=True, expand=True)) # Print grid of states

    @staticmethod
    def display_history(logs):
        """Renders the audit history in a stylized Rich Table."""
        if not logs: return console.print("[yellow]No history found.[/]") # Handle empty logs
        table = Table(title="📜 Recent Audits", header_style="bold yellow") # Initialize table
        table.add_column("Region"); table.add_column("Plate"); table.add_column("Status") # Columns
        for e in logs: # Loop through logs
            stat = "[green]PASS[/]" if e['valid'] and e['safe'] else "[red]FAIL[/]" # Determine status
            table.add_row(e['region'], e['plate'], stat) # Add row to table
        console.print(table) # Render the table

class PlateValidatorApp:
    """The Controller: Orchestrates logic between Data, UI, and Engine."""
    def __init__(self):
        """Initializes all sub-systems of the application."""
        self.registry = PatternRegistry() # Initialize data registry
        self.engine = ValidatorEngine() # Initialize logic engine
        self.security = SecurityValidator() # Initialize security layer
        self.audit = AuditManager() # Initialize persistence layer

    @staticmethod
    def _csv_cell(row, name):
        want = name.lower()
        for k, v in row.items():
            if k is not None and k.strip().lower() == want:
                return (v or "").strip()
        return ""

    def bulk_validate_csv(self, input_path, output_path="data/results.csv"):
        """Reads input CSV, validates rows, writes output_path. Returns (results, warning_messages)."""
        results = []
        warnings = []
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                warnings.append("CSV has no header row; nothing was processed.")
            else:
                lowered = {(h or "").strip().lower() for h in fieldnames if h is not None and str(h).strip()}
                for req in ("region", "plate"):
                    if req not in lowered:
                        warnings.append(
                            f"Missing required column '{req}'. Use headers 'region' and 'plate' (case-insensitive)."
                        )
                        break
                else:
                    rows = 0
                    for row in reader:
                        rows += 1
                        region = self._csv_cell(row, "region")
                        plate = self._csv_cell(row, "plate")
                        if not region:
                            results.append({"Region": "", "Plate": plate, "Status": "FAIL"})
                            continue
                        r_data = self.registry.get_format(region)
                        if not r_data:
                            results.append({"Region": region, "Plate": plate, "Status": "FAIL"})
                            continue
                        v, _ = self.engine.validate(plate, r_data)
                        s, _ = self.security.is_appropriate(plate)
                        results.append(
                            {"Region": region, "Plate": plate, "Status": "PASS" if v and s else "FAIL"}
                        )
                    if rows == 0:
                        warnings.append(
                            "No data rows after the header; results contain only the column header."
                        )
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(output_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=["Region", "Plate", "Status"])
            writer.writeheader()
            writer.writerows(results)
        return results, warnings

    def process_bulk(self):
        """Processes a CSV file of plates and exports results to results.csv."""
        path = input("Enter CSV path (e.g., data/input.csv): ").strip()
        if not os.path.exists(path):
            return console.print("[red]File not found.[/]")
        _, warnings = self.bulk_validate_csv(path)
        for w in warnings:
            console.print(f"[yellow]Warning:[/] {w}")
        console.print("[green]Bulk processing complete. Results saved to data/results.csv[/]")

    def run(self):
        """Executes the main application loop and handles user input."""
        console.print("\n[bold cyan]🏎️  Validator v1.5[/] [dim](L: List | H: History | B: Bulk | Q: Quit)[/]")
        choice = input("Select Option or State Code: ").strip().upper() # Get user choice
        if choice == 'Q': sys.exit() # Handle quit
        if choice == 'L': return UIManager.display_menu(self.registry.patterns) # Handle menu
        if choice == 'H': return UIManager.display_history(self.audit.get_all_logs()) # Handle history
        if choice == 'B': return self.process_bulk() # Handle bulk processing
        
        region = self.registry.get_format(choice) # Attempt to fetch regional data
        if not region: return console.print("[red]Invalid Region Code.[/]") # Handle unknown codes

        plate_in = input(f"Enter {region['name']} Plate: ").strip() # Get plate string
        valid, clean = self.engine.validate(plate_in, region) # Perform validation
        safe, word = self.security.is_appropriate(plate_in) # Perform security check
        
        self.audit.log_attempt({"region": choice, "plate": clean, "valid": valid, "safe": safe}) # Log results

        if not safe: # Display security failure
            console.print(Panel(f"[red]REJECTED:[/] Found restricted word: '{word}'", title="Security"))
        elif valid: # Display success
            console.print(Panel(f"[green]VALID:[/] {clean}", subtitle=region['name'], border_style="green"))
        else: # Display format failure with suggestions
            msg = self.engine.get_failure_reason(clean, region) # Get the "why"
            fix = self.engine.suggest_correction(clean, region) # Get the "fix"
            if fix: msg += f"\n[yellow]Did you mean:[/] {fix}?" # Append suggestion if found
            console.print(Panel(msg, title="Format Error", border_style="red")) # Render panel

if __name__ == "__main__":
    app = PlateValidatorApp() # Create the application instance
    while True: app.run() # Run the persistent execution loop