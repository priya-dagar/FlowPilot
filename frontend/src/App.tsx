import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import AgentWorkspace from "./pages/AgentWorkspace";
import Approvals from "./pages/Approvals";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";

function Placeholder({ name }: { name: string }) {
  return <div className="p-8 text-neutral-400">{name} page — coming next</div>;
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/history" element={<History />} />
            <Route path="/requests" element={<AgentWorkspace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}