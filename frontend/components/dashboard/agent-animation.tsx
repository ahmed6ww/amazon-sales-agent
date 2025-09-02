'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface AgentAnimationProps {
  currentStep: string;
  progress: number;
  isActive: boolean;
}

interface AgentStep {
  id: string;
  name: string;
  icon: string;
  description: string;
  keywords: string[];
}

const agentSteps: AgentStep[] = [
  {
    id: 'scraping',
    name: 'Data Parser',
    icon: '🔍',
    description: 'Extracting product data',
    keywords: ['MVP Scraper', 'Product Info', 'Amazon Data']
  },
  {
    id: 'research_analysis',
    name: 'Research Agent',
    icon: '🤖',
    description: 'AI analysis of product',
    keywords: ['AI Analysis', 'Market Research', 'Product Insights']
  },
  {
    id: 'keyword_analysis',
    name: 'Keyword Agent',
    icon: '📊',
    description: 'Processing keyword data',
    keywords: ['Keyword Processing', 'Categorization', 'Competition']
  },
  {
    id: 'scoring_analysis',
    name: 'Scoring Agent',
    icon: '🎯',
    description: 'Scoring and prioritizing',
    keywords: ['Intent Scoring', 'Prioritization', 'AI Scoring']
  },
  {
    id: 'seo_optimization',
    name: 'SEO Agent',
    icon: '🎨',
    description: 'Optimization recommendations',
    keywords: ['SEO Optimization', 'Title Generation', 'Content Strategy']
  }
];

export function AgentAnimation({ currentStep, progress, isActive }: AgentAnimationProps) {
  const getStepStatus = (stepId: string) => {
    const stepIndex = agentSteps.findIndex(step => step.id === stepId);
    const currentIndex = agentSteps.findIndex(step => step.id === currentStep);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex && isActive) return 'active';
    if (stepIndex === currentIndex && !isActive && progress === 100) return 'completed';
    return 'idle';
  };

  const getStepProgress = (stepId: string) => {
    const stepIndex = agentSteps.findIndex(step => step.id === stepId);
    const currentIndex = agentSteps.findIndex(step => step.id === currentStep);
    
    if (stepIndex < currentIndex) return 100;
    if (stepIndex === currentIndex) {
      // Map overall progress to step progress
      const stepProgress = ((progress - (stepIndex * 20)) / 20) * 100;
      return Math.max(0, Math.min(100, stepProgress));
    }
    return 0;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {agentSteps.map((step, index) => {
        const status = getStepStatus(step.id);
        const stepProgress = getStepProgress(step.id);
        
        return (
          <Card
            key={step.id}
            className={cn(
              'transition-all duration-500 relative overflow-hidden',
              {
                'ring-2 ring-blue-400 shadow-lg scale-105': status === 'active',
                'bg-green-50 border-green-200': status === 'completed',
                'bg-gray-50': status === 'idle'
              }
            )}
          >
            <CardContent className="p-4">
              {/* Status Badge */}
              <div className="flex justify-between items-start mb-3">
                <Badge
                  variant={
                    status === 'completed' ? 'default' : 
                    status === 'active' ? 'secondary' : 
                    'outline'
                  }
                  className={cn(
                    'text-xs',
                    {
                      'bg-green-500': status === 'completed',
                      'bg-blue-500 animate-pulse': status === 'active'
                    }
                  )}
                >
                  {status === 'completed' ? '✅' : 
                   status === 'active' ? '⚡' : 
                   '⏳'}
                </Badge>
                
                {/* Agent Icon */}
                <div
                  className={cn(
                    'text-2xl transition-transform duration-300',
                    {
                      'animate-bounce': status === 'active',
                      'scale-110': status === 'completed'
                    }
                  )}
                >
                  {step.icon}
                </div>
              </div>

              {/* Agent Info */}
              <div className="space-y-2">
                <h3 className="font-semibold text-sm">{step.name}</h3>
                <p className="text-xs text-muted-foreground">
                  {status === 'active' ? step.description : 
                   status === 'completed' ? 'Completed' : 
                   'Waiting...'}
                </p>

                {/* Progress Bar */}
                {(status === 'active' || status === 'completed') && (
                  <div className="space-y-1">
                    <Progress 
                      value={stepProgress} 
                      className="h-2"
                    />
                    <div className="text-xs text-center text-muted-foreground">
                      {Math.round(stepProgress)}%
                    </div>
                  </div>
                )}

                {/* Keywords */}
                {status === 'active' && (
                  <div className="space-y-1">
                    <div className="text-xs font-medium">Current Task:</div>
                    <div className="flex flex-wrap gap-1">
                      {step.keywords.slice(0, 2).map((keyword, idx) => (
                        <span
                          key={idx}
                          className="text-xs bg-blue-100 text-blue-700 px-1 py-0.5 rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Active Background Effect */}
              {status === 'active' && (
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 animate-pulse" />
              )}

              {/* Completed Background Effect */}
              {status === 'completed' && (
                <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-emerald-500/5" />
              )}
            </CardContent>

            {/* Connection Line */}
            {index < agentSteps.length - 1 && (
              <div className="hidden lg:block absolute -right-6 top-1/2 transform -translate-y-1/2 z-10">
                <div
                  className={cn(
                    'w-12 h-0.5 transition-colors duration-500',
                    {
                      'bg-green-400': status === 'completed',
                      'bg-blue-400': status === 'active',
                      'bg-gray-300': status === 'idle'
                    }
                  )}
                />
                <div
                  className={cn(
                    'absolute -right-1 -top-1 w-2 h-2 rounded-full transition-colors duration-500',
                    {
                      'bg-green-400': status === 'completed',
                      'bg-blue-400 animate-pulse': status === 'active',
                      'bg-gray-300': status === 'idle'
                    }
                  )}
                />
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
} 