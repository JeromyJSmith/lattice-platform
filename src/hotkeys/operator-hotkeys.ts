import { useHotkeys } from '@tanstack/react-hotkeys'

export function useOperatorHotkeys(options: {
  onToggleSidebar: () => void
  onFocusRuntime: () => void
}) {
  useHotkeys([
    { hotkey: 'Mod+b', callback: options.onToggleSidebar },
    { hotkey: 'Mod+k', callback: options.onFocusRuntime },
  ])
}
