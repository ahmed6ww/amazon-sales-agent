"use client"

import FileUpload from "@/components/dashboard/file-upload"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Info } from "lucide-react"

export default function UploadPage() {
  const handleFilesUpload = (files: { revenueCompetitors: File | null; designCompetitors: File | null }) => {
    console.log("Files uploaded:", files)
    // Handle file upload logic here
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Data</h1>
        <p className="text-gray-600 mt-2">
          Upload your Helium 10 Cerebro data files for keyword analysis
        </p>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
            <div>
              <h3 className="font-medium text-blue-900 mb-2">Before You Upload</h3>
              <p className="text-sm text-blue-800 mb-3">
                Make sure you have completed your research setup with an ASIN or product URL. 
                If you haven&apos;t started a research project yet, you can do so from the research page.
              </p>
              <div className="flex gap-2">
                <Badge className="bg-blue-100 text-blue-700 border-blue-300">
                  Helium 10 Diamond Plan Required
                </Badge>
                <Badge className="bg-blue-100 text-blue-700 border-blue-300">
                  CSV Format Only
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Upload Component */}
      <FileUpload 
        onFilesUpload={handleFilesUpload}
        isUploading={false}
      />
    </div>
  )
} 