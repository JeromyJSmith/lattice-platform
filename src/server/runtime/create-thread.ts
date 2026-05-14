import { createServerFn } from "@tanstack/react-start";

export const createThread = createServerFn({
  method: "POST",
})
  .inputValidator((data: { title?: string }) => data)
  .handler(async ({ data }) => {
    return {
      threadId: `thread-${crypto.randomUUID()}`,
      title: data.title ?? "Untitled Thread",
      createdAt: new Date().toISOString(),
    };
  });
