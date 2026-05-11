import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'

export function EventTimeline(props: { items: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const rowVirtualizer = useVirtualizer({
    count: props.items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 28,
  })

  return (
    <div ref={parentRef} className="h-64 overflow-auto border rounded">
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            className="absolute left-0 top-0 w-full px-3 py-1 text-xs"
            style={{
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {props.items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}
