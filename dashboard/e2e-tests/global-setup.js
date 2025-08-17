/**
 * Global Setup for Playwright E2E Tests
 *
 * Pre-test setup to ensure both frontend and backend services are ready
 * for comprehensive end-to-end testing.
 *
 * Author: Roo (Elite Software Engineer)
 * Created: 2025-08-16
 * Integration: E2E Test Setup
 */

import { chromium } from "@playwright/test";

export default async function globalSetup() {
  console.log("🚀 Starting Global E2E Test Setup...");

  // Launch browser to perform health checks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for frontend to be ready
    console.log("📱 Checking frontend health at http://localhost:3000...");
    await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
    console.log("✅ Frontend is ready");

    // Wait for backend to be ready
    console.log("🔧 Checking backend health at http://localhost:8080...");
    const response = await page.request.get("http://localhost:8080/health");
    if (response.ok()) {
      console.log("✅ Backend is ready");
    } else {
      throw new Error(`Backend health check failed: ${response.status()}`);
    }

    // Check API endpoints
    console.log("🔍 Checking Virtuous Cycle API endpoints...");
    const statusResponse = await page.request.get(
      "http://localhost:8080/v1/virtuous-cycle/status"
    );
    if (statusResponse.ok()) {
      console.log("✅ Virtuous Cycle API is ready");
    } else {
      throw new Error(
        `Virtuous Cycle API check failed: ${statusResponse.status()}`
      );
    }
  } catch (error) {
    console.error("❌ Global setup failed:", error);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }

  console.log("🎉 Global E2E Test Setup Complete");
}
