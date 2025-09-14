"use client"

import React, { useMemo, useState, useEffect } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronRight, Star, TrendingUp, Package, Search, Target } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { config, getFullApiUrl } from '@/lib/config';
import apiClient, { api as apiHelpers } from '@/lib/api';

const Section = ({ title, children, isExpandable = false }: { 
  title: string; 
  children: React.ReactNode; 
  isExpandable?: boolean;
}) => {
  const [isExpanded, setIsExpanded] = useState(!isExpandable);
  
  return (
    <Card className="mb-6">
      <CardHeader 
        className={isExpandable ? "cursor-pointer hover:bg-gray-50" : ""}
        onClick={() => isExpandable && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {title}
          </CardTitle>
          {isExpandable && (
            isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />
          )}
        </div>
      </CardHeader>
      {isExpanded && <CardContent>{children}</CardContent>}
    </Card>
  );
};

const KeyValue = ({ label, value }: { label: string; value: string | number }) => (
  <div className="flex justify-between items-start py-1 border-b border-gray-100 last:border-b-0">
    <span className="font-medium text-gray-600 text-sm">{label}:</span>
    <span className="text-sm text-gray-900 text-right max-w-xs">
      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
    </span>
  </div>
);

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
  if (score === 3) return <Badge className="bg-green-600 text-white">Intent: 3</Badge>;
  return <Badge>Intent: {score}</Badge>;
};

// Safe number formatter to avoid calling toLocaleString on undefined/null
const fmtNumber = (value: unknown, fallback = '0'): string => {
  const n =
    typeof value === 'number'
      ? value
      : typeof value === 'string'
      ? Number(value)
      : NaN;
  return Number.isFinite(n) ? n.toLocaleString() : fallback;
};

// Normalize potential value to an array for safe mapping/joining
const toArr = (v: unknown): any[] => (Array.isArray(v) ? v : v == null ? [] : [v]);

const TestResultsPage = () => {
  // Form state
  const [asinOrUrl, setAsinOrUrl] = useState('');
  const [marketplace, setMarketplace] = useState('US');
  const [mainKeyword, setMainKeyword] = useState<string>('');
  const [revenueCsv, setRevenueCsv] = useState<File | null>(null);
  const [designCsv, setDesignCsv] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data state
  const [response, setResponse] = useState<any | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Image gallery hooks must be unconditional (before any early return)
  const scrapedProductForImages = response?.ai_analysis_keywords?.scraped_product as any | undefined;
  const galleryImages: string[] = useMemo(() => {
    const raw = toArr(scrapedProductForImages?.images?.all_images).filter(Boolean) as string[];
    const normalize = (u: string): string => {
      try {
        // Strip query/fragment
        const base = u.split('?')[0].split('#')[0].trim();
        // Only upgrade Amazon media hosts
        if (!/\b(m\.media-amazon\.com|images-na\.ssl-images-amazon\.com)\b/i.test(base)) return base;
        // Turn thumbnails like .../I/51GKBz7WVYL._AC_US40_.jpg -> .../I/51GKBz7WVYL.jpg
        const m = base.match(/^(https?:\/\/[^\s]+\/images\/[^/]+\/[^.]+)(\._[^.]+_)?\.(jpg|jpeg|png|webp)$/i);
        if (m) return `${m[1]}.${m[3]}`;
        return base.replace(/\._[^./]+_(\.[a-zA-Z0-9]+)$/i, '$1');
      } catch {
        return u;
      }
    };
    const isProduct = (u: string): boolean => {
      const lower = u.toLowerCase();
      if (!/(\.jpg|\.jpeg|\.png|\.webp)$/i.test(lower)) return false;
      const noisy = ['\/images\/g\/', '/g/', 'play-icon', 'overlay', 'sprite', 'icon_', '360_icon', 'placeholder'];
      if (noisy.some((n) => lower.includes(n.replace(/\\/g, '')))) return false;
      return true;
    };
    const upgraded = raw.map(normalize).filter(isProduct);
    // Dedupe
    const seen = new Set<string>();
    return upgraded.filter((u) => (seen.has(u) ? false : (seen.add(u), true)));
  }, [scrapedProductForImages]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  useEffect(() => {
    const initial = (scrapedProductForImages?.images?.main_image as string) || galleryImages[0] || null;
    setSelectedImage(initial);
  }, [scrapedProductForImages, galleryImages]);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      // Prefer library client; fallback to direct fetch if bundler cache causes export mismatch
      const callViaClient = async () => {
        if ((apiHelpers as any)?.testResearchKeywords) {
          return (apiHelpers as any).testResearchKeywords({
            asin_or_url: asinOrUrl,
            marketplace,
            main_keyword: mainKeyword || undefined,
            revenue_csv: revenueCsv,
            design_csv: designCsv,
          });
        }
        if ((apiClient as any)?.testResearchKeywords) {
          return (apiClient as any).testResearchKeywords({
            asin_or_url: asinOrUrl,
            marketplace,
            main_keyword: mainKeyword || undefined,
            revenue_csv: revenueCsv,
            design_csv: designCsv,
          });
        }
        return { success: false, error: 'Client method not available' } as any;
      };

      let result = await callViaClient();
      if (!result?.success) {
        // Fallback direct fetch
        const formData = new FormData();
        formData.append('asin_or_url', asinOrUrl);
        formData.append('marketplace', marketplace || 'US');
        if (mainKeyword) formData.append('main_keyword', mainKeyword);
        if (revenueCsv) formData.append('revenue_csv', revenueCsv);
        if (designCsv) formData.append('design_csv', designCsv);

        const resp = await fetch(getFullApiUrl(config.api.endpoints.testResearchKeywords), {
          method: 'POST',
          body: formData,
        });
        if (!resp.ok) {
          const e = await resp.json().catch(() => ({}));
          throw new Error(e?.message || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        result = { success: true, data } as any;
      }

      if (!result.success) {
        throw new Error(result.error || 'Request failed');
      }

      setResponse(result.data as any);
    } catch (e: any) {
      setError(e?.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Only work with real API data - no mock fallback
  if (!response) {
    return (
      <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Amazon SEO Analysis Results</h1>
                <p className="text-gray-600 mt-1">Run analysis to see results</p>
              </div>
            </div>

            {/* Controls */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-4">
              <Input placeholder="ASIN or URL" value={asinOrUrl} onChange={(e) => setAsinOrUrl(e.target.value)} />
              <Input placeholder="Marketplace (US)" value={marketplace} onChange={(e) => setMarketplace(e.target.value)} />
              <Input placeholder="Main keyword" value={mainKeyword} onChange={(e) => setMainKeyword(e.target.value)} />
              <div>
                <Label htmlFor="revenueCsv" className="text-xs text-gray-600">Revenue CSV (Helium10 Top Revenue) – optional</Label>
                <Input id="revenueCsv" type="file" accept=".csv" onChange={(e) => setRevenueCsv(e.target.files?.[0] || null)} />
              </div>
              <div>
                <Label htmlFor="designCsv" className="text-xs text-gray-600">Design CSV (Helium10 Relevant Designs) – optional</Label>
                <Input id="designCsv" type="file" accept=".csv" onChange={(e) => setDesignCsv(e.target.files?.[0] || null)} />
              </div>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <Button onClick={handleRun} disabled={loading}>
                {loading ? 'Running…' : 'Run test-research-keywords'}
              </Button>
              <span className="text-xs text-gray-500">Endpoint: {getFullApiUrl(config.api.endpoints.testResearchKeywords)}</span>
            </div>
            {error && (
              <div className="text-sm text-red-600">{error}</div>
            )}
            {loading && (
              <div className="text-sm text-blue-600">Analysis in progress...</div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  const { asin, marketplace: resMarketplace, ai_analysis_keywords, seo_analysis, source } = response;
  const { structured_data, final_output, scraped_product } = ai_analysis_keywords || {};
  const { product_context, items, stats } = structured_data || {};
  const { analysis } = seo_analysis || {};
  const { current_seo, optimized_seo, comparison, analysis_metadata } = analysis || {};

  

  return (
        <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header + Controls */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Amazon SEO Analysis Results</h1>
              <p className="text-gray-600 mt-1">
                {asin ? (
                  <>
                    ASIN: <a href={asin} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                      {asin.replace('http://amazon.com/dp/', '')}
                    </a> • {resMarketplace || marketplace} Marketplace
                  </>
                ) : (
                  'Analysis results will appear here'
                )}
              </p>
            </div>
            {scraped_product?.reviews && (
              <div className="text-right">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                  <span className="font-semibold">4.4 out of 5 stars</span>
                </div>
                <div className="text-sm text-gray-600">93 ratings</div>
              </div>
            )}
          </div>          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-4">
            <Input placeholder="ASIN or URL" value={asinOrUrl} onChange={(e) => setAsinOrUrl(e.target.value)} />
            <Input placeholder="Marketplace (US)" value={marketplace} onChange={(e) => setMarketplace(e.target.value)} />
            <Input placeholder="Main keyword" value={mainKeyword} onChange={(e) => setMainKeyword(e.target.value)} />
            <div>
              <Label htmlFor="revenueCsv" className="text-xs text-gray-600">Revenue CSV (Helium10 Top Revenue) – optional</Label>
              <Input id="revenueCsv" type="file" accept=".csv" onChange={(e) => setRevenueCsv(e.target.files?.[0] || null)} />
            </div>
            <div>
              <Label htmlFor="designCsv" className="text-xs text-gray-600">Design CSV (Helium10 Relevant Designs) – optional</Label>
              <Input id="designCsv" type="file" accept=".csv" onChange={(e) => setDesignCsv(e.target.files?.[0] || null)} />
            </div>
          </div>
          <div className="flex items-center gap-3 mb-2">
            <Button onClick={handleRun} disabled={loading}>
              {loading ? 'Running…' : 'Run test-research-keywords'}
            </Button>
            <span className="text-xs text-gray-500">Endpoint: {getFullApiUrl(config.api.endpoints.testResearchKeywords)}</span>
          </div>
          {error && (
            <div className="text-sm text-red-600">{error}</div>
          )}
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-blue-600 font-semibold">Total Keywords</div>
              <div className="text-2xl font-bold">{items?.length || 0}</div>
              <div className="text-sm text-blue-600">Analyzed</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-green-600 font-semibold">Coverage Improvement</div>
              <div className="text-2xl font-bold">+{comparison?.coverage_improvement?.delta_pct_points || 0}%</div>
              <div className="text-sm text-green-600">{comparison?.coverage_improvement?.before_coverage_pct || 0}% → {comparison?.coverage_improvement?.after_coverage_pct || 0}%</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-purple-600 font-semibold">Volume Increase</div>
              <div className="text-2xl font-bold">+{fmtNumber(comparison?.volume_improvement?.delta_volume)}</div>
              <div className="text-sm text-purple-600">Search Volume</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-orange-600 font-semibold">Optimization Score</div>
              <div className="text-2xl font-bold">{comparison?.summary_metrics?.overall_improvement_score || 0}/10</div>
              <div className="text-sm text-orange-600">Perfect Score</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap gap-3">
            <Button
              variant={activeTab === 'overview' ? 'default' : 'outline'}
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-2"
            >
              <Package size={16} />
              Overview
            </Button>
            <Button
              variant={activeTab === 'keywords' ? 'default' : 'outline'}
              onClick={() => setActiveTab('keywords')}
              className="flex items-center gap-2"
            >
              <Search size={16} />
              Keywords
            </Button>
            <Button
              variant={activeTab === 'seo' ? 'default' : 'outline'}
              onClick={() => setActiveTab('seo')}
              className="flex items-center gap-2"
            >
              <TrendingUp size={16} />
              SEO Analysis
            </Button>
            <Button
              variant={activeTab === 'product' ? 'default' : 'outline'}
              onClick={() => setActiveTab('product')}
              className="flex items-center gap-2"
            >
              <Target size={16} />
              Product Details
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <Section title="Product Information">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <KeyValue label="Title" value={product_context?.title || 'N/A'} />
                <KeyValue label="Brand" value={product_context?.brand || 'N/A'} />
                <KeyValue label="Form" value={product_context?.form || 'N/A'} />
                <KeyValue label="Pack Size" value={product_context?.pack_size || 'N/A'} />
                <KeyValue label="Unit Size" value={product_context?.unit_size_each_oz || 'N/A'} />
              </div>
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-gray-600 text-sm">Attributes:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {toArr(product_context?.attributes).map((attr: string, i: number) => (
                      <Badge key={i} variant="outline">{attr}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-600 text-sm">Use Cases:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {toArr(product_context?.use_cases).map((use: string, i: number) => (
                      <Badge key={i} variant="secondary">{use}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Section>

          <Section title="Product Images">
            {galleryImages.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Preview</h4>
                  {selectedImage ? (
                    <Image
                      src={selectedImage}
                      alt="Selected Product Image"
                      width={500}
                      height={500}
                      className="rounded-lg object-cover border max-h-[500px] w-auto"
                      priority
                    />
                  ) : (
                    <div className="w-full h-[300px] bg-gray-100 border rounded-lg grid place-items-center text-gray-500">
                      No preview available
                    </div>
                  )}
                </div>
                <div>
                  <h4 className="font-medium mb-2">Gallery ({scraped_product?.images?.image_count ?? galleryImages.length} total)</h4>
                  <div className="grid grid-cols-4 sm:grid-cols-5 gap-2 max-h-[520px] overflow-auto pr-1">
                    {galleryImages.map((img: string, i: number) => {
                      const isActive = img === selectedImage;
                      return (
                        <button
                          key={i}
                          type="button"
                          onClick={() => setSelectedImage(img)}
                          className={`relative aspect-square rounded overflow-hidden border focus:outline-none ${
                            isActive ? 'ring-2 ring-blue-500 border-blue-500' : 'hover:ring-2 hover:ring-gray-300'
                          }`}
                          title={`Image ${i + 1}`}
                        >
                          <Image
                            src={img}
                            alt={`Product image ${i + 1}`}
                            width={120}
                            height={120}
                            className="w-full h-full object-cover"
                          />
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No images available</p>
            )}
          </Section>

          <Section title="Category Distribution">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries((stats || {}) as Record<string, { count: number; examples: string[] }>).map(([category, data]) => (
                <div key={category} className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-gray-900">{data?.count || 0}</div>
                  <div className={`text-sm px-2 py-1 rounded-full mt-1 ${getCategoryColor(category)}`}>
                    {category}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        </div>
      )}

      {/* Keywords Tab */}
      {activeTab === 'keywords' && (
        <div className="space-y-6">
          <Section title="Keyword Analysis">
            <div className="overflow-x-auto">
              <table className="w-full table-auto">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium">Keyword</th>
                    <th className="text-right py-3 px-4 font-medium">Volume</th>
                    <th className="text-center py-3 px-4 font-medium">Intent</th>
                    <th className="text-center py-3 px-4 font-medium">Relevancy</th>
                    <th className="text-right py-3 px-4 font-medium">Title Density</th>
                    <th className="text-center py-3 px-4 font-medium">Category</th>
                    <th className="text-center py-3 px-4 font-medium">Root</th>
                  </tr>
                </thead>
                <tbody>
                  {(items || []).map((kw: { 
                    phrase: string; 
                    search_volume: number; 
                    intent_score: number; 
                    relevancy_score: number; 
                    title_density: number; 
                    category: string; 
                    root: string; 
                  }, i: number) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-sm">{kw.phrase}</td>
                      <td className="text-right py-3 px-4 text-sm">{fmtNumber(kw.search_volume)}</td>
                      <td className="text-center py-3 px-4">{getIntentBadge(kw.intent_score ?? 0)}</td>
                      <td className="text-center py-3 px-4">
                        <Badge variant="outline">{kw.relevancy_score}/10</Badge>
                      </td>
                      <td className="text-right py-3 px-4 text-sm">{kw.title_density}</td>
                      <td className="text-center py-3 px-4">
                        <Badge className={getCategoryColor(kw.category)}>{kw.category}</Badge>
                      </td>
                      <td className="text-center py-3 px-4">
                        <Badge variant="secondary">{kw.root}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        </div>
      )}

      {/* SEO Tab */}
      {activeTab === 'seo' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Row 1: Titles (Left = Current, Right = Optimized) */}
          <div className="space-y-6">
            <Section title={`Current Title (${current_seo?.title_analysis?.character_count ?? 0} chars)`}>
              <div className="space-y-2">
                <div className="bg-red-50 p-3 rounded border text-sm border-red-200">
                  {current_seo?.title_analysis?.content || '—'}
                </div>
                <div className="text-sm text-gray-600">
                  Keywords found: {toArr(current_seo?.title_analysis?.keywords_found).join(', ')}
                </div>
              </div>
            </Section>
          </div>

          {/* Right title */}
          <div className="space-y-6">
            <Section title={`Optimized Title (${optimized_seo?.optimized_title?.character_count ?? 0} chars)`}>
              <div className="space-y-2">
                <div className="bg-green-50 p-3 rounded border text-sm border-green-200">
                  {optimized_seo?.optimized_title?.content || '—'}
                </div>
                <div className="text-sm text-gray-600">
                  Keywords included: {toArr(optimized_seo?.optimized_title?.keywords_included).join(', ')}
                </div>
              </div>
            </Section>
          </div>

          {/* Paired bullet points aligned by index across both columns */}
          <div className="md:col-span-2">
            <Section title="Bullet Points (Current vs Optimized)">
              {(() => {
                const curr = toArr(current_seo?.bullets_analysis);
                const opt = toArr(optimized_seo?.optimized_bullets);
                const maxLen = Math.max(curr.length, opt.length);
                return (
                  <div className="space-y-6">
                    {Array.from({ length: maxLen }).map((_, i) => {
                      const c = curr[i];
                      const o = opt[i];
                      return (
                        <div key={i} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Current bullet */}
                          <div className="border rounded-lg p-4 h-full">
                            <h5 className="font-medium text-gray-700 mb-2">Bullet Point {i + 1}</h5>
                            <div className="bg-gray-50 p-3 rounded text-sm mb-3 min-h-[56px]">
                              {c?.content || '—'}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div>
                                <strong>Keywords Found:</strong>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {toArr(c?.keywords_found).map((kw: string, j: number) => (
                                    <Badge key={j} variant="outline" className="text-xs">{kw}</Badge>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <strong>Opportunities:</strong>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {toArr(c?.opportunities).map((op: string, j: number) => (
                                    <Badge key={j} variant="secondary" className="text-xs">{op}</Badge>
                                  ))}
                                </div>
                              </div>
                            </div>
                            <div className="flex gap-4 mt-3 text-xs text-gray-600">
                              <span>Keywords: {c?.keyword_count ?? 0}</span>
                              <span>Characters: {c?.character_count ?? 0}</span>
                              <span>Density: {c?.keyword_density ?? 0}%</span>
                            </div>
                          </div>

                          {/* Optimized bullet */}
                          <div className="border rounded-lg p-4 bg-green-50 border-green-200 h-full">
                            <h5 className="font-medium text-green-700 mb-2">Optimized Bullet Point {i + 1}</h5>
                            <div className="bg-white p-3 rounded text-sm mb-3 border min-h-[56px]">
                              {o?.content || '—'}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div>
                                <strong>Keywords Included:</strong>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {toArr(o?.keywords_included).map((kw: string, j: number) => (
                                    <Badge key={j} className="bg-green-600 text-white text-xs">{kw}</Badge>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <strong>Improvements:</strong>
                                <ul className="list-disc list-inside mt-1 text-xs text-gray-600">
                                  {toArr(o?.improvements).map((imp: string, j: number) => (
                                    <li key={j}>{imp}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                            <div className="flex gap-4 mt-3 text-xs text-gray-600">
                              <span>Characters: {o?.character_count ?? 0}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })()}
            </Section>
          </div>

          {/* Row 3: Remaining sections (Left current details, Right optimized details) */}
          <div className="space-y-6">
            <Section title="Current Root Coverage" isExpandable>
              <div className="space-y-4">
                <div className="p-4 bg-red-50 rounded-lg">
                  <h4 className="font-medium text-red-600 mb-2">Coverage</h4>
                  <div className="text-2xl font-bold text-red-600">{current_seo?.root_coverage?.coverage_percentage ?? 0}%</div>
                  <div className="text-sm text-red-600">{current_seo?.root_coverage?.covered_roots ?? 0} of {current_seo?.root_coverage?.total_roots ?? 0} roots covered</div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-600 mb-2">Root Volumes</h4>
                  <div className="space-y-1 text-sm">
                    {Object.entries((current_seo?.root_coverage?.root_volumes || {}) as Record<string, number>).map(([root, volume]) => (
                      <div key={root} className="flex justify-between">
                        <span>{root}:</span>
                        <span className="font-medium">{fmtNumber(volume)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Section>

            <Section title="Character Usage" isExpandable>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Title</h4>
                  <div className="text-2xl font-bold">{current_seo?.total_character_usage?.title_chars ?? 0}</div>
                  <div className="text-sm text-gray-600">characters used</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Bullets</h4>
                  <div className="text-2xl font-bold">{current_seo?.total_character_usage?.bullets_total_chars ?? 0}</div>
                  <div className="text-sm text-gray-600">avg: {current_seo?.total_character_usage?.bullets_avg_chars ?? 0} chars</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Backend</h4>
                  <div className="text-2xl font-bold">{current_seo?.total_character_usage?.backend_chars ?? 0}</div>
                  <div className="text-sm text-gray-600">characters used</div>
                </div>
              </div>
            </Section>

            <Section title="Current SEO Metrics">
              <div className="space-y-2">
                <KeyValue label="Coverage" value={`${comparison?.coverage_improvement?.before_coverage_pct ?? 0}%`} />
                <KeyValue label="Keywords Covered" value={comparison?.coverage_improvement?.before_covered ?? 0} />
                <KeyValue label="Total Keywords" value={comparison?.coverage_improvement?.total_keywords ?? 0} />
              </div>
            </Section>
          </div>

          <div className="space-y-6">
            <Section title="Backend Keywords Strategy">
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Recommended backend search terms to capture misspellings, synonyms, and alternate word orders:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {toArr(optimized_seo?.optimized_backend_keywords).map((term: string, i: number) => (
                    <Badge key={i} variant="outline" className="text-xs">{term}</Badge>
                  ))}
                </div>
              </div>
            </Section>

            <Section title="Keyword Strategy Details" isExpandable>
              <div className="space-y-6">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Primary Roots</h4>
                  <div className="flex flex-wrap gap-2">
                    {toArr(optimized_seo?.keyword_strategy?.primary_roots).map((root: string, i: number) => (
                      <Badge key={i} className="bg-blue-600 text-white">{root}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Priority Clusters</h4>
                  <div className="space-y-2">
                    {toArr(optimized_seo?.keyword_strategy?.priority_clusters).map((cluster: string, i: number) => (
                      <div key={i} className="p-2 bg-blue-50 rounded text-sm">{cluster}</div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Frontend Phrase Variants</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                    {toArr(optimized_seo?.keyword_strategy?.phrase_variants_in_frontend).map((phrase: string, i: number) => (
                      <Badge key={i} variant="outline" className="text-xs">{phrase}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Backend Misspellings & Synonyms</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                    {toArr(optimized_seo?.keyword_strategy?.misspellings_and_synonyms_in_backend).map((term: string, i: number) => (
                      <Badge key={i} variant="secondary" className="text-xs">{term}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Exclusions</h4>
                  <div className="flex flex-wrap gap-2">
                    {toArr(optimized_seo?.keyword_strategy?.exclusions).map((exclusion: string, i: number) => (
                      <Badge key={i} variant="destructive" className="text-xs">{exclusion}</Badge>
                    ))}
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Rationale</h4>
                  <p className="text-sm text-gray-600">{optimized_seo?.rationale || '—'}</p>
                </div>
              </div>
            </Section>

            <Section title="Optimized SEO Metrics">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-600 mb-3">Optimized</h4>
                  <div className="space-y-2">
                    <KeyValue label="Coverage" value={`${comparison?.coverage_improvement?.after_coverage_pct ?? 0}%`} />
                    <KeyValue label="Keywords Covered" value={comparison?.coverage_improvement?.after_covered ?? 0} />
                    <KeyValue label="Volume Increase" value={`+${fmtNumber(comparison?.volume_improvement?.delta_volume)}`} />
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-600 mb-3">Improvement</h4>
                  <div className="space-y-2">
                    <KeyValue label="Coverage Gain" value={`+${comparison?.coverage_improvement?.delta_pct_points ?? 0}%`} />
                    <KeyValue label="Intent Improvement" value={`+${comparison?.intent_improvement?.delta ?? 0}`} />
                    <KeyValue label="Overall Score" value={`${comparison?.summary_metrics?.overall_improvement_score ?? 0}/10`} />
                  </div>
                </div>
              </div>
            </Section>
          </div>
        </div>
      )}

      {/* Product Details Tab */}
      {activeTab === 'product' && (
        <div className="space-y-6">
          <Section title="Product Details" isExpandable>
            <div className="space-y-4">
              {Object.entries((scraped_product?.elements?.detailBullets_feature_div?.kv || {}) as Record<string, unknown>).map(([key, value]) => (
                <KeyValue key={key} label={key} value={typeof value === 'number' ? value : String(value)} />
              ))}
            </div>
          </Section>

          <Section title="Feature Bullets" isExpandable>
            <div className="space-y-3">
              {toArr(scraped_product?.elements?.["feature-bullets"]?.bullets).map((bullet: string, i: number) => (
                <div key={i} className="p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                  <div className="text-sm">{bullet}</div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Customer Reviews" isExpandable>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500 fill-current" />
                  <span className="font-semibold text-lg">4.4 out of 5 stars</span>
                </div>
                <span className="text-gray-600">93 ratings</span>
              </div>
              
              <div className="space-y-3">
                {toArr(scraped_product?.reviews?.sample_reviews).map((review: string, i: number) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-lg border">
                    <p className="text-sm text-gray-700 italic">&quot;{review}&quot;</p>
                  </div>
                ))}
              </div>
            </div>
          </Section>

          <Section title="Analysis Metadata" isExpandable>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(analysis_metadata as Record<string, unknown>).map(([key, value]) => (
                <KeyValue 
                  key={key} 
                  label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} 
                  value={typeof value === 'number' ? value : String(value)} 
                />
              ))}
            </div>
          </Section>
        </div>
      )}

      {/* Footer */}
      <Card className="mt-8">
        <CardContent className="p-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              <strong>Final Output:</strong> {final_output}
            </div>
            <div>
              <strong>Source:</strong> {source}
            </div>
          </div>
          {/* Debug raw */}
          {response && (
            <div className="mt-4">
              <details>
                <summary className="cursor-pointer text-xs text-gray-500">Show raw API response</summary>
                <pre className="text-[11px] bg-gray-50 p-2 rounded border overflow-auto max-h-64">{JSON.stringify(response, null, 2)}</pre>
              </details>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default TestResultsPage;
