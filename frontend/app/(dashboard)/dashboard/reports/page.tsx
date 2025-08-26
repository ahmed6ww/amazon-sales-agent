"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileText, Download, Eye, Share, Calendar, BarChart3 } from "lucide-react"

const reports = [
  {
    id: 1,
    title: "Silicone License Plate Frame - SEO Analysis",
    type: "SEO Comparison",
    asin: "B08XYZ123",
    marketplace: "Amazon US",
    generatedAt: "2024-01-15",
    fileSize: "2.3 MB",
    format: "PDF",
    status: "ready"
  },
  {
    id: 2,
    title: "Car Phone Mount - Keyword Dataset",
    type: "Keyword Analysis",
    asin: "B07ABC456",
    marketplace: "Amazon UK",
    generatedAt: "2024-01-14",
    fileSize: "1.8 MB",
    format: "CSV",
    status: "ready"
  },
  {
    id: 3,
    title: "Dashboard Camera - Complete Report",
    type: "Full Analysis",
    asin: "B09DEF789",
    marketplace: "Amazon DE",
    generatedAt: "2024-01-13",
    fileSize: "4.1 MB",
    format: "PDF",
    status: "ready"
  },
  {
    id: 4,
    title: "Seat Covers - Competitor Analysis",
    type: "Competitor Research",
    asin: "B06GHI012",
    marketplace: "Amazon CA",
    generatedAt: "2024-01-12",
    fileSize: "0 MB",
    format: "PDF",
    status: "generating"
  }
]

const reportTypes = [
  {
    type: "SEO Comparison",
    count: reports.filter(r => r.type === "SEO Comparison").length,
    color: "bg-blue-100 text-blue-700"
  },
  {
    type: "Keyword Analysis", 
    count: reports.filter(r => r.type === "Keyword Analysis").length,
    color: "bg-green-100 text-green-700"
  },
  {
    type: "Full Analysis",
    count: reports.filter(r => r.type === "Full Analysis").length,
    color: "bg-purple-100 text-purple-700"
  },
  {
    type: "Competitor Research",
    count: reports.filter(r => r.type === "Competitor Research").length,
    color: "bg-orange-100 text-orange-700"
  }
]

export default function ReportsPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-2">
            Access and manage your generated keyword research reports
          </p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <BarChart3 className="h-4 w-4 mr-2" />
          Generate Report
        </Button>
      </div>

      {/* Report Type Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {reportTypes.map((type) => (
          <Card key={type.type}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{type.type}</p>
                  <p className="text-2xl font-bold text-gray-900">{type.count}</p>
                </div>
                <div className="h-8 w-8 bg-blue-500 rounded-lg flex items-center justify-center">
                  <FileText className="h-4 w-4 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle>Generated Reports</CardTitle>
          <CardDescription>
            All your keyword research reports and downloads
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reports.map((report) => (
              <div 
                key={report.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium">{report.title}</h4>
                      <Badge className={
                        report.type === "SEO Comparison" ? "bg-blue-100 text-blue-700" :
                        report.type === "Keyword Analysis" ? "bg-green-100 text-green-700" :
                        report.type === "Full Analysis" ? "bg-purple-100 text-purple-700" :
                        "bg-orange-100 text-orange-700"
                      }>
                        {report.type}
                      </Badge>
                      <Badge 
                        className={report.status === "ready" 
                          ? "bg-green-100 text-green-700" 
                          : "bg-yellow-100 text-yellow-700"
                        }
                      >
                        {report.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>ASIN: {report.asin}</span>
                      <span>•</span>
                      <span>{report.marketplace}</span>
                      <span>•</span>
                      <span>{report.format}</span>
                      {report.status === "ready" && (
                        <>
                          <span>•</span>
                          <span>{report.fileSize}</span>
                        </>
                      )}
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {report.generatedAt}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {report.status === "ready" && (
                    <>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        Preview
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Share className="h-4 w-4 mr-1" />
                        Share
                      </Button>
                    </>
                  )}
                  {report.status === "generating" && (
                    <div className="flex items-center gap-2 text-sm text-yellow-600">
                      <div className="w-4 h-4 border-2 border-yellow-600/30 border-t-yellow-600 rounded-full animate-spin"></div>
                      Generating...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                Need a custom report?
              </h3>
              <p className="text-blue-700 mt-1">
                Generate detailed analysis reports with custom parameters
              </p>
            </div>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <FileText className="h-4 w-4 mr-2" />
              Custom Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 