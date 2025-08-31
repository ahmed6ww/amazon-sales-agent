import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg"></div>
          <span className="text-xl font-semibold text-gray-900">KeywordAI</span>
        </div>
        <a href="/dashboard">
          <Button variant="outline" size="lg" className="border-blue-200 text-blue-600 hover:bg-blue-50 px-6 py-2">
            Get Started
          </Button>
        </a>
      </nav>

      {/* Hero Section */}
      <section className="px-6 py-20 max-w-6xl mx-auto text-center">
        <Badge className="mb-6 bg-blue-50 text-blue-700 border-blue-200">
          AI-Powered Amazon Research
        </Badge>
        
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Intelligent Amazon
          <span className="bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">
            {" "}Keyword Research{" "}
          </span>
          Platform
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
          Transform your Amazon listings with AI agents that analyze competitors, score keywords, 
          and generate optimized SEO strategies using advanced Helium 10 data intelligence.
        </p>

                 <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
           <a href="/dashboard">
             <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg h-12">
               Start Research
             </Button>
           </a>
           <a href="/test">
             <Button variant="outline" size="lg" className="border-gray-300 text-gray-700 px-8 py-4 text-lg h-12">
               View Demo
             </Button>
           </a>
         </div>

        <div className="mt-16 relative">
          <div className="bg-gradient-to-t from-blue-50 to-transparent p-8 rounded-2xl border border-blue-100">
            <div className="bg-white rounded-xl shadow-lg p-6 max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                </div>
                <span className="text-sm text-gray-500">Amazon Keyword Analysis</span>
              </div>
              <div className="space-y-3 text-left">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-700">Processing ASIN: B08XYZ123...</span>
                  <Badge className="bg-blue-100 text-blue-700">In Progress</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">247</div>
                    <div className="text-sm text-gray-600">Keywords Found</div>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">15</div>
                    <div className="text-sm text-gray-600">Competitors Analyzed</div>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">98%</div>
                    <div className="text-sm text-gray-600">Relevancy Score</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powered by AI Agents
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our intelligent agent system orchestrates complex research workflows to deliver 
              actionable insights for your Amazon business.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-blue-600 rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Research Agent</h3>
              <p className="text-gray-600">Automatically fetches competitor data from Helium 10 APIs</p>
            </Card>

            <Card className="p-6 border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-blue-600 rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Keyword Agent</h3>
              <p className="text-gray-600">Categorizes and scores keywords using advanced algorithms</p>
            </Card>

            <Card className="p-6 border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-blue-600 rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Scoring Agent</h3>
              <p className="text-gray-600">Prioritizes keywords by relevancy, volume, and competition</p>
            </Card>

            <Card className="p-6 border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-blue-600 rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">SEO Agent</h3>
              <p className="text-gray-600">Generates optimized titles and bullet points for listings</p>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Simple three-step process to transform your Amazon listings
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Input Your ASIN</h3>
              <p className="text-gray-600">
                Enter your Amazon product URL or ASIN along with marketplace selection
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Analysis</h3>
              <p className="text-gray-600">
                Our agents analyze competitors, extract keywords, and score relevancy automatically
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Get Results</h3>
              <p className="text-gray-600">
                Receive categorized keywords, SEO comparison, and optimized listing suggestions
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="px-6 py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Results
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get detailed insights and actionable recommendations for every aspect of your listing
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="p-8 border-blue-100">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">SEO Comparison</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border-l-4 border-red-400">
                  <span className="text-sm text-gray-700">Current Title Coverage</span>
                  <span className="font-semibold text-red-600">42%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border-l-4 border-green-400">
                  <span className="text-sm text-gray-700">Optimized Title Coverage</span>
                  <span className="font-semibold text-green-600">89%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                  <span className="text-sm text-gray-700">Keyword Opportunities</span>
                  <span className="font-semibold text-blue-600">+24</span>
                </div>
              </div>
            </Card>

            <Card className="p-8 border-blue-100">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Keyword Categories</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Relevant Keywords</span>
                  <Badge className="bg-green-100 text-green-700">156 found</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Design-Specific</span>
                  <Badge className="bg-blue-100 text-blue-700">43 found</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">High-Intent</span>
                  <Badge className="bg-purple-100 text-purple-700">28 found</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Competitor Brands</span>
                  <Badge className="bg-orange-100 text-orange-700">12 found</Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Optimize Your Amazon Listings?
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Join sellers who are already using AI-powered keyword research to improve their 
            Amazon performance and increase sales.
          </p>
                     <div className="flex flex-col sm:flex-row gap-4 justify-center">
             <a href="/dashboard">
               <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg h-12">
                 Start Your Research
               </Button>
             </a>
             <a href="/test">
               <Button variant="outline" size="lg" className="border-gray-300 text-gray-700 px-8 py-4 text-lg h-12">
                 Schedule Demo
               </Button>
             </a>
           </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 border-t border-gray-100">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg"></div>
              <span className="text-xl font-semibold text-gray-900">KeywordAI</span>
            </div>
            <div className="flex space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-blue-600 transition-colors">Privacy</a>
              <a href="#" className="hover:text-blue-600 transition-colors">Terms</a>
              <a href="#" className="hover:text-blue-600 transition-colors">Support</a>
              <a href="#" className="hover:text-blue-600 transition-colors">Documentation</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-100 text-center text-sm text-gray-500">
            © 2024 KeywordAI. All rights reserved. Powered by AI agents and Helium 10 data.
          </div>
        </div>
      </footer>
    </div>
  );
}
