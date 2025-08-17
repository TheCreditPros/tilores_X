import {
  Analytics,
  CheckCircle,
  CloudDone,
  DarkMode,
  Info,
  LightMode,
  Refresh,
  Speed,
  TrendingUp,
  WarningAmber,
} from "@mui/icons-material";
import {
  Alert,
  Avatar,
  Backdrop,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  createTheme,
  CssBaseline,
  Grid,
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
  Tooltip,
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
  const KpiCard = ({ title, value, trend, icon: Icon, color = "primary" }) => (
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
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );

  const PhaseCard = ({ phase, title, metrics, status = "operational" }) => {
    const statusColors = {
      operational: "success",
      warning: "warning",
      error: "error",
    };

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
            <Chip
              label={status}
              color={statusColors[status]}
              size="small"
              sx={{ textTransform: "capitalize" }}
            />
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

        {/* KPIs */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Overall Quality Score"
              value={data.kpi?.qualityScore?.value || "Loading..."}
              trend={data.kpi?.qualityScore?.trend || null}
              icon={TrendingUp}
              color="success"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Total Traces Processed"
              value={data.kpi?.tracesProcessed?.value || "Loading..."}
              trend={data.kpi?.tracesProcessed?.trend || null}
              icon={Analytics}
              color="info"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="Optimization Triggers"
              value={data.kpi?.optimizationsTriggers?.value || "Loading..."}
              trend={data.kpi?.optimizationsTriggers?.trend || null}
              icon={Speed}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <KpiCard
              title="System Uptime"
              value={data.kpi?.systemUptime?.value || "Loading..."}
              trend={data.kpi?.systemUptime?.trend || null}
              icon={CloudDone}
              color="success"
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
                      <Tooltip
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
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="baseline" fill="#8884d8" name="Baseline" />
                      <Bar dataKey="current" fill="#00ff88" name="Current" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Alerts */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardHeader title="🚨 Active Alerts & Actions" />
              <CardContent>
                <Stack spacing={2}>
                  <Alert severity="error" icon={<WarningAmber />}>
                    <Typography variant="body2">
                      <strong>HIGH:</strong> Edge case handling at 86.4% (below
                      90% threshold)
                    </Typography>
                  </Alert>
                  <Alert severity="warning" icon={<Info />}>
                    <Typography variant="body2">
                      <strong>MEDIUM:</strong> A/B test #47 ready for review
                    </Typography>
                  </Alert>
                  <Alert severity="success" icon={<CheckCircle />}>
                    <Typography variant="body2">
                      <strong>INFO:</strong> Cycle #48 scheduled to start in 2
                      hours
                    </Typography>
                  </Alert>
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
