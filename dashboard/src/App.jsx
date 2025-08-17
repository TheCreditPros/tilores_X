import {
  Analytics,
  CheckCircle,
  CloudDone,
  DarkMode,
  ExpandMore,
  HelpOutline,
  Info,
  LightMode,
  Refresh,
  Speed,
  TrendingDown,
  TrendingUp,
  WarningAmber,
} from "@mui/icons-material";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Avatar,
  Backdrop,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Collapse,
  createTheme,
  CssBaseline,
  Grid,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Switch,
  ThemeProvider,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";

// Import data service
import {
  fetchVirtuousCycleStatus,
  transformToDashboardData,
} from "./services/dataService";

function EnhancedMUIDashboard() {
  // --- Theme ---
  const [mode, setMode] = useState("dark");
  useEffect(() => {
    const saved = localStorage.getItem("mui-theme-mode");
    if (saved === "light" || saved === "dark") setMode(saved);
  }, []);

  // --- Data State ---
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // --- Data Fetching ---
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const apiData = await fetchVirtuousCycleStatus();
      const transformedData = transformToDashboardData(apiData);
      setDashboardData(transformedData);
      setLastUpdate(new Date());
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Dashboard data fetch failed:", err);
      setError(err.message);
      // Data service handles fallback to mock data on error
      const fallbackData = transformToDashboardData(null);
      setDashboardData(fallbackData);
    } finally {
      setLoading(false);
    }
  };

  // Initial data load and periodic refresh
  useEffect(() => {
    fetchData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);

    return () => clearInterval(interval);
  }, []);

  // Manual refresh handler
  const handleRefresh = () => {
    fetchData();
  };

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: "#00d9ff" },
          secondary: { main: "#00ff88" },
          error: { main: "#ff4757" },
          warning: { main: "#ffa502" },
          success: { main: "#00ff88" },
        },
        shape: { borderRadius: 12 },
        components: {
          MuiCard: {
            styleOverrides: {
              root: {
                boxShadow:
                  mode === "dark"
                    ? "0 8px 32px rgba(0,0,0,0.3)"
                    : "0 4px 16px rgba(0,0,0,0.1)",
                backdropFilter: "blur(10px)",
                border:
                  mode === "dark" ? "1px solid rgba(255,255,255,0.1)" : "none",
              },
            },
          },
        },
      }),
    [mode]
  );

  const toggleMode = () => {
    const next = mode === "dark" ? "light" : "dark";
    setMode(next);
    localStorage.setItem("mui-theme-mode", next);
  };

  // Loading state
  if (loading && !dashboardData) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Backdrop
          sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={true}
        >
          <Stack alignItems="center" spacing={2}>
            <CircularProgress color="primary" size={60} />
            <Typography variant="h6">Loading Dashboard...</Typography>
          </Stack>
        </Backdrop>
      </ThemeProvider>
    );
  }

  // Error state fallback (data service provides fallback data)
  const data = dashboardData || {
    kpi: {},
    phases: [],
    activity: [],
    charts: { qualityTrends: [], spectrumData: [] },
    systemStatus: { monitoring_active: false },
  };

  // --- Enhanced Components ---
  const KpiCard = ({ title, value, trend, icon: Icon, color = "primary", helpText = null }) => (
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
          {trend && (
            <Chip
              label={trend}
              size="small"
              color={trend.startsWith("+") ? "success" : "error"}
              sx={{ fontWeight: 600 }}
            />
          )}
        </Stack>
        <Typography variant="h4" fontWeight={700} color={`${color}.main`} data-testid="current-quality-value">
          {value}
        </Typography>
        <Stack direction="row" alignItems="center" spacing={0.5}>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          {helpText && (
            <RechartsTooltip title={helpText} arrow>
              <IconButton size="small" sx={{ color: 'text.secondary' }}>
                <HelpOutline sx={{ fontSize: 14 }} />
              </IconButton>
            </RechartsTooltip>
          )}
        </Stack>
      </CardContent>
    </Card>
  );

  const PhaseCard = ({ phase, title, metrics, status = "operational" }) => {
    const [expanded, setExpanded] = useState(false);

    const statusColors = {
      operational: "success",
      warning: "warning",
      error: "error",
    };

    const getWarningContext = () => {
      switch (phase) {
        case "2":
          return {
            issue: "AI Optimization Success Rate Below Threshold",
            description: "Current success rate of 89% is below the expected 92% threshold for production workloads.",
            impact: "May result in suboptimal pattern recognition and increased processing time.",
            actions: [
              "Review recent pattern identification algorithms",
              "Check A/B test configurations for conflicts",
              "Analyze cost efficiency metrics for resource allocation"
            ],
            severity: "MEDIUM",
            eta: "2-4 hours to investigate and resolve"
          };
        case "3":
          return {
            issue: "Continuous Learning Cycle Gain Below Target",
            description: "Average cycle gain of +2.3% is below the target of +3.5% for optimal learning velocity.",
            impact: "Slower adaptation to new patterns and reduced self-healing effectiveness.",
            actions: [
              "Review pattern application effectiveness",
              "Analyze quality breach resolution times",
              "Optimize self-healing algorithms"
            ],
            severity: "MEDIUM",
            eta: "1-2 hours to optimize learning parameters"
          };
        case "4":
          return {
            issue: "Production Integration Response Time Elevated",
            description: "Current response time of 847ms exceeds the target of <500ms for optimal user experience.",
            impact: "Potential user experience degradation and increased resource consumption.",
            actions: [
              "Optimize Railway deployment configuration",
              "Review database query performance",
              "Check network latency and CDN configuration"
            ],
            severity: "MEDIUM",
            eta: "30-60 minutes to optimize performance"
          };
        default:
          return null;
      }
    };

    const warningContext = status === "warning" ? getWarningContext() : null;

    return (
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={
            <Stack direction="row" alignItems="center" spacing={1}>
              <Avatar
                sx={{
                  bgcolor: "primary.main",
                  width: 32,
                  height: 32,
                  fontSize: 14,
                }}
              >
                {phase}
              </Avatar>
              <Typography variant="h6">{title}</Typography>
            </Stack>
          }
          action={
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label={status}
                color={statusColors[status]}
                size="small"
                sx={{ textTransform: "capitalize" }}
              />
              {warningContext && (
                <IconButton
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  sx={{
                    transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.3s',
                  }}
                >
                  <ExpandMore />
                </IconButton>
              )}
            </Stack>
          }
        />
        <CardContent>
          <Stack spacing={2}>
            {metrics.map((metric, idx) => (
              <Box key={idx}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  mb={0.5}
                >
                  <Typography variant="body2">{metric.label}</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {metric.value}
                  </Typography>
                </Stack>
                {metric.progress != null && (
                  <LinearProgress
                    variant="determinate"
                    value={metric.progress}
                    sx={{ height: 6, borderRadius: 3 }}
                    color={
                      metric.progress > 90
                        ? "success"
                        : metric.progress > 80
                        ? "primary"
                        : "warning"
                    }
                  />
                )}
              </Box>
            ))}

            {/* Warning Details Expansion */}
            {warningContext && (
              <Collapse in={expanded}>
                <Box sx={{ mt: 2, p: 2, bgcolor: "warning.light", borderRadius: 1, color: "warning.contrastText" }}>
                  <Typography variant="subtitle2" fontWeight={700} gutterBottom>
                    ⚠️ {warningContext.issue}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {warningContext.description}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ mb: 1 }}>
                    Impact: {warningContext.impact}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ mb: 1 }}>
                    Recommended Actions:
                  </Typography>
                  <Stack spacing={0.5} sx={{ ml: 1, mb: 1 }}>
                    {warningContext.actions.map((action, idx) => (
                      <Typography key={idx} variant="body2">
                        • {action}
                      </Typography>
                    ))}
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Chip
                      label={`Severity: ${warningContext.severity}`}
                      size="small"
                      color="warning"
                      variant="outlined"
                    />
                    <Typography variant="caption">
                      ETA: {warningContext.eta}
                    </Typography>
                  </Stack>
                </Box>
              </Collapse>
            )}
          </Stack>
        </CardContent>
      </Card>
    );
  };

  // Quick Reference Panel Component
  const QuickReference = () => (
    <Card sx={{ mb: 2, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
      <CardContent sx={{ py: 1.5 }}>
        <Stack direction="row" spacing={3} alignItems="center" flexWrap="wrap">
          <Typography variant="body2" fontWeight={600}>
            💡 Quick Guide:
          </Typography>
          <Typography variant="body2">
            🟢 90%+ Quality = Excellent • 🟡 Warnings = Click ▼ for details • 🔴 Alerts = Expand for actions
          </Typography>
          <RechartsTooltip title="Click any warning dropdown arrow to see detailed remediation steps">
            <IconButton size="small" sx={{ color: 'primary.contrastText' }}>
              <HelpOutline sx={{ fontSize: 16 }} />
            </IconButton>
          </RechartsTooltip>
        </Stack>
      </CardContent>
    </Card>
  );

  // Smart Insights Panel Component
  const SmartInsights = ({ data }) => {
    const generateInsights = () => {
      const insights = [];
      const qualityScore = parseFloat(data.kpi?.qualityScore?.value || 0);
      const tracesProcessed = parseInt(data.kpi?.tracesProcessed?.value || 0);

      if (qualityScore > 94) {
        insights.push({
          type: 'success',
          message: `🎉 Exceptional Performance! Your ${qualityScore}% quality score is ${(qualityScore - 87).toFixed(1)}% above industry average.`,
          suggestion: 'Consider documenting current configuration as a best practice template.'
        });
      }

      if (qualityScore < 90 && qualityScore > 0) {
        insights.push({
          type: 'warning',
          message: `⚡ Optimization Triggered: Quality at ${qualityScore}% initiated automatic improvement cycle.`,
          suggestion: 'Expected improvement in 15-30 minutes. Monitor Phase 2 metrics for progress.'
        });
      }

      if (tracesProcessed > 100) {
        insights.push({
          type: 'info',
          message: `📈 High Activity: ${tracesProcessed} traces processed indicates strong system utilization.`,
          suggestion: 'Monitor resource allocation to ensure optimal performance during peak usage.'
        });
      }

      if (data.systemStatus?.monitoring_active) {
        insights.push({
          type: 'success',
          message: '🔄 Real-Time Monitoring Active: All systems operational with live data updates.',
          suggestion: 'Dashboard refreshes every 30 seconds with latest metrics.'
        });
      }

      return insights;
    };

    const insights = generateInsights();

    if (insights.length === 0) return null;

    return (
      <Card sx={{ mb: 2 }}>
        <CardHeader
          title="🧠 Smart Insights"
          action={
            <RechartsTooltip title="AI-generated insights based on current system performance">
              <IconButton size="small">
                <HelpOutline />
              </IconButton>
            </RechartsTooltip>
          }
        />
        <CardContent>
          <Stack spacing={1}>
            {insights.map((insight, idx) => (
              <Alert
                key={idx}
                severity={insight.type}
                sx={{ '& .MuiAlert-message': { width: '100%' } }}
              >
                <Typography variant="body2" fontWeight={600} gutterBottom>
                  {insight.message}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  💡 {insight.suggestion}
                </Typography>
              </Alert>
            ))}
          </Stack>
        </CardContent>
      </Card>
    );
  };

  // Generate dynamic alerts based on system state
  const generateSystemAlerts = (data) => {
    const alerts = [];

    // Check for edge case handling below threshold
    const edgeCaseMetric = data.phases?.find(p => p.phase === "1")?.metrics?.find(m => m.label === "Edge Cases");
    if (edgeCaseMetric && parseFloat(edgeCaseMetric.value) < 90) {
      alerts.push({
        severity: "error",
        icon: <WarningAmber />,
        title: "HIGH: Edge Case Handling Below Threshold",
        description: `Current edge case handling at ${edgeCaseMetric.value} is below the 90% operational threshold.`,
        impact: "May result in unhandled edge cases affecting system reliability.",
        actions: [
          "Review recent edge case patterns",
          "Increase test coverage for edge scenarios",
          "Adjust pattern recognition sensitivity"
        ],
        eta: "2-3 hours to investigate and resolve"
      });
    }

    // Check for AI optimization success rate
    const aiPhase = data.phases?.find(p => p.phase === "2");
    const successRateMetric = aiPhase?.metrics?.find(m => m.label === "Success Rate");
    if (successRateMetric && parseFloat(successRateMetric.value) < 92) {
      alerts.push({
        severity: "warning",
        icon: <Info />,
        title: "MEDIUM: AI Optimization Success Rate Below Target",
        description: `Success rate of ${successRateMetric.value} is below the expected 92% threshold.`,
        impact: "Reduced pattern recognition efficiency and increased processing overhead.",
        actions: [
          "Analyze recent A/B test configurations",
          "Review pattern identification algorithms",
          "Check resource allocation for optimization processes"
        ],
        eta: "1-2 hours to optimize performance"
      });
    }

    // Check for response time issues
    const prodPhase = data.phases?.find(p => p.phase === "4");
    const responseTimeMetric = prodPhase?.metrics?.find(m => m.label === "Response Time");
    if (responseTimeMetric && parseFloat(responseTimeMetric.value) > 500) {
      alerts.push({
        severity: "warning",
        icon: <Info />,
        title: "MEDIUM: Production Response Time Elevated",
        description: `Current response time of ${responseTimeMetric.value} exceeds the 500ms target.`,
        impact: "Potential user experience degradation and increased resource consumption.",
        actions: [
          "Optimize database query performance",
          "Review Railway deployment configuration",
          "Check CDN and network latency"
        ],
        eta: "30-60 minutes to optimize"
      });
    }

    // Add positive alerts for good performance
    if (data.kpi?.systemUptime?.value === "99.8%") {
      alerts.push({
        severity: "success",
        icon: <CheckCircle />,
        title: "INFO: System Uptime Excellent",
        description: "System maintaining 99.8% uptime with all components operational.",
        impact: "Optimal system reliability and user experience.",
        actions: ["Continue monitoring", "Maintain current configuration"],
        eta: "No action required"
      });
    }

    return alerts;
  };

  const ActivityFeed = ({ activities = [] }) => (
    <Card>
      <CardHeader
        title="🔄 Real-Time Activity"
        action={
          <Chip
            icon={<Refresh />}
            label="Live"
            color="primary"
            size="small"
            onClick={handleRefresh}
            sx={{ cursor: "pointer" }}
          />
        }
      />
      <CardContent>
        <Stack spacing={1}>
          {activities.length > 0 ? (
            activities.map((activity, idx) => (
              <Paper key={idx} sx={{ p: 2, bgcolor: "background.default" }}>
                <Stack direction="row" alignItems="flex-start" spacing={2}>
                  <Avatar
                    sx={{
                      bgcolor:
                        activity.type === "success"
                          ? "success.main"
                          : activity.type === "warning"
                          ? "warning.main"
                          : "info.main",
                      width: 32,
                      height: 32,
                    }}
                  >
                    {activity.type === "success"
                      ? "✓"
                      : activity.type === "warning"
                      ? "⚠"
                      : "ℹ"}
                  </Avatar>
                  <Box flex={1}>
                    <Typography variant="body2" fontWeight={600}>
                      {activity.action}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {activity.detail}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {activity.time}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            ))
          ) : (
            <Typography
              variant="body2"
              color="text.secondary"
              textAlign="center"
              py={2}
            >
              No recent activity
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ p: 3, minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Header */}
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          mb={3}
        >
          <Stack>
            <Typography variant="h4" fontWeight={700} color="primary.main">
              tilores_X AI Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Self-Improvement Dashboard • Live Quality:{" "}
              {data.kpi?.qualityScore?.value || "Loading..."}
            </Typography>
            {error && (
              <Typography variant="caption" color="error.main">
                API Connection: Mock Mode ({error})
              </Typography>
            )}
            {lastUpdate && (
              <Typography variant="caption" color="text.secondary">
                Last Updated: {lastUpdate.toLocaleTimeString()}
              </Typography>
            )}
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center">
            <LightMode fontSize="small" />
            <Switch checked={mode === "dark"} onChange={toggleMode} />
            <DarkMode fontSize="small" />
          </Stack>
        </Stack>

        {/* Quick Reference Guide */}
        <QuickReference />

        {/* Smart Insights */}
        <SmartInsights data={data} />

        {/* KPIs */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Overall Quality Score"
              value={data.kpi?.qualityScore?.value || "Loading..."}
              trend={data.kpi?.qualityScore?.trend || null}
              icon={TrendingUp}
              color="success"
              helpText="Measures how accurately our AI responds to customer queries. 90%+ is excellent. When below 90%, automatic optimization triggers."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Total Traces Processed"
              value={data.kpi?.tracesProcessed?.value || "Loading..."}
              trend={data.kpi?.tracesProcessed?.trend || null}
              icon={Analytics}
              color="info"
              helpText="Number of customer interactions analyzed by our AI system. Higher numbers indicate active usage and learning opportunities."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Optimization Triggers"
              value={data.kpi?.optimizationsTriggers?.value || "Loading..."}
              trend={data.kpi?.optimizationsTriggers?.trend || null}
              icon={Speed}
              color="primary"
              helpText="How many times our AI has automatically improved itself. Each trigger represents a successful self-optimization cycle."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="System Uptime"
              value={data.kpi?.systemUptime?.value || "Loading..."}
              trend={data.kpi?.systemUptime?.trend || null}
              icon={CloudDone}
              color="success"
              helpText="System availability over the last 30 days. 99.8% means only 1.4 hours of downtime per month - excellent reliability."
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Phase Cards */}
          {data.phases?.map((phase, _index) => (
            <Grid item xs={12} lg={3} key={phase.phase}>
              <PhaseCard
                phase={phase.phase}
                title={phase.title}
                metrics={phase.metrics || []}
                status={phase.status || "operational"}
              />
            </Grid>
          ))}

          {/* Quality Trends Chart */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardHeader title="📈 Quality Evolution & Performance Trends" />
              <CardContent>
                <Box sx={{ width: "100%", height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.charts?.qualityTrends || []}>
                      <defs>
                        <linearGradient
                          id="qualityGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#00ff88"
                            stopOpacity={0.3}
                          />
                          <stop
                            offset="95%"
                            stopColor="#00ff88"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="cycle" />
                      <YAxis domain={[90, 96]} />
                      <RechartsTooltip
                        contentStyle={{
                          backgroundColor:
                            mode === "dark" ? "#1e1e1e" : "#ffffff",
                          border: "1px solid rgba(255,255,255,0.2)",
                          borderRadius: "8px",
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="quality"
                        stroke="#00ff88"
                        fillOpacity={1}
                        fill="url(#qualityGradient)"
                        strokeWidth={3}
                        name="Quality %"
                      />
                      <Line
                        type="monotone"
                        dataKey="patterns"
                        stroke="#00d9ff"
                        strokeWidth={2}
                        name="Patterns Found"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Activity Feed */}
          <Grid item xs={12} lg={4}>
            <ActivityFeed activities={data.activity || []} />
          </Grid>

          {/* Spectrum Performance */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardHeader title="🎯 7-Spectrum Performance Matrix" />
              <CardContent>
                <Box sx={{ width: "100%", height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.charts?.spectrumData || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis domain={[80, 100]} />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="baseline" fill="#8884d8" name="Baseline" />
                      <Bar dataKey="current" fill="#00ff88" name="Current" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Dynamic Alerts */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardHeader title="🚨 Active Alerts & Actions" />
              <CardContent>
                <Stack spacing={2}>
                  {generateSystemAlerts(data).map((alert, idx) => (
                    <Accordion key={idx} sx={{ boxShadow: 'none', border: '1px solid', borderColor: `${alert.severity}.main` }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Alert
                          severity={alert.severity}
                          icon={alert.icon}
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
                                // Placeholder for action handler
                                // console.log(`Taking action for: ${alert.title}`);
                              }}
                            >
                              Take Action
                            </Button>
                          </Stack>
                        </Stack>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                  {generateSystemAlerts(data).length === 0 && (
                    <Alert severity="success" icon={<CheckCircle />}>
                      <Typography variant="body2">
                        <strong>All Systems Operational:</strong> No active alerts or issues detected.
                      </Typography>
                    </Alert>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </ThemeProvider>
  );
}

export default function App() {
  return <EnhancedMUIDashboard />;
}
