import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/requests", label: "Requests" },
  { to: "/approvals", label: "Approvals" },
  { to: "/history", label: "History" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-border bg-panel h-screen flex flex-col justify-between p-4">
      <div>
        <div className="mb-8 flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-accent flex items-center justify-center text-sm font-bold">
            F
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight">FlowPilot</div>
            <div className="text-[11px] text-neutral-500 leading-tight">Console v1</div>
          </div>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-accent/15 text-accent font-medium"
                    : "text-neutral-400 hover:bg-white/5 hover:text-neutral-200"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="text-xs text-neutral-500">Backend: localhost:8000</div>
    </aside>
  );
}