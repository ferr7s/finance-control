import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Insight } from "@/types";

export function InsightCard({ insight }: { insight: Insight }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{insight.title}</CardTitle>
        <Badge>{insight.severity}</Badge>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-6 text-white/60">{insight.content}</p>
      </CardContent>
    </Card>
  );
}
