import type { RequestStatus } from "../types";

const styles: Record<RequestStatus, string> = {
  pending_agent: "bg-white/5 text-neutral-400",
  pending_approval: "bg-amber-500/15 text-amber-400",
  approved: "bg-emerald-500/15 text-emerald-400",
  rejected: "bg-red-500/15 text-red-400",
  completed: "bg-emerald-500/15 text-emerald-400",
  needs_clarification: "bg-white/5 text-neutral-400",
};

export default function StatusBadge({ status }: { status: RequestStatus }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded ${styles[status]}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}