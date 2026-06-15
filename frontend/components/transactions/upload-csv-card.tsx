"use client";

import { useState } from "react";
import { Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export function UploadCsvCard() {
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const input = form.elements.namedItem("file") as HTMLInputElement;
    if (!input.files?.[0]) return;
    const formData = new FormData();
    formData.append("file", input.files[0]);
    setLoading(true);
    try {
      const result = await api.importCsv(formData);
      setMessage(`${result.imported} importadas, ${result.ignored} ignoradas, ${result.total_rows} linhas lidas.`);
      form.reset();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao importar CSV.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Importar CSV bancário</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row">
          <Input name="file" type="file" accept=".csv,text/csv" />
          <Button disabled={loading} type="submit">
            <Upload size={16} />
            Importar
          </Button>
        </form>
        {message ? <p className="mt-3 text-sm text-slate-400">{message}</p> : null}
      </CardContent>
    </Card>
  );
}
