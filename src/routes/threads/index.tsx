import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/threads/")({
  component: ThreadsPage,
});

function ThreadsPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold mb-3">Threads</h1>
      <ul className="list-disc pl-6">
        <li>
          <Link to="/threads/$threadId" params={{ threadId: "thread-local" }}>
            thread-local
          </Link>
        </li>
      </ul>
    </main>
  );
}
