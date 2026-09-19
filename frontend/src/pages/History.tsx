import { useState } from "react";
import { getRequestDetail } from "../api/client";
import type { RequestDetailResponse } from "../types";
import TraceStep from "../components/TraceStep";
import StatusBadge from "../components/StatusBadge";

export default function History() {
  const [requestId, setRequestId] = useState("");
  const [data, setData] = useState<RequestDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLookup() {
    if (!requestId.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await getRequestDetail(Number(requestId));
      setData(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request not found");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-xl font-semibold mb-1">History</h1>
      <p className="text-sm text-neutral-500 mb-6">
        Look up a request by ID to see its full audit trail.
      </p>

      <div className="flex gap-2 mb-6">
        <input
          type="number"
          value={requestId}
          onChange={(e) => setRequestId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleLookup()}
          placeholder="Request ID"
          className="w-32 bg-black/40 border border-border rounded px-3 py-1.5 text-sm"
        />
        <button
          onClick={handleLookup}
          disabled={loading}
          className="px-4 py-1.5 text-sm rounded-md bg-accent text-white disabled:opacity-50"
        >
          {loading ? "Looking up..." : "Look up"}
        </button>
      </div>

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      {data && (
        <>
          <div className="border border-border rounded-md p-4 bg-panel mb-6">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium">
                Request #{data.request.id}
              </div>
              <StatusBadge status={data.request.status} />
            </div>
            <div className="grid grid-cols-2 gap-y-2 text-sm">
              <div className="text-neutral-500">Employee ID</div>
              <div>{data.request.employee_id}</div>
              <div className="text-neutral-500">Days Requested</div>
              <div>{data.request.days_requested ?? "—"}</div>
              <div className="text-neutral-500 col-span-2">Raw Request</div>
              <div className="col-span-2 text-neutral-300">
                "{data.request.raw_text}"
              </div>
            </div>
          </div>

          <h2 className="text-sm font-medium text-neutral-300 mb-3">Audit Trail</h2>
          <div className="space-y-2">
            {data.audit_trail.map((t, i) => (
              <TraceStep key={i} step={t.step} detail={t.detail} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}