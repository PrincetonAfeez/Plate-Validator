# 🏎️ License Plate Validator

A high-precision validation tool designed to verify vehicle license plates against regional formatting standards using Advanced Regular Expressions.

## 🛠️ Planned Features
- **Multi-Region Support:** Validation for US States, UK, and EU formats.
- **Pattern Matching:** Strict RegEx enforcement for alphanumeric sequences.
- **Real-time Feedback:** Instant reporting on format mismatches.
- **JSON Registry:** Externalized format definitions for easy scalability.




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

Step 2: Now build the modular class structure

Step 3: