/**
 * LangSmith Alert Generation Utilities
 * Separated from LangSmithIntegration.jsx to fix React refresh warning
 */

/**
 * Generate LangSmith-enhanced alerts based on system state
 */
export const generateLangSmithEnhancedAlerts = (data) => {
  const alerts = [];

  // Edge Case Handling Alert
  const edgeCaseMetric = data.phases?.find(p => p.phase === "1")?.metrics?.find(m => m.label === "Edge Cases");
  if (edgeCaseMetric && parseFloat(edgeCaseMetric.value) < 90) {
    alerts.push({
      id: 'edge_case_handling',
      severity: "error",
      title: "HIGH: Edge Case Handling Below Threshold",
      description: `Current edge case handling at ${edgeCaseMetric.value} is below the 90% operational threshold.`,
      impact: "May result in unhandled edge cases affecting system reliability.",
      actions: [
        "Review recent edge case patterns",
        "Increase test coverage for edge scenarios",
        "Adjust pattern recognition sensitivity"
      ],
      eta: "2-3 hours to investigate and resolve",
      data: { metric: edgeCaseMetric.value }
    });
  }

  // AI Optimization Alert
  const aiPhase = data.phases?.find(p => p.phase === "2");
  const successRateMetric = aiPhase?.metrics?.find(m => m.label === "Success Rate");
  if (successRateMetric && parseFloat(successRateMetric.value) < 92) {
    alerts.push({
      id: 'ai_optimization',
      severity: "warning",
      title: "MEDIUM: AI Optimization Success Rate Below Target",
      description: `Success rate of ${successRateMetric.value} is below the expected 92% threshold.`,
      impact: "Reduced pattern recognition efficiency and increased processing overhead.",
      actions: [
        "Analyze recent A/B test configurations",
        "Review pattern identification algorithms",
        "Check resource allocation for optimization processes"
      ],
      eta: "1-2 hours to optimize performance",
      data: { successRate: successRateMetric.value, phase: 2 }
    });
  }

  // Quality Score Alert
  const qualityScore = parseFloat(data.kpi?.qualityScore?.value || 100);
  if (qualityScore < 90) {
    alerts.push({
      id: 'quality_drop',
      severity: "error",
      title: "CRITICAL: Quality Score Below Threshold",
      description: `Overall quality score at ${qualityScore}% has dropped below the 90% threshold.`,
      impact: "Direct impact on customer experience and system reliability.",
      actions: [
        "Trigger immediate optimization cycle",
        "Review recent model changes",
        "Analyze customer feedback patterns"
      ],
      eta: "30-60 minutes for emergency response",
      data: { qualityScore }
    });
  }

  // Production Integration Alert
  const prodPhase = data.phases?.find(p => p.phase === "4");
  const responseTimeMetric = prodPhase?.metrics?.find(m => m.label === "Response Time");
  if (responseTimeMetric && parseFloat(responseTimeMetric.value) > 500) {
    alerts.push({
      id: 'production_integration',
      severity: "warning",
      title: "MEDIUM: Production Response Time Elevated",
      description: `Current response time of ${responseTimeMetric.value} exceeds the 500ms target.`,
      impact: "Potential user experience degradation and increased resource consumption.",
      actions: [
        "Optimize database query performance",
        "Review Railway deployment configuration",
        "Check CDN and network latency"
      ],
      eta: "30-60 minutes to optimize",
      data: { responseTime: responseTimeMetric.value }
    });
  }

  // Positive System Performance Alert
  if (data.kpi?.systemUptime?.value === "99.8%") {
    alerts.push({
      id: 'system_excellent',
      severity: "success",
      title: "INFO: System Performance Excellent",
      description: "System maintaining 99.8% uptime with optimal performance metrics.",
      impact: "Excellent system reliability and user experience.",
      actions: ["Continue monitoring", "Document current configuration"],
      eta: "No action required",
      data: { uptime: "99.8%" }
    });
  }

  return alerts;
};
