"use client"

import { useState } from "react"
import ResearchForm from "@/components/dashboard/research-form"
import FileUpload from "@/components/dashboard/file-upload"
import ResultsDisplay from "@/components/dashboard/results-display"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, ArrowRight } from "lucide-react"

type ResearchStep = "input" | "upload" | "processing" | "results"

interface ResearchData {
  asin: string
  marketplace: string
  productUrl?: string
}

export default function ResearchPage() {
  const [currentStep, setCurrentStep] = useState<ResearchStep>("input")
  const [researchData, setResearchData] = useState<ResearchData | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const steps = [
    { id: "input", title: "Product Input", description: "Enter ASIN or product URL" },
    { id: "upload", title: "Data Upload", description: "Upload Helium 10 files" },
    { id: "processing", title: "AI Analysis", description: "Processing your data" },
    { id: "results", title: "Results", description: "View optimization report" }
  ]

  const getStepIndex = (step: ResearchStep) => {
    return steps.findIndex(s => s.id === step)
  }

  const handleResearchSubmit = (data: ResearchData) => {
    setResearchData(data)
    setCurrentStep("upload")
  }

  const handleFilesUpload = () => {
    setIsLoading(true)
    setCurrentStep("processing")
    
    // Simulate processing time
    setTimeout(() => {
      setIsLoading(false)
      setCurrentStep("results")
    }, 5000)
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Keyword Research</h1>
        <p className="text-gray-600 mt-2">
          Comprehensive Amazon keyword analysis powered by AI agents
        </p>
      </div>

      {/* Progress Steps */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const isActive = currentStep === step.id
              const isCompleted = getStepIndex(currentStep) > index
              const isAccessible = getStepIndex(currentStep) >= index
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors ${
                      isCompleted 
                        ? "bg-green-500 border-green-500 text-white" 
                        : isActive 
                          ? "bg-blue-500 border-blue-500 text-white"
                          : isAccessible
                            ? "border-blue-200 text-blue-500"
                            : "border-gray-200 text-gray-400"
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <span className="text-sm font-medium">{index + 1}</span>
                      )}
                    </div>
                    <div className="mt-2 text-center">
                      <h3 className={`text-sm font-medium ${
                        isActive ? "text-blue-600" : isCompleted ? "text-green-600" : "text-gray-500"
                      }`}>
                        {step.title}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">{step.description}</p>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <ArrowRight className={`h-5 w-5 mx-4 ${
                      getStepIndex(currentStep) > index ? "text-green-500" : "text-gray-300"
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <div className="min-h-[600px]">
        {currentStep === "input" && (
          <div className="space-y-6">
            <ResearchForm 
              onSubmit={handleResearchSubmit}
              isLoading={isLoading}
            />
          </div>
        )}

        {currentStep === "upload" && researchData && (
          <div className="space-y-6">
            {/* Research Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Research Configuration</CardTitle>
                <CardDescription>
                  Confirmed research parameters for your analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">ASIN</Badge>
                    <span className="font-mono">{researchData.asin}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">Marketplace</Badge>
                    <span>{researchData.marketplace}</span>
                  </div>
                  {researchData.productUrl && (
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">URL</Badge>
                      <span className="truncate text-sm">{researchData.productUrl}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <FileUpload 
              onFilesUpload={handleFilesUpload}
              isUploading={isLoading}
            />
          </div>
        )}

        {currentStep === "processing" && (
          <ResultsDisplay isLoading={true} />
        )}

        {currentStep === "results" && (
          <ResultsDisplay isLoading={false} />
        )}
      </div>
    </div>
  )
} 