"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function TestStylesPage() {
  return (
    <div className="p-8 space-y-4 fade-in">
      <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
        Test Styles Page
      </h1>
      
      <Card className="overflow-hidden border-t-4 border-t-primary hover-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Test Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p>This is a test card to verify that styles are working properly.</p>
          <Button className="mt-4 btn-scale">Test Button</Button>
        </CardContent>
      </Card>
    </div>
  );
}
