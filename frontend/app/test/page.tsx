'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getFullApiUrl } from '../../lib/config';

interface KeywordResult {
  keyword_phrase: string;
  category: string;
  search_volume?: number;
  relevancy_score: number;
  title_density?: number;
  top_10_competitors: number;
  total_competitors: number;
  root_word: string;
  root_volume?: number;
}

interface ScoredKeyword {
  keyword_phrase: string;
  category: string;
  intent_score: number;
  priority_score: number;
  search_volume?: number;
  relevancy_score: number;
  competition_level: string;
  opportunity_score: number;
  business_value: string;
  opportunity_type: string;
  root_word: string;
}

interface CategoryStat {
  category_name: string;
  total_keywords: number;
  avg_intent_score: number;
  avg_priority_score: number;
  total_search_volume: number;
  high_priority_count: number;
  critical_priority_count: number;
}

interface KeywordTestResults {
  success: boolean;
  total_keywords: number;
  keywords: KeywordResult[];
  category_stats: {
    category: string;
    count: number;
    percentage: number;
  }[];
  summary: {
    processing_time: number;
    data_quality_score: number;
    top_10_competitors: string[];
    total_competitors: number;
  };
}

interface ScoringTestResults {
  success: boolean;
  total_keywords_analyzed: number;
  priority_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    filtered: number;
  };
  critical_keywords: ScoredKeyword[];
  high_priority_keywords: ScoredKeyword[];
  top_opportunities: ScoredKeyword[];
  category_stats: CategoryStat[];
  summary: {
    processing_time: number;
    confidence_score: number;
    actionable_keywords: number;
    quick_wins: number;
  };
  insights: {
    avg_priority_score: number;
    high_value_keywords: number;
    quick_wins: number;
    total_search_volume: number;
  };
}

export default function TestPage() {
  const [file, setFile] = useState<File | null>(null);
  const [asin, setAsin] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [keywordResults, setKeywordResults] = useState<KeywordTestResults | null>(null);
  const [scoringResults, setScoringResults] = useState<ScoringTestResults | null>(null);
  const [activeTest, setActiveTest] = useState<'keyword' | 'scoring' | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
    } else {
      alert('Please select a valid CSV file');
    }
  };

  const testKeywordAgent = async () => {
    if (!file) {
      alert('Please select a CSV file first');
      return;
    }

    setIsLoading(true);
    setActiveTest('keyword');
    setKeywordResults(null);
    setScoringResults(null);

    try {
      // Upload CSV first
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch(getFullApiUrl('/api/v1/upload/csv'), {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const uploadData = await uploadResponse.json();
      console.log('CSV uploaded successfully:', uploadData);

      // Test the keyword agent with the uploaded data (limit to first 50 rows for testing)
      const limitedData = uploadData.data.slice(0, 50);
      console.log('Testing with', limitedData.length, 'keywords');

      const testResponse = await fetch(getFullApiUrl('/api/v1/test/keyword-agent'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          csv_data: limitedData,
          asin: asin || null
        }),
      });

      if (!testResponse.ok) {
        const errorText = await testResponse.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Test failed (${testResponse.status}): ${errorText}`);
      }

      const testData = await testResponse.json();
      setKeywordResults(testData);

    } catch (error) {
      console.error('Error testing keyword agent:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testScoringAgent = async () => {
    if (!file) {
      alert('Please select a CSV file first');
      return;
    }

    setIsLoading(true);
    setActiveTest('scoring');
    setKeywordResults(null);
    setScoringResults(null);

    try {
      // Upload CSV first
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch(getFullApiUrl('/api/v1/upload/csv'), {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const uploadData = await uploadResponse.json();
      console.log('CSV uploaded successfully:', uploadData);

      // Test the scoring agent with the uploaded data (limit to first 30 rows for testing)
      const limitedData = uploadData.data.slice(0, 30);
      console.log('Testing scoring agent with', limitedData.length, 'keywords');

      const testResponse = await fetch(getFullApiUrl('/api/v1/test/scoring-agent'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          csv_data: limitedData,
          asin: asin || null
        }),
      });

      if (!testResponse.ok) {
        const errorText = await testResponse.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Test failed (${testResponse.status}): ${errorText}`);
      }

      const testData = await testResponse.json();
      setScoringResults(testData);

    } catch (error) {
      console.error('Error testing scoring agent:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadResults = () => {
    const results = activeTest === 'keyword' ? keywordResults : scoringResults;
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${activeTest}_agent_results.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const generateCSV = () => {
    if (activeTest === 'keyword' && keywordResults) {
      const csvContent = [
        ['Keyword Phrase', 'Category', 'Search Volume', 'Relevancy Score', 'Title Density', 'Top 10 Competitors', 'Total Competitors', 'Root Word'].join(','),
        ...keywordResults.keywords.map(kw => [
          `"${kw.keyword_phrase}"`,
          kw.category,
          kw.search_volume || '',
          kw.relevancy_score,
          kw.title_density || '',
          kw.top_10_competitors,
          kw.total_competitors,
          kw.root_word
        ].join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.setAttribute('hidden', '');
      a.setAttribute('href', url);
      a.setAttribute('download', 'keyword_analysis_results.csv');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } else if (activeTest === 'scoring' && scoringResults) {
      const allKeywords = [
        ...scoringResults.critical_keywords,
        ...scoringResults.high_priority_keywords
      ];
      
      const csvContent = [
        ['Keyword Phrase', 'Category', 'Intent Score', 'Priority Score', 'Search Volume', 'Relevancy Score', 'Competition Level', 'Opportunity Score', 'Business Value', 'Opportunity Type', 'Root Word'].join(','),
        ...allKeywords.map(kw => [
          `"${kw.keyword_phrase}"`,
          kw.category,
          kw.intent_score,
          kw.priority_score.toFixed(1),
          kw.search_volume || '',
          kw.relevancy_score,
          kw.competition_level,
          kw.opportunity_score.toFixed(1),
          `"${kw.business_value}"`,
          kw.opportunity_type,
          kw.root_word
        ].join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.setAttribute('hidden', '');
      a.setAttribute('href', url);
      a.setAttribute('download', 'scoring_analysis_results.csv');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const getPriorityBadgeColor = (score: number) => {
    if (score >= 80) return 'bg-red-500';
    if (score >= 60) return 'bg-orange-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getIntentBadgeColor = (score: number) => {
    if (score === 3) return 'bg-purple-500';
    if (score === 2) return 'bg-blue-500';
    if (score === 1) return 'bg-gray-500';
    return 'bg-red-500';
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">🧪 Agentic Workflow Test Page</h1>
      
      {/* Input Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Test Configuration</CardTitle>
          <CardDescription>Upload a Helium10 CSV file and test the agents</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              CSV File (Helium10 Cerebro format)
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              ASIN (Optional)
            </label>
            <input
              type="text"
              value={asin}
              onChange={(e) => setAsin(e.target.value)}
              placeholder="B00O64QJOC"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div className="flex gap-4">
            <Button 
              onClick={testKeywordAgent}
              disabled={!file || isLoading}
              className="flex-1"
            >
              {isLoading && activeTest === 'keyword' ? 'Testing Keyword Agent...' : '🔍 Test Keyword Agent'}
            </Button>
            
            <Button 
              onClick={testScoringAgent}
              disabled={!file || isLoading}
              className="flex-1"
              variant="secondary"
            >
              {isLoading && activeTest === 'scoring' ? 'Testing Scoring Agent...' : '🎯 Test Scoring Agent'}
            </Button>
          </div>
          
          {file && (
            <p className="text-sm text-gray-600">
              Selected file: {file.name} ({(file.size / 1024).toFixed(1)} KB)
              <br />
              <span className="text-xs text-gray-500">
                Note: Processing limited to first {activeTest === 'scoring' ? '30' : '50'} keywords for testing
              </span>
            </p>
          )}
        </CardContent>
      </Card>

      {/* Keyword Agent Results */}
      {keywordResults && activeTest === 'keyword' && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              🔍 Keyword Agent Results
              <div className="flex gap-2">
                <Button onClick={generateCSV} variant="outline" size="sm">
                  📊 Download CSV
                </Button>
                <Button onClick={downloadResults} variant="outline" size="sm">
                  💾 Download JSON
                </Button>
              </div>
            </CardTitle>
            <CardDescription>
              Processed {keywordResults.total_keywords} keywords with categorization and analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{keywordResults.total_keywords}</div>
                <div className="text-sm text-blue-800">Total Keywords</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{keywordResults.category_stats?.length || 0}</div>
                <div className="text-sm text-green-800">Categories Found</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {keywordResults.keywords.filter(k => k.relevancy_score > 50).length}
                </div>
                <div className="text-sm text-purple-800">High Relevancy</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {keywordResults.keywords.filter(k => (k.search_volume || 0) > 500).length}
                </div>
                <div className="text-sm text-orange-800">High Volume</div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Keyword</th>
                    <th className="px-4 py-2 text-left">Category</th>
                    <th className="px-4 py-2 text-left">Volume</th>
                    <th className="px-4 py-2 text-left">Relevancy</th>
                    <th className="px-4 py-2 text-left">Title Density</th>
                    <th className="px-4 py-2 text-left">Root Word</th>
                  </tr>
                </thead>
                <tbody>
                  {keywordResults.keywords.slice(0, 20).map((keyword, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2 font-medium">{keyword.keyword_phrase}</td>
                      <td className="px-4 py-2">
                        <Badge variant="outline">{keyword.category}</Badge>
                      </td>
                      <td className="px-4 py-2">{keyword.search_volume?.toLocaleString() || 'N/A'}</td>
                      <td className="px-4 py-2">{keyword.relevancy_score.toFixed(1)}%</td>
                      <td className="px-4 py-2">{keyword.title_density?.toFixed(1) || 'N/A'}%</td>
                      <td className="px-4 py-2">{keyword.root_word}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scoring Agent Results */}
      {scoringResults && activeTest === 'scoring' && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                🎯 Scoring Agent Results
                <div className="flex gap-2">
                  <Button onClick={generateCSV} variant="outline" size="sm">
                    📊 Download CSV
                  </Button>
                  <Button onClick={downloadResults} variant="outline" size="sm">
                    💾 Download JSON
                  </Button>
                </div>
              </CardTitle>
              <CardDescription>
                Analyzed {scoringResults.total_keywords_analyzed} keywords with intent scoring and prioritization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{scoringResults.priority_distribution.critical}</div>
                  <div className="text-sm text-red-800">Critical</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{scoringResults.priority_distribution.high}</div>
                  <div className="text-sm text-orange-800">High Priority</div>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{scoringResults.priority_distribution.medium}</div>
                  <div className="text-sm text-yellow-800">Medium</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{scoringResults.priority_distribution.low}</div>
                  <div className="text-sm text-green-800">Low Priority</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-gray-600">{scoringResults.priority_distribution.filtered}</div>
                  <div className="text-sm text-gray-800">Filtered</div>
                </div>
              </div>

              {/* Insights */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-xl font-bold text-blue-600">{scoringResults.insights.avg_priority_score.toFixed(1)}</div>
                  <div className="text-sm text-blue-800">Avg Priority Score</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-xl font-bold text-purple-600">{scoringResults.insights.high_value_keywords}</div>
                  <div className="text-sm text-purple-800">High Value Keywords</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-xl font-bold text-green-600">{scoringResults.insights.quick_wins}</div>
                  <div className="text-sm text-green-800">Quick Wins</div>
                </div>
                <div className="bg-indigo-50 p-4 rounded-lg">
                  <div className="text-xl font-bold text-indigo-600">{scoringResults.insights.total_search_volume.toLocaleString()}</div>
                  <div className="text-sm text-indigo-800">Total Volume</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Critical Keywords */}
          {scoringResults.critical_keywords.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>🏆 Critical Keywords ({scoringResults.critical_keywords.length})</CardTitle>
                <CardDescription>Must-target keywords with highest commercial intent</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="min-w-full table-auto">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="px-4 py-2 text-left">Keyword</th>
                        <th className="px-4 py-2 text-left">Intent</th>
                        <th className="px-4 py-2 text-left">Priority</th>
                        <th className="px-4 py-2 text-left">Volume</th>
                        <th className="px-4 py-2 text-left">Competition</th>
                        <th className="px-4 py-2 text-left">Opportunity</th>
                        <th className="px-4 py-2 text-left">Business Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scoringResults.critical_keywords.slice(0, 10).map((keyword, index) => (
                        <tr key={index} className="border-b">
                          <td className="px-4 py-2 font-medium">{keyword.keyword_phrase}</td>
                          <td className="px-4 py-2">
                            <Badge className={getIntentBadgeColor(keyword.intent_score)}>
                              {keyword.intent_score}/3
                            </Badge>
                          </td>
                          <td className="px-4 py-2">
                            <Badge className={getPriorityBadgeColor(keyword.priority_score)}>
                              {keyword.priority_score.toFixed(1)}
                            </Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.search_volume?.toLocaleString() || 'N/A'}</td>
                          <td className="px-4 py-2">
                            <Badge variant={keyword.competition_level === 'low' ? 'default' : keyword.competition_level === 'medium' ? 'secondary' : 'destructive'}>
                              {keyword.competition_level}
                            </Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.opportunity_score.toFixed(1)}</td>
                          <td className="px-4 py-2 text-sm max-w-xs truncate" title={keyword.business_value}>
                            {keyword.business_value}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* High Priority Keywords */}
          {scoringResults.high_priority_keywords.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>🎯 High Priority Keywords ({scoringResults.high_priority_keywords.length})</CardTitle>
                <CardDescription>Important keywords for market positioning</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="min-w-full table-auto">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="px-4 py-2 text-left">Keyword</th>
                        <th className="px-4 py-2 text-left">Intent</th>
                        <th className="px-4 py-2 text-left">Priority</th>
                        <th className="px-4 py-2 text-left">Volume</th>
                        <th className="px-4 py-2 text-left">Competition</th>
                        <th className="px-4 py-2 text-left">Opportunity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scoringResults.high_priority_keywords.slice(0, 10).map((keyword, index) => (
                        <tr key={index} className="border-b">
                          <td className="px-4 py-2 font-medium">{keyword.keyword_phrase}</td>
                          <td className="px-4 py-2">
                            <Badge className={getIntentBadgeColor(keyword.intent_score)}>
                              {keyword.intent_score}/3
                            </Badge>
                          </td>
                          <td className="px-4 py-2">
                            <Badge className={getPriorityBadgeColor(keyword.priority_score)}>
                              {keyword.priority_score.toFixed(1)}
                            </Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.search_volume?.toLocaleString() || 'N/A'}</td>
                          <td className="px-4 py-2">
                            <Badge variant={keyword.competition_level === 'low' ? 'default' : keyword.competition_level === 'medium' ? 'secondary' : 'destructive'}>
                              {keyword.competition_level}
                            </Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.opportunity_score.toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Top Opportunities */}
          {scoringResults.top_opportunities.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>🚀 Top Opportunities ({scoringResults.top_opportunities.length})</CardTitle>
                <CardDescription>Best opportunities for quick wins and growth</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="min-w-full table-auto">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="px-4 py-2 text-left">Keyword</th>
                        <th className="px-4 py-2 text-left">Opportunity Type</th>
                        <th className="px-4 py-2 text-left">Opportunity Score</th>
                        <th className="px-4 py-2 text-left">Volume</th>
                        <th className="px-4 py-2 text-left">Competition</th>
                        <th className="px-4 py-2 text-left">Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scoringResults.top_opportunities.slice(0, 10).map((keyword, index) => (
                        <tr key={index} className="border-b">
                          <td className="px-4 py-2 font-medium">{keyword.keyword_phrase}</td>
                          <td className="px-4 py-2">
                            <Badge variant="outline">{keyword.opportunity_type.replace('_', ' ')}</Badge>
                          </td>
                          <td className="px-4 py-2">
                            <Badge className="bg-green-500">{keyword.opportunity_score.toFixed(1)}</Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.search_volume?.toLocaleString() || 'N/A'}</td>
                          <td className="px-4 py-2">
                            <Badge variant={keyword.competition_level === 'low' ? 'default' : 'secondary'}>
                              {keyword.competition_level}
                            </Badge>
                          </td>
                          <td className="px-4 py-2">{keyword.priority_score.toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Category Performance */}
          {scoringResults.category_stats.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>📊 Category Performance</CardTitle>
                <CardDescription>Performance analysis by keyword category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {scoringResults.category_stats.map((stat, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h4 className="font-semibold text-lg mb-2">{stat.category_name}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Total Keywords:</span>
                          <span className="font-medium">{stat.total_keywords}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Intent Score:</span>
                          <span className="font-medium">{stat.avg_intent_score.toFixed(1)}/3</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Priority:</span>
                          <span className="font-medium">{stat.avg_priority_score.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Critical Count:</span>
                          <span className="font-medium text-red-600">{stat.critical_priority_count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>High Priority:</span>
                          <span className="font-medium text-orange-600">{stat.high_priority_count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Volume:</span>
                          <span className="font-medium">{stat.total_search_volume.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">
                {activeTest === 'keyword' ? 'Testing Keyword Agent...' : 'Testing Scoring Agent...'}
              </p>
              <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 