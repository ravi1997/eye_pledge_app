# Form Submission & Success Page Flow

## Overview
The Eye Donation Pledge Form now successfully submits data and navigates to a success page with a reference number.

## Form Submission Flow

### 1. **Form HTML** (`templates/pledge_form.html`)
- Method: POST
- Action: `{{ url_for('pledge_form') }}`
- All form fields match the backend expectations

### 2. **Backend Processing** (`app.py` - `/pledge` route)

#### Field Mapping (HTML → Database)
| HTML Field Name | Database Field | Type |
|---|---|---|
| donor_name | donor_name | text |
| gender | donor_gender | text |
| date_of_birth | donor_dob | date |
| age | donor_age | integer |
| blood_group | donor_blood_group | text |
| donor_mobile | donor_mobile | text |
| donor_email | donor_email | email |
| marital_status | donor_marital_status | text |
| occupation | donor_occupation | text |
| id_proof_type | donor_id_proof_type | text |
| id_proof_number | donor_id_proof_number | text |
| address_line1 | address_line1 | text |
| address_line2 | address_line2 | text |
| city | city | text |
| district | district | text |
| state | state | text |
| pincode | pincode | text |
| country | country | text |
| date_of_pledge | date_of_pledge | date |
| time_of_pledge | time_of_pledge | time |
| organs_consented | organs_consented | text |
| language_of_consent | language_preference | text |
| place | place_of_pledge | text |
| additional_notes | pledge_additional_notes | text |
| witness1_name | witness1_name | text |
| witness1_relationship | witness1_relationship | text |
| witness1_mobile | witness1_mobile | text |
| witness1_email | witness1_email | email |
| witness1_telephone | witness1_telephone | text |
| witness1_address | witness1_address | text |
| witness2_name | witness2_name | text |
| witness2_relationship | witness2_relationship | text |
| witness2_mobile | witness2_mobile | text |
| witness2_email | witness2_email | email |
| witness2_telephone | witness2_telephone | text |
| witness2_address | witness2_address | text |
| donor_consent | (validated) | boolean |

#### Validation
Required fields checked in `validate_pledge()`:
- donor_name
- address_line1
- city
- state
- pincode
- donor_mobile
- donor_email
- witness1_name
- donor_consent

#### Processing Steps
1. Form submitted via POST
2. Server-side validation performed
3. If validation fails: Return form with error messages
4. If validation passes:
   - Generate unique reference number: `NEB-YYYY-XXXXXX`
   - Create `EyeDonationPledge` object
   - Save to database
   - Redirect to success page

### 3. **Success Page** (`templates/success.html`)

#### Route
`/success/<ref_num>`

#### Display Information
- Reference number (e.g., NEB-2025-000001)
- Pledge summary with donor details
- Important information about the pledge
- Contact information
- Action buttons:
  - View Pledge Details
  - Back to Home
  - Print Page

## Playwright Test Updates

### URL Pattern Fixes
Changed all `waitForURL` calls from glob patterns to regex patterns:

**Before (incorrect):**
```javascript
await page.waitForURL(`${BASE_URL}/success/**`, { timeout: 10000 });
```

**After (correct):**
```javascript
await page.waitForURL(new RegExp(`${BASE_URL}/success/.*`), { timeout: 10000 });
```

### Updated Tests
1. `E2E: User submits pledge with all fields filled` ✅
2. `E2E: User submits pledge with minimal fields` ✅
3. `E2E: User corrects form errors and resubmits` ✅
4. `Witness: Witness 1 is mandatory, Witness 2 is optional` ✅

## Complete Workflow

```
┌─────────────────┐
│  Fill Form      │
│  Page: /pledge  │
└────────┬────────┘
         │ POST
         │
         ▼
┌─────────────────────────┐
│  Server Validation      │
│  - Check required fields│
│  - Validate email       │
│  - Validate mobile      │
└────────┬────────────────┘
         │
    ┌────┴─────┐
    │           │
    ▼           ▼
 ERROR      SUCCESS
    │           │
    │           ├─ Generate Reference #
    │           ├─ Save to Database
    │           └─ Redirect
    │
    └─► Return to Form
        with Error Messages
        
        
        ▼ (on success)
        
┌──────────────────────┐
│   Success Page       │
│  /success/<ref_num>  │
│  - Show Reference #  │
│  - Show Summary      │
│  - Print/View Links  │
└──────────────────────┘
```

## Key Changes Made

1. ✅ Updated form field names to match HTML
2. ✅ Updated validation function to use correct field names  
3. ✅ Updated form data mapping in pledge creation
4. ✅ Fixed success.html route parameter
5. ✅ Updated all Playwright tests to use regex URL patterns
6. ✅ Verified backend routes and templates exist

## Testing the Flow

To test the complete submission flow:

```bash
# 1. Start the Flask app
python app.py

# 2. Run the Playwright tests
npm test

# 3. Navigate to http://localhost:5000/pledge
# 4. Fill the form and submit
# 5. Verify redirect to success page with reference number
```

## Important Notes

- Reference numbers follow the format: `NEB-YYYY-XXXXXX` (where YYYY is year, XXXXXX is sequence)
- All date fields use ISO format: YYYY-MM-DD
- Mobile numbers are validated as 10-digit strings
- Email addresses are validated for @ symbol
- Consent checkbox is mandatory
- Pledge data is persisted in the database
- Success page displays a summary and provides options to view or print the pledge
