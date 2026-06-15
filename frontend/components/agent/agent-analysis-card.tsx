import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentAnalysis } from "@/types";

export function AgentAnalysisCard({ analysis }: { analysis: AgentAnalysis }) {
  const metadata = analysis.metadata ?? analysis.metadata_json;
  return (
    <Card>
      <CardHeader>
        <CardTitle>{analysis.title}</CardTitle>
        <Badge>{analysis.source}</Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm leading-6 text-slate-300">{analysis.content}</p>
        {metadata ? <pre className="overflow-auto rounded-md bg-[#0f1620] p-3 text-xs text-slate-400">{JSON.stringify(metadata, null, 2)}</pre> : null}
      </CardContent>
    </Card>
  );
}
