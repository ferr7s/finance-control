import { GenerateInsightsButton } from "@/components/insights/generate-insights-button";
import { InsightCard } from "@/components/insights/insight-card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function InsightsPage() {
  const insights = await api.insights();
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <GenerateInsightsButton />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {insights.map((insight) => (
          <InsightCard key={insight.id} insight={insight} />
        ))}
      </div>
    </div>
  );
}
