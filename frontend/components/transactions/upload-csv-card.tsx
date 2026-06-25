"use client";

import { useRef, useState } from "react";
import { Upload, Check, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { currency } from "@/lib/formatters";
import type { CsvPreviewResult } from "@/types";

type Phase = "idle" | "previewing" | "importing" | "done" | "error";

export function UploadCsvCard() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CsvPreviewResult | null>(null);
  const [result, setResult] = useState<{ imported: number; ignored: number; errors: string[] } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  function isOfx(f: File) {
    return f.name.toLowerCase().endsWith(".ofx");
  }

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPhase("previewing");
    setErrorMsg(null);
    try {
      const data = isOfx(selected) ? await api.importOfxPreview(selected) : await api.importCsvPreview(selected);
      setPreview(data);
    } catch (err) {
      setPhase("error");
      setErrorMsg(err instanceof Error ? err.message : "Falha ao gerar prévia.");
    }
  }

  async function handleImport() {
    if (!file) return;
    setPhase("importing");
    try {
      const data = isOfx(file) ? await api.importOfx(file) : await api.importCsv(file);
      setResult(data);
      setPhase("done");
    } catch (err) {
      setPhase("error");
      setErrorMsg(err instanceof Error ? err.message : "Falha ao importar.");
    }
  }

  function reset() {
    setPhase("idle");
    setFile(null);
    setPreview(null);
    setResult(null);
    setErrorMsg(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Importar CSV / OFX</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {phase === "idle" && (
          <>
            <p className="text-xs text-white/40">
              Importe transações a partir de um arquivo CSV ou OFX exportado do seu banco. Duplicatas são detectadas automaticamente.
            </p>
            <input ref={inputRef} type="file" accept=".csv,.ofx" className="hidden" onChange={handleFileChange} />
            <Button onClick={() => inputRef.current?.click()}>
              <Upload size={14} className="mr-2" />
              Selecionar arquivo
            </Button>
          </>
        )}

        {phase === "previewing" && preview && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="border border-border p-3">
                <div className="text-xs text-white/30">Total</div>
                <div className="font-semibold">{preview.total_rows}</div>
              </div>
              <div className="border border-border p-3">
                <div className="text-xs text-white/30">A importar</div>
                <div className="font-semibold text-success">{preview.importable}</div>
              </div>
              <div className="border border-border p-3">
                <div className="text-xs text-white/30">Duplicatas</div>
                <div className="font-semibold text-white/40">{preview.duplicates}</div>
              </div>
            </div>

            {preview.errors.length > 0 && (
              <div className="border border-danger/40 bg-danger/10 p-3 text-xs text-danger space-y-1">
                {preview.errors.map((e, i) => <div key={i}>{e}</div>)}
              </div>
            )}

            {preview.sample_rows.length > 0 && (
              <div className="overflow-x-auto border border-border">
                <table className="min-w-full divide-y divide-border text-xs">
                  <thead className="bg-[#111923] text-left text-[10px] uppercase text-white/30">
                    <tr>
                      <th className="px-2 py-2">Status</th>
                      <th className="px-2 py-2">Data</th>
                      <th className="px-2 py-2">Descrição</th>
                      <th className="px-2 py-2">Valor</th>
                      <th className="px-2 py-2">Categoria</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {preview.sample_rows.map((row, i) => (
                      <tr key={i} className="bg-muted/35">
                        <td className="px-2 py-2">
                          {row.status === "ready" ? (
                            <span className="text-success">pronto</span>
                          ) : (
                            <span className="text-white/30">duplicata</span>
                          )}
                        </td>
                        <td className="px-2 py-2 text-white/40">{row.date}</td>
                        <td className="px-2 py-2 max-w-48 truncate">{row.description}</td>
                        <td className={`px-2 py-2 font-medium ${Number(row.amount) >= 0 ? "text-success" : "text-danger"}`}>
                          {currency(row.amount)}
                        </td>
                        <td className="px-2 py-2 text-white/40">{row.category}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {preview.total_rows > preview.sample_rows.length && (
                  <div className="px-2 py-2 text-[10px] text-white/30">
                    Mostrando {preview.sample_rows.length} de {preview.total_rows} linhas
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-2">
              <Button onClick={handleImport} disabled={preview.importable === 0}>
                <Check size={14} className="mr-2" />
                Confirmar importação ({preview.importable})
              </Button>
              <Button className="border-white/10 bg-transparent text-white/50 hover:bg-white/5 hover:text-white" onClick={reset}>Cancelar</Button>
            </div>
          </div>
        )}

        {phase === "importing" && (
          <p className="text-sm text-white/40">Importando transações...</p>
        )}

        {phase === "done" && result && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-success text-sm">
              <Check size={14} />
              <span>{result.imported} transações importadas com sucesso.</span>
            </div>
            {result.ignored > 0 && (
              <p className="text-xs text-white/40">{result.ignored} ignoradas (duplicatas ou erros).</p>
            )}
            {result.errors.length > 0 && (
              <div className="border border-danger/40 bg-danger/10 p-3 text-xs text-danger space-y-1">
                {result.errors.map((e, i) => <div key={i}>{e}</div>)}
              </div>
            )}
            <Button className="border-white/10 bg-transparent text-white/50 hover:bg-white/5 hover:text-white" onClick={reset}>Importar outro arquivo</Button>
          </div>
        )}

        {phase === "error" && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-danger text-sm">
              <X size={14} />
              <span>{errorMsg}</span>
            </div>
            <Button className="border-white/10 bg-transparent text-white/50 hover:bg-white/5 hover:text-white" onClick={reset}>Tentar novamente</Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
