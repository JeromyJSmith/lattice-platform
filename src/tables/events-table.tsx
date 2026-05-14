import { RunsTable } from "./runs-table";

export function EventsTable(props: { events: Array<{ id: string }> }) {
  return <RunsTable runs={props.events} />;
}
