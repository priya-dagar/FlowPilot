export type RequestStatus =
  | "pending_agent"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "completed"
  | "needs_clarification";

export interface TraceStep {
  step: string;
  detail: string;
}

export interface SubmitLeaveResponse {
  request_id: number;
  status: RequestStatus;
  trace: TraceStep[];
}

export interface LeaveRequestDetail {
  id: number;
  employee_id: number;
  raw_text: string;
  days_requested: number | null;
  status: RequestStatus;
}

export interface RequestDetailResponse {
  request: LeaveRequestDetail;
  audit_trail: TraceStep[];
}

export interface ApprovalDecisionResponse {
  request_id: number;
  final_status: RequestStatus;
}

export interface PendingApproval {
  request_id: number;
  employee_name: string;
  raw_text: string;
  days_requested: number | null;
}

export interface RecentRequest {
  id: number;
  employee_name: string;
  raw_text: string;
  days_requested: number | null;
  status: RequestStatus;
}

export interface DashboardSummary {
  total: number;
  pending: number;
  completed: number;
  recent: RecentRequest[];
}

export interface Employee {
  id: number;
  name: string;
  email: string;
  leave_balance: number;
}