import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for tilores_X Dashboard E2E Testing
 *
 * Comprehensive end-to-end testing configuration for full-stack integration
 * between MUI Dashboard frontend and Virtuous Cycle API backend.
 *
 * Author: Roo (Elite Software Engineer)
 * Created: 2025-08-16
 * Integration: Frontend-Backend E2E Testing
 */

export default defineConfig({
  testDir: './e2e-tests',

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['line']
  ],

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Take screenshot when test fails */
    screenshot: 'only-on-failure',

    /* Record video when test fails */
    video: 'retain-on-failure',

    /* Global timeout for actions */
    actionTimeout: 10000,

    /* Global timeout for navigation */
    navigationTimeout: 30000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: true, // Use existing servers
    timeout: 30 * 1000, // 30 seconds
  },

  /* Global setup and teardown */
  globalSetup: './e2e-tests/global-setup.js',
  globalTeardown: './e2e-tests/global-teardown.js',

  /* Test timeout */
  timeout: 30 * 1000,

  /* Expect timeout */
  expect: {
    timeout: 5 * 1000,
  },
});
