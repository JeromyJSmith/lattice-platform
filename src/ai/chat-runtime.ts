export async function runRuntimeChat(prompt: string) {
  const response = await fetch("/api/runtime/openrouter", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) throw new Error("Runtime chat request failed");
  return (await response.json()) as { text: string };
}
