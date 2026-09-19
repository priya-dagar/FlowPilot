interface Props {
  step: string;
  detail: string;
}

const stepLabels: Record<string, string> = {
  parse_request: "Parse Request",
  policy_check: "Policy Check",
  balance_check: "Balance Check",
  final_decision: "Decision",
  manager_decision: "Manager Decision",
  action_execution: "Action Execution",
};

export default function TraceStep({ step, detail }: Props) {
  return (
    <div className="border border-border rounded-md p-3 bg-black/30">
      <div className="text-xs text-accent font-medium mb-1">
        {stepLabels[step] || step}
      </div>
      <div className="text-sm text-neutral-300">{detail}</div>
    </div>
  );
}