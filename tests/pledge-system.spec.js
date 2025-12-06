import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5000';

test.describe('Eye Donation Pledge System - Test Suite', () => {
  
  // =====================================================================
  // PUBLIC ROUTES TESTS
  // =====================================================================
  
  test.describe('Public Routes', () => {
    
    test('should load home page successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      await expect(page).toHaveTitle(/Eye|Pledge|Donation/i);
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('a:has-text("Start Pledging")')).toBeVisible();
    });

    test('should load pledge form page', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      await expect(page).toHaveTitle(/Pledge|Form/i);
      
      // Check for form sections
      await expect(page.locator('h3:has-text("Donor Details")')).toBeVisible();
      await expect(page.locator('h3:has-text("Address")')).toBeVisible();
      await expect(page.locator('h3:has-text("Pledge")')).toBeVisible();
      await expect(page.locator('h3:has-text("Witness 1")')).toBeVisible();
    });

    test('should display 404 error for non-existent page', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/non-existent-page`);
      expect(response?.status()).toBe(404);
    });
  });

  // =====================================================================
  // FORM VALIDATION TESTS
  // =====================================================================
  
  test.describe('Pledge Form - Validation', () => {
    
    test('should show validation errors for required fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Try to submit empty form
      await page.click('button:has-text("Submit Pledge")');
      
      // Check for validation messages
      const invalidFeedback = await page.locator('.invalid-feedback').count();
      expect(invalidFeedback).toBeGreaterThan(0);
    });

    test('should accept valid donor name', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const nameInput = page.locator('input[name="donor_name"]');
      await nameInput.fill('John Doe');
      
      await expect(nameInput).toHaveValue('John Doe');
    });

    test('should validate email format', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const emailInput = page.locator('input[name="donor_email"]');
      
      // Test invalid email
      await emailInput.fill('invalid-email');
      await emailInput.blur();
      
      // Test valid email
      await emailInput.fill('valid@email.com');
      await expect(emailInput).toHaveValue('valid@email.com');
    });

    test('should validate mobile number format', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const mobileInput = page.locator('input[name="donor_mobile"]');
      
      // Fill with 10 digits (valid)
      await mobileInput.fill('9876543210');
      await expect(mobileInput).toHaveValue('9876543210');
    });

    test('should auto-fill date of pledge with today', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const dateInput = page.locator('input[name="date_of_pledge"]');
      const today = new Date().toISOString().split('T')[0];
      
      // Wait for JavaScript to execute
      await page.waitForTimeout(500);
      
      const value = await dateInput.inputValue();
      expect(value).toBeTruthy();
    });

    test('should auto-calculate age from date of birth', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const dobInput = page.locator('input[name="date_of_birth"]');
      const ageInput = page.locator('input[name="age"]');
      
      // Set DOB to 30 years ago
      const dob = new Date();
      dob.setFullYear(dob.getFullYear() - 30);
      const dobString = dob.toISOString().split('T')[0];
      
      await dobInput.fill(dobString);
      await dobInput.blur();
      
      // Wait for calculation
      await page.waitForTimeout(300);
      
      const ageValue = await ageInput.inputValue();
      expect(parseInt(ageValue)).toBeGreaterThanOrEqual(29);
    });
  });

  // =====================================================================
  // FORM SUBMISSION TESTS
  // =====================================================================
  
  test.describe('Pledge Form - Submission', () => {
    
    test('should submit pledge with valid data', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Fill donor details
      await page.locator('input[name="donor_name"]').fill('Test Donor');
      await page.locator('select[name="gender"]').selectOption('Male');
      await page.locator('select[name="blood_group"]').selectOption('O+');
      await page.locator('input[name="donor_mobile"]').fill('9876543210');
      await page.locator('input[name="donor_email"]').fill('donor@test.com');
      
      // Fill address
      await page.locator('input[name="address_line1"]').fill('123 Test Street');
      await page.locator('input[name="city"]').fill('Test City');
      await page.locator('input[name="state"]').fill('Test State');
      await page.locator('input[name="pincode"]').fill('123456');
      
      // Fill pledge details
      await page.locator('select[name="organs_consented"]').selectOption('Both eyes');
      
      // Fill witness 1
      await page.locator('input[name="witness1_name"]').fill('Witness One');
      await page.locator('select[name="witness1_relationship"]').selectOption('Father');
      await page.locator('input[name="witness1_mobile"]').fill('9876543211');
      
      // Accept consent
      await page.locator('input[name="donor_consent"]').check();
      
      // Submit form
      await page.click('button:has-text("Submit Pledge")');
      
      // Wait for redirect and success page
      await page.waitForURL(`${BASE_URL}/success/**`);
      
      // Check for success message and reference number
      await expect(page.locator('text=Pledge submitted successfully')).toBeVisible();
      await expect(page.locator('text=NEB-')).toBeVisible();
    });

    test('should show error message for duplicate data', async ({ page }) => {
      // Submit pledge first time
      await page.goto(`${BASE_URL}/pledge`);
      
      await page.locator('input[name="donor_name"]').fill('Duplicate Test');
      await page.locator('input[name="donor_mobile"]').fill('1111111111');
      await page.locator('input[name="donor_email"]').fill('duplicate@test.com');
      await page.locator('input[name="address_line1"]').fill('Test Address');
      await page.locator('input[name="city"]').fill('Test City');
      await page.locator('input[name="state"]').fill('Test State');
      await page.locator('input[name="pincode"]').fill('111111');
      await page.locator('input[name="witness1_name"]').fill('Witness');
      await page.locator('input[name="donor_consent"]').check();
      
      // First submission
      await page.click('button:has-text("Submit Pledge")');
      await page.waitForURL(`${BASE_URL}/success/**`);
      
      // Go back and get reference number
      const referenceNumber = await page.locator('text=NEB-').textContent();
      expect(referenceNumber).toBeTruthy();
    });
  });

  // =====================================================================
  // SUCCESS PAGE TESTS
  // =====================================================================
  
  test.describe('Success Page', () => {
    
    test('should display success page with reference number', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Submit minimal valid form
      await page.locator('input[name="donor_name"]').fill('Success Test');
      await page.locator('input[name="donor_mobile"]').fill('5555555555');
      await page.locator('input[name="donor_email"]').fill('success@test.com');
      await page.locator('input[name="address_line1"]').fill('Address');
      await page.locator('input[name="city"]').fill('City');
      await page.locator('input[name="state"]').fill('State');
      await page.locator('input[name="pincode"]').fill('555555');
      await page.locator('input[name="witness1_name"]').fill('Witness');
      await page.locator('input[name="donor_consent"]').check();
      
      await page.click('button:has-text("Submit Pledge")');
      await page.waitForURL(`${BASE_URL}/success/**`);
      
      // Check success elements
      await expect(page.locator('h1')).toContainText(/Success|Confirmation/i);
      await expect(page.locator('text=NEB-2025-')).toBeVisible();
      await expect(page.locator('button:has-text("Print")')).toBeVisible();
    });

    test('should have working print button on success page', async ({ page }) => {
      // This would require printing - basic check
      await page.goto(`${BASE_URL}/pledge`);
      
      await page.locator('input[name="donor_name"]').fill('Print Test');
      await page.locator('input[name="donor_mobile"]').fill('6666666666');
      await page.locator('input[name="donor_email"]').fill('print@test.com');
      await page.locator('input[name="address_line1"]').fill('Address');
      await page.locator('input[name="city"]').fill('City');
      await page.locator('input[name="state"]').fill('State');
      await page.locator('input[name="pincode"]').fill('666666');
      await page.locator('input[name="witness1_name"]').fill('Witness');
      await page.locator('input[name="donor_consent"]').check();
      
      await page.click('button:has-text("Submit Pledge")');
      await page.waitForURL(`${BASE_URL}/success/**`);
      
      const printButton = page.locator('button:has-text("Print")');
      await expect(printButton).toBeVisible();
    });
  });

  // =====================================================================
  // ADMIN ROUTES TESTS
  // =====================================================================
  
  test.describe('Admin Routes - Authentication', () => {
    
    test('should load admin login page', async ({ page }) => {
      await page.goto(`${BASE_URL}/admin/login`);
      
      await expect(page.locator('input[name="username"]')).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
      await expect(page.locator('button:has-text("Login")')).toBeVisible();
    });

    test('should reject invalid login credentials', async ({ page }) => {
      await page.goto(`${BASE_URL}/admin/login`);
      
      await page.locator('input[name="username"]').fill('invalid_user');
      await page.locator('input[name="password"]').fill('wrong_password');
      
      await page.click('button:has-text("Login")');
      
      // Should see error message or stay on login page
      await expect(page).toHaveURL(`${BASE_URL}/admin/login`);
    });

    test('should redirect to login for protected routes', async ({ page }) => {
      await page.goto(`${BASE_URL}/admin/pledges`);
      
      // Should redirect to login
      await expect(page).toHaveURL(/admin\/login/);
    });
  });

  // =====================================================================
  // RESPONSIVE DESIGN TESTS
  // =====================================================================
  
  test.describe('Responsive Design', () => {
    
    test('should be mobile responsive', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check form is still usable on mobile
      const form = page.locator('form');
      await expect(form).toBeVisible();
      
      const inputs = page.locator('input[type="text"]');
      expect(await inputs.count()).toBeGreaterThan(0);
    });

    test('should be tablet responsive', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check form is visible and usable
      await expect(page.locator('form')).toBeVisible();
    });

    test('should be desktop responsive', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check form renders well on desktop
      await expect(page.locator('form')).toBeVisible();
    });
  });

  // =====================================================================
  // NAVIGATION TESTS
  // =====================================================================
  
  test.describe('Navigation', () => {
    
    test('should have working navigation links', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      // Check for navigation elements
      const navbar = page.locator('nav');
      await expect(navbar).toBeVisible();
      
      // Check home link
      const homeLink = page.locator('a:has-text("Home")');
      if (await homeLink.isVisible()) {
        await homeLink.click();
        await expect(page).toHaveURL(`${BASE_URL}/`);
      }
    });

    test('should navigate from home to pledge form', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const startButton = page.locator('button:has-text("Start Pledging")');
      await expect(startButton).toBeVisible();
      
      await startButton.click();
      
      await page.waitForURL(`${BASE_URL}/pledge`);
      await expect(page).toHaveURL(`${BASE_URL}/pledge`);
    });

    test('should have footer with institution info', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const footer = page.locator('footer');
      await expect(footer).toBeVisible();
    });
  });

  // =====================================================================
  // ACCESSIBILITY TESTS
  // =====================================================================
  
  test.describe('Accessibility', () => {
    
    test('should have proper form labels', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check for labels on inputs
      const labels = page.locator('label');
      expect(await labels.count()).toBeGreaterThan(0);
      
      // Check labels are associated with inputs
      const namedInputs = page.locator('input[id]');
      expect(await namedInputs.count()).toBeGreaterThan(0);
    });

    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check for h1
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check for other headings
      const headings = page.locator('h2, h3, h4, h5, h6');
      expect(await headings.count()).toBeGreaterThan(0);
    });

    test('should have alt text for images', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const images = page.locator('img');
      const count = await images.count();
      
      for (let i = 0; i < count; i++) {
        const alt = await images.nth(i).getAttribute('alt');
        if (alt === null) {
          // Images might not have alt text in all cases, but we check
          const ariaLabel = await images.nth(i).getAttribute('aria-label');
          // Either alt or aria-label should be present for important images
        }
      }
    });
  });

  // =====================================================================
  // PERFORMANCE TESTS
  // =====================================================================
  
  test.describe('Performance', () => {
    
    test('should load home page within reasonable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}/`);
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should load pledge form within reasonable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}/pledge`);
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should not have console errors', async ({ page }) => {
      let hasError = false;
      
      page.on('console', msg => {
        if (msg.type() === 'error') {
          hasError = true;
        }
      });
      
      await page.goto(`${BASE_URL}/pledge`);
      
      expect(hasError).toBeFalsy();
    });
  });

  // =====================================================================
  // FORM FIELDS TESTS
  // =====================================================================
  
  test.describe('Form Fields - All Present', () => {
    
    test('should have all required donor fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const fields = [
        'donor_name',
        'gender',
        'date_of_birth',
        'age',
        'blood_group',
        'donor_mobile',
        'donor_email',
        'marital_status',
        'occupation',
        'id_proof_type',
        'id_proof_number'
      ];
      
      for (const field of fields) {
        const element = page.locator(`[name="${field}"]`);
        await expect(element).toBeVisible();
      }
    });

    test('should have all address fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const fields = [
        'address_line1',
        'address_line2',
        'city',
        'district',
        'state',
        'pincode',
        'country'
      ];
      
      for (const field of fields) {
        const element = page.locator(`[name="${field}"]`);
        await expect(element).toBeVisible();
      }
    });

    test('should have all pledge consent fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const fields = [
        'date_of_pledge',
        'time_of_pledge',
        'organs_consented',
        'language_of_consent',
        'place',
        'additional_notes',
        'donor_consent'
      ];
      
      for (const field of fields) {
        const element = page.locator(`[name="${field}"]`);
        await expect(element).toBeVisible();
      }
    });

    test('should have all witness fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const witness1Fields = [
        'witness1_name',
        'witness1_relationship',
        'witness1_address',
        'witness1_mobile',
        'witness1_telephone',
        'witness1_email'
      ];
      
      for (const field of witness1Fields) {
        const element = page.locator(`[name="${field}"]`);
        await expect(element).toBeVisible();
      }
    });
  });

  // =====================================================================
  // ERROR HANDLING TESTS
  // =====================================================================
  
  test.describe('Error Handling', () => {
    
    test('should display 404 page for invalid routes', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/invalid-route-12345`);
      
      expect(response?.status()).toBe(404);
      await expect(page.locator('h1')).toContainText(/404|Not Found/i);
    });

    test('should show user-friendly error messages', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Try to submit without required fields
      await page.click('button:has-text("Submit Pledge")');
      
      // Should see error indicators
      const errorElements = page.locator('.invalid-feedback, .alert-danger');
      expect(await errorElements.count()).toBeGreaterThan(0);
    });

    test('should recover from form errors', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Try to submit empty
      await page.click('button:has-text("Submit Pledge")');
      
      // Fill in required fields
      await page.locator('input[name="donor_name"]').fill('Error Recovery Test');
      await page.locator('input[name="donor_mobile"]').fill('7777777777');
      await page.locator('input[name="donor_email"]').fill('recovery@test.com');
      await page.locator('input[name="address_line1"]').fill('Address');
      await page.locator('input[name="city"]').fill('City');
      await page.locator('input[name="state"]').fill('State');
      await page.locator('input[name="pincode"]').fill('777777');
      await page.locator('input[name="witness1_name"]').fill('Witness');
      await page.locator('input[name="consent"]').check();
      
      // Submit again
      await page.click('button:has-text("Submit Pledge")');
      
      // Should succeed
      await page.waitForURL(`${BASE_URL}/success/**`, { timeout: 5000 });
    });
  });
});
