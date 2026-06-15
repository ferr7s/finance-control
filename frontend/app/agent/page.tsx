import { AgentAnalysisCard } from "@/components/agent/agent-analysis-card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AgentPage() {
  const analyses = await api.analyses();
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {analyses.map((analysis) => (
        <AgentAnalysisCard key={analysis.id} analysis={analysis} />
      ))}
    </div>
  );
}
