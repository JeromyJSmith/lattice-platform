import { createFileRoute, Link } from "@tanstack/react-router";

const agents = ["claude-code", "pi", "hermes", "openrouter"] as const;

export const Route = createFileRoute("/agents/")({
  component: AgentsPage,
});

function AgentsPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold mb-3">Agents</h1>
      <ul className="list-disc pl-6">
        {agents.map((agent) => (
          <li key={agent}>
            <Link to="/agents/$agentId" params={{ agentId: agent }}>
              {agent}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
