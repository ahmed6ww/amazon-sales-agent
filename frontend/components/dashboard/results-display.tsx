"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Download,
  BarChart3,
  Filter,
  Star,
  Copy,
  ExternalLink,
  TrendingUp,
  Target,
  Zap,
} from "lucide-react";

// Updated data types to match new backend structure
interface KeywordItem {
  phrase: string;
  search_volume: number;
  root: string;
  category:
    | "Relevant"
    | "Design-Specific"
    | "Irrelevant"
    | "Branded"
    | "Spanish"
    | "Outlier";
  represents_variants: number;
  intent_score: number;
  title_density: number;
  cpr: number;
  competition: {
    competing_products: number;
    ranking_competitors: number;
    competitor_rank_avg: number;
    competitor_performance_score: number;
  };
  opportunity_decision: "Opportunity" | "Ignore";
  opportunity_reason: string;
}

interface SEOAnalysis {
  optimized_title: {
    content: string;
    first_80_chars: string;
    main_root_included: boolean;
    design_root_included: boolean;
    key_benefit_included: boolean;
    character_count: number;
    keywords_included: string[];
    guideline_compliance: {
      character_limit: string;
      capitalization: string;
      special_characters: string;
      promotional_language: string;
      subjective_claims: string;
    };
  };
  optimized_bullets: Array<{
    content: string;
    character_count: number;
    primary_benefit: string;
    keywords_included: string[];
    guideline_compliance: string;
    total_search_volume?: number; // Task 6: Total search volume for this bullet
  }>;
  strategy: {
    first_80_optimization: string;
    keyword_integration: string;
    compliance_approach: string;
  };
}

interface KeywordRootOptimization {
  analysis_summary: {
    total_keywords_processed: number;
    total_roots_identified: number;
    meaningful_roots: number;
    priority_roots_selected: number;
  };
  efficiency_metrics: {
    reduction_percentage: number;
    processing_efficiency: string;
  };
  priority_roots: string[];
  keyword_categorization: {
    [key: string]: any;
  };
  recommendations: {
    amazon_search_terms: string[];
    optimization_notes: string[];
  };
}

interface AnalysisResult {
  success: boolean;
  asin: string;
  marketplace: string;
  ai_analysis_keywords: {
    success: boolean;
    structured_data: {
      product_context: any;
      items: KeywordItem[];
      stats: {
        total_keywords: number;
        relevant_count: number;
        design_specific_count: number;
        irrelevant_count: number;
        branded_count: number;
        spanish_count: number;
        outlier_count: number;
      };
    };
  };
  seo_analysis: SEOAnalysis;
  keyword_root_optimization: KeywordRootOptimization;
  source: string;
}

interface ResultsDisplayProps {
  isLoading?: boolean;
  results?: AnalysisResult | null;
}

export default function ResultsDisplay({
  isLoading,
  results,
}: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<"seo" | "keywords" | "roots">(
    "seo"
  );
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const categoryColors = {
    Relevant: "bg-green-50 text-green-700 border-green-200",
    "Design-Specific": "bg-blue-50 text-blue-700 border-blue-200",
    Irrelevant: "bg-red-50 text-red-700 border-red-200",
    Branded: "bg-orange-50 text-orange-700 border-orange-200",
    Spanish: "bg-purple-50 text-purple-700 border-purple-200",
    Outlier: "bg-yellow-50 text-yellow-700 border-yellow-200",
  };

  const competitionColors = {
    Low: "text-green-600",
    Medium: "text-yellow-600",
    High: "text-red-600",
  };

  const keywords = results?.ai_analysis_keywords?.structured_data?.items || [];
  const stats = results?.ai_analysis_keywords?.structured_data?.stats;
  const seoAnalysis = results?.seo_analysis;
  const rootOptimization = results?.keyword_root_optimization;

  const filteredKeywords =
    selectedCategory === "all"
      ? keywords
      : keywords.filter((k) => k.category === selectedCategory);

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Processing Your Research
          </CardTitle>
          <CardDescription>
            Our AI agents are analyzing your keywords and competitors...
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span>Research Agent: Fetching competitor data</span>
              <span className="text-blue-600">100%</span>
            </div>
            <Progress value={100} className="h-2" />

            <div className="flex justify-between text-sm">
              <span>Keyword Agent: Processing keywords</span>
              <span className="text-blue-600">75%</span>
            </div>
            <Progress value={75} className="h-2" />

            <div className="flex justify-between text-sm">
              <span>Scoring Agent: Analyzing relevancy</span>
              <span className="text-blue-600">45%</span>
            </div>
            <Progress value={45} className="h-2" />

            <div className="flex justify-between text-sm">
              <span>SEO Agent: Generating optimizations</span>
              <span className="text-gray-400">0%</span>
            </div>
            <Progress value={0} className="h-2" />
          </div>

          <div className="text-center text-sm text-muted-foreground">
            Estimated completion time: 2-3 minutes
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!results) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-gray-600" />
            No Results Available
          </CardTitle>
          <CardDescription>Run an analysis to see results here</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                Analysis Complete
              </CardTitle>
              <CardDescription>
                Comprehensive keyword research and SEO optimization
                recommendations
              </CardDescription>
            </div>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {stats?.total_keywords || 0}
              </div>
              <div className="text-sm text-muted-foreground">
                Total Keywords
              </div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {stats?.relevant_count || 0}
              </div>
              <div className="text-sm text-muted-foreground">
                Relevant Keywords
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {stats?.design_specific_count || 0}
              </div>
              <div className="text-sm text-muted-foreground">
                Design-Specific
              </div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {rootOptimization?.analysis_summary?.priority_roots_selected ||
                  0}
              </div>
              <div className="text-sm text-muted-foreground">
                Priority Roots
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === "seo" ? "default" : "outline"}
          onClick={() => setActiveTab("seo")}
        >
          SEO Optimization
        </Button>
        <Button
          variant={activeTab === "keywords" ? "default" : "outline"}
          onClick={() => setActiveTab("keywords")}
        >
          Keyword Analysis
        </Button>
        <Button
          variant={activeTab === "roots" ? "default" : "outline"}
          onClick={() => setActiveTab("roots")}
        >
          Root Analysis
        </Button>
      </div>

      {/* SEO Optimization Tab */}
      {activeTab === "seo" && seoAnalysis && (
        <div className="space-y-6">
          {/* 80-Character Optimization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                Mobile Optimization (First 80 Characters)
              </CardTitle>
              <CardDescription>
                Critical for mobile search visibility
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-sm font-medium text-blue-900 mb-2">
                  Optimized Title (First 80 chars):
                </div>
                <div className="text-lg font-mono bg-white p-3 rounded border">
                  {seoAnalysis.optimized_title.first_80_chars}
                </div>
                <div className="flex items-center gap-4 mt-3 text-sm">
                  <Badge
                    className={
                      seoAnalysis.optimized_title.main_root_included
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }
                  >
                    Main Root:{" "}
                    {seoAnalysis.optimized_title.main_root_included ? "✓" : "✗"}
                  </Badge>
                  <Badge
                    className={
                      seoAnalysis.optimized_title.design_root_included
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }
                  >
                    Design Root:{" "}
                    {seoAnalysis.optimized_title.design_root_included
                      ? "✓"
                      : "✗"}
                  </Badge>
                  <Badge
                    className={
                      seoAnalysis.optimized_title.key_benefit_included
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }
                  >
                    Key Benefit:{" "}
                    {seoAnalysis.optimized_title.key_benefit_included
                      ? "✓"
                      : "✗"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Full Title and Bullets */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">
                  Optimized Title
                </CardTitle>
                <CardDescription>
                  Amazon-compliant title with keyword optimization
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm">
                    {seoAnalysis.optimized_title.content}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-muted-foreground">
                      {seoAnalysis.optimized_title.character_count} characters
                    </span>
                    <Button variant="ghost" size="sm" className="h-6 px-2">
                      <Copy className="h-3 w-3 mr-1" />
                      Copy
                    </Button>
                  </div>
                </div>

                <div className="pt-2 border-t">
                  <div className="text-sm font-medium mb-2">
                    Keywords Included:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {seoAnalysis.optimized_title.keywords_included.map(
                      (keyword, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="text-xs"
                        >
                          {keyword}
                        </Badge>
                      )
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">
                  Optimized Bullet Points
                </CardTitle>
                <CardDescription>
                  Benefit-focused bullets with keyword integration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {seoAnalysis.optimized_bullets.map((bullet, index) => (
                  <div
                    key={index}
                    className="p-3 bg-green-50 border border-green-200 rounded-md"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-sm flex-1">{bullet.content}</p>
                      {/* Task 6: Display total search volume for this bullet */}
                      {bullet.total_search_volume !== undefined &&
                        bullet.total_search_volume > 0 && (
                          <Badge
                            variant="secondary"
                            className="ml-2 bg-blue-100 text-blue-700 border-blue-300"
                          >
                            <TrendingUp className="h-3 w-3 mr-1" />
                            {bullet.total_search_volume.toLocaleString()} vol
                          </Badge>
                        )}
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {bullet.keywords_included.map((keyword, idx) => (
                          <Badge
                            key={idx}
                            variant="outline"
                            className="text-xs"
                          >
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                      <Button variant="ghost" size="sm" className="h-6 px-2">
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Compliance Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-green-600" />
                Amazon Compliance Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(
                  seoAnalysis.optimized_title.guideline_compliance
                ).map(([key, value]) => (
                  <div
                    key={key}
                    className="text-center p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="text-sm font-medium capitalize">
                      {key.replace("_", " ")}
                    </div>
                    <Badge
                      className={
                        value === "PASS"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }
                    >
                      {value}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Keywords Tab */}
      {activeTab === "keywords" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Keyword Analysis</CardTitle>
                <CardDescription>
                  Categorized keywords with performance metrics
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="text-sm border rounded px-2 py-1"
                >
                  <option value="all">All Categories</option>
                  <option value="Relevant">Relevant</option>
                  <option value="Design-Specific">Design-Specific</option>
                  <option value="Irrelevant">Irrelevant</option>
                  <option value="Branded">Branded</option>
                  <option value="Spanish">Spanish</option>
                  <option value="Outlier">Outlier</option>
                </select>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <div className="space-y-3">
              {filteredKeywords.map((keyword, index) => (
                <div
                  key={index}
                  className="p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium">{keyword.phrase}</h4>
                      <Badge className={categoryColors[keyword.category]}>
                        {keyword.category}
                      </Badge>
                      <div className="flex items-center gap-1">
                        {[...Array(keyword.intent_score)].map((_, i) => (
                          <Star
                            key={i}
                            className="h-3 w-3 fill-yellow-400 text-yellow-400"
                          />
                        ))}
                        <span className="text-xs text-muted-foreground ml-1">
                          Intent {keyword.intent_score}
                        </span>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">
                        Search Volume
                      </span>
                      <div className="font-medium">
                        {keyword.search_volume.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">
                        Title Density
                      </span>
                      <div className="font-medium">
                        {keyword.title_density}%
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">CPR</span>
                      <div className="font-medium">{keyword.cpr}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Competition</span>
                      <div className="font-medium">
                        {keyword.competition.competing_products.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Opportunity</span>
                      <Badge
                        className={
                          keyword.opportunity_decision === "Opportunity"
                            ? "bg-green-100 text-green-700"
                            : "bg-gray-100 text-gray-700"
                        }
                      >
                        {keyword.opportunity_decision}
                      </Badge>
                    </div>
                  </div>

                  <div className="mt-2 text-xs text-muted-foreground">
                    Root: {keyword.root} | {keyword.opportunity_reason}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Root Analysis Tab */}
      {activeTab === "roots" && rootOptimization && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                Keyword Root Optimization
              </CardTitle>
              <CardDescription>
                Intelligent keyword grouping and efficiency analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {rootOptimization.analysis_summary.total_keywords_processed}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Total Keywords
                  </div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {rootOptimization.analysis_summary.total_roots_identified}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Roots Identified
                  </div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {rootOptimization.analysis_summary.meaningful_roots}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Meaningful Roots
                  </div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {rootOptimization.efficiency_metrics
                      ?.reduction_percentage || 0}
                    %
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Complexity Reduction
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">
                    Priority Roots for Amazon Search
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {rootOptimization.priority_roots
                      .slice(0, 10)
                      .map((root, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="bg-blue-50 text-blue-700"
                        >
                          {root}
                        </Badge>
                      ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">
                    Optimization Recommendations
                  </h4>
                  <div className="space-y-2">
                    {rootOptimization.recommendations.optimization_notes.map(
                      (note, index) => (
                        <div
                          key={index}
                          className="text-sm text-muted-foreground bg-gray-50 p-2 rounded"
                        >
                          {note}
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
