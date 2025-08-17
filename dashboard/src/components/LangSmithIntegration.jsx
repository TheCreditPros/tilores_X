/**
 * LangSmith Integration Components for tilores_X Dashboard
 *
 * Provides UI components for deep linking and contextual navigation
 * to LangSmith for AI operations investigation.
 */

import React, { useState } from 'react';
import {
  Button,
  IconButton,
  Chip,
  Stack,
  Typography,
  Box,
  Alert,
  Card,
  CardHeader,
  CardContent,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Launch,
  Analytics,
  ExpandMore,
  Science,
  TrendingUp,
  CheckCircle,
  WarningAmber,
  Info
} from '@mui/icons-material';

import {
  LangSmithService,
  generateLangSmithContext,
  LANGSMITH_QUICK_LINKS,
  trackLangSmithNavigation
} from '../services/langsmithService';

/**
 * LangSmith Navigation Button Component
 */
export const LangSmithButton = ({
  link,
  variant = "outlined",
  size = "small",
  fullWidth = false,
  sourceComponent = "dashboard"
}) => {
  const handleNavigation = () => {
    trackLangSmithNavigation(link.label, sourceComponent);
    window.open(link.url, '_blank', 'noopener,noreferrer');
  };

  return (
    <Button
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      startIcon={link.icon ? <span>{link.icon}</span> : <Launch />}
      onClick={handleNavigation}
      sx={{
        textTransform: 'none',
        borderColor: 'primary.main',
        '&:hover': {
          bgcolor: 'primary.main',
          color: 'primary.contrastText'
        }
      }}
    >
      {link.label}
    </Button>
  );
};

/**
 * LangSmith Quick Access Panel
 */
export const LangSmithQuickAccess = () => {
  return (
    <Card sx={{ mb: 2, bgcolor: 'info.main', color: 'info.contrastText' }}>
      <CardContent sx={{ py: 1.5 }}>
        <Stack direction="row" spacing={3} alignItems="center" flexWrap="wrap">
          <Typography variant="body2" fontWeight={600}>
            🚀 LangSmith Quick Access:
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {LANGSMITH_QUICK_LINKS.map((link, idx) => (
              <Button
                key={idx}
                size="small"
                variant="outlined"
                startIcon={<span>{link.icon}</span>}
                onClick={() => {
                  trackLangSmithNavigation(link.label, 'quick_access');
                  window.open(link.url, '_blank');
                }}
                sx={{
                  color: 'info.contrastText',
                  borderColor: 'info.contrastText',
                  textTransform: 'none',
                  '&:hover': {
                    bgcolor: 'info.contrastText',
                    color: 'info.main'
                  }
                }}
              >
                {link.label}
              </Button>
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
};

/**
 * Enhanced KPI Card with LangSmith Integration
 */
export const LangSmithKpiCard = ({
  title,
  value,
  trend,
  icon: Icon,
  color = "primary",
  helpText = null,
  langsmithLink = null
}) => (
  <Card sx={{ height: "100%" }}>
    <CardContent>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        mb={1}
      >
        <Avatar sx={{ bgcolor: `${color}.main`, width: 40, height: 40 }}>
          <Icon />
        </Avatar>
        <Stack direction="row" spacing={0.5} alignItems="center">
          {trend && (
            <Chip
              label={trend}
              size="small"
              color={trend.startsWith("+") ? "success" : "error"}
              sx={{ fontWeight: 600 }}
            />
          )}
          {/* LangSmith Quick Link */}
          {langsmithLink && (
            <IconButton
              size="small"
              onClick={() => {
                trackLangSmithNavigation(`${title} Analysis`, 'kpi_card');
                window.open(langsmithLink, '_blank');
              }}
              sx={{ color: 'primary.main' }}
              title="Investigate in LangSmith"
            >
              <Launch sx={{ fontSize: 16 }} />
            </IconButton>
          )}
        </Stack>
      </Stack>

      <Typography variant="h4" fontWeight={700} color={`${color}.main`} data-testid="current-quality-value">
        {value}
      </Typography>

      <Stack direction="row" alignItems="center" spacing={0.5}>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
        {helpText && (
          <Tooltip title={helpText} arrow>
            <IconButton size="small" sx={{ color: 'text.secondary' }}>
              <HelpOutline sx={{ fontSize: 14 }} />
            </IconButton>
          </Tooltip>
        )}
      </Stack>
    </CardContent>
  </Card>
);

/**
 * Enhanced Alert with LangSmith Investigation Links
 */
export const LangSmithAlert = ({ alert }) => {
  const langsmithContext = generateLangSmithContext(alert.id, alert.data);

  return (
    <Accordion sx={{ boxShadow: 'none', border: '1px solid', borderColor: `${alert.severity}.main` }}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Alert
          severity={alert.severity}
          icon={alert.severity === 'error' ? <WarningAmber /> : alert.severity === 'warning' ? <Info /> : <CheckCircle />}
          sx={{ width: '100%', '& .MuiAlert-message': { width: '100%' } }}
        >
          <Typography variant="body2" fontWeight={600}>
            {alert.title}
          </Typography>
        </Alert>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={2}>
          <Typography variant="body2">
            <strong>Description:</strong> {alert.description}
          </Typography>
          <Typography variant="body2">
            <strong>Impact:</strong> {alert.impact}
          </Typography>

          {/* LangSmith Investigation Section */}
          <Box sx={{
            p: 2,
            bgcolor: 'primary.light',
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'primary.main'
          }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              🔬 Investigate in LangSmith
            </Typography>

            {/* Primary Investigation Action */}
            <Box sx={{ mb: 2 }}>
              <LangSmithButton
                link={langsmithContext.primaryAction}
                variant="contained"
                fullWidth
                sourceComponent="alert_investigation"
              />
            </Box>

            {/* Secondary Investigation Actions */}
            {langsmithContext.secondaryActions.length > 0 && (
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {langsmithContext.secondaryActions.map((link, idx) => (
                  <LangSmithButton
                    key={idx}
                    link={link}
                    variant="outlined"
                    size="small"
                    sourceComponent="alert_secondary"
                  />
                ))}
              </Stack>
            )}
          </Box>

          {/* Recommended Actions */}
          <Box>
            <Typography variant="body2" fontWeight={600} gutterBottom>
              Recommended Actions:
            </Typography>
            <Stack spacing={0.5} sx={{ ml: 1 }}>
              {alert.actions.map((action, actionIdx) => (
                <Typography key={actionIdx} variant="body2">
                  • {action}
                </Typography>
              ))}
            </Stack>
          </Box>

          {/* Action Buttons */}
          <Stack direction="row" spacing={2} alignItems="center">
            <Chip
              label={`ETA: ${alert.eta}`}
              size="small"
              variant="outlined"
            />
            <Button
              size="small"
              variant="outlined"
              color={alert.severity}
              onClick={() => {
                // Enhanced action handler with LangSmith context
                console.log(`Taking action for: ${alert.title}`);
                console.log(`LangSmith context available: ${langsmithContext.primaryAction.url}`);
              }}
            >
              Take Action
            </Button>
          </Stack>
        </Stack>
      </AccordionDetails>
    </Accordion>
  );
};

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

export default {
  LangSmithButton,
  LangSmithQuickAccess,
  LangSmithKpiCard,
  LangSmithAlert,
  generateLangSmithEnhancedAlerts
};
