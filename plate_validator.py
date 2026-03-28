import re # Library for Regular Expression matching
import json # Library for loading regional patterns
import sys # Library for system operations
from rich.console import Console # UI Library
from rich.panel import Panel # UI Layout

console = Console() # Initialize the console

class PatternRegistry:
    """Handles loading and retrieving plate formats from external data."""
    def __init__(self, filepath="data/patterns.json"):
        try:
            with open(filepath, "r") as f:
                self.patterns = json.load(f) # Load JSON into dictionary
        except FileNotFoundError:
            self.patterns = {} # Fallback to empty if file is missing

    def get_format(self, region_code):
        """Returns the specific pattern data for a region."""
        return self.patterns.get(region_code)