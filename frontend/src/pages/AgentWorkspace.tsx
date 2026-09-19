import { useState } from "react";
import { submitLeaveRequest } from "../api/client";
import type { TraceStep as TraceStepType, RequestStatus } from "../types";
import TraceStep from "../components/TraceStep";

export default function AgentWorkspace() {
  const [employeeId, setEmployeeId] = useState(2);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trace, setTrace] = useState<TraceStepType[]>([]);
  const [status, setStatus] = useState<RequestStatus | null>(null);
  const [requestId, setRequestId] = useState<number | null>(null);

  async function handleSubmit() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setTrace([]);
    setStatus(null);
    try {
      const res = await submitLeaveRequest(employeeId, text);
      setTrace(res.trace);
      setStatus(res.status);
      setRequestId(res.request_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-xl font-semibold mb-1">Agent Workspace</h1>
      <p className="text-sm text-neutral-500 mb-6">
        Submit a leave request in plain language and watch the agent process it.
      </p>

      <div className="border border-border rounded-md p-4 bg-panel mb-6">
        <label className="block text-xs text-neutral-400 mb-1">Employee ID</label>
        <input
          type="number"
          value={employeeId}
          onChange={(e) => setEmployeeId(Number(e.target.value))}
          className="w-24 mb-4 bg-black/40 border border-border rounded px-2 py-1 text-sm"
        />

        <label className="block text-xs text-neutral-400 mb-1">What do you need?</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="I need leave for 3 days starting September 25."
          rows={3}
          className="w-full bg-black/40 border border-border rounded px-3 py-2 text-sm resize-none"
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-3 bg-accent text-white text-sm font-medium px-4 py-2 rounded-md disabled:opacity-50"
        >
          {loading ? "Running..." : "Run FlowPilot"}
        </button>
      </div>

      {error && (
        <div className="text-sm text-red-400 mb-4">{error}</div>
      )}

      {trace.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-neutral-300">Agent Execution</h2>
            {status && (
              <span className="text-xs px-2 py-1 rounded bg-white/5 text-neutral-300">
                {status}
              </span>
            )}
          </div>
          <div className="space-y-2">
            {trace.map((t, i) => (
              <TraceStep key={i} step={t.step} detail={t.detail} />
            ))}
          </div>
          {status === "pending_approval" && requestId && (
            <p className="text-xs text-neutral-500 mt-3">
              Request #{requestId} is now waiting in the Approval Center.
            </p>
          )}
        </div>
      )}
    </div>
  );
}