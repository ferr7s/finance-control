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
  const manifest = await api.manifest();
  return (
    <div className="space-y-4">
      <section className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Status do Agent Gateway</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-slate-300">
            <Badge className="gap-2 border-accent/30 text-accent">
              <ShieldCheck size={14} />
              Protegido por API key
            </Badge>
            <div className="font-mono text-xs text-slate-500">http://localhost:8000</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Header Authorization</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="block rounded-md bg-[#0f1620] p-3 text-xs text-slate-300">Authorization: Bearer dev-local-key</code>
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
          <pre className="overflow-auto rounded-md bg-[#0f1620] p-4 text-xs text-slate-300">{JSON.stringify(mcpConfig, null, 2)}</pre>
        </CardContent>
      </Card>

      <Card className="border-accent/30">
        <CardContent className="py-1 text-sm text-slate-300">
          Endpoints financeiros expostos para agentes são read-only. Apenas análises textuais podem ser salvas em agent_analyses.
        </CardContent>
      </Card>
    </div>
  );
}
