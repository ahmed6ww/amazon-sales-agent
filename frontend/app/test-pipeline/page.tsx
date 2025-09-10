'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AgentAnimation } from '@/components/dashboard/agent-animation';

interface AnalysisResult {
  analysis_id: string;
  research_analysis: {
    success: boolean;
    product_title: string;
    ai_analysis: string;
    mvp_data_summary: {
      title_extracted: boolean;
      images_count: number;
      aplus_sections: number;
      reviews_count: number;
      qa_questions: number;
    };
    data_quality_score: number;
  };
  keyword_analysis: {
    total_keywords: number;
    keywords_by_category: Record<string, number>;
    top_opportunities: string[];
    recommended_focus_areas: string[];
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
      search_volume: number;
      opportunity_score: number;
    }>;
    processing_method: string;
  };
  seo_analysis: {
    optimizations_generated: number;
    title_optimization: string;
    bullet_optimizations: number;
    backend_keywords: string[];
    content_gaps: number;
    competitive_advantages: number;
    seo_score: number;
    processing_method: string;
  };
  timestamp: string;
  pipeline_status: string;
}

interface AnalysisStatus {
  analysis_id: string;
  status: string;
  current_step: string;
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  error?: string;
  results?: AnalysisResult;
}

export default function TestPipeline() {
  const [url, setUrl] = useState('https://www.amazon.ae/PNY-GeForce-RTXTM-Triple-Graphics/dp/B0DYPFGL88/');
  const [marketplace, setMarketplace] = useState('amazon.ae');
  const [mainKeyword, setMainKeyword] = useState('graphics card');
  const [revenueFile, setRevenueFile] = useState<File | null>(null);
  const [designFile, setDesignFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startAnalysis = async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setStatus(null);

    try {
      // Create form data for CSV files
      const formData = new FormData();
      
      formData.append('asin_or_url', url);
      formData.append('marketplace', marketplace);
      formData.append('main_keyword', mainKeyword);

      // Use uploaded files or create dummy files
      if (revenueFile) {
        formData.append('revenue_csv', revenueFile);
      } else {
        // Create dummy CSV content if no file uploaded
        const dummyRevenueCSV = `Keyword,Search Volume,Relevancy
graphics card,100000,1.0
gaming gpu,80000,0.9
rtx 4070,60000,0.8
nvidia graphics,50000,0.7`;
        const revenueBlob = new Blob([dummyRevenueCSV], { type: 'text/csv' });
        formData.append('revenue_csv', revenueBlob, 'revenue.csv');
      }

      if (designFile) {
        formData.append('design_csv', designFile);
      } else {
        // Create dummy CSV content if no file uploaded
        const dummyDesignCSV = `Keyword,Search Volume,Relevancy
video card,40000,0.8
gpu gaming,30000,0.7`;
        const designBlob = new Blob([dummyDesignCSV], { type: 'text/csv' });
        formData.append('design_csv', designBlob, 'design.csv');
      }

      console.log('Starting analysis with data:', {
        url,
        marketplace, 
        mainKeyword,
        hasRevenueFile: !!revenueFile,
        hasDesignFile: !!designFile
      });

      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const data = await response.json();
      console.log('Analysis started, response data:', data);

      // Start polling for status
      pollStatus(data.analysis_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsLoading(false);
    }
  };

  const pollStatus = async (id: string) => {
    try {
      console.log('Polling status for analysis ID:', id);
      const response = await fetch(`/api/v1/analyze/${id}/status`);
      console.log('Status poll response:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Status poll error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const statusData: AnalysisStatus = await response.json();
      console.log('Status data received:', statusData);
      setStatus(statusData);

      if (statusData.status === 'completed') {
        console.log('Analysis completed, fetching results...');
        // Get final results
        const resultsResponse = await fetch(`/api/v1/analyze/${id}/results`);
        console.log('Results response status:', resultsResponse.status);
        
        if (resultsResponse.ok) {
          const resultsData = await resultsResponse.json();
          console.log('Results data received:', resultsData);
          // The backend returns {success: true, results: actualData}
          // So we need to extract the actual results
          if (resultsData.success && resultsData.results) {
            setResults(resultsData.results);
          } else {
            console.error('Unexpected results format:', resultsData);
            setError('Results format is unexpected');
          }
        } else {
          const errorText = await resultsResponse.text();
          console.error('Results fetch error:', errorText);
          setError(`Failed to fetch results: ${errorText}`);
        }
        setIsLoading(false);
      } else if (statusData.status === 'failed') {
        console.error('Analysis failed:', statusData.error);
        setError(`Analysis failed: ${statusData.error || 'Unknown error'}`);
        setIsLoading(false);
      } else {
        // Continue polling
        console.log(`Analysis in progress (${statusData.progress}%), continuing to poll...`);
        setTimeout(() => pollStatus(id), 2000);
      }
    } catch (err) {
      console.error('Polling error:', err);
      setError(err instanceof Error ? err.message : 'Polling error');
      setIsLoading(false);
    }
  };

  const resetTest = () => {
    setIsLoading(false);
    setStatus(null);
    setResults(null);
    setError(null);
    setRevenueFile(null);
    setDesignFile(null);
    // Reset file inputs
    const revenueInput = document.getElementById('revenue-csv') as HTMLInputElement;
    const designInput = document.getElementById('design-csv') as HTMLInputElement;
    if (revenueInput) revenueInput.value = '';
    if (designInput) designInput.value = '';
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">🤖 AI Pipeline Test Dashboard</h1>
        <p className="text-lg text-muted-foreground">
          Test the complete Amazon Sales Agent pipeline with real-time visualization
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle>🔧 Pipeline Configuration</CardTitle>
                  <CardDescription>
          Configure your test parameters and start the AI analysis. Upload CSV files or use demo data for testing.
        </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="url">Amazon Product URL</Label>
              <Input
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.amazon.com/..."
                disabled={isLoading}
              />
            </div>
            <div>
              <Label htmlFor="marketplace">Marketplace</Label>
              <Input
                id="marketplace"
                value={marketplace}
                onChange={(e) => setMarketplace(e.target.value)}
                placeholder="amazon.com"
                disabled={isLoading}
              />
            </div>
            <div>
              <Label htmlFor="keyword">Main Keyword</Label>
              <Input
                id="keyword"
                value={mainKeyword}
                onChange={(e) => setMainKeyword(e.target.value)}
                placeholder="graphics card"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="revenue-csv">Revenue CSV File (Optional)</Label>
              <Input
                id="revenue-csv"
                type="file"
                accept=".csv"
                onChange={(e) => setRevenueFile(e.target.files?.[0] || null)}
                disabled={isLoading}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Upload Helium 10 revenue keyword data or leave empty for demo data
              </p>
            </div>
            <div>
              <Label htmlFor="design-csv">Design CSV File (Optional)</Label>
              <Input
                id="design-csv"
                type="file"
                accept=".csv"
                onChange={(e) => setDesignFile(e.target.files?.[0] || null)}
                disabled={isLoading}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Upload Helium 10 design keyword data or leave empty for demo data
              </p>
            </div>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-sm mb-2">📄 CSV Format Expected</h4>
            <p className="text-xs text-muted-foreground mb-2">
              Your CSV files should contain columns: <code>Keyword</code>, <code>Search Volume</code>, <code>Relevancy</code>
            </p>
            <div className="text-xs font-mono bg-white p-2 rounded border">
              Keyword,Search Volume,Relevancy<br/>
              graphics card,100000,1.0<br/>
              gaming gpu,80000,0.9
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              💡 If no files are uploaded, demo data will be used automatically
            </p>
          </div>

          <div className="flex gap-4">
            <Button 
              onClick={startAnalysis} 
              disabled={isLoading || !url}
              className="flex-1"
            >
              {isLoading ? 'Running Analysis...' : '🚀 Start AI Pipeline Test'}
            </Button>
            {(status || results || error) && (
              <Button variant="outline" onClick={resetTest}>
                🔄 Reset Test
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Status & Animation */}
      {isLoading && status && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              ⚡ Pipeline Status
              <Badge variant={status.status === 'completed' ? 'default' : 'secondary'}>
                {status.status}
              </Badge>
            </CardTitle>
            <CardDescription>{status.message}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Overall Progress</span>
                  <span>{status.progress}%</span>
                </div>
                <Progress value={status.progress} className="w-full" />
              </div>
              
              <AgentAnimation
                currentStep={status.current_step}
                progress={status.progress}
                isActive={status.status === 'processing'}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">❌ Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Debug: Show what's in results */}
      {results && (
        <Card className="mb-4 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-600">🔍 Debug: Available Data Keys</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">Available keys in results: {Object.keys(results).join(', ')}</p>
            <p className="text-sm">Has research_analysis: {results.research_analysis ? 'Yes' : 'No'}</p>
            {results.research_analysis && (
              <p className="text-sm">Research keys: {Object.keys(results.research_analysis).join(', ')}</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">📊 Analysis Results</h2>

          {/* Research Results */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🔍 Research Analysis
                <Badge variant="default">{results.research_analysis ? 'AI Powered' : 'Missing Data'}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!results.research_analysis && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
                  <p className="text-yellow-800">⚠️ Research analysis data is missing from the response.</p>
                </div>
              )}
              {results.research_analysis && (
              <div className="space-y-4">
              <div>
                <h4 className="font-semibold">Product Title:</h4>
                <p className="text-sm bg-muted p-2 rounded">{results.research_analysis?.product_title || 'No title available'}</p>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.research_analysis?.mvp_data_summary?.title_extracted ? '✅' : '❌'}
                  </div>
                  <div className="text-sm">Title</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.research_analysis?.mvp_data_summary?.images_count || 0}
                  </div>
                  <div className="text-sm">Images</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.research_analysis?.mvp_data_summary?.aplus_sections || 0}
                  </div>
                  <div className="text-sm">A+ Content</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.research_analysis?.mvp_data_summary?.reviews_count || 0}
                  </div>
                  <div className="text-sm">Reviews</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.research_analysis?.mvp_data_summary?.qa_questions || 0}
                  </div>
                  <div className="text-sm">Q&A</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">AI Analysis:</h4>
                <p className="text-sm bg-muted p-3 rounded whitespace-pre-wrap">
                  {results.research_analysis?.ai_analysis || 'No AI analysis available'}
                </p>
              </div>
              </div>
              )}
            </CardContent>
          </Card>

          {/* Keyword Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                📊 Keyword Analysis
                <Badge variant="secondary">
                  {results.keyword_analysis?.total_keywords || 0} Total
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(results.keyword_analysis?.keywords_by_category || {}).map(([category, count]) => (
                  <div key={category} className="text-center">
                    <div className="text-2xl font-bold text-green-600">{count}</div>
                    <div className="text-sm capitalize">{category.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="font-semibold mb-2">Top Opportunities:</h4>
                <div className="flex flex-wrap gap-2">
                  {(results.keyword_analysis?.top_opportunities || []).slice(0, 10).map((keyword, index) => (
                    <Badge key={index} variant="outline">{keyword}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scoring Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🎯 Scoring Analysis
                <Badge variant="default">
                  {results.scoring_analysis?.processing_method === 'ai_scoring' ? 'AI Powered' : 'Direct Processing'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(results.scoring_analysis?.priority_distribution || {}).map(([priority, count]) => (
                  <div key={priority} className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{count}</div>
                    <div className="text-sm capitalize">{priority}</div>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="font-semibold mb-2">Top Critical Keywords:</h4>
                <div className="space-y-2">
                  {(results.scoring_analysis?.top_critical_keywords || []).slice(0, 5).map((kw, index) => (
                    <div key={index} className="flex justify-between items-center bg-muted p-2 rounded">
                      <span className="font-medium">{kw.keyword}</span>
                      <div className="flex gap-4 text-sm">
                        <span>Intent: {kw.intent_score}</span>
                        <span>Priority: {kw.priority_score}</span>
                        <span>Volume: {kw.search_volume?.toLocaleString() || 0}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* SEO Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🎨 SEO Optimization
                <Badge variant="default">
                  {results.seo_analysis?.processing_method === 'ai_seo' ? 'AI Powered' : 'Direct Processing'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.seo_analysis?.seo_score || 0}
                  </div>
                  <div className="text-sm">SEO Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.seo_analysis?.bullet_optimizations || 0}
                  </div>
                  <div className="text-sm">Bullet Points</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.seo_analysis?.backend_keywords?.length || 0}
                  </div>
                  <div className="text-sm">Backend Keywords</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.seo_analysis?.content_gaps || 0}
                  </div>
                  <div className="text-sm">Content Gaps</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Optimized Title:</h4>
                <p className="text-sm bg-muted p-3 rounded">
                  {results.seo_analysis?.title_optimization || 'No title optimization available'}
                </p>
              </div>

              {(results.seo_analysis?.backend_keywords?.length || 0) > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Backend Keywords:</h4>
                  <div className="flex flex-wrap gap-2">
                    {(results.seo_analysis?.backend_keywords || []).slice(0, 15).map((keyword, index) => (
                      <Badge key={index} variant="outline">{keyword}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pipeline Summary */}
          <Card>
            <CardHeader>
              <CardTitle>📈 Pipeline Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">
                    {results.research_analysis?.data_quality_score || 0}/5
                  </div>
                  <div className="text-sm">Data Quality</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">
                    {results.keyword_analysis?.total_keywords || 0}
                  </div>
                  <div className="text-sm">Keywords Analyzed</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600">
                    {results.scoring_analysis?.total_analyzed || 0}
                  </div>
                  <div className="text-sm">Keywords Scored</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-orange-600">
                    {results.seo_analysis?.optimizations_generated || 0}
                  </div>
                  <div className="text-sm">Optimizations</div>
                </div>
              </div>

              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">
                  ✅ <strong>Pipeline Status:</strong> {results.pipeline_status || 'unknown'} at {new Date(results.timestamp || Date.now()).toLocaleString()}
                </p>
              </div>

              {/* Debug Info */}
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-800">
                  🔍 Debug: View Raw Results (Click to expand)
                </summary>
                <div className="mt-2 p-4 bg-gray-50 rounded border">
                  <pre className="text-xs overflow-auto max-h-64">
                    {JSON.stringify(results, null, 2)}
                  </pre>
                </div>
              </details>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 