"use client";

import { useState } from "react";
import { Copy } from "lucide-react";

import { Button } from "@/components/ui/button";

export function CopyManifestButton({ manifest }: { manifest: unknown }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(JSON.stringify(manifest, null, 2));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }
  return (
    <Button onClick={copy}>
      <Copy size={16} />
      {copied ? "Copiado" : "Copiar manifest"}
    </Button>
  );
}
