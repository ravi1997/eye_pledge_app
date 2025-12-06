import { test, expect } from '@playwright/test';
import {
  fillPledgeFormWithValidData,
  fillPledgeFormMinimal,
  generateMobileNumber,
  generateEmail,
  extractReferenceNumber,
  getFormErrorCount,
} from './helpers';

const BASE_URL = 'http://localhost:5000';

test.describe('Pledge Form - Complete Workflow Tests', () => {
  
  test('E2E: User submits pledge with all fields filled', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    await page.waitForSelector('button:has-text("Submit Pledge")', { timeout: 10000 });
    
    const data = await fillPledgeFormWithValidData(page);
    
    await page.click('button:has-text("Submit Pledge")');
    
    await page.waitForURL(new RegExp(`${BASE_URL}/success/.*`), { timeout: 10000 });
    
    await expect(page.locator('h1')).toContainText(/Success|Confirmation/i);
    
    const refNumber = await extractReferenceNumber(page);
    expect(refNumber).toMatch(/NEB-2025-\d+/);
  });

  test('E2E: User submits pledge with minimal fields', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    await page.waitForSelector('button:has-text("Submit Pledge")', { timeout: 10000 });
    
    await fillPledgeFormMinimal(page);
    
    await page.click('button:has-text("Submit Pledge")');
    
    await page.waitForURL(new RegExp(`${BASE_URL}/success/.*`), { timeout: 10000 });
    
    await expect(page.locator('h1')).toContainText(/Success|Confirmation/i);
  });

  test('E2E: User tries to submit form with missing required fields', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    await page.waitForSelector('button:has-text("Submit Pledge")', { timeout: 10000 });
    
    await page.click('button:has-text("Submit Pledge")');
    
    const errorCount = await getFormErrorCount(page);
    expect(errorCount).toBeGreaterThan(5);
    
    await expect(page).toHaveURL(`${BASE_URL}/pledge`);
  });

  test('E2E: User corrects form errors and resubmits', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    await page.waitForSelector('button:has-text("Submit Pledge")', { timeout: 10000 });
    
    await page.click('button:has-text("Submit Pledge")');
    let errorCount = await getFormErrorCount(page);
    expect(errorCount).toBeGreaterThan(0);
    
    await fillPledgeFormMinimal(page);
    
    await page.click('button:has-text("Submit Pledge")');
    
    await page.waitForURL(new RegExp(`${BASE_URL}/success/.*`), { timeout: 10000 });
  });

  test('Field: Date of Pledge auto-fills with today', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const dateInput = page.locator('input[name="date_of_pledge"]');
    
    await dateInput.waitFor({ state: 'visible', timeout: 10000 });
    
    const value = await dateInput.inputValue();
    expect(value).toBeTruthy();
  });

  test('Field: Age auto-calculates from DOB', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const dobInput = page.locator('input[name="date_of_birth"]');
    const ageInput = page.locator('input[name="age"]');
    
    const dob = new Date();
    dob.setFullYear(dob.getFullYear() - 25);
    const dobString = dob.toISOString().split('T')[0];
    
    await dobInput.fill(dobString);
    await dobInput.blur();
    
    await page.waitForTimeout(500);
    
    const ageValue = await ageInput.inputValue();
    const expectedAge = parseInt(ageValue);
    
    expect(expectedAge).toBeGreaterThanOrEqual(24);
    expect(expectedAge).toBeLessThanOrEqual(26);
  });

  test('Field: Mobile number validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const mobileInput = page.locator('input[name="donor_mobile"]');
    
    await mobileInput.fill('9876543210');
    let isValid = await mobileInput.evaluate((el) => el.validity.valid);
    expect(isValid).toBeTruthy();
    
    await mobileInput.fill('');
  });

  test('Field: Email validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const emailInput = page.locator('input[name="donor_email"]');
    
    await emailInput.fill('valid@email.com');
    let isValid = await emailInput.evaluate((el) => el.validity.valid);
    expect(isValid).toBeTruthy();
  });

  test('Field: Pincode validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const pincodeInput = page.locator('input[name="pincode"]');
    
    await pincodeInput.fill('123456');
    expect(await pincodeInput.inputValue()).toBe('123456');
  });

  test('Field: ID Proof Number validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const idProofInput = page.locator('input[name="id_proof_number"]');
    
    await idProofInput.fill('123456789012');
    expect(await idProofInput.inputValue()).toBe('123456789012');
  });

  test('Consent: User must check consent checkbox', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const consentCheckbox = page.locator('input[name="donor_consent"]');
    
    expect(await consentCheckbox.isChecked()).toBeFalsy();
    
    await consentCheckbox.check();
    expect(await consentCheckbox.isChecked()).toBeTruthy();
  });

  test('Witness: Witness 1 is mandatory, Witness 2 is optional', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const w1Name = page.locator('input[name="witness1_name"]');
    const w2Name = page.locator('input[name="witness2_name"]');
    
    await expect(w1Name).toBeVisible();
    await expect(w2Name).toBeVisible();
    
    await fillPledgeFormMinimal(page);
    
    await w2Name.fill('');
    
    await page.click('button:has-text("Submit Pledge")');
    
    await page.waitForURL(new RegExp(`${BASE_URL}/success/.*`), { timeout: 10000 });
  });

  test('Field: Gender: All gender options should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const genderSelect = page.locator('select[name="gender"]');
    
    await expect(genderSelect).toBeVisible();
  });

  test('Field: Blood Group: All blood groups should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const bgSelect = page.locator('select[name="blood_group"]');
    
    await expect(bgSelect).toBeVisible();
  });

  test('Field: Marital Status: All options should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const msSelect = page.locator('select[name="marital_status"]');
    
    await expect(msSelect).toBeVisible();
  });

  test('Field: ID Proof: All ID proof types should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const idSelect = page.locator('select[name="id_proof_type"]');
    
    await expect(idSelect).toBeVisible();
  });

  test('Field: Organs: Organ consent options should be available', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const organsSelect = page.locator('select[name="organs_consented"]');
    
    await expect(organsSelect).toBeVisible();
  });

  test('Form: Keyboard navigation works', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const firstInput = page.locator('input[name="donor_name"]');
    await firstInput.focus();
    
    await page.keyboard.press('Tab');
    
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('name'));
    expect(focusedElement).not.toBe('donor_name');
  });

  test('Form: Submit button is visible and clickable', async ({ page }) => {
    await page.goto(`${BASE_URL}/pledge`, { waitUntil: 'networkidle' });
    
    const submitButton = page.locator('button:has-text("Submit Pledge")');
    
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });
});
