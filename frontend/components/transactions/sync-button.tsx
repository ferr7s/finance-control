"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { SyncStatus } from "@/types";

function formatSyncedAt(iso: string | null | undefined): string {
  if (!iso) return "";
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return "agora mesmo";
  if (diff < 3600) return `${Math.floor(diff / 60)} min atrás`;
  return `${Math.floor(diff / 3600)}h atrás`;
}

export function SyncButton() {
  const [statuses, setStatuses] = useState<SyncStatus[]>([]);
  const [triggering, setTriggering] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isRunning = statuses.some((s) => s.status === "running" || s.status === "pending");
  const lastSync = statuses.find((s) => s.synced_at);
  const hasError = statuses.some((s) => s.status === "failed");
  const totalSynced = statuses.reduce((sum, s) => sum + (s.transactions_synced ?? 0), 0);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.syncStatus();
      setStatuses(data);
    } catch {
      // sync server may not be running yet
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (isRunning) {
      pollRef.current = setInterval(fetchStatus, 3000);
    } else {
      if (pollRef.current) clearInterval(pollRef.current);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [isRunning, fetchStatus]);

  const handleSync = async () => {
    setTriggering(true);
    try {
      await api.triggerSync();
      await fetchStatus();
    } catch {
      // sync server offline
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <Button onClick={handleSync} disabled={triggering || isRunning} className="gap-2">
        <RefreshCw size={13} className={isRunning ? "animate-spin" : ""} />
        {isRunning ? "Sincronizando..." : "Sincronizar"}
      </Button>

      {lastSync?.synced_at && (
        <span className="text-[10px] uppercase tracking-widest text-white/30">
          {hasError ? (
            <span className="text-danger/70">Falha — {statuses.find((s) => s.error)?.error?.slice(0, 60)}</span>
          ) : (
            <>
              {totalSynced > 0 && <span className="mr-2 text-white/50">{totalSynced} tx</span>}
              {formatSyncedAt(lastSync.synced_at)}
            </>
          )}
        </span>
      )}
    </div>
  );
}
