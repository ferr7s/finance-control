import { Badge } from "@/components/ui/badge";
import type { AgentTool } from "@/types";

export function AgentToolsTable({ tools }: { tools: AgentTool[] }) {
  return (
    <div className="overflow-x-auto border border-border">
      <table className="min-w-full divide-y divide-border text-sm">
        <thead className="bg-[#111923] text-left text-xs uppercase text-white/30">
          <tr>
            <th className="px-3 py-3">Tool</th>
            <th className="px-3 py-3">Método</th>
            <th className="px-3 py-3">Endpoint</th>
            <th className="px-3 py-3">Segurança</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {tools.map((tool) => (
            <tr key={tool.name} className="bg-muted/35">
              <td className="px-3 py-3">
                <div className="font-medium">{tool.name}</div>
                <div className="text-xs text-white/30">{tool.description}</div>
              </td>
              <td className="px-3 py-3 text-white/40">{tool.method}</td>
              <td className="px-3 py-3 font-mono text-xs text-white/40">{tool.endpoint}</td>
              <td className="px-3 py-3">
                <Badge>{tool.write_safe ? "write-safe" : "read-only"}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
