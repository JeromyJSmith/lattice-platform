import {
  getCoreRowModel,
  useReactTable,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table'
import type { RunRow } from '#/server/runtime/list-runs'

const helper = createColumnHelper<RunRow>()

const columns = [
  helper.accessor('run_id', {
    header: 'Run ID',
    cell: (info) => {
      const id = info.getValue()
      const short = id.length > 8 ? id.slice(-8) : id
      return (
        <span title={id} className="font-mono">
          {short}
        </span>
      )
    },
  }),
  helper.accessor('status', { header: 'Status' }),
  helper.accessor('task', {
    header: 'Task',
    cell: (info) => info.getValue() || '—',
  }),
  helper.accessor('agent_kind', {
    header: 'Agent',
    cell: (info) => info.getValue() || '—',
  }),
  helper.accessor('started_at', {
    header: 'Started',
    cell: (info) => info.getValue() ?? '—',
  }),
]

export function RunsTable(props: {
  runs: Array<RunRow>
  activeRunId?: string | null
  onRowClick?: (row: RunRow) => void
}) {
  const table = useReactTable({
    data: props.runs,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <table className="w-full text-sm">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th key={header.id} className="text-left p-2">
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.length === 0 ? (
          <tr>
            <td className="p-2 opacity-60" colSpan={columns.length}>
              No runs yet.
            </td>
          </tr>
        ) : (
          table.getRowModel().rows.map((row) => {
            const isActive = row.original.run_id === props.activeRunId
            return (
              <tr
                key={row.id}
                onClick={() => props.onRowClick?.(row.original)}
                className={
                  'cursor-pointer transition ' +
                  (isActive
                    ? 'bg-[rgba(79,184,178,0.18)] hover:bg-[rgba(79,184,178,0.24)]'
                    : 'hover:bg-[rgba(79,184,178,0.08)]')
                }
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="p-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )
          })
        )}
      </tbody>
    </table>
  )
}
