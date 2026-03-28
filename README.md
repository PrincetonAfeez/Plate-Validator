# 🏎️ Plate-Validator (v1.3)

A high-precision, modular license plate validation system designed for global scalability. This tool uses Advanced Regular Expressions and a "Zero-Trust" security layer to verify vehicle identifiers across 50+ regions.

## 🏛️ System Architecture

The application is built on the **Provider Pattern**, ensuring that logic and data remain decoupled for easy maintenance:

- **`PatternRegistry` (Data Provider):** Dynamically loads regional formats from an external `patterns.json` database.
- **`ValidatorEngine` (Logic Provider):** Executes RegEx matching and provides "Deep Explainer" diagnostics for failed inputs.
- **`SecurityValidator` (Middleware):** A robust safety layer that prevents filter bypass via automated **Leetspeak Normalization**.
- **`PlateValidatorApp` (Orchestrator):** Manages the state machine, user interaction, and persistent logging.

---

## 🚀 Key Features

### 1. 🌍 50-State & International Registry
Full support for all **50 US States**, plus international standards for the **UK** and **France**. The system is built to be "Region-Agnostic"—adding a new country requires zero code changes, only a JSON entry.

### 2. 🛡️ Leetspeak-Aware Security
The `SecurityValidator` doesn't just check for "BAD" words; it uses a translation map to catch obfuscated entries. 
* *Example:* Inputting `B4D-PL4T3` is automatically normalized to `BADPLATE` before passing through the blacklist.

### 3. 🔍 Deep Regex Explainer
When validation fails, the engine analyzes the string to provide human-readable feedback, distinguishing between **Length Mismatches** and **Pattern/Character Mismatches**.

### 4. 📊 Persistent Audit Trail
Every validation attempt is logged to `data/audit_log.json`. Users can view a formatted history of the last 10 attempts directly in the CLI using the `H` (History) command.

### 5. 🎨 Optimized Rectangular UX
Leveraging the `Rich` library, the UI features a vertical, rectangular column layout for region selection, making it easy to navigate 50+ options in a standard terminal window.

---

## 🛠️ Usage

1. **View Regions:** Type `L` to see the rectangular grid of supported states.
2. **Verify Plate:** Enter a State Code (e.g., `TX`), then input the plate number.
3. **Check History:** Type `H` to see a table of recent passes and fails.


License Plate Validator Tutorial

I want to build these 3 CLI apps to learn  Data Integrity & Validation (The "Guard") with a focus on RegEx, Error Handling, and Data Cleansing

License Plate Validator: Use RegEx to validate CA license plate patterns.

Goal: Deep-dive into specific pattern matching (State Standards).
1: Validate standard CA plates: `1ABC234` (1 Digit, 3 Letters, 3 Digits).
2: Validate personalized/commercial plates: 2–7 characters (Letters/Numbers only).
3: Reject any string containing prohibited symbols or lowercase letters.
4: Return a Boolean (`True/False`) and a specific error message if the pattern fails.

This architecture follows the Provider Pattern: One class stores the "source of truth" (the patterns), and the other performs the execution.

Step 1: Create the Pattern Registry
Store the California (CA) patterns in a JSON file. CA plates typically follow the 1ABC234 format for autos -> data/patterns.json

Step 2: Build the PlateValidator Skeleton and implement the logic

Step 3: Expand the Registry (data/patterns.json)
Add Texas and Florida to demonstrate how the system handles different alphanumeric structures.

Step 4: Implement "Strict Mode" (Offensive Filter)
Add a SecurityValidator class to plate_validator.py to ensure plates don't contain "not-safe-for-work" (NSFW) strings.

step 5: Expand the Registry (data/patterns.json) for all 50 states

Step 6: Expand the Registry & European support (data/patterns.json) to also include the UK and France

Step 7: The "Deep Regex" Explainer
Add a helper method to the ValidatorEngine to analyze where the user's input deviated from the required pattern.

Step 8: Vertical Rectangular UI & Logging
Refactor the display_menu to use a vertical rectangular layout (Columns) and add the audit logging logic.

Step 9: Add a display_history method and update the input logic to trigger it when the user types 'H'.

Step 10: Fil Content Filter Check
To ensure the SecurityValidator is catching "BAD" words

Step 11: Adding "leetspeak" normalization is a high-level System Architect move. It ensures that the SecurityValidator isn't fooled by simple character substitutions (like B4D instead of BAD).

The app is now remarkably robust
1. Global Formats -> 50-State + International Registry (JSON Data)
2. Security Middleware (Content Filtering)
3. Validation Engine (RegEx)
4. Deep Explainer (Failure Logic)
5. Audit Logging (Persistence)
6. Interactive UI (Rich Tables/Columns)
7. Advanced Filtering (Leetspeak Normalization)

Step 12: The Testing Suite (pytest)
Before adding new logic, ensure not to  break the old logic. This is called Regression Testing.