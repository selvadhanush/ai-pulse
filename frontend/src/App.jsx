import React, { useState } from "react";
import { api, setToken } from "./api.js";
import Login from "./pages/Login.jsx";
import OrgPicker from "./pages/OrgPicker.jsx";
import Diagnostic from "./pages/Diagnostic.jsx";
import Report from "./pages/Report.jsx";
import Dashboard from "./pages/Dashboard.jsx";

export default function App() {
  const [step, setStep] = useState("login");
  const [session, setSession] = useState(null);
  const [org, setOrg] = useState(null);

  async function enterOrg(o) {
    setOrg(o);
    if (o.role === "admin") return setStep("dashboard");
    // Employees who already submitted go straight to their report
    try {
      const report = await api("/reports/me");
      setStep(report.answered > 0 ? "report" : "diagnostic");
    } catch {
      setStep("diagnostic");
    }
  }

  function signOut() {
    setToken("");
    setSession(null);
    setOrg(null);
    setStep("login");
  }

  const signedIn = step !== "login";

  return (
    <>
      {signedIn && (
        <header className="nav">
          <strong>AI Pulse</strong>
          <div className="nav-info">
            <span>{session.name}</span>
            {org && <span>{org.org_name}</span>}
            {org && <span className="badge badge-role">{org.role}</span>}
          </div>
          <div className="nav-actions">
            {session.organizations.length > 1 && (
              <button className="secondary" onClick={() => { setOrg(null); setStep("org"); }}>Switch Organization</button>
            )}
            <button className="secondary" onClick={signOut}>Sign Out</button>
          </div>
        </header>
      )}
      <div className="wrap">
        {!signedIn && <h1>AI Pulse</h1>}
        {step === "login" && (
          <Login onDone={(s) => { setSession(s); setStep("org"); }} />
        )}
        {step === "org" && <OrgPicker orgs={session.organizations} onPick={enterOrg} />}
        {step === "diagnostic" && <Diagnostic onDone={() => setStep("report")} />}
        {step === "report" && <Report onRetake={() => setStep("diagnostic")} />}
        {step === "dashboard" && <Dashboard org={org} />}
      </div>
    </>
  );
}
