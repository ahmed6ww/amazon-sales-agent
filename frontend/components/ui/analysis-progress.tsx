"use client";

import { Progress } from "@/components/ui/progress";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2 } from "lucide-react";

interface AnalysisProgressProps {
  progress: number;
  message: string;
  elapsedTime?: string;
}

export function AnalysisProgress({
  progress,
  message,
  elapsedTime,
}: AnalysisProgressProps) {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          Analysis in Progress
        </CardTitle>
        <CardDescription>
          Your Amazon product analysis is being processed. This may take 10-15
          minutes.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">{message}</span>
            <span className="font-medium text-blue-600">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Elapsed Time */}
        {elapsedTime && (
          <div className="text-sm text-gray-500 text-center">
            Elapsed time: {elapsedTime}
          </div>
        )}

        {/* Info Message */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
          <p className="font-medium mb-1">💡 You can safely close this tab!</p>
          <p className="text-blue-700">
            Your analysis will continue running in the background. Come back
            anytime to check the results.
          </p>
        </div>

        {/* Status Messages */}
        <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 space-y-1">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                progress >= 10 ? "bg-green-500" : "bg-gray-300"
              }`}
            />
            <span>Scraping product data...</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                progress >= 30 ? "bg-green-500" : "bg-gray-300"
              }`}
            />
            <span>Analyzing keywords...</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                progress >= 60 ? "bg-green-500" : "bg-gray-300"
              }`}
            />
            <span>Scoring intent & metrics...</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                progress >= 90 ? "bg-green-500" : "bg-gray-300"
              }`}
            />
            <span>Generating SEO optimization...</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
