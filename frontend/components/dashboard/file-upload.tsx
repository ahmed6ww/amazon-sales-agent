"use client"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Upload, FileText, X, Check, AlertTriangle } from "lucide-react"

interface FileUploadProps {
  onFilesUpload?: (files: { revenueCompetitors: File | null; designCompetitors: File | null }) => void
  isUploading?: boolean
}

interface UploadedFile {
  file: File
  progress: number
  status: "uploading" | "complete" | "error"
}

export default function FileUpload({ onFilesUpload, isUploading }: FileUploadProps) {
  const [revenueFile, setRevenueFile] = useState<UploadedFile | null>(null)
  const [designFile, setDesignFile] = useState<UploadedFile | null>(null)

  const handleFileSelect = useCallback((
    event: React.ChangeEvent<HTMLInputElement>,
    type: "revenue" | "design"
  ) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file')
      return
    }

    const uploadedFile: UploadedFile = {
      file,
      progress: 0,
      status: "uploading"
    }

    if (type === "revenue") {
      setRevenueFile(uploadedFile)
    } else {
      setDesignFile(uploadedFile)
    }

    // Simulate upload progress
    const interval = setInterval(() => {
      const setter = type === "revenue" ? setRevenueFile : setDesignFile
      setter(prev => {
        if (!prev) return null
        const newProgress = Math.min(prev.progress + 10, 100)
        const newStatus = newProgress === 100 ? "complete" : "uploading"
        
        if (newProgress === 100) {
          clearInterval(interval)
        }
        
        return { ...prev, progress: newProgress, status: newStatus }
      })
    }, 200)

    // Reset input
    event.target.value = ""
  }, [])

  const removeFile = (type: "revenue" | "design") => {
    if (type === "revenue") {
      setRevenueFile(null)
    } else {
      setDesignFile(null)
    }
  }

  const handleSubmit = () => {
    if (revenueFile?.status === "complete" || designFile?.status === "complete") {
      onFilesUpload?.({
        revenueCompetitors: revenueFile?.status === "complete" ? revenueFile.file : null,
        designCompetitors: designFile?.status === "complete" ? designFile.file : null
      })
    }
  }

  const getFileIcon = (status: string) => {
    switch (status) {
      case "complete":
        return <Check className="h-4 w-4 text-green-600" />
      case "error":
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <FileText className="h-4 w-4 text-blue-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete":
        return "bg-green-50 border-green-200"
      case "error":
        return "bg-red-50 border-red-200"
      default:
        return "bg-blue-50 border-blue-200"
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5 text-blue-600" />
            Upload Helium 10 Data
          </CardTitle>
          <CardDescription>
            Upload your Helium 10 Cerebro reverse ASIN data files for comprehensive competitor analysis
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Revenue Competitors Upload */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Top 10 Revenue Competitors</h4>
                <p className="text-sm text-muted-foreground">
                  CSV export from Helium 10 Cerebro showing top revenue-generating competitors
                </p>
              </div>
              <Badge variant="outline" className="text-xs">Required</Badge>
            </div>
            
            {!revenueFile ? (
              <div className="border-2 border-dashed border-blue-200 rounded-lg p-6 text-center hover:border-blue-300 transition-colors">
                <Upload className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-gray-700 mb-1">
                  Drop your CSV file here or click to browse
                </p>
                <p className="text-xs text-muted-foreground mb-3">
                  Maximum file size: 10MB
                </p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileSelect(e, "revenue")}
                  className="hidden"
                  id="revenue-upload"
                />
                <Button asChild variant="outline" size="sm">
                  <label htmlFor="revenue-upload" className="cursor-pointer">
                    Select File
                  </label>
                </Button>
              </div>
            ) : (
              <div className={`p-4 rounded-lg border ${getStatusColor(revenueFile.status)}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getFileIcon(revenueFile.status)}
                    <span className="text-sm font-medium">{revenueFile.file.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {(revenueFile.file.size / 1024).toFixed(1)} KB
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile("revenue")}
                    className="h-6 w-6 p-0"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
                {revenueFile.status === "uploading" && (
                  <Progress value={revenueFile.progress} className="h-2" />
                )}
              </div>
            )}
          </div>

          {/* Design Competitors Upload */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Top 10 Design Competitors</h4>
                <p className="text-sm text-muted-foreground">
                  CSV export from Helium 10 Cerebro showing top design-relevant competitors
                </p>
              </div>
              <Badge variant="outline" className="text-xs">Optional</Badge>
            </div>
            
            {!designFile ? (
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-gray-300 transition-colors">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-gray-700 mb-1">
                  Drop your CSV file here or click to browse
                </p>
                <p className="text-xs text-muted-foreground mb-3">
                  Maximum file size: 10MB
                </p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileSelect(e, "design")}
                  className="hidden"
                  id="design-upload"
                />
                <Button asChild variant="outline" size="sm">
                  <label htmlFor="design-upload" className="cursor-pointer">
                    Select File
                  </label>
                </Button>
              </div>
            ) : (
              <div className={`p-4 rounded-lg border ${getStatusColor(designFile.status)}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getFileIcon(designFile.status)}
                    <span className="text-sm font-medium">{designFile.file.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {(designFile.file.size / 1024).toFixed(1)} KB
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile("design")}
                    className="h-6 w-6 p-0"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
                {designFile.status === "uploading" && (
                  <Progress value={designFile.progress} className="h-2" />
                )}
              </div>
            )}
          </div>

          {/* Instructions */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-amber-800 mb-2">How to get this data:</h4>
            <ol className="text-sm text-amber-700 space-y-1 list-decimal list-inside">
              <li>Log into your Helium 10 account (Diamond plan or above required)</li>
              <li>Go to Cerebro tool and enter your competitor ASINs</li>
              <li>Run reverse ASIN lookup for revenue and design competitors</li>
              <li>Export the results as CSV files</li>
              <li>Upload the files here for analysis</li>
            </ol>
          </div>

          {/* Submit Button */}
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-muted-foreground">
              {revenueFile?.status === "complete" && "Revenue file ready"}
              {designFile?.status === "complete" && (revenueFile?.status === "complete" ? " • Design file ready" : "Design file ready")}
            </div>
            <Button
              onClick={handleSubmit}
              disabled={!revenueFile?.status || revenueFile.status !== "complete" || isUploading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isUploading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </div>
              ) : (
                "Start Analysis"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 