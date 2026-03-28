# 🏎️ License Plate-Validator (v1.1)

A modular license plate validation system built with **Python** and **RegEx**.

## 🚀 Features
- **Multi-State Support:** Registry-based patterns for CA, TX, and FL.
- **Strict Mode:** Integrated `SecurityValidator` to filter offensive content.
- **Data-Driven:** Patterns are decoupled from logic using a JSON registry.

## 🏛️ Architecture
- `PatternRegistry`: Data Provider for regional formats.
- `ValidatorEngine`: Logic Provider for RegEx execution.
- `SecurityValidator`: Middleware for safety and compliance.




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

