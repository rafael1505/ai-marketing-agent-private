import React from "react";
import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DashboardPage({
  params
}: {
  params: { locale: string }
}) {
  const locale = params.locale || "en";
  const t = getTranslations(locale === "pt" ? "pt" : "en");
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">{t.nav.dashboard}</h1>
          <p className="text-muted-foreground mt-1">Welcome to your marketing command center</p>
        </div>
        <Button asChild className="shadow-md">
          <Link href={`/${locale}/materials/create`}>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-4 w-4 mr-2" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            {t.materials.create}
          </Link>
        </Button>
      </div>      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="overflow-hidden border-t-4 border-t-primary">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Materials
            </CardTitle>
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-primary"
              >
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <div className="flex items-center mt-1">
              <div className="h-2 w-2 rounded-full bg-green-500 mr-1"></div>
              <p className="text-xs text-muted-foreground">
                +0% from last month
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="overflow-hidden border-t-4 border-t-accent">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completed
            </CardTitle>
            <div className="h-8 w-8 rounded-full bg-accent/10 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-accent"
              >
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <div className="flex items-center mt-1">
              <div className="h-2 w-2 rounded-full bg-green-500 mr-1"></div>
              <p className="text-xs text-muted-foreground">
                +0% from last month
              </p>
            </div>          </CardContent>
        </Card>
        
        <Card className="overflow-hidden border-t-4 border-t-[#3b82f6]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              In Progress
            </CardTitle>
            <div className="h-8 w-8 rounded-full bg-[#3b82f6]/10 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-[#3b82f6]"
              >
                <rect width="20" height="14" x="2" y="5" rx="2" />
                <path d="M2 10h20" />
              </svg>
            </div>
          </CardHeader>          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <div className="flex items-center mt-1">
              <div className="h-2 w-2 rounded-full bg-yellow-500 mr-1"></div>
              <p className="text-xs text-muted-foreground">
                +0% from last month
              </p>
            </div>
          </CardContent>
        </Card>
      </div>      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="col-span-full shadow-md transition-all hover:border-primary">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">Your marketing materials activity</p>
            </div>
            <div className="rounded-full bg-secondary/80 p-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-36 bg-muted/30 rounded-lg border border-dashed border-muted">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground mb-2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4"/>
                <path d="M12 8h.01"/>
              </svg>
              <p className="text-muted-foreground">No recent activity</p>
              <Button variant="ghost" size="sm" className="mt-2">Create your first material</Button>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="shadow-md transition-all hover:border-primary">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">Frequently used tools</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2 hover:bg-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                <span className="text-sm">New Material</span>
              </Button>
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2 hover:bg-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
                  <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
                  <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
                </svg>
                <span className="text-sm">Analytics</span>
              </Button>
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2 hover:bg-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#3b82f6]">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
                <span className="text-sm">Templates</span>
              </Button>
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2 hover:bg-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-500">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
                <span className="text-sm">Help & Docs</span>
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card className="shadow-md transition-all hover:border-primary">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold">Marketing Insights</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">AI-powered recommendations</p>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted/30 p-4 rounded-lg border border-dashed border-muted">
              <p className="text-sm">Start generating marketing materials to get personalized AI insights and recommendations based on your content.</p>
            </div>
            <Button className="w-full">Generate First Insight</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
