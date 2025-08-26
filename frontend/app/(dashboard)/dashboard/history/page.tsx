"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Search, BarChart3, Download, ArrowRight, Calendar, Clock } from "lucide-react"

const historyData = [
  {
    id: 1,
    asin: "B08XYZ123",
    productName: "Silicone License Plate Frame",
    marketplace: "Amazon US",
    status: "completed",
    keywordsFound: 247,
    optimizationScore: 89,
    createdAt: "2024-01-15",
    updatedAt: "2 hours ago"
  },
  {
    id: 2,
    asin: "B07ABC456",
    productName: "Car Phone Mount",
    marketplace: "Amazon UK",
    status: "completed",
    keywordsFound: 156,
    optimizationScore: 76,
    createdAt: "2024-01-14",
    updatedAt: "1 day ago"
  },
  {
    id: 3,
    asin: "B09DEF789",
    productName: "Dashboard Camera",
    marketplace: "Amazon DE",
    status: "completed",
    keywordsFound: 198,
    optimizationScore: 92,
    createdAt: "2024-01-13",
    updatedAt: "2 days ago"
  },
  {
    id: 4,
    asin: "B06GHI012",
    productName: "Seat Covers",
    marketplace: "Amazon CA",
    status: "processing",
    keywordsFound: 89,
    optimizationScore: 0,
    createdAt: "2024-01-12",
    updatedAt: "3 days ago"
  }
]

export default function HistoryPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Research History</h1>
          <p className="text-gray-600 mt-2">
            View and manage your past keyword research activities
          </p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Search className="h-4 w-4 mr-2" />
          New Research
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Researches</p>
                <p className="text-2xl font-bold text-gray-900">{historyData.length}</p>
              </div>
              <Search className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Keywords</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round(historyData.reduce((acc, item) => acc + item.keywordsFound, 0) / historyData.length)}
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Optimization</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round(historyData.filter(item => item.status === 'completed').reduce((acc, item) => acc + item.optimizationScore, 0) / historyData.filter(item => item.status === 'completed').length)}%
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-gray-900">{historyData.length}</p>
              </div>
              <Calendar className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* History List */}
      <Card>
        <CardHeader>
          <CardTitle>Research History</CardTitle>
          <CardDescription>
            All your keyword research activities and results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {historyData.map((item) => (
              <div 
                key={item.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Search className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium">{item.productName}</h4>
                      <Badge 
                        className={item.status === "completed" 
                          ? "bg-green-100 text-green-700" 
                          : "bg-yellow-100 text-yellow-700"
                        }
                      >
                        {item.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>ASIN: {item.asin}</span>
                      <span>•</span>
                      <span>{item.marketplace}</span>
                      <span>•</span>
                      <span>{item.keywordsFound} keywords</span>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {item.updatedAt}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  {item.status === "completed" && (
                    <div className="text-right">
                      <p className="text-sm font-medium">Optimization Score</p>
                      <p className="text-lg font-bold text-blue-600">{item.optimizationScore}%</p>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2">
                    {item.status === "completed" && (
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4 mr-1" />
                        Export
                      </Button>
                    )}
                    <Button variant="ghost" size="sm">
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 