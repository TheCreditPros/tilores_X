/**
 * LangSmith Integration Service for tilores_X Dashboard
 *
 * Provides deep linking and contextual navigation to LangSmith
 * for AI operations investigation and analysis.
 */

// LangSmith Configuration
const LANGSMITH_CONFIG = {
  BASE_URL: 'https://smith.langchain.com',
  ORG_ID: 'b36f2280-93a9-4523-bf03-707ac1032a33',

  // Project mapping (updated with actual LangSmith projects from workspace)
  PROJECTS: {
    PRODUCTION: 'tilores_x', // Main production project (948 runs)
    EXPERIMENTS: 'tilores-speed-experiments', // Speed optimization experiments (280 runs)
    DEVELOPMENT: 'tilores_unified' // Unified development project (4,543 runs)
  }
};

/**
 * LangSmith URL Builder Service
 */
export const LangSmithService = {
  // Base URLs
  getOrgUrl: () => `${LANGSMITH_CONFIG.BASE_URL}/o/${LANGSMITH_CONFIG.ORG_ID}`,

  getProjectUrl: () =>
    `${LANGSMITH_CONFIG.BASE_URL}/o/${LANGSMITH_CONFIG.ORG_ID}`,

  // Quality Investigation Links
  getQualityTraces: (timeRange = '24h', minScore = 90) =>
    `${LangSmithService.getProjectUrl()}/traces?` +
    `filter=feedback.score<${minScore}&` +
    `timeRange=${timeRange}&` +
    `sort=timestamp:desc`,

  getQualityAnalytics: (dateRange = 'last_24_hours') =>
    `${LangSmithService.getProjectUrl()}/analytics?` +
    `view=quality&` +
    `dateRange=${dateRange}`,

  // Optimization & Experiments
  getOptimizationExperiments: () =>
    `${LangSmithService.getProjectUrl()}/experiments?` +
    `filter=name:optimization&` +
    `status=running`,

  getPhaseExperiment: (phase) =>
    `${LangSmithService.getProjectUrl()}/experiments?` +
    `filter=name:phase_${phase}&` +
    `sort=created_at:desc`,

  getABTestResults: (testName) =>
    `${LangSmithService.getProjectUrl()}/experiments?` +
    `filter=name:${testName}&` +
    `view=results`,

  // Error & Edge Case Analysis
  getEdgeCaseAnalysis: () =>
    `${LangSmithService.getProjectUrl()}/traces?` +
    `filter=tags:edge_case&` +
    `timeRange=24h&` +
    `sort=timestamp:desc`,

  getErrorAnalysis: (errorType, timeRange = '6h') =>
    `${LangSmithService.getProjectUrl()}/traces?` +
    `filter=error:true&` +
    `tags:${errorType}&` +
    `timeRange=${timeRange}`,

  // Model Performance
  getModelComparison: (models = ['gpt-4o-mini', 'llama-3.3-70b']) =>
    `${LangSmithService.getProjectUrl()}/compare?` +
    `models=${models.join(',')}&` +
    `metric=feedback.score`,

  // Virtuous Cycle Specific
  getVirtuousCycleTrace: (cycleId) =>
    `${LangSmithService.getProjectUrl()}/traces?` +
    `filter=tags:virtuous_cycle_${cycleId}&` +
    `sort=timestamp:desc`,

  getPatternAnalysis: (pattern) =>
    `${LangSmithService.getProjectUrl()}/analytics?` +
    `view=patterns&` +
    `filter=pattern:${pattern}`,

  // Datasets
  getTrainingDataset: (datasetName = 'tilores_customer_queries') =>
    `${LangSmithService.getProjectUrl()}/datasets?` +
    `filter=name:${datasetName}`,

  getEdgeCaseDataset: () =>
    `${LangSmithService.getProjectUrl()}/datasets?` +
    `filter=tags:edge_cases`
};

/**
 * Generate contextual LangSmith links based on alert type
 */
export const generateLangSmithContext = (alertType) => {
  switch (alertType) {
    case 'edge_case_handling':
      return {
        primaryAction: {
          label: "View Edge Case Traces",
          url: LangSmithService.getEdgeCaseAnalysis(),
          icon: "🔍"
        },
        secondaryActions: [
          {
            label: "Edge Case Dataset",
            url: LangSmithService.getEdgeCaseDataset(),
            icon: "📚"
          },
          {
            label: "Pattern Analysis",
            url: LangSmithService.getPatternAnalysis('edge_cases'),
            icon: "📊"
          }
        ]
      };

    case 'ai_optimization':
      return {
        primaryAction: {
          label: "View Optimization Experiments",
          url: LangSmithService.getOptimizationExperiments(),
          icon: "🧪"
        },
        secondaryActions: [
          {
            label: "Model Comparison",
            url: LangSmithService.getModelComparison(),
            icon: "⚡"
          },
          {
            label: "Phase 2 Experiments",
            url: LangSmithService.getPhaseExperiment(2),
            icon: "🔬"
          }
        ]
      };

    case 'quality_drop':
      return {
        primaryAction: {
          label: "View Failed Quality Traces",
          url: LangSmithService.getQualityTraces('6h', 90),
          icon: "🚨"
        },
        secondaryActions: [
          {
            label: "Quality Analytics",
            url: LangSmithService.getQualityAnalytics(),
            icon: "📈"
          },
          {
            label: "Error Analysis",
            url: LangSmithService.getErrorAnalysis('quality_failure'),
            icon: "❌"
          }
        ]
      };

    case 'production_integration':
      return {
        primaryAction: {
          label: "View Performance Traces",
          url: LangSmithService.getQualityTraces('1h'),
          icon: "⚡"
        },
        secondaryActions: [
          {
            label: "Model Performance",
            url: LangSmithService.getModelComparison(),
            icon: "📊"
          }
        ]
      };

    default:
      return {
        primaryAction: {
          label: "Open LangSmith",
          url: LangSmithService.getOrgUrl(),
          icon: "🚀"
        },
        secondaryActions: []
      };
  }
};

/**
 * Quick access links for common LangSmith navigation
 */
export const LANGSMITH_QUICK_LINKS = [
  {
    label: "Quality Dashboard",
    url: LangSmithService.getQualityAnalytics(),
    icon: "📊",
    description: "Overall quality metrics and trends"
  },
  {
    label: "Active Experiments",
    url: LangSmithService.getOptimizationExperiments(),
    icon: "🧪",
    description: "Currently running A/B tests"
  },
  {
    label: "Recent Traces",
    url: LangSmithService.getQualityTraces('1h'),
    icon: "🔍",
    description: "Latest customer interactions"
  },
  {
    label: "Model Performance",
    url: LangSmithService.getModelComparison(),
    icon: "⚡",
    description: "Compare model effectiveness"
  }
];

/**
 * Track LangSmith navigation for analytics
 */
export const trackLangSmithNavigation = (linkLabel, sourceComponent) => {
  // Analytics tracking placeholder
  // Will track: ${linkLabel} from ${sourceComponent}
  void linkLabel; // Mark as intentionally unused
  void sourceComponent; // Mark as intentionally unused

  // Optional: Send to analytics service
  // analytics.track('langsmith_navigation', {
  //   label: linkLabel,
  //   source: sourceComponent,
  //   timestamp: new Date().toISOString()
  // });
};

export default LangSmithService;
