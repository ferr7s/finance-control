"use client";

import { useState } from "react";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function GenerateInsightsButton() {
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      await api.generateInsights();
      window.location.reload();
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button onClick={generate} disabled={loading}>
      <RefreshCw size={16} />
      Gerar insights
    </Button>
  );
}
