import { runtimeIngestionSchema } from "./ingestion-schema";

export function getPixeltableIngestionStatus() {
  const env = typeof process !== "undefined" ? process.env : {};
  const enabled = env.PIXELTABLE_ENABLED === "true";
  const explicitTcp = env.PIXELTABLE_SERVICE_URL;
  const transportMode: "uds" | "tcp" =
    explicitTcp && /^https?:\/\//i.test(explicitTcp) ? "tcp" : "uds";
  return {
    enabled,
    schema: runtimeIngestionSchema,
    transportMode,
    serviceUrl: explicitTcp ?? null,
    socketPath: env.PIXELTABLE_SOCK ?? "/tmp/vwbridge-pxt.sock",
  };
}

