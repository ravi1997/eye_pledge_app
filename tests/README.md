# Eye Donation Pledge System - Playwright Test Suite

Comprehensive automated testing suite for the Eye Donation Pledge Form application using Playwright JavaScript.

## Overview

This test suite provides end-to-end (E2E), integration, and unit test coverage for all critical user workflows and system functionality.

### Test Coverage

- ✅ **Public Routes**: Home, pledge form, success page
- ✅ **Form Validation**: Required fields, format validation, conditional logic
- ✅ **Form Submission**: Success flow, error handling, recovery
- ✅ **Data Persistence**: Database storage, reference number generation
- ✅ **Admin Features**: Authentication, dashboard, search/filter (when implemented)
- ✅ **Responsive Design**: Mobile, tablet, desktop viewports
- ✅ **Accessibility**: Form labels, heading hierarchy, alt text
- ✅ **Performance**: Page load times, console errors
- ✅ **UI/UX**: Layout consistency, spacing, typography, colors

## Quick Start

### Prerequisites

```bash
# Node.js 16+ is required
node --version

# Python 3.8+ for Flask backend
python --version
```

### Installation

```bash
# 1. Install Playwright and dependencies
npm install

# Or install specific browsers
npx playwright install chromium firefox webkit
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- tests/pledge-form.spec.js

# Run in headed mode (see browser)
npm test -- --headed

# Run in debug mode (interactive)
npm test -- --debug

# Run with specific browser
npm test -- --project=chromium

# Run on specific viewport size
npm test -- --project="Mobile Chrome"
```

### Advanced Options

```bash
# Run tests with detailed reporting
npm test -- --reporter=html

# View HTML report after running tests
npx playwright show-report

# Run tests in parallel
npm test -- --workers=4

# Run tests serially
npm test -- --workers=1

# Update snapshots (if using visual tests)
npm test -- --update-snapshots

# Continue even if tests fail
npm test -- --continue-on-failure
```

## Test Suite Structure

### 1. **pledge-system.spec.js** (Main Test Suite - 12 Test Groups)

Comprehensive tests covering all major functionality:

#### Public Routes Tests
- Load home page successfully
- Load pledge form page
- Display 404 error for non-existent pages

#### Form Validation Tests
- Show validation errors for required fields
- Accept valid donor name
- Validate email format
- Validate mobile number format
- Auto-fill date of pledge with today
- Auto-calculate age from DOB

#### Form Submission Tests
- Submit pledge with valid data
- Show error message for duplicate data

#### Success Page Tests
- Display success page with reference number
- Working print button on success page

#### Admin Routes Tests
- Load admin login page
- Reject invalid login credentials
- Redirect to login for protected routes

#### Responsive Design Tests
- Mobile responsive (375x667)
- Tablet responsive (768x1024)
- Desktop responsive (1920x1080)

#### Navigation Tests
- Working navigation links
- Navigate from home to pledge form
- Footer with institution info

#### Accessibility Tests
- Proper form labels
- Proper heading hierarchy
- Alt text for images

#### Performance Tests
- Page load within 3 seconds
- No console errors

#### Form Fields Tests
- All donor fields present
- All address fields present
- All pledge consent fields present
- All witness fields present

#### Error Handling Tests
- Display 404 page
- Show user-friendly error messages
- Recover from form errors

### 2. **pledge-form.spec.js** (Form Workflow Tests - 35+ Tests)

Detailed workflow and field-level tests:

#### Complete Workflow Tests
- E2E: User submits pledge with all fields
- E2E: User submits with minimal fields
- E2E: User tries incomplete submission
- E2E: User corrects errors and resubmits

#### Field-Level Tests
- Date auto-fill verification
- Age calculation from DOB
- Mobile number validation
- Email validation
- Pincode validation (6 digits)
- ID proof number validation (12 digits)

#### Selection Field Tests
- Gender options available
- Blood group options available
- Marital status options available
- ID proof type options available
- Organs consent options available

#### Consent and Witness Tests
- Consent checkbox is required
- Witness 1 is mandatory
- Witness 2 is optional
- All witness fields present

#### Interaction Tests
- Keyboard navigation works
- Submit button is visible and enabled

### 3. **ui-responsive.spec.js** (UI/UX Tests - 40+ Tests)

Desktop, tablet, and mobile specific tests:

#### Desktop Layout (1920x1080)
- Home page desktop layout
- Pledge form desktop layout
- Proper section spacing

#### Tablet Layout (768x1024)
- Home page tablet layout
- Pledge form tablet layout
- Navigation accessibility
- Form scrolling

#### Mobile Layout (375x667)
- Home page mobile layout
- Form scrolling and accessibility
- Section accessibility
- Tappable button sizes
- Input field sizes
- Keyboard interaction

#### Bootstrap Grid System
- Container spacing
- Form grid layout
- Responsive columns

#### Typography and Readability
- Heading visibility and size
- Label styling
- Body text readability

#### Colors and Contrast
- Button styling
- Input styling
- Error state styling

#### Spacing and Layout Consistency
- Form section spacing
- Field height consistency
- Navbar accessibility
- Footer accessibility
- Button hover effects

## Test Helpers (helpers.js)

Reusable utility functions for common test operations:

### Data Generation
```javascript
import { generateMobileNumber, generateEmail, generateTestPledgeData } from './helpers';

const mobile = generateMobileNumber(); // "9876543210"
const email = generateEmail(); // "testdonor+timestamp@test.com"
const data = generateTestPledgeData(); // { donorName, mobile, email, state, city, ... }
```

### Form Filling
```javascript
import { fillPledgeFormWithValidData, fillPledgeFormMinimal } from './helpers';

// Fill with all fields
await fillPledgeFormWithValidData(page);

// Fill with minimum required fields
await fillPledgeFormMinimal(page);
```

### Assertions and Verification
```javascript
import { 
  extractReferenceNumber, 
  getFormErrorCount,
  expectValidationError,
  expectFieldVisible 
} from './helpers';

const refNumber = await extractReferenceNumber(page); // "NEB-2025-123456"
const errorCount = await getFormErrorCount(page);
await expectValidationError(page, 'donor_name');
await expectFieldVisible(page, 'donor_email');
```

### Viewport Management
```javascript
import { setMobileViewport, setTabletViewport, setDesktopViewport } from './helpers';

await setMobileViewport(page);
await setTabletViewport(page);
await setDesktopViewport(page);
```

### Admin Operations
```javascript
import { loginAsAdmin } from './helpers';

const success = await loginAsAdmin(page, 'admin', 'admin123');
```

### Performance and Diagnostics
```javascript
import { 
  measurePageLoadTime, 
  setupConsoleLogging,
  waitForNetworkIdle,
  blockImages 
} from './helpers';

const loadTime = await measurePageLoadTime(page, '/pledge');
const logs = setupConsoleLogging(page);
await waitForNetworkIdle(page);
await blockImages(page); // Speed up tests
```

### Screenshots and Debugging
```javascript
import { takeScreenshot } from './helpers';

await takeScreenshot(page, 'pledge-form-error');
```

## Configuration

### playwright.config.js

Key settings:

```javascript
{
  testDir: './tests',
  timeout: 30000,                  // Per test timeout
  expect: { timeout: 5000 },       // Assertion timeout
  retries: 2,                      // Retry failed tests (CI only)
  workers: 4,                      // Parallel workers
  use: {
    baseURL: 'http://localhost:5000',
    trace: 'on-first-retry',       // Record trace on failure
    screenshot: 'only-on-failure', // Screenshot on failure
    video: 'retain-on-failure',    // Video on failure
  },
  webServer: {
    command: 'python -m flask run',
    url: 'http://localhost:5000',
    reuseExistingServer: true,
  },
  projects: [
    { name: 'chromium' },
    { name: 'firefox' },
    { name: 'webkit' },
    { name: 'Mobile Chrome' },
    { name: 'Mobile Safari' },
  ]
}
```

## Test Reports

### HTML Report
```bash
# Run tests and generate HTML report
npm test

# View report
npx playwright show-report
```

Report includes:
- Test results with pass/fail status
- Screenshots on failure
- Video recordings
- Trace files for debugging

### JSON Report
```bash
# Generate JSON report
npm test -- --reporter=json > results.json
```

### JUnit XML Report
```bash
# For CI/CD integration
npm test -- --reporter=junit
```

## Debugging and Troubleshooting

### Visual Debugging

```bash
# Run tests in headed mode
npm test -- --headed

# Opens browser so you can see what happens
# Press PAUSE button in Playwright Inspector to pause execution
```

### Debug Mode

```bash
# Interactive debugging
npm test -- --debug

# Opens Playwright Inspector
# Step through code, inspect elements, modify DOM
```

### Trace Viewer

```bash
# View detailed traces for failed tests
npx playwright show-trace test-results/trace.zip

# Shows:
# - DOM snapshots
# - Network activity
# - Screenshots
# - Console logs
```

### Playwright Inspector

```bash
# Inspect elements and debug
PWDEBUG=1 npm test

# Or programmatically in tests:
await page.pause();
```

### Common Issues

**Tests timeout**
```bash
# Increase timeout
npm test -- --timeout=60000

# Or per test:
test.setTimeout(60000);
```

**Flask server not starting**
```bash
# Start Flask separately
python -m flask run

# Then run tests without webServer
# (Remove webServer from playwright.config.js or set reuseExistingServer=true)
```

**Network errors**
```bash
# Disable network blocking
# Comment out blockImages(page) if used in helpers
```

**Element not found**
```bash
# Check selectors with Playwright Inspector
PWDEBUG=1 npm test
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Writing New Tests

### Basic Test Template

```javascript
import { test, expect } from '@playwright/test';
import { fillPledgeFormWithValidData } from './helpers';

test('descriptive test name', async ({ page }) => {
  // Arrange: Setup
  await page.goto('/pledge');
  
  // Act: Perform action
  await fillPledgeFormWithValidData(page);
  await page.click('button:has-text("Submit Pledge")');
  
  // Assert: Verify result
  await page.waitForURL(/\/success\/.*/);
  await expect(page.locator('h1')).toContainText('Success');
});
```

### Test Groups

```javascript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup for each test
    await page.goto('/pledge');
  });

  test('test 1', async ({ page }) => {
    // Test code
  });

  test('test 2', async ({ page }) => {
    // Test code
  });
});
```

### Skip or Focus Tests

```javascript
// Skip this test
test.skip('skipped test', async ({ page }) => {
  // Won't run
});

// Run only this test
test.only('focused test', async ({ page }) => {
  // Only this will run
});
```

## Performance Benchmarks

Target metrics:
- Home page load: < 2 seconds
- Pledge form load: < 3 seconds
- Form submission: < 5 seconds
- Page render: 60 FPS (no jank)

## Accessibility Standards

Tests verify compliance with:
- WCAG 2.1 Level A
- Form labels and associations
- Semantic HTML
- Keyboard navigation
- Color contrast

## Test Data

Tests use randomly generated test data:
- Mobile numbers: 10 digits starting with 9-8
- Emails: `testdonor+timestamp@test.com`
- Names: Mix of common first/last names
- Addresses: Generic test addresses

## Continuous Testing

### Watch Mode

```bash
# Rerun tests when files change
npm test -- --watch

# Or with specific file
npm test -- tests/pledge-form.spec.js --watch
```

### Scheduled Testing

For CI/CD, schedule daily test runs:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM
```

## Performance Optimization

To speed up test execution:

```javascript
// In helpers.js or tests
await blockImages(page);  // Skip loading images
await page.route('**/*.css', route => route.abort());  // Skip CSS
test.setTimeout(60000);   // But keep reasonable timeout
```

## Best Practices

1. **Use meaningful test names**: Describe what is being tested
2. **DRY principle**: Use helper functions for repeated code
3. **Isolation**: Each test should be independent
4. **Cleanup**: Reset data between tests if needed
5. **Assertions**: Use specific assertions, not generic truthy checks
6. **Wait wisely**: Use waitForURL, waitForFunction instead of timeout
7. **Descriptive errors**: Add context to assertion failures
8. **Comments**: Document complex test logic

## Support and Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Inspector](https://playwright.dev/docs/inspector)
- [Trace Viewer](https://trace.playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging](https://playwright.dev/docs/debug)

## Contributing

When adding new features to the application:

1. Write tests for the new feature in appropriate spec file
2. Verify all tests pass: `npm test`
3. Check test coverage
4. Add helper functions if needed
5. Update this README with new test descriptions

## License

Tests are part of the Eye Donation Pledge System project.
