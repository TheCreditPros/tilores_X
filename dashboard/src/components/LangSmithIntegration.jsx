/**
 * LangSmith Integration Components for tilores_X Dashboard
 *
 * Provides UI components for deep linking and contextual navigation
 * to LangSmith for AI operations investigation.
 */

// React hooks not needed in this component currently
import {
  Button,
  IconButton,
  Chip,
  Stack,
  Typography,
  Box,
  Alert,
  Card,
  CardContent,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip
} from '@mui/material';
import {
  Launch,
  ExpandMore,
  CheckCircle,
  WarningAmber,
  Info,
  HelpOutline
} from '@mui/icons-material';

import {
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
                // Taking action for: alert.title
                // LangSmith context available: langsmithContext.primaryAction.url
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


export default {
  LangSmithButton,
  LangSmithQuickAccess,
  LangSmithKpiCard,
  LangSmithAlert
};
