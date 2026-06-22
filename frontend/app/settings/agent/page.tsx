import { ShieldCheck } from "lucide-react";

import { AgentToolsTable } from "@/components/agent/agent-tools-table";
import { CopyManifestButton } from "@/components/agent/copy-manifest-button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

const mcpConfig = {
  mcpServers: {
    "finance-control": {
      command: "python",
      args: ["-m", "backend.app.mcp.server"],
      env: {
        FINANCE_CONTROL_API_URL: "http://localhost:8000",
        AGENT_API_KEY: "dev-local-key"
      }
    }
  }
};

export default async function AgentSettingsPage() {
  const [manifest, agentHealth] = await Promise.all([
    api.manifest(),
    api
      .agentHealth()
      .then((health) => ({ ok: true as const, health }))
      .catch(() => ({ ok: false as const, health: null }))
  ]);
  return (
    <div className="space-y-4">
      <section className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Status do Agent Gateway</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-white/60">
            <Badge className={`gap-2 ${agentHealth.ok ? "border-accent/30 text-accent" : "border-warning/40 text-warning"}`}>
              <ShieldCheck size={14} />
              {agentHealth.ok ? "Online e read-only" : "API key diferente do exemplo"}
            </Badge>
            {agentHealth.ok ? (
              <div className="text-xs text-white/30">
                Status: {agentHealth.health.status} · Read-only: {agentHealth.health.read_only ? "sim" : "não"}
              </div>
            ) : null}
            <div className="font-mono text-xs text-white/30">http://localhost:8000</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Header Authorization</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="block bg-black p-3 text-xs text-white/60">Authorization: Bearer dev-local-key</code>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Manifest</CardTitle>
          </CardHeader>
          <CardContent>
            <CopyManifestButton manifest={manifest} />
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Tools REST disponíveis</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentToolsTable tools={manifest.tools} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Configuração MCP</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="overflow-auto bg-black p-4 text-xs text-white/60">{JSON.stringify(mcpConfig, null, 2)}</pre>
        </CardContent>
      </Card>

      <Card className="border-accent/30">
        <CardContent className="py-1 text-sm text-white/60">
          Endpoints financeiros expostos para agentes são read-only. Apenas análises textuais podem ser salvas em agent_analyses.
        </CardContent>
      </Card>
    </div>
  );
}
