"use client"

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, ScatterChart, Scatter } from 'recharts';
import { ChevronDown, ChevronRight, Search, Target, TrendingUp, Package, Star, ExternalLink, Download, Filter, Eye } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LucideIcon } from 'lucide-react';

// Type definitions
interface TabButtonProps {
  id: string;
  label: string;
  icon: LucideIcon;
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
  id: string;
}

const AmazonAnalysisResults = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Parse the actual data from your system response
  const systemData = {
    success: true,
    asin: "B0D5BL35MS",
    marketplace: "US",
    product: {
      title: "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
      brand: "Brewer Outdoor Solutions",
      form: "Freeze-dried strawberry slices",
      attributes: ["Organic", "No sugar added", "Gluten free"],
      packSize: "4 Pack",
      unitSize: "1.2 oz",
      useCases: ["Baking", "Smoothies", "Cereals", "Travel", "Snacking"],
      rating: "4.4 out of 5 stars",
      reviews: "93 ratings",
      bsr: "#71,397 in Grocery & Gourmet Food",
      categoryRank: "#179 in Dried Berries"
    }
  };

  // Category distribution from actual data
  const categoryData = [
    { name: 'Relevant', count: 13, color: '#10B981', percentage: 35.1 },
    { name: 'Design-Specific', count: 12, color: '#3B82F6', percentage: 32.4 },
    { name: 'Irrelevant', count: 6, color: '#EF4444', percentage: 16.2 },
    { name: 'Branded', count: 4, color: '#F59E0B', percentage: 10.8 },
    { name: 'Spanish', count: 1, color: '#8B5CF6', percentage: 2.7 },
    { name: 'Outlier', count: 1, color: '#6B7280', percentage: 2.7 }
  ];

  // Root word analysis from actual data
  const rootWordData = [
    { root: 'strawberry', volume: 16268, count: 25, avgIntent: 2.2 },
    { root: 'apple', volume: 3235, count: 4, avgIntent: 0 },
    { root: 'slice', volume: 2607, count: 6, avgIntent: 2.8 },
    { root: 'chip', volume: 371, count: 1, avgIntent: 2 },
    { root: 'fruit', volume: 297, count: 1, avgIntent: 2 },
    { root: 'shortcake', volume: 229, count: 2, avgIntent: 1 },
    { root: 'fresa', volume: 288, count: 1, avgIntent: 2 }
  ];

  // Top keywords with all metrics from actual data
  const keywordData = [
    {
      phrase: "dried strawberries",
      searchVolume: 8603,
      root: "strawberry",
      category: "Relevant",
      relevancyScore: 5,
      intentScore: 2,
      titleDensity: 21,
      cpr: 41,
      competingProducts: 819,
      rankingCompetitors: 9,
      competitorRankAvg: 44.4,
      competitorPerformanceScore: 6
    },
    {
      phrase: "freeze dried apples",
      searchVolume: 2686,
      root: "apple",
      category: "Irrelevant",
      relevancyScore: 4,
      intentScore: 0,
      titleDensity: 2,
      cpr: 28,
      competingProducts: 417,
      rankingCompetitors: 6,
      competitorRankAvg: 8.8,
      competitorPerformanceScore: 8
    },
    {
      phrase: "freeze dried strawberries bulk",
      searchVolume: 909,
      root: "strawberry",
      category: "Design-Specific",
      relevancyScore: 3,
      intentScore: 3,
      titleDensity: 0,
      cpr: 12,
      competingProducts: 640,
      rankingCompetitors: 9,
      competitorRankAvg: 15.9,
      competitorPerformanceScore: 10
    },
    {
      phrase: "freeze dried strawberry",
      searchVolume: 847,
      root: "strawberry",
      category: "Relevant",
      relevancyScore: 3,
      intentScore: 2,
      titleDensity: 5,
      cpr: 11,
      competingProducts: 632,
      rankingCompetitors: 9,
      competitorRankAvg: 16.4,
      competitorPerformanceScore: 8
    },
    {
      phrase: "freeze dried apple slices",
      searchVolume: 773,
      root: "slice",
      category: "Irrelevant",
      relevancyScore: 6,
      intentScore: 0,
      titleDensity: 5,
      cpr: 11,
      competingProducts: 221,
      rankingCompetitors: 6,
      competitorRankAvg: 10.2,
      competitorPerformanceScore: 8
    },
    {
      phrase: "freeze dried strawberry slices",
      searchVolume: 713,
      root: "slice",
      category: "Design-Specific",
      relevancyScore: 8,
      intentScore: 3,
      titleDensity: 4,
      cpr: 10,
      competingProducts: 301,
      rankingCompetitors: 9,
      competitorRankAvg: 36,
      competitorPerformanceScore: 6
    },
    {
      phrase: "bulk freeze dried strawberries",
      searchVolume: 482,
      root: "strawberry",
      category: "Design-Specific",
      relevancyScore: 2,
      intentScore: 3,
      titleDensity: 1,
      cpr: 9,
      competingProducts: 712,
      rankingCompetitors: 9,
      competitorRankAvg: 22.1,
      competitorPerformanceScore: 8
    },
    {
      phrase: "freeze-dried strawberries",
      searchVolume: 470,
      root: "strawberry",
      category: "Relevant",
      relevancyScore: 4,
      intentScore: 2,
      titleDensity: 4,
      cpr: 8,
      competingProducts: 548,
      rankingCompetitors: 9,
      competitorRankAvg: 15.9,
      competitorPerformanceScore: 10
    }
  ];

  // SEO comparison metrics from actual data
  const seoComparison = {
    current: {
      titleChars: 199,
      keywordsCovered: 9,
      coveragePercentage: 36,
      titleKeywords: 3,
      bulletKeywords: 10,
      backendKeywords: 0
    },
    optimized: {
      titleChars: 187,
      keywordsCovered: 25,
      coveragePercentage: 100,
      titleKeywords: 5,
      bulletKeywords: 16,
      backendKeywords: 11
    },
    improvement: {
      coverageDelta: 64,
      volumeIncrease: 4169,
      intentImprovement: 16,
      overallScore: 10
    }
  };

  // Intent score distribution
  const intentDistribution = [
    { intent: 0, count: 6, label: 'Irrelevant' },
    { intent: 1, count: 3, label: 'Low Intent' },
    { intent: 2, count: 21, label: 'Medium Intent' },
    { intent: 3, count: 7, label: 'High Intent' }
  ];

  // Competition analysis
  const competitionData = keywordData.map(kw => ({
    keyword: kw.phrase.slice(0, 20) + '...',
    difficulty: kw.competitorPerformanceScore,
    opportunity: Math.max(0, 10 - kw.competitorPerformanceScore + (kw.intentScore * 2)),
    volume: kw.searchVolume
  }));

    // Navigation component
  const TabButton = ({ id, label, icon: Icon }: TabButtonProps) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        activeTab === id ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
      }`}
    >
      <Icon size={18} />
      {label}
    </button>
  );

  const ExpandableSection = ({ title, children, id }: SectionProps) => {
    const isExpanded = expandedSection === id;
    return (
      <Card className="mb-4">
        <CardHeader 
          className="cursor-pointer hover:bg-gray-50"
          onClick={() => setExpandedSection(isExpanded ? null : id)}
        >
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{title}</CardTitle>
            {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          </div>
        </CardHeader>
        {isExpanded && (
          <CardContent>
            {children}
          </CardContent>
        )}
      </Card>
    );
  };

    const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'Relevant': 'bg-green-100 text-green-800',
      'Design-Specific': 'bg-blue-100 text-blue-800',
      'Irrelevant': 'bg-red-100 text-red-800',
      'Branded': 'bg-purple-100 text-purple-800',
      'Spanish': 'bg-yellow-100 text-yellow-800',
      'Outlier': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const getIntentBadge = (score: number) => {
    if (score === 0) return <Badge variant="destructive">Intent: 0</Badge>;
    if (score === 1) return <Badge variant="secondary">Intent: 1</Badge>;
    if (score === 2) return <Badge variant="outline">Intent: 2</Badge>;
    if (score === 3) return <Badge className="bg-green-600">Intent: 3</Badge>;
    return <Badge>Intent: {score}</Badge>;
  };

  const filteredKeywords = selectedCategory === 'all' 
    ? keywordData 
    : keywordData.filter(kw => kw.category === selectedCategory);

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Amazon Keyword Analysis Results</h1>
              <p className="text-gray-600 mt-1">ASIN: {systemData.asin} • {systemData.marketplace} Marketplace</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-yellow-500 fill-current" />
                <span className="font-semibold">{systemData.product.rating}</span>
              </div>
              <div className="text-sm text-gray-600">{systemData.product.reviews}</div>
            </div>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-blue-600 font-semibold">Total Keywords</div>
              <div className="text-2xl font-bold">37</div>
              <div className="text-sm text-blue-600">Analyzed</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-green-600 font-semibold">Coverage Improvement</div>
              <div className="text-2xl font-bold">+{seoComparison.improvement.coverageDelta}%</div>
              <div className="text-sm text-green-600">36% → 100%</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-purple-600 font-semibold">Volume Increase</div>
              <div className="text-2xl font-bold">+{seoComparison.improvement.volumeIncrease.toLocaleString()}</div>
              <div className="text-sm text-purple-600">Search Volume</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-orange-600 font-semibold">Optimization Score</div>
              <div className="text-2xl font-bold">{seoComparison.improvement.overallScore}/10</div>
              <div className="text-sm text-orange-600">Perfect Score</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap gap-3">
            <TabButton id="overview" label="Overview" icon={Package} />
            <TabButton id="keywords" label="Keywords" icon={Search} />
            <TabButton id="competition" label="Competition" icon={Target} />
            <TabButton id="seo" label="SEO Analysis" icon={TrendingUp} />
            <TabButton id="insights" label="Insights" icon={Eye} />
          </div>
        </CardContent>
      </Card>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Keyword Categories</CardTitle>
                <CardDescription>Distribution of 37 analyzed keywords</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      label={(entry: any) => `${entry.name} (${entry.count})`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number | string, name: string) => [value, name]} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Root Word Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Root Word Volume Analysis</CardTitle>
                <CardDescription>Search volume by keyword root</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={rootWordData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="root" />
                    <YAxis />
                    <Tooltip formatter={(value: number | string, name: string) => [typeof value === 'number' ? value.toLocaleString() : value, name]} />
                    <Bar dataKey="volume" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Intent Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Intent Score Distribution</CardTitle>
              <CardDescription>Keywords categorized by search intent (0-3 scale)</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={intentDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Product Information */}
          <Card>
            <CardHeader>
              <CardTitle>Product Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-gray-700">Title:</span>
                    <p className="text-gray-900 mt-1 text-sm">{systemData.product.title}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Brand:</span>
                    <p className="text-gray-900 mt-1">{systemData.product.brand}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Form:</span>
                    <p className="text-gray-900 mt-1">{systemData.product.form}</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-gray-700">Attributes:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {systemData.product.attributes.map((attr, index) => (
                        <Badge key={index} variant="outline">{attr}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Use Cases:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {systemData.product.useCases.map((use, index) => (
                        <Badge key={index} variant="secondary">{use}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Rankings:</span>
                    <p className="text-gray-900 mt-1 text-sm">
                      {systemData.product.bsr}<br/>
                      {systemData.product.categoryRank}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Keywords Tab */}
      {activeTab === 'keywords' && (
        <div className="space-y-6">
          {/* Filter Controls */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <Filter className="h-4 w-4" />
                <span className="font-medium">Filter by category:</span>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={selectedCategory === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory('all')}
                  >
                    All (37)
                  </Button>
                  {categoryData.map(cat => (
                    <Button
                      key={cat.name}
                      variant={selectedCategory === cat.name ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedCategory(cat.name)}
                    >
                      {cat.name} ({cat.count})
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Keywords Table */}
          <Card>
            <CardHeader>
              <CardTitle>Keyword Analysis Table</CardTitle>
              <CardDescription>
                Showing {filteredKeywords.length} keywords with complete metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-2">Keyword</th>
                      <th className="text-right py-3 px-2">Volume</th>
                      <th className="text-center py-3 px-2">Intent</th>
                      <th className="text-center py-3 px-2">Relevancy</th>
                      <th className="text-right py-3 px-2">Title Density</th>
                      <th className="text-right py-3 px-2">CPR</th>
                      <th className="text-center py-3 px-2">Category</th>
                      <th className="text-center py-3 px-2">Root</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredKeywords.map((keyword, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-2 font-medium text-sm max-w-[200px]">
                          <div className="truncate" title={keyword.phrase}>
                            {keyword.phrase}
                          </div>
                        </td>
                        <td className="text-right py-3 px-2 text-sm">
                          {keyword.searchVolume.toLocaleString()}
                        </td>
                        <td className="text-center py-3 px-2">
                          {getIntentBadge(keyword.intentScore)}
                        </td>
                        <td className="text-center py-3 px-2">
                          <Badge variant="outline">{keyword.relevancyScore}/10</Badge>
                        </td>
                        <td className="text-right py-3 px-2 text-sm">
                          {keyword.titleDensity}
                        </td>
                        <td className="text-right py-3 px-2 text-sm">
                          {keyword.cpr}
                        </td>
                        <td className="text-center py-3 px-2">
                          <Badge className={getCategoryColor(keyword.category)}>
                            {keyword.category}
                          </Badge>
                        </td>
                        <td className="text-center py-3 px-2 text-sm">
                          <Badge variant="secondary">{keyword.root}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Competition Tab */}
      {activeTab === 'competition' && (
        <div className="space-y-6">
          {/* Competition Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">7.8</div>
                  <div className="text-sm text-gray-600">Avg Competitors in Top 10</div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">25.4</div>
                  <div className="text-sm text-gray-600">Avg Competitor Rank</div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">7.2</div>
                  <div className="text-sm text-gray-600">Avg Performance Score</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Competition Analysis Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Keyword Opportunity vs Competition</CardTitle>
              <CardDescription>
                Bubble size represents search volume. Higher opportunity, lower difficulty = better targets
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart data={competitionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="difficulty" 
                    name="Competition Difficulty"
                    domain={[0, 10]}
                  />
                  <YAxis 
                    dataKey="opportunity" 
                    name="Opportunity Score"
                    domain={[0, 15]}
                  />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    formatter={(value: number | string, name: string) => [value, name]}
                    labelFormatter={(label: string) => `Keyword: ${label}`}
                  />
                  <Scatter dataKey="volume" fill="#3B82F6" />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Competition Details Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Competition Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3">Keyword</th>
                      <th className="text-right py-3">Competing Products</th>
                      <th className="text-right py-3">Top 10 Competitors</th>
                      <th className="text-right py-3">Avg Competitor Rank</th>
                      <th className="text-center py-3">Performance Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keywordData.slice(0, 8).map((keyword, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-3 font-medium text-sm">{keyword.phrase}</td>
                        <td className="text-right py-3 text-sm">
                          {keyword.competingProducts.toLocaleString()}
                        </td>
                        <td className="text-right py-3 text-sm">
                          {keyword.rankingCompetitors}
                        </td>
                        <td className="text-right py-3 text-sm">
                          {keyword.competitorRankAvg}
                        </td>
                        <td className="text-center py-3">
                          <Badge 
                            className={
                              keyword.competitorPerformanceScore >= 8 
                                ? 'bg-red-100 text-red-800'
                                : keyword.competitorPerformanceScore >= 6
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                            }
                          >
                            {keyword.competitorPerformanceScore}/10
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* SEO Analysis Tab */}
      {activeTab === 'seo' && (
        <div className="space-y-6">
          {/* SEO Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-red-600">Current SEO</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Keyword Coverage:</span>
                    <span className="font-bold">{seoComparison.current.coveragePercentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Title Keywords:</span>
                    <span>{seoComparison.current.titleKeywords}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Title Length:</span>
                    <span>{seoComparison.current.titleChars} chars</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Backend Keywords:</span>
                    <span>{seoComparison.current.backendKeywords}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">Optimized SEO</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Keyword Coverage:</span>
                    <span className="font-bold text-green-600">{seoComparison.optimized.coveragePercentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Title Keywords:</span>
                    <span className="text-green-600">{seoComparison.optimized.titleKeywords}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Title Length:</span>
                    <span>{seoComparison.optimized.titleChars} chars</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Backend Keywords:</span>
                    <span className="text-green-600">{seoComparison.optimized.backendKeywords}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-blue-600">Improvement</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Coverage Gain:</span>
                    <span className="font-bold text-blue-600">+{seoComparison.improvement.coverageDelta}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Volume Increase:</span>
                    <span className="text-blue-600">+{seoComparison.improvement.volumeIncrease.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Intent Improvement:</span>
                    <span className="text-blue-600">+{seoComparison.improvement.intentImprovement}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Overall Score:</span>
                    <span className="font-bold text-blue-600">{seoComparison.improvement.overallScore}/10</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Title Optimization */}
          <ExpandableSection title="Title Optimization" id="title">
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Current Title ({seoComparison.current.titleChars} chars)</h4>
                <div className="bg-red-50 p-3 rounded border text-sm border-red-200">
                  {systemData.product.title}
                </div>
                <div className="mt-2 text-sm text-gray-600">Keywords found: {seoComparison.current.titleKeywords}</div>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Optimized Title ({seoComparison.optimized.titleChars} chars)</h4>
                <div className="bg-green-50 p-3 rounded border text-sm border-green-200">
                  BREWER Freeze Dried Strawberries Bulk - Organic Strawberry Slices 4 Pack (1.2 oz Each), No Sugar Added, Gluten Free Fruit Snack for Smoothies, Baking & Cereal - Freeze-Dried Strawberries
                </div>
                <div className="mt-2 text-sm text-gray-600">Keywords included: {seoComparison.optimized.titleKeywords}</div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <h5 className="font-medium mb-2">Key Improvements:</h5>
                <ul className="list-disc list-inside text-sm space-y-1">
                  <li>Front-loaded primary query &lsquo;freeze dried strawberries bulk&rsquo;</li>
                  <li>Added hyphenated variant &lsquo;freeze-dried strawberries&rsquo; for indexing breadth</li>
                  <li>Improved readability while maintaining keyword density</li>
                  <li>Optimized character usage: {seoComparison.current.titleChars} → {seoComparison.optimized.titleChars} chars</li>
                </ul>
              </div>
            </div>
          </ExpandableSection>

          {/* Backend Keywords */}
          <ExpandableSection title="Backend Keywords Strategy" id="backend">
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Recommended backend search terms to capture misspellings, synonyms, and alternate word orders:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {[
                  'freezedried strawberry',
                  'freezer dried strawberries', 
                  'free dried strawberries',
                  'dried freeze strawberries',
                  'freeze dry strawberries',
                  'freeze dry strawberry',
                  'dried strawberrries',
                  'dehydrated strawberries sliced',
                  'dehydrated strawberries bulk',
                  'fresa'
                ].map((term, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {term}
                  </Badge>
                ))}
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h5 className="font-medium mb-2">Strategy Notes:</h5>
                <ul className="list-disc list-inside text-sm space-y-1">
                  <li>Captures common misspellings and alternate spellings</li>
                  <li>Includes &lsquo;dehydrated&rsquo; synonyms for broader reach</li>
                  <li>Spanish keyword &lsquo;fresa&rsquo; for Hispanic market</li>
                  <li>Avoids duplicating front-end keywords per Amazon guidelines</li>
                </ul>
              </div>
            </div>
          </ExpandableSection>
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          {/* Key Insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">Opportunities</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">High-Intent Keywords</div>
                      <div className="text-sm text-gray-600">7 keywords with intent score 3 identified</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Zero Title Density</div>
                      <div className="text-sm text-gray-600">Multiple high-volume keywords with 0 title density</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Strawberry Root Dominance</div>
                      <div className="text-sm text-gray-600">16,268 combined volume for strawberry-related terms</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Design-Specific Potential</div>
                      <div className="text-sm text-gray-600">12 design-specific keywords with high intent scores</div>
                    </div>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-red-600">Challenges</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">High Competition</div>
                      <div className="text-sm text-gray-600">Several keywords with 600+ competing products</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Irrelevant Keywords</div>
                      <div className="text-sm text-gray-600">6 irrelevant keywords (apple-related) diluting focus</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Branded Competition</div>
                      <div className="text-sm text-gray-600">4 competitor brand terms present in dataset</div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <div className="font-medium">Low Coverage</div>
                      <div className="text-sm text-gray-600">Current listing only covers 36% of relevant keywords</div>
                    </div>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Strategic Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3 text-blue-600">Immediate Actions (0-30 days)</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                      <span>Implement optimized title with primary keywords front-loaded</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                      <span>Add backend keywords to capture misspellings and variants</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                      <span>Focus on &lsquo;bulk&rsquo; and &lsquo;slices&rsquo; design-specific terms</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                      <span>Optimize bullet points for intent score 3 keywords</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-3 text-purple-600">Long-term Strategy (30+ days)</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2"></div>
                      <span>Monitor performance of optimized keywords</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2"></div>
                      <span>Expand into related root words (fruit, snack)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2"></div>
                      <span>Test seasonal keywords and trends</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2"></div>
                      <span>A/B test title variations for CTR improvement</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Download Options */}
          <Card>
            <CardHeader>
              <CardTitle>Export Data</CardTitle>
              <CardDescription>Download analysis results in various formats</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Download Keywords CSV
                </Button>
                <Button variant="outline" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  SEO Report PDF
                </Button>
                <Button variant="outline" className="flex items-center gap-2">
                  <ExternalLink className="h-4 w-4" />
                  Share Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AmazonAnalysisResults;
