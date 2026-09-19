import { useEffect, useState } from "react";
import { getDashboardSummary } from "../api/client";
import type { DashboardSummary } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-xl font-semibold mb-1">Dashboard</h1>
      <p className="text-sm text-neutral-500 mb-6">
        AI-powered process automation overview.
      </p>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {data && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="border border-border rounded-md p-4 bg-panel">
              <div className="text-xs text-neutral-500 mb-1">Total Requests</div>
              <div className="text-2xl font-semibold">{data.total}</div>
            </div>
            <div className="border border-border rounded-md p-4 bg-panel">
              <div className="text-xs text-neutral-500 mb-1">Pending Approval</div>
              <div className="text-2xl font-semibold">{data.pending}</div>
            </div>
            <div className="border border-border rounded-md p-4 bg-panel">
              <div className="text-xs text-neutral-500 mb-1">Completed</div>
              <div className="text-2xl font-semibold">{data.completed}</div>
            </div>
          </div>

          <h2 className="text-sm font-medium text-neutral-300 mb-3">Recent Requests</h2>
          <div className="space-y-2">
            {data.recent.length === 0 && (
              <p className="text-sm text-neutral-500">No requests yet.</p>
            )}
            {data.recent.map((r) => (
              <div
                key={r.id}
                className="border border-border rounded-md p-3 bg-panel flex items-center justify-between"
              >
                <div>
                  <div className="text-sm font-medium">{r.employee_name}</div>
                  <div className="text-xs text-neutral-500">
                    #{r.id} · {r.days_requested ?? "?"} day
                    {r.days_requested === 1 ? "" : "s"} · "{r.raw_text}"
                  </div>
                </div>
                <StatusBadge status={r.status} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}