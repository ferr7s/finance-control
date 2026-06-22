"use client";

import { type ChangeEvent, type FormEvent, useRef, useState } from "react";
import { Eye, Upload } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { CsvImportPreview, CsvPreviewRow } from "@/types";

const currency = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

function formDataFor(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return formData;
}

function amount(value: string) {
  return currency.format(Number(value));
}

function statusLabel(row: CsvPreviewRow) {
  return row.status === "duplicate" ? "Duplicada" : "Pronta";
}

export function UploadCsvCard() {
  const router = useRouter();
  const formRef = useRef<HTMLFormElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CsvImportPreview | null>(null);
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    setPreview(null);
    setMessage("");
  }

  async function onPreview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setMessage("Selecione um arquivo CSV.");
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const result = await api.importCsvPreview(formDataFor(file));
      setPreview(result);
      if (result.errors.length > 0) {
        setMessage(result.errors.join(" "));
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao pré-visualizar CSV.");
    } finally {
      setLoading(false);
    }
  }

  async function onImport() {
    if (!file || !preview) return;

    setImporting(true);
    setMessage("");
    try {
      const result = await api.importCsv(formDataFor(file));
      setMessage(`${result.imported} importadas, ${result.ignored} ignoradas, ${result.total_rows} linhas lidas.`);
      setPreview(null);
      setFile(null);
      formRef.current?.reset();
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao importar CSV.");
    } finally {
      setImporting(false);
    }
  }

  const canPreview = Boolean(file) && !loading && !importing;
  const canImport = Boolean(file && preview && preview.importable > 0) && !loading && !importing;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Importar CSV bancário</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form ref={formRef} onSubmit={onPreview} className="grid gap-3 lg:grid-cols-[1fr_auto]">
          <Input name="file" type="file" accept=".csv,text/csv" onChange={onFileChange} />
          <div className="grid gap-2 sm:grid-cols-2 lg:flex">
            <Button disabled={!canPreview} type="submit">
              <Eye size={16} />
              {loading ? "Analisando" : "Pré-visualizar"}
            </Button>
            <Button disabled={!canImport} type="button" onClick={onImport}>
              <Upload size={16} />
              {importing ? "Importando" : "Importar"}
            </Button>
          </div>
        </form>

        {preview ? (
          <div className="space-y-3">
            <div className="grid gap-2 sm:grid-cols-3">
              <div className="rounded-md border border-border bg-[#0f1620] p-3">
                <div className="text-xs text-slate-500">Linhas lidas</div>
                <div className="text-lg font-semibold text-slate-100">{preview.total_rows}</div>
              </div>
              <div className="rounded-md border border-border bg-[#0f1620] p-3">
                <div className="text-xs text-slate-500">Prontas</div>
                <div className="text-lg font-semibold text-emerald-300">{preview.importable}</div>
              </div>
              <div className="rounded-md border border-border bg-[#0f1620] p-3">
                <div className="text-xs text-slate-500">Duplicadas</div>
                <div className="text-lg font-semibold text-amber-300">{preview.duplicates}</div>
              </div>
            </div>

            {preview.sample_rows.length > 0 ? (
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="min-w-full text-sm">
                  <thead className="bg-[#111923] text-left text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Data</th>
                      <th className="px-3 py-2">Descrição</th>
                      <th className="px-3 py-2 text-right">Valor</th>
                      <th className="px-3 py-2">Categoria</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.sample_rows.map((row) => (
                      <tr key={row.external_id} className="border-t border-border">
                        <td className="whitespace-nowrap px-3 py-2 text-slate-300">{statusLabel(row)}</td>
                        <td className="whitespace-nowrap px-3 py-2 text-slate-400">{row.date}</td>
                        <td className="min-w-56 px-3 py-2 text-slate-100">{row.description}</td>
                        <td className="whitespace-nowrap px-3 py-2 text-right text-slate-100">{amount(row.amount)}</td>
                        <td className="whitespace-nowrap px-3 py-2 text-slate-400">{row.category}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        ) : null}

        {preview?.errors.length ? (
          <div className="rounded-md border border-red-900/70 bg-red-950/30 p-3 text-sm text-red-200">
            {preview.errors.join(" ")}
          </div>
        ) : null}

        {message ? <p className="text-sm text-slate-400">{message}</p> : null}
      </CardContent>
    </Card>
  );
}
