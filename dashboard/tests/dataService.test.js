import { describe, test, expect, vi, beforeEach } from 'vitest';
import { fetchVirtuousCycleStatus, transformToDashboardData } from '../src/services/dataService';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      interceptors: {
        response: {
          use: vi.fn()
        }
      }
    }))
  }
}));

describe('Data Service Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchVirtuousCycleStatus', () => {
    test('should fetch data successfully', async () => {
      const mockData = {
        monitoring_active: true,
        langsmith_available: true,
        frameworks_available: true,
        quality_threshold: 0.90,
        last_optimization: null,
        metrics: {
          traces_processed: 24900,
          quality_checks: 156,
          optimizations_triggered: 3,
          improvements_deployed: 2,
          current_quality: 0.947,
          last_update: "2025-08-16T17:43:15.355Z"
        },
        component_status: {
          langsmith_client: true,
          quality_collector: true,
          phase2_orchestrator: true,
          phase3_orchestrator: true,
          phase4_orchestrator: true
        }
      };

      const axios = await import('axios');
      const mockAxiosInstance = axios.default.create();
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await fetchVirtuousCycleStatus();
      expect(result).toHaveProperty('monitoring_active');
      expect(result).toHaveProperty('metrics');
      expect(result).toHaveProperty('component_status');
    });

    test('should handle API errors gracefully', async () => {
      const axios = await import('axios');
      const mockAxiosInstance = axios.default.create();
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      const result = await fetchVirtuousCycleStatus();

      // Should return mock data on error
      expect(result).toHaveProperty('monitoring_active');
      expect(result).toHaveProperty('metrics');
    });
  });

  describe('transformToDashboardData', () => {
    test('should transform API data correctly', () => {
      const apiData = {
        monitoring_active: true,
        metrics: {
          traces_processed: 1000,
          current_quality: 0.95,
          optimizations_triggered: 3
        },
        component_status: {
          langsmith_client: true
        }
      };

      const result = transformToDashboardData(apiData);

      expect(result).toHaveProperty('kpi');
      expect(result).toHaveProperty('phases');
      expect(result).toHaveProperty('activity');
      expect(result).toHaveProperty('charts');
      expect(result).toHaveProperty('systemStatus');
    });

    test('should handle null input', () => {
      const result = transformToDashboardData(null);

      expect(result).toHaveProperty('kpi');
      expect(result).toHaveProperty('phases');
      expect(result.phases.length).toBeGreaterThan(0);
    });

    test('should handle missing metrics', () => {
      const incompleteData = {
        monitoring_active: true
      };

      const result = transformToDashboardData(incompleteData);

      expect(result).toHaveProperty('kpi');
      expect(result.kpi).toHaveProperty('qualityScore');
    });
  });
});
