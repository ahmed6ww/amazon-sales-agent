"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface KeywordData {
  keyword_phrase: string;
  final_category: string;
  search_volume: number;
  relevancy_score: number;
  title_density: number;
  root_word: string;
  broad_search_volume: number;
  is_zero_title_density: boolean;
}

interface CategoryStats {
  keyword_count: number;
  total_search_volume: number;
  avg_relevancy_score: number;
  top_keywords: string[];
}

interface TestResults {
  success: boolean;
  result?: {
    total_keywords: number;
    processed_keywords: number;
    filtered_keywords: number;
    processing_time: number;
    data_quality_score: number;
    category_stats: Record<string, CategoryStats>;
    keywords_by_category: Record<string, KeywordData[]>;
    top_opportunities: string[];
    coverage_gaps: string[];
    warnings: string[];
  };
  error?: string;
}

export default function TestPage() {
  const [file, setFile] = useState<File | null>(null);
  const [asin, setAsin] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<TestResults | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
    } else {
      alert('Please select a CSV file');
    }
  };

  const testKeywordAgent = async () => {
    if (!file) {
      alert('Please upload a CSV file first');
      return;
    }

    setIsLoading(true);
    setResults(null);

    try {
      // First upload the CSV file
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8000/api/v1/upload/csv', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const uploadData = await uploadResponse.json();
      console.log('CSV uploaded successfully:', uploadData);

      // Test the keyword agent with the uploaded data (limit to first 50 rows for testing)
      const testData = uploadData.data.slice(0, 50); // Limit data for testing
      console.log('Testing with', testData.length, 'keywords');
      
      const testResponse = await fetch('http://localhost:8000/api/v1/test/keyword-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          csv_data: testData,
          asin: asin || null
        }),
      });

      if (!testResponse.ok) {
        const errorText = await testResponse.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Test failed (${testResponse.status}): ${errorText}`);
      }

      const testData = await testResponse.json();
      setResults(testData);

    } catch (error) {
      console.error('Error testing keyword agent:', error);
      setResults({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const downloadResults = () => {
    if (!results?.result) return;

    const csvContent = generateCSV(results.result);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'keyword_analysis_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const generateCSV = (result: any) => {
    const headers = [
      'Keyword',
      'Category',
      'Search Volume',
      'Relevancy Score',
      'Title Density',
      'Root Word',
      'Broad Search Volume',
      'Zero Title Density'
    ];

    let csvContent = headers.join(',') + '\n';

    Object.entries(result.keywords_by_category).forEach(([category, keywords]) => {
      (keywords as KeywordData[]).forEach(keyword => {
        const row = [
          `"${keyword.keyword_phrase}"`,
          category,
          keyword.search_volume,
          keyword.relevancy_score.toFixed(2),
          keyword.title_density,
          keyword.root_word || '',
          keyword.broad_search_volume,
          keyword.is_zero_title_density ? 'Yes' : 'No'
        ];
        csvContent += row.join(',') + '\n';
      });
    });

    return csvContent;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🧪 Keyword Agent Test Page
          </h1>
          <p className="text-gray-600">
            Test the keyword categorization and analysis workflow with Helium10 CSV data
          </p>
        </div>

        {/* Input Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">📁 Input Data</h2>
          
          <div className="space-y-4">
            {/* ASIN Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ASIN or Product URL (Optional)
              </label>
              <input
                type="text"
                value={asin}
                onChange={(e) => setAsin(e.target.value)}
                placeholder="B00O64QJOC or https://amazon.com/dp/B00O64QJOC"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Helium10 Cerebro CSV File
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {file && (
                <p className="text-sm text-green-600 mt-1">
                  ✅ {file.name} selected
                </p>
              )}
            </div>

            {/* Test Button */}
            <Button
              onClick={testKeywordAgent}
              disabled={!file || isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Testing Keyword Agent...
                </>
              ) : (
                '🚀 Test Keyword Agent (First 50 Keywords)'
              )}
            </Button>
            
            <p className="text-sm text-gray-500 mt-2">
              ℹ️ For testing purposes, only the first 50 keywords will be processed
            </p>
          </div>
        </Card>

        {/* Results Section */}
        {results && (
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">📊 Test Results</h2>
              {results.success && results.result && (
                <Button onClick={downloadResults} variant="outline">
                  📥 Download CSV
                </Button>
              )}
            </div>

            {results.success && results.result ? (
              <div className="space-y-6">
                {/* Summary Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {results.result.total_keywords}
                    </div>
                    <div className="text-sm text-gray-600">Total Keywords</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {results.result.processed_keywords}
                    </div>
                    <div className="text-sm text-gray-600">Processed</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {results.result.filtered_keywords}
                    </div>
                    <div className="text-sm text-gray-600">Filtered</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {results.result.data_quality_score.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Quality Score</div>
                  </div>
                </div>

                {/* Category Distribution */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">📈 Category Distribution</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {Object.entries(results.result.category_stats).map(([category, stats]) => (
                      <div key={category} className="bg-white border rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <Badge className="capitalize">
                            {category.replace('_', ' ')}
                          </Badge>
                          <span className="font-bold">{stats.keyword_count}</span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <div>Volume: {stats.total_search_volume.toLocaleString()}</div>
                          <div>Avg Relevancy: {stats.avg_relevancy_score.toFixed(1)}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Opportunities */}
                {results.result.top_opportunities.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3">🎯 Top Opportunities</h3>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <ul className="space-y-1">
                        {results.result.top_opportunities.map((opportunity, index) => (
                          <li key={index} className="text-green-800">
                            • {opportunity}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Coverage Gaps */}
                {results.result.coverage_gaps.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3">⚠️ Coverage Gaps</h3>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <ul className="space-y-1">
                        {results.result.coverage_gaps.map((gap, index) => (
                          <li key={index} className="text-yellow-800">
                            • {gap}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {results.result.warnings.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3">🚨 Warnings</h3>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <ul className="space-y-1">
                        {results.result.warnings.map((warning, index) => (
                          <li key={index} className="text-red-800">
                            • {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Processing Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-2">⚡ Processing Info</h3>
                  <div className="text-sm text-gray-600">
                    <p>Processing Time: {results.result.processing_time.toFixed(3)}s</p>
                    <p>Data Quality Score: {results.result.data_quality_score.toFixed(2)}%</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-800 mb-2">❌ Error</h3>
                <p className="text-red-700">{results.error}</p>
              </div>
            )}
          </Card>
        )}

        {/* Instructions */}
        <Card className="p-6 mt-6 bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">📋 Instructions</h3>
          <div className="text-blue-700 space-y-2">
            <p>1. Upload a Helium10 Cerebro CSV file (like the sample file in the backend)</p>
            <p>2. Optionally enter an ASIN or product URL for context</p>
            <p>3. Click "Test Keyword Agent" to run the analysis</p>
            <p>4. Review the categorized keywords and download results as CSV</p>
            <p>5. Check the browser console for detailed logs</p>
          </div>
        </Card>
      </div>
    </div>
  );
} 