import { runtimeTools } from "./runtime-tools";

export function AgentUI() {
  return (
    <section className="rounded border p-4">
      <h3 className="font-semibold mb-2">TanStack AI Runtime Surface</h3>
      <ul className="list-disc pl-5 text-sm">
        {runtimeTools.map((tool) => (
          <li key={tool.id}>
            <span className="font-medium">{tool.id}</span>: {tool.description}
          </li>
        ))}
      </ul>
    </section>
  );
}
