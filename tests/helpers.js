/**
 * Test Utilities and Helpers for Eye Donation Pledge System
 */

/**
 * Generate a random 10-digit mobile number
 */
export function generateMobileNumber() {
  const randomDigits = Math.floor(Math.random() * 9000000000) + 1000000000;
  return randomDigits.toString();
}

/**
 * Generate a random email address
 */
export function generateEmail() {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return `testdonor+${timestamp}-${random}@test.com`;
}

/**
 * Fill pledge form with valid test data
 */
export async function fillPledgeFormWithValidData(page) {
  const mobileNumber = generateMobileNumber();
  const email = generateEmail();

  // Wait for form to load
  await page.waitForLoadState('networkidle');

  // Donor Details
  await page.locator('input[name="donor_name"]').fill('Test Donor User');
  await page.locator('select[name="gender"]').selectOption('Male');
  
  // Set DOB to 30 years ago
  const dob = new Date();
  dob.setFullYear(dob.getFullYear() - 30);
  const dobString = dob.toISOString().split('T')[0];
  await page.locator('input[name="date_of_birth"]').fill(dobString);
  
  await page.locator('select[name="blood_group"]').selectOption('O+');
  await page.locator('input[name="donor_mobile"]').fill(mobileNumber);
  await page.locator('input[name="donor_email"]').fill(email);
  await page.locator('select[name="marital_status"]').selectOption('Single');
  await page.locator('input[name="occupation"]').fill('Engineer');
  await page.locator('select[name="id_proof_type"]').selectOption('Aadhaar');
  await page.locator('input[name="id_proof_number"]').fill('123456789012');

  // Address
  await page.locator('input[name="address_line1"]').fill('123 Test Street');
  await page.locator('input[name="address_line2"]').fill('Apartment 456');
  await page.locator('input[name="city"]').fill('Test City');
  await page.locator('input[name="district"]').fill('Test District');
  await page.locator('input[name="state"]').fill('Test State');
  await page.locator('input[name="pincode"]').fill('123456');
  await page.locator('input[name="country"]').fill('India');

  // Pledge & Consent
  await page.locator('select[name="organs_consented"]').selectOption('Both eyes');
  await page.locator('select[name="language_of_consent"]').selectOption('English');
  await page.locator('input[name="place"]').fill('Test Location');
  await page.locator('textarea[name="additional_notes"]').fill('Test pledge notes');

  // Witness 1 (Mandatory)
  await page.locator('input[name="witness1_name"]').fill('Witness One Person');
  await page.locator('select[name="witness1_relationship"]').selectOption('Father');
  await page.locator('input[name="witness1_mobile"]').fill(generateMobileNumber());
  await page.locator('input[name="witness1_email"]').fill(generateEmail());
  await page.locator('input[name="witness1_address"]').fill('Witness Address 1');

  // Consent
  await page.locator('input[name="donor_consent"]').check();

  return {
    mobileNumber,
    email,
    dobString,
  };
}

/**
 * Fill pledge form with minimal valid data
 */
export async function fillPledgeFormMinimal(page) {
  const mobileNumber = generateMobileNumber();
  const email = generateEmail();

  // Only required fields
  await page.locator('input[name="donor_name"]').fill('Minimal Donor');
  await page.locator('input[name="donor_mobile"]').fill(mobileNumber);
  await page.locator('input[name="donor_email"]').fill(email);
  await page.locator('input[name="address_line1"]').fill('Test Address');
  await page.locator('input[name="city"]').fill('City');
  await page.locator('input[name="state"]').fill('State');
  await page.locator('input[name="pincode"]').fill('123456');
  await page.locator('input[name="witness1_name"]').fill('Witness');
  await page.locator('input[name="donor_consent"]').check();

  return {
    mobileNumber,
    email,
  };
}

/**
 * Extract reference number from success page
 */
export async function extractReferenceNumber(page) {
  const referenceElement = page.locator('text=NEB-2025-');
  const text = await referenceElement.textContent();
  const match = text?.match(/(NEB-2025-\d+)/);
  return match ? match[1] : null;
}

/**
 * Verify form validation error appears
 */
export async function expectValidationError(page, fieldName) {
  const field = page.locator(`[name="${fieldName}"]`);
  const errorMessage = field.locator('~ .invalid-feedback');
  return await errorMessage.isVisible();
}

/**
 * Verify form field is visible
 */
export async function expectFieldVisible(page, fieldName) {
  const field = page.locator(`[name="${fieldName}"]`);
  return await field.isVisible();
}

/**
 * Wait for success page with timeout
 */
export async function waitForSuccessPage(page, timeout = 5000) {
  await page.waitForURL(/\/success\/.*/, { timeout });
}

/**
 * Login to admin dashboard
 */
export async function loginAsAdmin(page, username = 'admin', password = 'admin123') {
  await page.goto('/admin/login');
  await page.locator('input[name="username"]').fill(username);
  await page.locator('input[name="password"]').fill(password);
  await page.click('button:has-text("Login")');
  
  // Wait for redirect to dashboard
  try {
    await page.waitForURL('/admin/pledges', { timeout: 3000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Submit pledge form
 */
export async function submitPledgeForm(page) {
  await page.click('button:has-text("Submit Pledge")');
}

/**
 * Get form error count
 */
export async function getFormErrorCount(page) {
  const errors = page.locator('.invalid-feedback, .alert-danger');
  return await errors.count();
}

/**
 * Set viewport size to mobile
 */
export async function setMobileViewport(page) {
  await page.setViewportSize({ width: 375, height: 667 });
}

/**
 * Set viewport size to tablet
 */
export async function setTabletViewport(page) {
  await page.setViewportSize({ width: 768, height: 1024 });
}

/**
 * Set viewport size to desktop
 */
export async function setDesktopViewport(page) {
  await page.setViewportSize({ width: 1920, height: 1080 });
}

/**
 * Check if element is in viewport
 */
export async function isElementInViewport(page, selector) {
  return await page.locator(selector).isInViewport();
}

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page, timeout = 3000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Get all console messages and errors
 */
export function setupConsoleLogging(page) {
  const logs = {
    logs: [],
    errors: [],
    warnings: [],
  };

  page.on('console', msg => {
    if (msg.type() === 'log') {
      logs.logs.push(msg.text());
    } else if (msg.type() === 'error') {
      logs.errors.push(msg.text());
    } else if (msg.type() === 'warning') {
      logs.warnings.push(msg.text());
    }
  });

  return logs;
}

/**
 * Get page load time
 */
export async function measurePageLoadTime(page, url) {
  const startTime = Date.now();
  await page.goto(url);
  const endTime = Date.now();
  return endTime - startTime;
}

/**
 * Verify element visibility with custom message
 */
export async function expectElementVisible(page, selector, message = '') {
  const element = page.locator(selector);
  return await element.isVisible().then(visible => {
    if (!visible && message) {
      console.log(message);
    }
    return visible;
  });
}

/**
 * Get all form field values
 */
export async function getAllFormValues(page) {
  const values = {};
  
  const inputs = await page.locator('input, select, textarea').all();
  
  for (const input of inputs) {
    const name = await input.getAttribute('name');
    const type = await input.getAttribute('type');
    
    if (name) {
      if (type === 'checkbox' || type === 'radio') {
        values[name] = await input.isChecked();
      } else {
        values[name] = await input.inputValue();
      }
    }
  }
  
  return values;
}

/**
 * Test data generator - creates realistic pledge data
 */
export function generateTestPledgeData() {
  const firstNames = ['John', 'Rajesh', 'Priya', 'Ahmed', 'Sarah', 'Arjun', 'Neha'];
  const lastNames = ['Doe', 'Kumar', 'Singh', 'Khan', 'Johnson', 'Sharma', 'Gupta'];
  const occupations = ['Engineer', 'Doctor', 'Teacher', 'Manager', 'Student', 'Farmer', 'Nurse'];
  const states = ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Gujarat', 'Rajasthan', 'Bengal'];
  const cities = ['Mumbai', 'Bangalore', 'Chennai', 'Delhi', 'Ahmedabad', 'Jaipur', 'Kolkata'];

  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
  const state = states[Math.floor(Math.random() * states.length)];
  const city = cities[Math.floor(Math.random() * cities.length)];
  const occupation = occupations[Math.floor(Math.random() * occupations.length)];

  return {
    donorName: `${firstName} ${lastName}`,
    mobileNumber: generateMobileNumber(),
    email: generateEmail(),
    state,
    city,
    occupation,
    pincode: Math.floor(100000 + Math.random() * 900000).toString(),
  };
}

/**
 * Simulate network latency for testing
 */
export async function simulateNetworkLatency(page, delayMs = 1000) {
  await page.route('**/*', route => {
    setTimeout(() => route.continue(), delayMs);
  });
}

/**
 * Block images to speed up tests
 */
export async function blockImages(page) {
  await page.route('**/*.{png,jpg,jpeg,gif,webp,svg}', route => route.abort());
}

/**
 * Take screenshot with consistent naming
 */
export async function takeScreenshot(page, testName) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${testName}-${timestamp}.png`;
  await page.screenshot({ path: `test-results/${filename}` });
  return filename;
}

export default {
  generateMobileNumber,
  generateEmail,
  fillPledgeFormWithValidData,
  fillPledgeFormMinimal,
  extractReferenceNumber,
  expectValidationError,
  expectFieldVisible,
  waitForSuccessPage,
  loginAsAdmin,
  submitPledgeForm,
  getFormErrorCount,
  setMobileViewport,
  setTabletViewport,
  setDesktopViewport,
  isElementInViewport,
  waitForNetworkIdle,
  setupConsoleLogging,
  measurePageLoadTime,
  expectElementVisible,
  getAllFormValues,
  generateTestPledgeData,
  simulateNetworkLatency,
  blockImages,
  takeScreenshot,
};
