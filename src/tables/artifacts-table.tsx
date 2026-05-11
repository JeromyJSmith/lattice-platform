import { RunsTable } from './runs-table'

export function ArtifactsTable(props: { artifacts: Array<{ id: string }> }) {
  return <RunsTable runs={props.artifacts} />
}
