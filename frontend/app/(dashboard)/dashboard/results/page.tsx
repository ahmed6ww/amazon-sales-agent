"use client"

import ResultsDisplay from "@/components/dashboard/results-display"

export default function ResultsPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
        <p className="text-gray-600 mt-2">
          View and manage your keyword research results
        </p>
      </div>

      {/* Results Display */}
      <ResultsDisplay isLoading={false} />
    </div>
  )
} 