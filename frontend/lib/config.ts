/**
 * Configuration settings for the frontend application
 * Manages API endpoints and environment-specific settings
 */

export interface ApiConfig {
  baseUrl: string;
  version: string;
  endpoints: {
    analyze: string;
    upload: string;
    scraper: string;
    test: string;
    testResearchKeywords: string;
    amazonSalesIntelligence: string;
    startAnalysis: string;
    jobStatus: string;
    jobResults: string;
  };
}

export interface AppConfig {
  api: ApiConfig;
  environment: "development" | "production" | "staging";
  features: {
    enableDebugMode: boolean;
    enableAnalytics: boolean;
  };
}

// Environment detection with better fallbacks
const getEnvironment = (): "development" | "production" | "staging" => {
  // Check if we're in browser environment
  if (typeof window !== "undefined") {
    // In browser, check hostname for local development
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      return "development";
    }
  }

  // Check explicit environment variable
  if (process.env.NEXT_PUBLIC_ENVIRONMENT === "staging") {
    return "staging";
  }

  if (process.env.NEXT_PUBLIC_ENVIRONMENT === "production") {
    return "production";
  }

  // Fallback to NODE_ENV
  if (process.env.NODE_ENV === "development") {
    return "development";
  }

  // Default to production for safety
  return "production";
};

// Dynamic API URL detection
const getApiBaseUrl = (): string => {
  const env = getEnvironment();

  // If API URL is explicitly set, use it
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Environment-specific defaults
  switch (env) {
    case "development":
      // Check if we're in browser and detect port
      if (typeof window !== "undefined") {
        const isLocal =
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1";
        if (isLocal) {
          return "http://localhost:8000";
        }
      }
      return "http://localhost:8000";

    case "staging":
      return "https://amazon-sales-agent-staging.onrender.com"; // Update with your staging URL

    case "production":
    default:
      return "https://amazon-sales-agent.onrender.com";
  }
};

// Default configuration values
const DEFAULT_CONFIG = {
  development: {
    baseUrl: "http://localhost:8000",
    version: "v1",
  },
  production: {
    baseUrl: "https://amazon-sales-agent.onrender.com",
    version: "v1",
  },
  staging: {
    baseUrl: "https://amazon-sales-agent-staging.onrender.com", // Update if you have staging
    version: "v1",
  },
};

// Get environment-specific configuration
const getEnvConfig = () => {
  const env = getEnvironment();
  return {
    ...DEFAULT_CONFIG[env],
    baseUrl: getApiBaseUrl(), // Use dynamic URL detection
  };
};

// Main configuration object
export const config: AppConfig = {
  api: {
    baseUrl: getEnvConfig().baseUrl,
    version: getEnvConfig().version,
    endpoints: {
      analyze: "/api/v1/analyze",
      upload: "/api/v1/upload",
      scraper: "/api/v1/scraper",
      test: "/api/v1/test",
      testResearchKeywords: "/api/v1/test-research-keywords",
      amazonSalesIntelligence: "/api/v1/amazon-sales-intelligence",
      startAnalysis: "/api/v1/start-analysis",
      jobStatus: "/api/v1/job-status",
      jobResults: "/api/v1/job-results",
    },
  },
  environment: getEnvironment(),
  features: {
    enableDebugMode:
      getEnvironment() === "development" ||
      process.env.NEXT_PUBLIC_DEBUG_MODE === "true",
    enableAnalytics: getEnvironment() === "production",
  },
};

// Helper functions for API calls
export const getApiUrl = (
  endpoint: keyof typeof config.api.endpoints
): string => {
  return `${config.api.baseUrl}${config.api.endpoints[endpoint]}`;
};

export const getFullApiUrl = (path: string): string => {
  // Remove leading slash if present to avoid double slashes
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const fullUrl = `${config.api.baseUrl}${cleanPath}`;

  // Debug logging in development
  if (config.features.enableDebugMode) {
    console.log(
      `[getFullApiUrl] Input path: "${path}" -> Clean path: "${cleanPath}" -> Full URL: "${fullUrl}"`
    );
  }

  return fullUrl;
};

// Development helpers
export const isDevelopment = (): boolean =>
  config.environment === "development";
export const isProduction = (): boolean => config.environment === "production";
export const isStaging = (): boolean => config.environment === "staging";

// Debug logging helper
export const debugLog = (message: string, data?: unknown): void => {
  if (config.features.enableDebugMode) {
    console.log(`[DEBUG] ${message}`, data || "");
  }
};

// Configuration validation
export const validateConfig = (): boolean => {
  if (!config.api.baseUrl) {
    console.error("API base URL is not configured");
    return false;
  }

  // Log current configuration for debugging
  debugLog("Current configuration", getConfigInfo());

  return true;
};

// Export configuration for debugging
export const getConfigInfo = () => ({
  environment: config.environment,
  apiBaseUrl: config.api.baseUrl,
  endpoints: config.api.endpoints,
  features: config.features,
  detectedEnv: {
    NODE_ENV: process.env.NODE_ENV,
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    hostname:
      typeof window !== "undefined" ? window.location.hostname : "server",
  },
});

// Test function for debugging URL generation
export const testUrlGeneration = () => {
  console.log("=== URL Generation Test ===");
  console.log("Base URL:", config.api.baseUrl);
  console.log("Environment:", config.environment);

  const testPaths = [
    "/api/v1/analyze",
    "/api/v1/upload/csv",
    "/api/v1/test/keyword-agent",
    "api/v1/analyze", // without leading slash
  ];

  testPaths.forEach((path) => {
    console.log(`"${path}" -> "${getFullApiUrl(path)}"`);
  });
  console.log("=== End Test ===");
};

// Runtime configuration check
if (typeof window !== "undefined") {
  // Only run validation in browser
  validateConfig();
}
