"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  ArrowRight,
  Upload,
  Search,
  BarChart3,
  FileText,
} from "lucide-react";
import { getFullApiUrl } from "@/lib/config";
import ResultsDisplay from "@/components/dashboard/results-display";

interface AnalysisStatus {
  analysis_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  current_step: string;
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  error?: string;
  results?: AnalysisResults;
}

interface AnalysisResults {
  analysis_id: string;
  input: {
    asin_or_url: string;
    marketplace: string;
    main_keyword?: string;
    revenue_keywords_count: number;
    design_keywords_count: number;
  };
  research_analysis: {
    success: boolean;
    asin: string;
    marketplace: string;
    main_keyword?: string;
    revenue_competitors: number;
    design_competitors: number;
    product_attributes: {
      category: string;
      brand: string;
      title: string;
    };
  };
  keyword_analysis: {
    total_keywords: number;
    processed_keywords: number;
    categories_found: number;
    processing_time: number;
    data_quality_score: number;
  };
  scoring_analysis: {
    total_analyzed: number;
    priority_distribution: {
      critical: number;
      high: number;
      medium: number;
      low: number;
      filtered: number;
    };
    top_critical_keywords: Array<{
      keyword: string;
      intent_score: number;
      priority_score: number;
      search_volume?: number;
      opportunity_score: number;
    }>;
    top_opportunities: Array<{
      keyword: string;
      opportunity_score: number;
      opportunity_type: string;
      search_volume?: number;
    }>;
  };
  seo_recommendations: {
    title_optimization: {
      current_title: string;
      recommended_title: string;
      keywords_added: string[];
      improvement_score: number;
    };
    bullet_points: {
      recommended_bullets: string[];
      keywords_coverage: number;
    };
    backend_keywords: {
      recommended_keywords: string[];
      character_count: number;
      coverage_improvement: string;
    };
    content_gaps: string[];
    competitive_advantages: string[];
  };
  summary: {
    total_processing_time: string;
    confidence_score: number;
    actionable_keywords: number;
    quick_wins: number;
  };
}

type ResearchStep = "input" | "upload" | "processing" | "results";

export default function ResearchPage() {
  const [currentStep, setCurrentStep] = useState<ResearchStep>("input");
  const [asinOrUrl, setAsinOrUrl] = useState("");
  const [marketplace, setMarketplace] = useState("US");
  const [mainKeyword, setMainKeyword] = useState("");
  const [revenueFile, setRevenueFile] = useState<File | null>(null);
  const [designFile, setDesignFile] = useState<File | null>(null);
  const [, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisStatus | null>(
    null
  );
  const [results, setResults] = useState<any>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);

  const steps = [
    {
      id: "input",
      title: "Product Input",
      description: "Enter ASIN or product URL",
      icon: Search,
    },
    {
      id: "upload",
      title: "Data Upload",
      description: "Upload Helium 10 CSV files",
      icon: Upload,
    },
    {
      id: "processing",
      title: "AI Analysis",
      description: "Research → Keywords → Scoring → SEO",
      icon: BarChart3,
    },
    {
      id: "results",
      title: "Results",
      description: "Complete optimization report",
      icon: FileText,
    },
  ];

  // Poll for status updates
  useEffect(() => {
    if (
      analysisId &&
      (currentAnalysis?.status === "processing" ||
        currentAnalysis?.status === "pending")
    ) {
      const interval = setInterval(async () => {
        try {
          const response = await fetch(
            getFullApiUrl(`/api/v1/analyze/${analysisId}/status`)
          );
          if (response.ok) {
            const status = await response.json();
            setCurrentAnalysis(status);

            if (status.status === "completed") {
              // Fetch results
              const resultsResponse = await fetch(
                getFullApiUrl(`/api/v1/analyze/${analysisId}/results`)
              );
              if (resultsResponse.ok) {
                const resultsData = await resultsResponse.json();
                setResults(resultsData.results);
                setCurrentStep("results");
                setIsAnalyzing(false);
              }
            } else if (status.status === "failed") {
              setIsAnalyzing(false);
              setCurrentStep("input");
            }
          }
        } catch (error) {
          console.error("Error polling status:", error);
        }
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [analysisId, currentAnalysis?.status]);

  const getStepIndex = (step: ResearchStep) => {
    return steps.findIndex((s) => s.id === step);
  };

  const handleProductSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (asinOrUrl.trim()) {
      setCurrentStep("upload");
    }
  };

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    type: "revenue" | "design"
  ) => {
    const file = event.target.files?.[0];
    if (file && file.type === "text/csv") {
      if (type === "revenue") {
        setRevenueFile(file);
      } else {
        setDesignFile(file);
      }
    } else {
      alert("Please select a valid CSV file");
    }
  };

  const startAnalysis = async () => {
    if (!asinOrUrl || !revenueFile || !designFile) {
      alert("Please complete all required fields");
      return;
    }

    setIsAnalyzing(true);
    setCurrentStep("processing");
    setCurrentAnalysis(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("asin_or_url", asinOrUrl);
      formData.append("marketplace", marketplace);
      if (mainKeyword) {
        formData.append("main_keyword", mainKeyword);
      }
      formData.append("revenue_csv", revenueFile);
      formData.append("design_csv", designFile);

      const response = await fetch(
        getFullApiUrl("/api/v1/amazon-sales-intelligence"),
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        // Direct results from new endpoint
        setResults(data);
        setCurrentStep("results");
        setIsAnalyzing(false);
      } else {
        throw new Error(data.error || "Analysis failed");
      }
    } catch (error) {
      console.error("Error starting analysis:", error);
      alert(
        `Error: ${error instanceof Error ? error.message : "Unknown error"}`
      );
      setIsAnalyzing(false);
      setCurrentStep("upload");
    }
  };

  const resetResearch = () => {
    setCurrentStep("input");
    setAsinOrUrl("");
    setMainKeyword("");
    setRevenueFile(null);
    setDesignFile(null);
    setIsAnalyzing(false);
    setCurrentAnalysis(null);
    setResults(null);
    setAnalysisId(null);
  };

  const getStepIcon = (step: string) => {
    switch (step) {
      case "parsing_data":
        return "📊";
      case "research_analysis":
        return "🔍";
      case "keyword_analysis":
        return "🏷️";
      case "scoring_analysis":
        return "🎯";
      case "seo_optimization":
        return "📝";
      case "finalizing":
        return "✨";
      case "completed":
        return "🎉";
      default:
        return "⚙️";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "processing":
        return "bg-blue-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          🚀 Start New Research
        </h1>
        <p className="text-gray-600 mt-2">
          Complete AI-powered Amazon keyword research and SEO optimization
        </p>
      </div>

      {/* Progress Steps */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const currentIndex = getStepIndex(currentStep);
              const isActive = index === currentIndex;
              const isCompleted = index < currentIndex;
              const StepIcon = step.icon;

              return (
                <div key={step.id} className="flex items-center">
                  <div className="flex items-center">
                    <div
                      className={`
                      w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors
                      ${
                        isActive
                          ? "bg-blue-500 border-blue-500 text-white"
                          : isCompleted
                          ? "bg-green-500 border-green-500 text-white"
                          : "bg-gray-100 border-gray-300 text-gray-400"
                      }
                    `}
                    >
                      {isCompleted ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <StepIcon className="w-5 h-5" />
                      )}
                    </div>
                    <div className="ml-3">
                      <p
                        className={`text-sm font-medium ${
                          isActive
                            ? "text-blue-600"
                            : isCompleted
                            ? "text-green-600"
                            : "text-gray-500"
                        }`}
                      >
                        {step.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {step.description}
                      </p>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <ArrowRight className="w-5 h-5 text-gray-400 mx-4" />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      {currentStep === "input" && (
        <Card>
          <CardHeader>
            <CardTitle>Product Information</CardTitle>
            <CardDescription>
              Enter your Amazon product details to begin the analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProductSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    ASIN or Product URL *
                  </label>
                  <input
                    type="text"
                    value={asinOrUrl}
                    onChange={(e) => setAsinOrUrl(e.target.value)}
                    placeholder="B00O64QJOC or https://amazon.com/dp/B00O64QJOC"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Marketplace
                  </label>
                  <select
                    value={marketplace}
                    onChange={(e) => setMarketplace(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="US">United States</option>
                    <option value="UK">United Kingdom</option>
                    <option value="DE">Germany</option>
                    <option value="FR">France</option>
                    <option value="IT">Italy</option>
                    <option value="ES">Spain</option>
                    <option value="CA">Canada</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Main Keyword (Optional)
                </label>
                <input
                  type="text"
                  value={mainKeyword}
                  onChange={(e) => setMainKeyword(e.target.value)}
                  placeholder="changing pad"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <Button type="submit" className="w-full">
                Continue to File Upload
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {currentStep === "upload" && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Helium 10 Data</CardTitle>
            <CardDescription>
              Upload your Helium 10 Cerebro CSV files for competitor analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Revenue Competitors CSV *
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "revenue")}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {revenueFile && (
                  <p className="text-sm text-green-600 mt-1">
                    ✅ {revenueFile.name}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Design Competitors CSV *
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "design")}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                />
                {designFile && (
                  <p className="text-sm text-green-600 mt-1">
                    ✅ {designFile.name}
                  </p>
                )}
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => setCurrentStep("input")}
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={startAnalysis}
                disabled={!revenueFile || !designFile}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                🚀 Start AI Analysis
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {currentStep === "processing" && currentAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStepIcon(currentAnalysis.current_step)}
              AI Analysis in Progress
              <Badge className={getStatusColor(currentAnalysis.status)}>
                {currentAnalysis.status.toUpperCase()}
              </Badge>
            </CardTitle>
            <CardDescription>
              Analysis ID: {currentAnalysis.analysis_id}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>{currentAnalysis.message}</span>
                  <span>{currentAnalysis.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${currentAnalysis.progress}%` }}
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-sm">
                {[
                  { step: "parsing_data", label: "Parse Data" },
                  { step: "research_analysis", label: "Research" },
                  { step: "keyword_analysis", label: "Keywords" },
                  { step: "scoring_analysis", label: "Scoring" },
                  { step: "seo_optimization", label: "SEO" },
                  { step: "completed", label: "Complete" },
                ].map(({ step, label }) => (
                  <div
                    key={step}
                    className={`p-2 rounded text-center ${
                      currentAnalysis.current_step === step
                        ? "bg-blue-100 text-blue-800 font-medium"
                        : currentAnalysis.progress >
                          (step === "parsing_data"
                            ? 0
                            : step === "research_analysis"
                            ? 15
                            : step === "keyword_analysis"
                            ? 35
                            : step === "scoring_analysis"
                            ? 60
                            : step === "seo_optimization"
                            ? 80
                            : 95)
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {getStepIcon(step)} {label}
                  </div>
                ))}
              </div>

              {currentAnalysis.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h4 className="text-red-800 font-medium">Error</h4>
                  <p className="text-red-700">{currentAnalysis.error}</p>
                  <Button
                    variant="outline"
                    onClick={resetResearch}
                    className="mt-2"
                  >
                    Start Over
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {currentStep === "results" && results && (
        <div className="space-y-8">
          {/* Debug: Show results structure in development */}
          {process.env.NODE_ENV === "development" && (
            <Card className="border-yellow-200 bg-yellow-50">
              <CardHeader>
                <CardTitle className="text-yellow-800">
                  🐛 Debug: Results Structure
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-white p-2 rounded overflow-auto max-h-40">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Use the new ResultsDisplay component */}
          <ResultsDisplay isLoading={false} results={results} />

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button
              onClick={resetResearch}
              variant="outline"
              className="flex-1"
            >
              Start New Research
            </Button>
            <Button className="flex-1 bg-green-600 hover:bg-green-700">
              Download Full Report
              <FileText className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
