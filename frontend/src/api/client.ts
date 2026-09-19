import type {
  SubmitLeaveResponse,
  RequestDetailResponse,
  ApprovalDecisionResponse,
  PendingApproval,
  DashboardSummary,
  Employee,
} from "../types";

const BASE_URL = "http://localhost:8000";


async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function submitLeaveRequest(
  employeeId: number,
  rawText: string
): Promise<SubmitLeaveResponse> {
  const res = await fetch(`${BASE_URL}/requests/leave`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employee_id: employeeId, raw_text: rawText }),
  });
  return handleResponse(res);
}

export async function getRequestDetail(
  requestId: number
): Promise<RequestDetailResponse> {
  const res = await fetch(`${BASE_URL}/requests/${requestId}`);
  return handleResponse(res);
}

export async function decideApproval(
  requestId: number,
  decision: "approved" | "rejected"
): Promise<ApprovalDecisionResponse> {
  const res = await fetch(`${BASE_URL}/approvals/${requestId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision }),
  });
  return handleResponse(res);
}

export async function listPendingApprovals(): Promise<PendingApproval[]> {
  const res = await fetch(`${BASE_URL}/approvals`);
  return handleResponse(res);
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${BASE_URL}/dashboard`);
  return handleResponse(res);
}

export async function listEmployees(): Promise<Employee[]> {
  const res = await fetch(`${BASE_URL}/employees`);
  return handleResponse(res);
}