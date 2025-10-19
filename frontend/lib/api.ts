/**
 * API Client for Amazon Sales Agent Frontend
 * Centralized HTTP client with proper error handling and configuration
 */

import { getFullApiUrl, debugLog, config } from "./config";

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface AnalysisStatus {
  analysis_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  current_step: string;
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  error?: string;
  results?: unknown;
}

export interface AnalysisRequest {
  asin_or_url: string;
  marketplace: string;
  main_keyword?: string;
  revenue_csv: File;
  design_csv: File;
}

// HTTP Client configuration
const DEFAULT_TIMEOUT = parseInt(
  process.env.NEXT_PUBLIC_API_TIMEOUT || "30000"
);

class ApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    // Use the configuration system for environment-aware URL
    this.baseUrl = config.api.baseUrl;
    this.timeout = DEFAULT_TIMEOUT;
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = endpoint.startsWith("http")
      ? endpoint
      : getFullApiUrl(endpoint);

    debugLog("API Request", { url, method: options.method || "GET" });

    // Set up abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      debugLog("API Response", { url, status: response.status, data });

      return {
        success: true,
        data,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      debugLog("API Error", { url, error: errorMessage });

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // File upload method
  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<ApiResponse<T>> {
    const url = getFullApiUrl(endpoint);

    debugLog("File Upload Request", { url });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout * 2); // Double timeout for uploads

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      debugLog("Upload Response", { url, status: response.status, data });

      return {
        success: true,
        data,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      debugLog("Upload Error", { url, error: errorMessage });

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // GET request
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  // POST request
  async post<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // Specific API methods

  /**
   * Start a new analysis
   */
  async startAnalysis(
    request: AnalysisRequest
  ): Promise<
    ApiResponse<{
      analysis_id: string;
      status_url: string;
      results_url: string;
    }>
  > {
    const formData = new FormData();
    formData.append("asin_or_url", request.asin_or_url);
    formData.append("marketplace", request.marketplace);
    if (request.main_keyword) {
      formData.append("main_keyword", request.main_keyword);
    }
    formData.append("revenue_csv", request.revenue_csv);
    formData.append("design_csv", request.design_csv);

    return this.uploadRequest("/api/v1/analyze", formData);
  }

  /**
   * Get analysis status
   */
  async getAnalysisStatus(
    analysisId: string
  ): Promise<ApiResponse<AnalysisStatus>> {
    return this.get(`/api/v1/analyze/${analysisId}/status`);
  }

  /**
   * Get analysis results
   */
  async getAnalysisResults(analysisId: string): Promise<ApiResponse<unknown>> {
    return this.get(`/api/v1/analyze/${analysisId}/results`);
  }

  /**
   * Delete analysis
   */
  async deleteAnalysis(
    analysisId: string
  ): Promise<ApiResponse<{ message: string }>> {
    return this.delete(`/api/v1/analyze/${analysisId}`);
  }

  /**
   * List all analyses
   */
  async listAnalyses(): Promise<ApiResponse<{ analyses: AnalysisStatus[] }>> {
    return this.get("/api/v1/analyze");
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<ApiResponse<unknown>> {
    return this.get("/api/v1/test");
  }

  /**
   * Upload CSV files
   */
  async uploadCSV(file: File): Promise<ApiResponse<unknown>> {
    const formData = new FormData();
    formData.append("file", file);

    return this.uploadRequest("/api/v1/upload", formData);
  }

  /**
   * Scrape Amazon product
   */
  async scrapeProduct(
    asin: string,
    marketplace: string = "US"
  ): Promise<ApiResponse<unknown>> {
    return this.post("/api/v1/scraper", { asin, marketplace });
  }

  /**
   * Test Research Keywords endpoint - Complete pipeline analysis
   */
  async testResearchKeywords(request: {
    asin_or_url: string;
    marketplace?: string;
    main_keyword?: string;
    revenue_csv?: File;
    design_csv?: File;
  }): Promise<ApiResponse<unknown>> {
    const formData = new FormData();
    formData.append("asin_or_url", request.asin_or_url);
    formData.append("marketplace", request.marketplace || "US");
    if (request.main_keyword) {
      formData.append("main_keyword", request.main_keyword);
    }
    if (request.revenue_csv) {
      formData.append("revenue_csv", request.revenue_csv);
    }
    if (request.design_csv) {
      formData.append("design_csv", request.design_csv);
    }

    return this.longRunningUploadRequest(
      "/api/v1/amazon-sales-intelligence",
      formData
    );
  }

  /**
   * Amazon Sales Intelligence endpoint - Production pipeline analysis
   */
  async amazonSalesIntelligence(request: {
    asin_or_url: string;
    marketplace?: string;
    main_keyword?: string;
    revenue_csv?: File;
    design_csv?: File;
  }): Promise<ApiResponse<unknown>> {
    const formData = new FormData();
    formData.append("asin_or_url", request.asin_or_url);
    formData.append("marketplace", request.marketplace || "US");
    if (request.main_keyword) {
      formData.append("main_keyword", request.main_keyword);
    }
    if (request.revenue_csv) {
      formData.append("revenue_csv", request.revenue_csv);
    }
    if (request.design_csv) {
      formData.append("design_csv", request.design_csv);
    }

    return this.longRunningUploadRequest(
      "/api/v1/amazon-sales-intelligence",
      formData
    );
  }

  // Special method for long-running requests with extended timeout
  private async longRunningUploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<ApiResponse<T>> {
    const url = getFullApiUrl(endpoint);

    debugLog("Long-running Upload Request", { url });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000000); // 5 minutes timeout

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      debugLog("Long-running Upload Response", {
        url,
        status: response.status,
        data,
      });

      return {
        success: true,
        data,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      debugLog("Long-running Upload Error", { url, error: errorMessage });

      return {
        success: false,
        error: errorMessage,
      };
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export convenience methods
export const api = {
  startAnalysis: (request: AnalysisRequest) => apiClient.startAnalysis(request),
  getAnalysisStatus: (analysisId: string) =>
    apiClient.getAnalysisStatus(analysisId),
  getAnalysisResults: (analysisId: string) =>
    apiClient.getAnalysisResults(analysisId),
  deleteAnalysis: (analysisId: string) => apiClient.deleteAnalysis(analysisId),
  listAnalyses: () => apiClient.listAnalyses(),
  testConnection: () => apiClient.testConnection(),
  uploadCSV: (file: File) => apiClient.uploadCSV(file),
  scrapeProduct: (asin: string, marketplace?: string) =>
    apiClient.scrapeProduct(asin, marketplace),
  testResearchKeywords: (request: {
    asin_or_url: string;
    marketplace?: string;
    main_keyword?: string;
    revenue_csv?: File;
    design_csv?: File;
  }) => apiClient.testResearchKeywords(request),
  amazonSalesIntelligence: (request: {
    asin_or_url: string;
    marketplace?: string;
    main_keyword?: string;
    revenue_csv?: File;
    design_csv?: File;
  }) => apiClient.amazonSalesIntelligence(request),
};

export default apiClient;
