"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { 
  Search, 
  BarChart3, 
  FileText, 
  History, 
  Settings, 
  HelpCircle,
  Home,
  Upload,
  Database,
  TestTube
} from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

const navigationItems = [
  {
    title: "Overview",
    href: "/dashboard",
    icon: Home,
    description: "Dashboard overview"
  },
  {
    title: "New Research",
    href: "/dashboard/research",
    icon: Search,
    description: "Start keyword research"
  },
  {
    title: "Upload Data",
    href: "/dashboard/upload",
    icon: Upload,
    description: "Upload Helium 10 data"
  },
  {
    title: "Results",
    href: "/dashboard/results",
    icon: BarChart3,
    description: "View analysis results"
  },
  {
    title: "Reports",
    href: "/dashboard/reports",
    icon: FileText,
    description: "Generated reports"
  },
  {
    title: "History",
    href: "/dashboard/history",
    icon: History,
    description: "Research history"
  },
  {
    title: "Data Store",
    href: "/dashboard/data",
    icon: Database,
    description: "Manage datasets"
  },
  {
    title: "Pipeline Test",
    href: "/test-pipeline",
    icon: TestTube,
    description: "Test AI pipeline with visual results"
  }
]

const supportItems = [
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    description: "Account settings"
  },
  {
    title: "Help",
    href: "/dashboard/help",
    icon: HelpCircle,
    description: "Get help"
  }
]

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 md:hidden" 
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={cn(
        "fixed top-16 left-0 z-50 h-[calc(100vh-4rem)] w-64 border-r bg-background transition-transform duration-300 ease-in-out",
        "md:sticky md:top-16 md:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-full flex-col">
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <nav className="space-y-2">
              <div>
                <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Main
                </p>
                {navigationItems.map((item) => (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={pathname === item.href ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start gap-3 h-10",
                        pathname === item.href && "bg-blue-50 text-blue-700 border-blue-200"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.title}
                    </Button>
                  </Link>
                ))}
              </div>
              
              <div className="pt-6">
                <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Support
                </p>
                {supportItems.map((item) => (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={pathname === item.href ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start gap-3 h-10",
                        pathname === item.href && "bg-blue-50 text-blue-700 border-blue-200"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.title}
                    </Button>
                  </Link>
                ))}
              </div>
            </nav>
          </div>
          
          <div className="border-t p-4">
            <div className="rounded-lg bg-blue-50 p-3">
              <h4 className="text-sm font-medium text-blue-900">Need Help?</h4>
              <p className="text-xs text-blue-700 mt-1">
                Check our documentation for detailed guides
              </p>
              <Button 
                size="sm" 
                className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                View Docs
              </Button>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
} 