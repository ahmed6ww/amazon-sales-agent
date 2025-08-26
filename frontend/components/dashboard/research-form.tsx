"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Search, ExternalLink, AlertCircle } from "lucide-react"

const marketplaces = [
  { value: "us", label: "Amazon US", domain: "amazon.com" },
  { value: "uk", label: "Amazon UK", domain: "amazon.co.uk" },
  { value: "ca", label: "Amazon CA", domain: "amazon.ca" },
  { value: "de", label: "Amazon DE", domain: "amazon.de" },
  { value: "fr", label: "Amazon FR", domain: "amazon.fr" },
  { value: "it", label: "Amazon IT", domain: "amazon.it" },
  { value: "es", label: "Amazon ES", domain: "amazon.es" },
  { value: "jp", label: "Amazon JP", domain: "amazon.co.jp" },
  { value: "au", label: "Amazon AU", domain: "amazon.com.au" }
]

interface ResearchFormProps {
  onSubmit?: (data: { asin: string; marketplace: string; productUrl?: string }) => void
  isLoading?: boolean
}

export default function ResearchForm({ onSubmit, isLoading }: ResearchFormProps) {
  const [asin, setAsin] = useState("")
  const [productUrl, setProductUrl] = useState("")
  const [marketplace, setMarketplace] = useState("")
  const [inputType, setInputType] = useState<"asin" | "url">("asin")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!marketplace || (!asin && !productUrl)) return
    
    onSubmit?.({
      asin: inputType === "asin" ? asin : "",
      marketplace,
      productUrl: inputType === "url" ? productUrl : ""
    })
  }

  const extractASINFromUrl = (url: string) => {
    const asinMatch = url.match(/\/([A-Z0-9]{10})(?:\/|$|\?)/)
    return asinMatch ? asinMatch[1] : ""
  }

  const handleUrlChange = (url: string) => {
    setProductUrl(url)
    const extractedASIN = extractASINFromUrl(url)
    if (extractedASIN) {
      setAsin(extractedASIN)
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5 text-blue-600" />
          Start Keyword Research
        </CardTitle>
        <CardDescription>
          Enter your Amazon product details to begin comprehensive keyword analysis
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Input Type Selection */}
        <div className="flex gap-2">
          <Button
            type="button"
            variant={inputType === "asin" ? "default" : "outline"}
            onClick={() => setInputType("asin")}
            className="flex-1"
          >
            ASIN
          </Button>
          <Button
            type="button"
            variant={inputType === "url" ? "default" : "outline"}
            onClick={() => setInputType("url")}
            className="flex-1"
          >
            Product URL
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Product Input */}
          <div className="space-y-2">
            <Label htmlFor="product-input">
              {inputType === "asin" ? "Amazon ASIN" : "Product URL"}
            </Label>
            {inputType === "asin" ? (
              <Input
                id="product-input"
                placeholder="e.g., B08XYZ123"
                value={asin}
                onChange={(e) => setAsin(e.target.value.toUpperCase())}
                className="font-mono"
              />
            ) : (
              <Input
                id="product-input"
                placeholder="e.g., https://amazon.com/dp/B08XYZ123"
                value={productUrl}
                onChange={(e) => handleUrlChange(e.target.value)}
              />
            )}
            <p className="text-xs text-muted-foreground">
              {inputType === "asin" 
                ? "Enter the 10-character Amazon Standard Identification Number"
                : "Paste the full Amazon product URL"
              }
            </p>
          </div>

          {/* Marketplace Selection */}
          <div className="space-y-2">
            <Label htmlFor="marketplace">Marketplace</Label>
            <Select value={marketplace} onValueChange={setMarketplace}>
              <SelectTrigger>
                <SelectValue placeholder="Select Amazon marketplace" />
              </SelectTrigger>
              <SelectContent>
                {marketplaces.map((mp) => (
                  <SelectItem key={mp.value} value={mp.value}>
                    <div className="flex items-center justify-between w-full">
                      <span>{mp.label}</span>
                      <span className="text-xs text-muted-foreground ml-2">
                        {mp.domain}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Preview Section */}
          {(asin || productUrl) && marketplace && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  <ExternalLink className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-blue-900">Research Preview</h4>
                  <div className="mt-2 space-y-1">
                    {inputType === "asin" && asin && (
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">ASIN</Badge>
                        <span className="text-sm font-mono">{asin}</span>
                      </div>
                    )}
                    {inputType === "url" && productUrl && (
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">URL</Badge>
                        <span className="text-sm truncate">{productUrl}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">Marketplace</Badge>
                      <span className="text-sm">
                        {marketplaces.find(mp => mp.value === marketplace)?.label}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Info Alert */}
          <div className="flex gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
            <div className="text-sm text-amber-800">
              <p className="font-medium">Next Step Required</p>
              <p className="text-xs mt-1">
                                 After starting research, you&apos;ll need to upload your Helium 10 Cerebro data files 
                for competitor analysis.
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full h-12 bg-blue-600 hover:bg-blue-700" 
            disabled={!marketplace || (!asin && !productUrl) || isLoading}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Starting Research...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                Start Research
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
} 