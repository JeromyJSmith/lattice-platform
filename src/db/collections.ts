import {
  createCollection,
  localOnlyCollectionOptions,
} from "@tanstack/react-db";

export interface RunRow {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
}

export const runCollection = createCollection(
  localOnlyCollectionOptions<RunRow, string>({
    getKey: (item) => item.id,
    initialData: [],
  }),
);
