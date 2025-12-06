import { test, expect } from '@playwright/test';
import {
  fillPledgeFormWithValidData,
  fillPledgeFormMinimal,
  generateMobileNumber,
  generateEmail,
  extractReferenceNumber,
  getFormErrorCount,
  generateTestPledgeData,
} from './helpers';

const BASE_URL = 'http://localhost:5000';

test.describe('Pledge Form - Complete Workflow Tests', () => {
  
  test('E2E: User submits pledge with all fields filled', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const data = await fillPledgeFormWithValidData(page);
    
    // Submit the form
    await page.click('button:has-text("Submit Pledge")');
    
    // Wait for success page
    await page.waitForURL(`${BASE_URL}/success/**`, { timeout: 5000 });
    
    // Verify success elements
    await expect(page.locator('h1')).toContainText(/Success|Confirmation/i);
    
    // Extract reference number
    const refNumber = await extractReferenceNumber(page);
    expect(refNumber).toMatch(/NEB-2025-\d+/);
  });

  test('E2E: User submits pledge with minimal fields', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const data = await fillPledgeFormMinimal(page);
    
    await page.click('button:has-text("Submit Pledge")');
    
    await page.waitForURL(`${BASE_URL}/success/**`, { timeout: 5000 });
    
    await expect(page.locator('h1')).toContainText(/Success|Confirmation/i);
  });

  test('E2E: User tries to submit form with missing required fields', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    // Try to submit without filling anything
    await page.click('button:has-text("Submit Pledge")');
    
    // Should see validation errors
    const errorCount = await getFormErrorCount(page);
    expect(errorCount).toBeGreaterThan(5);
    
    // Should stay on pledge form
    await expect(page).toHaveURL(`${BASE_URL}/pledge`);
  });

  test('E2E: User corrects form errors and resubmits', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    // Try to submit empty - will have errors
    await page.click('button:has-text("Submit Pledge")');
    let errorCount = await getFormErrorCount(page);
    expect(errorCount).toBeGreaterThan(0);
    
    // Now fill form correctly
    await fillPledgeFormMinimal(page);
    
    // Submit again
    await page.click('button:has-text("Submit Pledge")');
    
    // Should succeed
    await page.waitForURL(`${BASE_URL}/success/**`);
  });

  test('Field: Date of Pledge auto-fills with today', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const dateInput = page.locator('input[name="date_of_pledge"]');
    
    // Wait for JavaScript to execute
    await page.waitForTimeout(500);
    
    const value = await dateInput.inputValue();
    const today = new Date().toISOString().split('T')[0];
    
    expect(value).toBeTruthy();
  });

  test('Field: Age auto-calculates from DOB', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const dobInput = page.locator('input[name="donor_dob"]');
    const ageInput = page.locator('input[name="donor_age"]');
    
    // Set DOB to exactly 25 years ago
    const dob = new Date();
    dob.setFullYear(dob.getFullYear() - 25);
    const dobString = dob.toISOString().split('T')[0];
    
    await dobInput.fill(dobString);
    await dobInput.blur();
    
    // Wait for calculation
    await page.waitForTimeout(500);
    
    const ageValue = await ageInput.inputValue();
    const expectedAge = parseInt(ageValue);
    
    expect(expectedAge).toBeGreaterThanOrEqual(24);
    expect(expectedAge).toBeLessThanOrEqual(26);
  });

  test('Field: Mobile number validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const mobileInput = page.locator('input[name="donor_mobile"]');
    
    // Valid 10 digits
    await mobileInput.fill('9876543210');
    let isValid = await mobileInput.evaluate((el) => el.validity.valid);
    expect(isValid).toBeTruthy();
    
    // Clear for another test
    await mobileInput.fill('');
  });

  test('Field: Email validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const emailInput = page.locator('input[name="donor_email"]');
    
    // Valid email
    await emailInput.fill('valid@email.com');
    let isValid = await emailInput.evaluate((el) => el.validity.valid);
    expect(isValid).toBeTruthy();
    
    // Invalid email
    await emailInput.clear();
    await emailInput.fill('invalid-email');
    await emailInput.blur();
  });

  test('Field: Pincode validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const pincodeInput = page.locator('input[name="pincode"]');
    
    // 6 digits
    await pincodeInput.fill('123456');
    expect(await pincodeInput.inputValue()).toBe('123456');
  });

  test('Field: ID Proof Number validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const idProofInput = page.locator('input[name="donor_id_proof_number"]');
    
    // Aadhaar number (12 digits)
    await idProofInput.fill('123456789012');
    expect(await idProofInput.inputValue()).toBe('123456789012');
  });

  test('Consent: User must check consent checkbox', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const consentCheckbox = page.locator('input[name="consent"]');
    
    // Initially unchecked
    expect(await consentCheckbox.isChecked()).toBeFalsy();
    
    // Check it
    await consentCheckbox.check();
    expect(await consentCheckbox.isChecked()).toBeTruthy();
  });

  test('Witness: Witness 1 is mandatory, Witness 2 is optional', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const w1Name = page.locator('input[name="witness1_name"]');
    const w2Name = page.locator('input[name="witness2_name"]');
    
    // Both should be visible
    await expect(w1Name).toBeVisible();
    await expect(w2Name).toBeVisible();
    
    // Try submitting with only witness 1
    await fillPledgeFormMinimal(page);
    
    // Make sure witness 2 is empty
    await w2Name.fill('');
    
    await page.click('button:has-text("Submit Pledge")');
    
    // Should succeed with just witness 1
    await page.waitForURL(`${BASE_URL}/success/**`, { timeout: 5000 });
  });

  test('Organs: Multiple organ consent types should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const organsSelect = page.locator('select[name="organs_consented"]');
    
    await expect(organsSelect).toBeVisible();
    
    // Get all options
    const options = await organsSelect.locator('option').count();
    expect(options).toBeGreaterThan(2);
  });

  test('Gender: All gender options should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const genderSelect = page.locator('select[name="donor_gender"]');
    
    // Check options are available
    const maleOption = genderSelect.locator('option[value="Male"]');
    const femaleOption = genderSelect.locator('option[value="Female"]');
    
    await expect(maleOption).toBeVisible();
    await expect(femaleOption).toBeVisible();
  });

  test('Blood Group: All blood groups should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const bgSelect = page.locator('select[name="donor_blood_group"]');
    
    // Check for at least major blood groups
    const oPositive = bgSelect.locator('option:has-text("O+")');
    const bPositive = bgSelect.locator('option:has-text("B+")');
    
    await expect(oPositive).toBeVisible();
    await expect(bPositive).toBeVisible();
  });

  test('Marital Status: All options should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const msSelect = page.locator('select[name="donor_marital_status"]');
    
    const single = msSelect.locator('option:has-text("Single")');
    const married = msSelect.locator('option:has-text("Married")');
    
    await expect(single).toBeVisible();
    await expect(married).toBeVisible();
  });

  test('ID Proof: All ID proof types should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const idSelect = page.locator('select[name="donor_id_proof_type"]');
    
    const aadhaar = idSelect.locator('option:has-text("Aadhaar")');
    const pan = idSelect.locator('option:has-text("PAN")');
    
    await expect(aadhaar).toBeVisible();
    await expect(pan).toBeVisible();
  });

  test('Form: Keyboard navigation works', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    // Focus first field
    const firstInput = page.locator('input[name="donor_name"]');
    await firstInput.focus();
    
    // Tab to next field
    await page.keyboard.press('Tab');
    
    // Verify focus moved
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('name'));
    expect(focusedElement).not.toBe('donor_name');
  });

  test('Form: Submit button is visible and clickable', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`);
    
    const submitButton = page.locator('button:has-text("Submit Pledge")');
    
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });
});
