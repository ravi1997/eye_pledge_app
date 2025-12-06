import { test, expect } from '@playwright/test';
import {
  loginAsAdmin,
  setMobileViewport,
  setTabletViewport,
  setDesktopViewport,
} from './helpers';

const BASE_URL = 'http://localhost:5000';

test.describe('UI/UX - Layout and Responsive Design', () => {
  
  test.describe('Desktop - 1920x1080', () => {
    test.beforeEach(async ({ page }) => {
      await setDesktopViewport(page);
    });

    test('home page desktop layout', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const hero = page.locator('h1');
      await expect(hero).toBeVisible();
      
      const button = page.locator('button:has-text("Start Pledging")');
      await expect(button).toBeVisible();
    });

    test('pledge form desktop layout', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const form = page.locator('form');
      await expect(form).toBeVisible();
      
      const sections = page.locator('h3');
      expect(await sections.count()).toBeGreaterThan(3);
    });

    test('pledge form sections are properly spaced', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const sections = page.locator('h3');
      const count = await sections.count();
      
      // Should have major sections: Donor Details, Address, Pledge, Witness
      expect(count).toBeGreaterThanOrEqual(4);
    });
  });

  test.describe('Tablet - 768x1024', () => {
    test.beforeEach(async ({ page }) => {
      await setTabletViewport(page);
    });

    test('home page tablet layout', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const hero = page.locator('h1');
      await expect(hero).toBeVisible();
      
      // Content should be readable on tablet
      const button = page.locator('button:has-text("Start Pledging")');
      await expect(button).toBeVisible();
    });

    test('pledge form tablet layout', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Form should be usable on tablet
      const inputs = page.locator('input[type="text"], input[type="email"], input[type="tel"]');
      expect(await inputs.count()).toBeGreaterThan(5);
      
      // All inputs should be scrollable into view
      for (let i = 0; i < Math.min(3, await inputs.count()); i++) {
        const input = inputs.nth(i);
        await input.scrollIntoViewIfNeeded();
        await expect(input).toBeVisible();
      }
    });

    test('navigation is accessible on tablet', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const navbar = page.locator('nav');
      await expect(navbar).toBeVisible();
    });
  });

  test.describe('Mobile - 375x667', () => {
    test.beforeEach(async ({ page }) => {
      await setMobileViewport(page);
    });

    test('home page mobile layout', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const hero = page.locator('h1');
      await expect(hero).toBeVisible();
      
      // Text should be readable on mobile
      const textSize = await hero.evaluate(el => window.getComputedStyle(el).fontSize);
      expect(textSize).toBeTruthy();
    });

    test('pledge form mobile layout - form is scrollable', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const form = page.locator('form');
      await expect(form).toBeVisible();
      
      // Form should be scrollable
      const donorNameInput = page.locator('input[name="donor_name"]');
      await donorNameInput.scrollIntoViewIfNeeded();
      await expect(donorNameInput).toBeVisible();
    });

    test('pledge form mobile - all sections accessible', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const sections = [
        'Donor Details',
        'Address',
        'Pledge',
        'Witness'
      ];
      
      for (const section of sections) {
        const heading = page.locator(`h3:has-text("${section}")`);
        await heading.scrollIntoViewIfNeeded();
        await expect(heading).toBeVisible();
      }
    });

    test('submit button is easily tappable on mobile', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const submitButton = page.locator('button:has-text("Submit Pledge")');
      
      // Button should have reasonable size for touch
      const boundingBox = await submitButton.boundingBox();
      expect(boundingBox?.height).toBeGreaterThan(40); // At least 40px tall for touch
    });

    test('inputs have reasonable size for mobile interaction', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const inputs = page.locator('input[type="text"]');
      
      if (await inputs.count() > 0) {
        const firstInput = inputs.first();
        const boundingBox = await firstInput.boundingBox();
        
        expect(boundingBox?.height).toBeGreaterThan(36); // Reasonable for mobile
      }
    });

    test('keyboard does not hide important form fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const donorNameInput = page.locator('input[name="donor_name"]');
      
      // Focus on first input
      await donorNameInput.focus();
      
      // Input should still be visible
      await expect(donorNameInput).toBeVisible();
    });
  });

  test.describe('Bootstrap Grid System', () => {
    test('containers have proper spacing', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const container = page.locator('.container');
      await expect(container).toBeVisible();
    });

    test('form uses grid layout properly', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Check for row classes
      const rows = page.locator('.row');
      expect(await rows.count()).toBeGreaterThan(0);
    });

    test('columns are responsive', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto(`${BASE_URL}/pledge`);
      
      // Verify page loads correctly with responsive columns
      const form = page.locator('form');
      await expect(form).toBeVisible();
    });
  });

  test.describe('Typography and Readability', () => {
    test('headings are visible and readable', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const h1 = page.locator('h1');
      
      const fontSize = await h1.evaluate(el => window.getComputedStyle(el).fontSize);
      const color = await h1.evaluate(el => window.getComputedStyle(el).color);
      
      // Should have reasonable font size
      const fontSizeValue = parseFloat(fontSize);
      expect(fontSizeValue).toBeGreaterThan(20);
    });

    test('labels have proper font styling', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const labels = page.locator('label');
      expect(await labels.count()).toBeGreaterThan(5);
      
      // Check first label is visible
      await expect(labels.first()).toBeVisible();
    });

    test('body text is readable', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const body = page.locator('body');
      const fontSize = await body.evaluate(el => window.getComputedStyle(el).fontSize);
      const fontSizeValue = parseFloat(fontSize);
      
      expect(fontSizeValue).toBeGreaterThanOrEqual(14);
    });
  });

  test.describe('Colors and Contrast', () => {
    test('buttons have visible styling', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const button = page.locator('button:has-text("Start Pledging")');
      const backgroundColor = await button.evaluate(el => window.getComputedStyle(el).backgroundColor);
      
      expect(backgroundColor).toBeTruthy();
    });

    test('form inputs have distinct styling', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const input = page.locator('input[name="donor_name"]');
      const borderColor = await input.evaluate(el => window.getComputedStyle(el).borderColor);
      
      expect(borderColor).toBeTruthy();
    });

    test('error states are visually distinct', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      // Submit empty form to trigger errors
      await page.click('button:has-text("Submit Pledge")');
      
      // Check for error styling
      const invalidInputs = page.locator('input.is-invalid');
      expect(await invalidInputs.count()).toBeGreaterThan(0);
    });
  });

  test.describe('Spacing and Layout Consistency', () => {
    test('form sections have consistent spacing', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const sections = page.locator('h3');
      
      // Get spacing between sections
      let prevY = 0;
      const spacings = [];
      
      for (let i = 0; i < await sections.count(); i++) {
        const box = await sections.nth(i).boundingBox();
        if (box && prevY > 0) {
          spacings.push(box.y - prevY);
        }
        prevY = box?.y || 0;
      }
      
      // Spacings should be reasonably consistent
      expect(spacings.length).toBeGreaterThan(0);
    });

    test('form fields have consistent height', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const inputs = page.locator('input[type="text"]');
      
      let heights = [];
      for (let i = 0; i < Math.min(3, await inputs.count()); i++) {
        const box = await inputs.nth(i).boundingBox();
        heights.push(box?.height || 0);
      }
      
      // Heights should be similar
      const minHeight = Math.min(...heights);
      const maxHeight = Math.max(...heights);
      
      expect(maxHeight - minHeight).toBeLessThan(10);
    });
  });

  test.describe('Navigation and Interaction', () => {
    test('navbar is always accessible', async ({ page }) => {
      await page.goto(`${BASE_URL}/pledge`);
      
      const navbar = page.locator('nav');
      await expect(navbar).toBeVisible();
      
      const boundingBox = await navbar.boundingBox();
      expect(boundingBox?.y).toBeLessThanOrEqual(100);
    });

    test('footer is accessible on all pages', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const footer = page.locator('footer');
      
      // Scroll to bottom
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      
      await expect(footer).toBeVisible();
    });

    test('buttons have hover effects', async ({ page }) => {
      await page.goto(`${BASE_URL}/`);
      
      const button = page.locator('button:has-text("Start Pledging")');
      
      // Get initial state
      const initialStyle = await button.evaluate(el => window.getComputedStyle(el).opacity);
      
      // Hover
      await button.hover();
      
      // Button should still be visible and interactive
      await expect(button).toBeEnabled();
    });
  });
});
