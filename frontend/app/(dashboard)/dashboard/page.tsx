"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Search, 
  BarChart3, 
  TrendingUp, 
  Clock, 
  ArrowRight,
  Plus,
  FileText,
  Users,
  Target
} from "lucide-react"
import Link from "next/link"

const recentResearches = [
  {
    id: 1,
    asin: "B08XYZ123",
    marketplace: "Amazon US",
    status: "completed",
    keywordsFound: 247,
    createdAt: "2 hours ago",
    optimizationScore: 89
  },
  {
    id: 2,
    asin: "B07ABC456",
    marketplace: "Amazon UK",
    status: "processing",
    keywordsFound: 156,
    createdAt: "4 hours ago",
    optimizationScore: 76
  },
  {
    id: 3,
    asin: "B09DEF789",
    marketplace: "Amazon DE",
    status: "completed",
    keywordsFound: 198,
    createdAt: "1 day ago",
    optimizationScore: 92
  }
]

const quickActions = [
  {
    title: "Start New Research",
    description: "Begin keyword analysis for a new product",
    icon: Search,
    href: "/dashboard/research",
    color: "bg-blue-500"
  },
  {
    title: "Upload Data",
    description: "Upload Helium 10 Cerebro files",
    icon: Plus,
    href: "/dashboard/upload",
    color: "bg-green-500"
  },
  {
    title: "View Reports",
    description: "Access your generated reports",
    icon: FileText,
    href: "/dashboard/reports",
    color: "bg-purple-500"
  },
  {
    title: "Analysis History",
    description: "Review past research results",
    icon: Clock,
    href: "/dashboard/history",
    color: "bg-orange-500"
  }
]

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome to KeywordAI</h1>
        <p className="text-gray-600 mt-2">
          AI-powered Amazon keyword research and SEO optimization platform
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Researches</p>
                <p className="text-2xl font-bold text-gray-900">24</p>
              </div>
              <div className="h-8 w-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <Search className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+12% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Keywords Found</p>
                <p className="text-2xl font-bold text-gray-900">5,847</p>
              </div>
              <div className="h-8 w-8 bg-green-500 rounded-lg flex items-center justify-center">
                <Target className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+8% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Optimization</p>
                <p className="text-2xl font-bold text-gray-900">85%</p>
              </div>
              <div className="h-8 w-8 bg-purple-500 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+5% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Competitors Analyzed</p>
                <p className="text-2xl font-bold text-gray-900">156</p>
              </div>
              <div className="h-8 w-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <Users className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+15% from last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Get started with keyword research and optimization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <Link key={action.title} href={action.href}>
                <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`h-8 w-8 ${action.color} rounded-lg flex items-center justify-center`}>
                      <action.icon className="h-4 w-4 text-white" />
                    </div>
                    <h3 className="font-medium group-hover:text-blue-600 transition-colors">
                      {action.title}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600">{action.description}</p>
                  <div className="mt-3 flex items-center text-sm text-blue-600 group-hover:text-blue-700">
                    <span>Get started</span>
                    <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Research */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Research</CardTitle>
              <CardDescription>
                Your latest keyword research activities
              </CardDescription>
            </div>
            <Button variant="outline" asChild>
              <Link href="/dashboard/history">
                View All
                <ArrowRight className="h-4 w-4 ml-2" />
              </Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentResearches.map((research) => (
              <div 
                key={research.id} 
                className="flex items-center justify-between p-4 border rounded-lg hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Search className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">ASIN: {research.asin}</h4>
                      <Badge 
                        className={research.status === "completed" 
                          ? "bg-green-100 text-green-700" 
                          : "bg-yellow-100 text-yellow-700"
                        }
                      >
                        {research.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      {research.marketplace} • {research.keywordsFound} keywords found • {research.createdAt}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">Optimization Score</p>
                    <p className="text-lg font-bold text-blue-600">{research.optimizationScore}%</p>
                  </div>
                  <Button variant="ghost" size="sm">
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Getting Started */}
      <Card className="bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                Ready to optimize your Amazon listings?
              </h3>
              <p className="text-blue-700 mt-1">
                Start your first keyword research in just a few clicks
              </p>
            </div>
            <Button className="bg-blue-600 hover:bg-blue-700" asChild>
              <Link href="/dashboard/research">
                Start Research
                <Search className="h-4 w-4 ml-2" />
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 