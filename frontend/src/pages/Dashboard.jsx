import React, { useEffect, useState } from "react";
import { api } from "../api.js";

function Section({ title, items }) {
  return (
    <>
      <h4>{title}</h4>
      <ul>{items.map((i) => <li key={i}>{i}</li>)}</ul>
    </>
  );
}

function ActionCard({ card, onClose }) {
  return (
    <div className="card">
      <button onClick={onClose} style={{ float: "right" }}>Close</button>
      <h3>{card.title}</h3>
      <p>{card.summary}</p>
      <Section title="Recommended guardrails" items={card.guardrails} />
      <Section title="Approved tooling policy" items={card.approved_tooling} />
      <Section title="Team guidance" items={card.team_guidance} />
    </div>
  );
}

export default function Dashboard({ org }) {
  const [data, setData] = useState(null);
  const [card, setCard] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/dashboard?org_id=${org.org_id}`).then(setData).catch((e) => setError(e.message));
  }, [org]);

  function openRisk(risk) {
    setError("");
    api(`/playbooks/${risk}`).then(setCard).catch((e) => setError(e.message));
  }

  if (error && !data) return <p>{error}</p>;
  if (!data) return <p>Loading…</p>;

  return (
    <div className="card">
      <h2>{data.organization}</h2>
      <table>
        <thead>
          <tr><th>Team</th><th>Responded</th><th>Average</th><th>Level</th></tr>
        </thead>
        <tbody>
          {data.departments.map((d) => (
            <tr key={d.department}>
              <td>{d.department}</td>
              <td>{d.responded} / {d.employees}</td>
              <td>{d.average_score ?? "–"}</td>
              <td>{d.level}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p><small>Teams with fewer than 5 respondents are grouped as "Other teams", with scores and risks hidden.</small></p>

      <h3>Top risks</h3>
      {data.top_risks.length === 0 && <p>No risks to show.</p>}
      <ul>
        {data.top_risks.map(([risk, count]) => (
          <li key={risk}>
            <button onClick={() => openRisk(risk)}>{risk.replaceAll("_", " ")} ({count})</button>
          </li>
        ))}
      </ul>
      {error && <p>{error}</p>}
      {card && <ActionCard card={card} onClose={() => setCard(null)} />}
    </div>
  );
}
