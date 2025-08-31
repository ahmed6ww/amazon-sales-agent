'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface AnalysisStatus {
  analysis_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  current_step: string;
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  error?: string;
  results?: any;
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
  research_analysis: any;
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

export default function Dashboard() {
  const [asinOrUrl, setAsinOrUrl] = useState('');
  const [marketplace, setMarketplace] = useState('US');
  const [mainKeyword, setMainKeyword] = useState('');
  const [revenueFile, setRevenueFile] = useState<File | null>(null);
  const [designFile, setDesignFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);

  // Poll for status updates
  useEffect(() => {
    if (analysisId && currentAnalysis?.status === 'processing') {
      const interval = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:8000/api/v1/analyze/${analysisId}/status`);
          if (response.ok) {
            const status = await response.json();
            setCurrentAnalysis(status);
            
            if (status.status === 'completed') {
              // Fetch results
              const resultsResponse = await fetch(`http://localhost:8000/api/v1/analyze/${analysisId}/results`);
              if (resultsResponse.ok) {
                const resultsData = await resultsResponse.json();
                setResults(resultsData.results);
                setIsAnalyzing(false);
              }
            } else if (status.status === 'failed') {
              setIsAnalyzing(false);
            }
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [analysisId, currentAnalysis?.status]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>, type: 'revenue' | 'design') => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      if (type === 'revenue') {
        setRevenueFile(file);
      } else {
        setDesignFile(file);
      }
    } else {
      alert('Please select a valid CSV file');
    }
  };

  const startAnalysis = async () => {
    if (!asinOrUrl || !revenueFile || !designFile) {
      alert('Please fill in all required fields and upload both CSV files');
      return;
    }

    setIsAnalyzing(true);
    setCurrentAnalysis(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('asin_or_url', asinOrUrl);
      formData.append('marketplace', marketplace);
      if (mainKeyword) {
        formData.append('main_keyword', mainKeyword);
      }
      formData.append('revenue_csv', revenueFile);
      formData.append('design_csv', designFile);

      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysisId(data.analysis_id);
      
      // Start polling for status
      setCurrentAnalysis({
        analysis_id: data.analysis_id,
        status: 'pending',
        current_step: 'initializing',
        progress: 0,
        message: 'Analysis queued for processing',
        started_at: new Date().toISOString()
      });

    } catch (error) {
      console.error('Error starting analysis:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setIsAnalyzing(false);
    }
  };

  const getStepIcon = (step: string) => {
    switch (step) {
      case 'parsing_data': return '📊';
      case 'research_analysis': return '🔍';
      case 'keyword_analysis': return '🏷️';
      case 'scoring_analysis': return '🎯';
      case 'seo_optimization': return '📝';
      case 'finalizing': return '✨';
      case 'completed': return '🎉';
      default: return '⚙️';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'processing': return 'bg-blue-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg"></div>
            <span className="text-xl font-semibold text-gray-900">KeywordAI</span>
            <Badge className="ml-2 bg-blue-50 text-blue-700 border-blue-200">
              Dashboard
            </Badge>
          </div>
          <div className="flex items-center space-x-4">
            <a href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
              ← Back to Home
            </a>
            <a href="/test" className="text-gray-600 hover:text-blue-600 transition-colors">
              Test Agents
            </a>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🚀 AI Analysis Dashboard</h1>
          <p className="text-gray-600 text-lg">
            Complete agentic workflow: Research → Keyword → Scoring → SEO optimization
          </p>
        </div>

        {/* Input Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Start New Analysis</CardTitle>
            <CardDescription>
              Upload your Helium10 competitor data and get comprehensive keyword analysis with SEO recommendations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
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
                  disabled={isAnalyzing}
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
                  disabled={isAnalyzing}
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
                disabled={isAnalyzing}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Revenue Competitors CSV *
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, 'revenue')}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  disabled={isAnalyzing}
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
                  onChange={(e) => handleFileChange(e, 'design')}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                  disabled={isAnalyzing}
                />
                {designFile && (
                  <p className="text-sm text-green-600 mt-1">
                    ✅ {designFile.name}
                  </p>
                )}
              </div>
            </div>

            <Button 
              onClick={startAnalysis}
              disabled={isAnalyzing || !asinOrUrl || !revenueFile || !designFile}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Running AI Analysis...
                </>
              ) : (
                '🚀 Start Complete AI Analysis'
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Progress Tracking */}
        {currentAnalysis && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getStepIcon(currentAnalysis.current_step)}
                Analysis Progress
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
                    { step: 'parsing_data', label: 'Parse Data' },
                    { step: 'research_analysis', label: 'Research' },
                    { step: 'keyword_analysis', label: 'Keywords' },
                    { step: 'scoring_analysis', label: 'Scoring' },
                    { step: 'seo_optimization', label: 'SEO' },
                    { step: 'completed', label: 'Complete' }
                  ].map(({ step, label }) => (
                    <div 
                      key={step}
                      className={`p-2 rounded text-center ${
                        currentAnalysis.current_step === step 
                          ? 'bg-blue-100 text-blue-800 font-medium' 
                          : currentAnalysis.progress > (
                            step === 'parsing_data' ? 0 :
                            step === 'research_analysis' ? 15 :
                            step === 'keyword_analysis' ? 35 :
                            step === 'scoring_analysis' ? 60 :
                            step === 'seo_optimization' ? 80 : 95
                          ) ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
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
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Display */}
        {results && (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="text-2xl font-bold text-blue-600">{results.summary.actionable_keywords}</div>
                  <div className="text-sm text-gray-600">Actionable Keywords</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="text-2xl font-bold text-green-600">{results.summary.quick_wins}</div>
                  <div className="text-sm text-gray-600">Quick Wins</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="text-2xl font-bold text-purple-600">{results.summary.confidence_score}%</div>
                  <div className="text-sm text-gray-600">Confidence Score</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="text-2xl font-bold text-orange-600">{results.keyword_analysis.total_keywords}</div>
                  <div className="text-sm text-gray-600">Total Keywords</div>
                </CardContent>
              </Card>
            </div>

            {/* Priority Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>🎯 Keyword Priority Distribution</CardTitle>
                <CardDescription>Keywords categorized by business priority and intent</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-red-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-600">{results.scoring_analysis.priority_distribution.critical}</div>
                    <div className="text-sm text-red-800">Critical</div>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-orange-600">{results.scoring_analysis.priority_distribution.high}</div>
                    <div className="text-sm text-orange-800">High Priority</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-yellow-600">{results.scoring_analysis.priority_distribution.medium}</div>
                    <div className="text-sm text-yellow-800">Medium</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">{results.scoring_analysis.priority_distribution.low}</div>
                    <div className="text-sm text-green-800">Low Priority</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-600">{results.scoring_analysis.priority_distribution.filtered}</div>
                    <div className="text-sm text-gray-800">Filtered</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Critical Keywords */}
            {results.scoring_analysis.top_critical_keywords.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>🏆 Critical Keywords</CardTitle>
                  <CardDescription>Must-target keywords with highest commercial intent</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="min-w-full table-auto">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="px-4 py-2 text-left">Keyword</th>
                          <th className="px-4 py-2 text-left">Intent Score</th>
                          <th className="px-4 py-2 text-left">Priority Score</th>
                          <th className="px-4 py-2 text-left">Search Volume</th>
                          <th className="px-4 py-2 text-left">Opportunity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.scoring_analysis.top_critical_keywords.map((keyword, index) => (
                          <tr key={index} className="border-b">
                            <td className="px-4 py-2 font-medium">{keyword.keyword}</td>
                            <td className="px-4 py-2">
                              <Badge className="bg-purple-500">{keyword.intent_score}/3</Badge>
                            </td>
                            <td className="px-4 py-2">
                              <Badge className="bg-red-500">{keyword.priority_score.toFixed(1)}</Badge>
                            </td>
                            <td className="px-4 py-2">{keyword.search_volume?.toLocaleString() || 'N/A'}</td>
                            <td className="px-4 py-2">{keyword.opportunity_score.toFixed(1)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* SEO Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>📝 SEO Optimization Recommendations</CardTitle>
                <CardDescription>AI-generated recommendations to improve your listing performance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Title Optimization */}
                <div>
                  <h4 className="font-semibold mb-2">📋 Title Optimization</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="mb-2">
                      <span className="text-sm text-gray-600">Current:</span>
                      <p className="text-gray-800">{results.seo_recommendations.title_optimization.current_title}</p>
                    </div>
                    <div className="mb-2">
                      <span className="text-sm text-gray-600">Recommended:</span>
                      <p className="text-green-800 font-medium">{results.seo_recommendations.title_optimization.recommended_title}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-500">
                        {results.seo_recommendations.title_optimization.improvement_score}% Improvement
                      </Badge>
                      <span className="text-sm text-gray-600">
                        Keywords added: {results.seo_recommendations.title_optimization.keywords_added.join(', ')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Bullet Points */}
                <div>
                  <h4 className="font-semibold mb-2">• Bullet Points Optimization</h4>
                  <div className="space-y-2">
                    {results.seo_recommendations.bullet_points.recommended_bullets.map((bullet, index) => (
                      <div key={index} className="bg-blue-50 p-3 rounded border-l-4 border-blue-500">
                        {bullet}
                      </div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    Keywords coverage: {results.seo_recommendations.bullet_points.keywords_coverage} keywords
                  </p>
                </div>

                {/* Backend Keywords */}
                <div>
                  <h4 className="font-semibold mb-2">🔍 Backend Keywords</h4>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="flex flex-wrap gap-1 mb-2">
                      {results.seo_recommendations.backend_keywords.recommended_keywords.slice(0, 10).map((keyword, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                      {results.seo_recommendations.backend_keywords.recommended_keywords.length > 10 && (
                        <Badge variant="outline" className="text-xs">
                          +{results.seo_recommendations.backend_keywords.recommended_keywords.length - 10} more
                        </Badge>
                      )}
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>Character count: {results.seo_recommendations.backend_keywords.character_count}/250</span>
                      <span>Coverage improvement: {results.seo_recommendations.backend_keywords.coverage_improvement}</span>
                    </div>
                  </div>
                </div>

                {/* Competitive Advantages */}
                <div>
                  <h4 className="font-semibold mb-2">🚀 Competitive Advantages</h4>
                  <div className="space-y-2">
                    {results.seo_recommendations.competitive_advantages.map((advantage, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <span className="text-green-500 mt-1">✓</span>
                        <span className="text-gray-700">{advantage}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Opportunities */}
            {results.scoring_analysis.top_opportunities.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>🚀 Top Opportunities</CardTitle>
                  <CardDescription>High-potential keywords with low competition</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {results.scoring_analysis.top_opportunities.map((opportunity, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <h4 className="font-medium mb-2">{opportunity.keyword}</h4>
                        <div className="flex justify-between items-center text-sm">
                          <Badge className="bg-green-500">
                            {opportunity.opportunity_score.toFixed(1)} Opportunity
                          </Badge>
                          <span className="text-gray-600">
                            {opportunity.search_volume?.toLocaleString() || 'N/A'} searches/month
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 capitalize">
                          {opportunity.opportunity_type.replace('_', ' ')}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 