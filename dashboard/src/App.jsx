import {
  Analytics,
  CheckCircle,
  CloudDone,
  DarkMode,
  ExpandMore,
  HelpOutline,
  LightMode,
  Refresh,
  Speed,
  TrendingUp,
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
  fetchAIChangesHistory,
  transformToDashboardData,
} from "./services/dataService";

// Import LangSmith integration
import {
  LangSmithQuickAccess,
  LangSmithKpiCard,
} from "./components/LangSmithIntegration";
import { generateLangSmithEnhancedAlerts } from "./utils/langsmithAlerts";
import { LangSmithService } from "./services/langsmithService";

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
  const [aiChangesData, setAiChangesData] = useState(null);
  const [aiChangesLoading, setAiChangesLoading] = useState(false);

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
      // No fallback data - dashboard requires real API connection
      setDashboardData(null);
    } finally {
      setLoading(false);
    }
  };

  // --- AI Changes Data Fetching ---
  const fetchAIChanges = async () => {
    try {
      setAiChangesLoading(true);
      const changesData = await fetchAIChangesHistory(10); // Get last 10 changes
      setAiChangesData(changesData);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("AI changes fetch failed:", err);
      setAiChangesData({
        recent_changes: [],
        summary: { error: err.message },
        governance: { rollback_available: false }
      });
    } finally {
      setAiChangesLoading(false);
    }
  };

  // Initial data load and periodic refresh
  useEffect(() => {
    fetchData();
    fetchAIChanges();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchData();
      fetchAIChanges();
    }, 30000);

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

  // Error state - show error message if no data available
  if (error && !dashboardData) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ p: 3, minHeight: "100vh", bgcolor: "background.default" }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Dashboard Unavailable
            </Typography>
            <Typography variant="body2">
              Cannot connect to tilores_X API: {error}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Please ensure the API server is running and accessible.
            </Typography>
            <Button
              variant="outlined"
              onClick={handleRefresh}
              sx={{ mt: 2 }}
              startIcon={<Refresh />}
            >
              Retry Connection
            </Button>
          </Alert>
        </Box>
      </ThemeProvider>
    );
  }

  const data = dashboardData || {
    kpi: {},
    phases: [],
    activity: [],
    charts: { qualityTrends: [], spectrumData: [] },
    systemStatus: { monitoring_active: false },
  };

  // --- Enhanced Components ---
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

  // AI Change Details Component for Governance and Rollback
  const AIChangeDetails = ({ changesData, loading: changesLoading }) => {
    const [expanded, setExpanded] = useState(false);

    if (changesLoading) {
      return (
        <Card sx={{ mt: 3 }}>
          <CardHeader title="🤖 AI Change Details - Governance & Rollback" />
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={2}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                Loading AI changes...
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      );
    }

    const changes = changesData?.recent_changes || [];
    const summary = changesData?.summary || {};
    const governance = changesData?.governance || {};

    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader
          title="🤖 AI Change Details - Governance & Rollback"
          action={
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label={governance.rollback_available ? "Rollback Available" : "No Rollback"}
                color={governance.rollback_available ? "success" : "default"}
                size="small"
              />
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
            </Stack>
          }
        />
        <CardContent>
          {/* Summary Stats */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={3}>
              <Typography variant="caption" color="text.secondary">Total Changes</Typography>
              <Typography variant="h6">{summary.total_changes_tracked || 0}</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" color="text.secondary">Success Rate</Typography>
              <Typography variant="h6" color="success.main">{summary.success_rate || "N/A"}</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" color="text.secondary">Quality Threshold</Typography>
              <Typography variant="h6">{governance.quality_threshold || "90%"}</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" color="text.secondary">Auto-Optimization</Typography>
              <Typography variant="h6" color={governance.auto_optimization_enabled ? "success.main" : "warning.main"}>
                {governance.auto_optimization_enabled ? "Enabled" : "Disabled"}
              </Typography>
            </Grid>
          </Grid>

          {/* Recent Changes */}
          <Collapse in={expanded}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                📋 Recent AI Changes & Optimizations
              </Typography>
              {changes.length > 0 ? (
                <Stack spacing={1}>
                  {changes.map((change, idx) => (
                    <Paper key={idx} sx={{ p: 2, bgcolor: "background.default" }}>
                      <Stack spacing={1}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" fontWeight={600}>
                            {change.type === "optimization_cycle" ? "🔧 Optimization Cycle" :
                             change.type === "optimization_failure" ? "❌ Optimization Failed" :
                             "🔄 AI Change"}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(change.timestamp).toLocaleString()}
                          </Typography>
                        </Stack>

                        <Typography variant="body2" color="text.secondary">
                          <strong>Trigger:</strong> {change.trigger_reason || "Unknown"}
                        </Typography>

                        {change.quality_score_before && (
                          <Typography variant="body2" color="text.secondary">
                            <strong>Quality Before:</strong> {(change.quality_score_before * 100).toFixed(1)}%
                          </Typography>
                        )}

                        {change.components_executed && change.components_executed.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            <strong>Components:</strong> {change.components_executed.join(", ")}
                          </Typography>
                        )}

                        {change.improvements_identified && change.improvements_identified.length > 0 && (
                          <Typography variant="body2" color="success.main">
                            <strong>Improvements:</strong> {change.improvements_identified.length} identified
                          </Typography>
                        )}

                        {change.error && (
                          <Typography variant="body2" color="error.main">
                            <strong>Error:</strong> {change.error}
                          </Typography>
                        )}

                        <Typography variant="caption" color="text.secondary">
                          ID: {change.change_id || change.cycle_id || "Unknown"}
                        </Typography>
                      </Stack>
                    </Paper>
                  ))}
                </Stack>
              ) : (
                <Alert severity="info">
                  <Typography variant="body2">
                    No AI changes recorded yet. The system will track optimization cycles, improvements, and changes here for governance and rollback purposes.
                  </Typography>
                </Alert>
              )}

              {/* Governance Information */}
              {governance.last_known_good_state && (
                <Box sx={{ mt: 2, p: 2, bgcolor: "success.light", borderRadius: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom color="success.contrastText">
                    🛡️ Last Known Good State (Rollback Point)
                  </Typography>
                  <Typography variant="body2" color="success.contrastText">
                    <strong>Cycle ID:</strong> {governance.last_known_good_state.cycle_id}
                  </Typography>
                  <Typography variant="body2" color="success.contrastText">
                    <strong>Quality:</strong> {(governance.last_known_good_state.quality_score * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="success.contrastText">
                    <strong>Improvements:</strong> {governance.last_known_good_state.improvements}
                  </Typography>
                  <Typography variant="caption" color="success.contrastText">
                    {new Date(governance.last_known_good_state.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              )}
            </Box>
          </Collapse>

          {summary.error && (
            <Alert severity="warning" sx={{ mt: 1 }}>
              <Typography variant="body2">
                AI Changes API: {summary.error}
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

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
                API Connection Failed: {error}
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

        {/* LangSmith Quick Access */}
        <LangSmithQuickAccess />

        {/* Smart Insights */}
        <SmartInsights data={data} />

        {/* KPIs */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <LangSmithKpiCard
              title="Overall Quality Score"
              value={data.kpi?.qualityScore?.value || "Loading..."}
              trend={data.kpi?.qualityScore?.trend || null}
              icon={TrendingUp}
              color="success"
              helpText="Measures how accurately our AI responds to customer queries. 90%+ is excellent. When below 90%, automatic optimization triggers."
              langsmithLink={LangSmithService.getQualityAnalytics()}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <LangSmithKpiCard
              title="Total Traces Processed"
              value={data.kpi?.tracesProcessed?.value || "Loading..."}
              trend={data.kpi?.tracesProcessed?.trend || null}
              icon={Analytics}
              color="info"
              helpText="Number of customer interactions analyzed by our AI system. Higher numbers indicate active usage and learning opportunities."
              langsmithLink={LangSmithService.getQualityTraces('1h')}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <LangSmithKpiCard
              title="Optimization Triggers"
              value={data.kpi?.optimizationsTriggers?.value || "Loading..."}
              trend={data.kpi?.optimizationsTriggers?.trend || null}
              icon={Speed}
              color="primary"
              helpText="How many times our AI has automatically improved itself. Each trigger represents a successful self-optimization cycle."
              langsmithLink={LangSmithService.getOptimizationExperiments()}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <LangSmithKpiCard
              title="System Uptime"
              value={data.kpi?.systemUptime?.value || "Loading..."}
              trend={data.kpi?.systemUptime?.trend || null}
              icon={CloudDone}
              color="success"
              helpText="System availability over the last 30 days. 99.8% means only 1.4 hours of downtime per month - excellent reliability."
              langsmithLink={LangSmithService.getModelComparison()}
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
                  {generateLangSmithEnhancedAlerts(data).map((alert, idx) => (
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
                  {generateLangSmithEnhancedAlerts(data).length === 0 && (
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

        {/* AI Change Details Section for Governance and Rollback */}
        <AIChangeDetails changesData={aiChangesData} loading={aiChangesLoading} />

        {/* Version Footer */}
        <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
            tilores_X Dashboard v1.0.0 • Build: {new Date().toISOString().slice(0,16).replace('T', ' ')} •
            LangSmith Integration: {data.systemStatus?.monitoring_active ? 'Active' : 'Inactive'} •
            Commit: b071436
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default function App() {
  return <EnhancedMUIDashboard />;
}
