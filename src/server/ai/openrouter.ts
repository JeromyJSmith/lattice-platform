import { OpenRouter } from "@openrouter/sdk";
import { requireEnv } from "../env";
import { defaultOpenRouterModel } from "./model-config";

let _client: OpenRouter | undefined;

function getClient() {
  if (!_client)
    _client = new OpenRouter({ apiKey: requireEnv("OPENROUTER_API_KEY") });
  return _client;
}

export async function generateOpenRouterText(prompt: string) {
  const completion = await getClient().chat.completions.create({
    model: defaultOpenRouterModel,
    messages: [{ role: "user", content: prompt }],
  });

  return completion.choices?.[0]?.message?.content ?? "";
}
