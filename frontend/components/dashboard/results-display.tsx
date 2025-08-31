"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  Download, 
  BarChart3, 
  Filter,
  Star,
  Copy,
  ExternalLink
} from "lucide-react"

// Mock data types
interface Keyword {
  keyword: string
  searchVolume: number
  relevancyScore: number
  titleDensity: number
  cpr: number
  competition: string
  category: "relevant" | "design-specific" | "irrelevant" | "branded"
  intent: 0 | 1 | 2 | 3
  rootSearchVolume: number
}

interface SEOComparison {
  current: {
    title: string
    bullets: string[]
    keywordCoverage: number
  }
  improved: {
    title: string
    bullets: string[]
    keywordCoverage: number
  }
}

const mockKeywords: Keyword[] = [
  {
    keyword: "license plate frame",
    searchVolume: 15420,
    relevancyScore: 95,
    titleDensity: 87,
    cpr: 2.3,
    competition: "High",
    category: "relevant",
    intent: 3,
    rootSearchVolume: 45200
  },
  {
    keyword: "silicone license plate frame",
    searchVolume: 3200,
    relevancyScore: 89,
    titleDensity: 64,
    cpr: 1.8,
    competition: "Medium",
    category: "design-specific",
    intent: 2,
    rootSearchVolume: 45200
  },
  {
    keyword: "car accessories",
    searchVolume: 8900,
    relevancyScore: 45,
    titleDensity: 23,
    cpr: 3.2,
    competition: "High",
    category: "irrelevant",
    intent: 1,
    rootSearchVolume: 25600
  }
]

const mockSEOComparison: SEOComparison = {
  current: {
    title: "License Plate Frame - Black Plastic",
    bullets: [
      "Durable plastic construction",
      "Easy to install",
      "Weather resistant"
    ],
    keywordCoverage: 42
  },
  improved: {
    title: "Silicone License Plate Frame - Durable Car Accessories for Weather Protection",
    bullets: [
      "Premium silicone license plate frame with superior durability and flexibility",
      "Universal fit car accessories designed for all standard license plates",
      "Weather resistant frame with UV protection for long-lasting performance"
    ],
    keywordCoverage: 89
  }
}

interface ResultsDisplayProps {
  isLoading?: boolean
}

export default function ResultsDisplay({ isLoading }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<"seo" | "keywords">("seo")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")

  const categoryColors = {
    relevant: "bg-green-50 text-green-700 border-green-200",
    "design-specific": "bg-blue-50 text-blue-700 border-blue-200",
    irrelevant: "bg-red-50 text-red-700 border-red-200",
    branded: "bg-orange-50 text-orange-700 border-orange-200"
  }

  const competitionColors = {
    Low: "text-green-600",
    Medium: "text-yellow-600",
    High: "text-red-600"
  }

  const filteredKeywords = selectedCategory === "all" 
    ? mockKeywords 
    : mockKeywords.filter(k => k.category === selectedCategory)

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
    )
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
                Comprehensive keyword research and SEO optimization recommendations
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
              <div className="text-2xl font-bold text-blue-600">247</div>
              <div className="text-sm text-muted-foreground">Total Keywords</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">156</div>
              <div className="text-sm text-muted-foreground">Relevant Keywords</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">28</div>
              <div className="text-sm text-muted-foreground">High Intent</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">89%</div>
              <div className="text-sm text-muted-foreground">Optimization Score</div>
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
          SEO Comparison
        </Button>
        <Button
          variant={activeTab === "keywords" ? "default" : "outline"}
          onClick={() => setActiveTab("keywords")}
        >
          Keyword Analysis
        </Button>
      </div>

      {/* SEO Comparison Tab */}
      {activeTab === "seo" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Current Listing</CardTitle>
              <CardDescription>
                Your existing SEO setup and keyword coverage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Title</label>
                <div className="mt-1 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm">{mockSEOComparison.current.title}</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground">Bullet Points</label>
                <div className="mt-1 space-y-2">
                  {mockSEOComparison.current.bullets.map((bullet, index) => (
                    <div key={index} className="p-2 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm">{bullet}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="pt-2 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Keyword Coverage</span>
                  <Badge className="bg-red-100 text-red-700">
                    {mockSEOComparison.current.keywordCoverage}%
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-green-600">Optimized Listing</CardTitle>
              <CardDescription>
                AI-generated SEO improvements and recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Improved Title</label>
                <div className="mt-1 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm">{mockSEOComparison.improved.title}</p>
                  <Button variant="ghost" size="sm" className="mt-2 h-6 px-2">
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground">Improved Bullet Points</label>
                <div className="mt-1 space-y-2">
                  {mockSEOComparison.improved.bullets.map((bullet, index) => (
                    <div key={index} className="p-2 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm">{bullet}</p>
                      <Button variant="ghost" size="sm" className="mt-1 h-6 px-2">
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="pt-2 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Keyword Coverage</span>
                  <Badge className="bg-green-100 text-green-700">
                    {mockSEOComparison.improved.keywordCoverage}%
                  </Badge>
                </div>
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
                  Categorized keywords with Helium 10 metrics and scoring
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
                  <option value="relevant">Relevant</option>
                  <option value="design-specific">Design-Specific</option>
                  <option value="irrelevant">Irrelevant</option>
                  <option value="branded">Branded</option>
                </select>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="space-y-3">
              {filteredKeywords.map((keyword, index) => (
                <div key={index} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium">{keyword.keyword}</h4>
                      <Badge className={categoryColors[keyword.category]}>
                        {keyword.category}
                      </Badge>
                      <div className="flex items-center gap-1">
                        {[...Array(keyword.intent)].map((_, i) => (
                          <Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        ))}
                        <span className="text-xs text-muted-foreground ml-1">
                          Intent {keyword.intent}
                        </span>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Search Volume</span>
                      <div className="font-medium">{keyword.searchVolume.toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Relevancy</span>
                      <div className="font-medium">{keyword.relevancyScore}%</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Title Density</span>
                      <div className="font-medium">{keyword.titleDensity}%</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">CPR</span>
                      <div className="font-medium">{keyword.cpr}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Competition</span>
                      <div className={`font-medium ${competitionColors[keyword.competition as keyof typeof competitionColors]}`}>
                        {keyword.competition}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-2 text-xs text-muted-foreground">
                    Root keyword search volume: {keyword.rootSearchVolume.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 