import { useEffect, useState } from "react";
import { listPendingApprovals, decideApproval } from "../api/client";
import type { PendingApproval } from "../types";

export default function Approvals() {
  const [items, setItems] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actingOn, setActingOn] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listPendingApprovals();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDecision(requestId: number, decision: "approved" | "rejected") {
    setActingOn(requestId);
    try {
      await decideApproval(requestId, decision);
      setItems((prev) => prev.filter((i) => i.request_id !== requestId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit decision");
    } finally {
      setActingOn(null);
    }
  }

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center gap-2 mb-1">
        <h1 className="text-xl font-semibold">Approval Center</h1>
        {items.length > 0 && (
          <span className="text-xs px-2 py-0.5 rounded bg-accent/15 text-accent">
            {items.length} Pending
          </span>
        )}
      </div>
      <p className="text-sm text-neutral-500 mb-6">
        Requests waiting on manager approval.
      </p>

      {loading && <p className="text-sm text-neutral-500">Loading...</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
      {!loading && items.length === 0 && !error && (
        <p className="text-sm text-neutral-500">No pending approvals.</p>
      )}

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.request_id}
            className="border border-border rounded-md p-4 bg-panel"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="font-medium text-sm">{item.employee_name}</div>
              <div className="text-xs text-neutral-500">
                Request #{item.request_id} · {item.days_requested} day
                {item.days_requested === 1 ? "" : "s"}
              </div>
            </div>
            <p className="text-sm text-neutral-400 mb-3">"{item.raw_text}"</p>
            <div className="flex gap-2">
              <button
                onClick={() => handleDecision(item.request_id, "rejected")}
                disabled={actingOn === item.request_id}
                className="px-3 py-1.5 text-sm rounded-md border border-border text-neutral-300 hover:bg-white/5 disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => handleDecision(item.request_id, "approved")}
                disabled={actingOn === item.request_id}
                className="px-3 py-1.5 text-sm rounded-md bg-accent text-white hover:bg-accent/90 disabled:opacity-50"
              >
                Approve
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}