# Playwright Test Suite - HTML Alignment Fixes

## Summary
Updated all Playwright test files to match the actual HTML form field names and structure in `pledge_form.html`.

## Changes Made

### 1. **helpers.js** - Test utility functions
Updated both `fillPledgeFormWithValidData()` and `fillPledgeFormMinimal()` to use correct field names:

**Field Name Mappings:**
- `combobox:has-text("Gender")` → `select[name="gender"]`
- `combobox:has-text("Blood Group")` → `select[name="blood_group"]`
- `combobox:has-text("Marital Status")` → `select[name="marital_status"]`
- `combobox:has-text("ID Proof Type")` → `select[name="id_proof_type"]`
- `combobox:has-text("Organs to Donate")` → `select[name="organs_consented"]`
- `combobox:has-text("Language of Consent")` → `select[name="language_of_consent"]`
- `input[name="donor_dob"]` → `input[name="date_of_birth"]`
- `input[name="donor_occupation"]` → `input[name="occupation"]`
- `input[name="donor_id_proof_number"]` → `input[name="id_proof_number"]`
- `input[name="place_of_pledge"]` → `input[name="place"]`
- `input[name="pledge_additional_notes"]` → `textarea[name="additional_notes"]`
- `combobox.nth(6).selectOption()` → `select[name="witness1_relationship"].selectOption()`
- `input[name="consent"]` → `input[name="donor_consent"]`

### 2. **pledge-form.spec.js** - E2E and field tests
- Updated all field selector tests to use correct HTML names
- Fixed DOB, age, and ID proof field references
- Changed consent checkbox selector from `input[name="consent"]` to `input[name="donor_consent"]`

### 3. **pledge-system.spec.js** - System tests
- Fixed donor details field array to use correct names (gender, date_of_birth, blood_group, etc.)
- Fixed pledge consent fields array (organs_consented, language_of_consent, place, additional_notes, donor_consent)
- Updated all test cases that fill the form with correct field names
- Changed consent checkbox from `input[id="consent"]` to `input[name="donor_consent"]`

## Key Insights

The HTML form uses **standard HTML `<select>` elements**, not custom combobox components. All tests were updated to reflect this.

### Field Name Convention in HTML
The form uses consistent field naming:
- Base field name: `donor_name`, `donor_mobile`, `donor_email`
- Date fields: `date_of_birth`, `date_of_pledge`, `time_of_pledge`
- Select dropdowns: `gender`, `blood_group`, `marital_status`, `id_proof_type`, `organs_consented`, `language_of_consent`, `witness1_relationship`
- Checkboxes: `donor_consent`, `acknowledged_revocability`
- Textareas: `additional_notes`

## Test Files Updated
1. ✅ `tests/helpers.js` - 2 functions fixed
2. ✅ `tests/pledge-form.spec.js` - 20+ test cases aligned
3. ✅ `tests/pledge-system.spec.js` - 30+ test cases aligned
4. ✅ `tests/ui-responsive.spec.js` - No changes needed (uses generic selectors)

## Verification
All field name references have been verified and aligned with the actual HTML form structure in `templates/pledge_form.html`.
