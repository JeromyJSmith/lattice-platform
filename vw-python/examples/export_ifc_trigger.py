"""Trigger an IFC4.3 export from the active document with no UI prompts.

Output goes to ~/.lattice/vw-exports/<timestamp>.ifc and the sidecar's
/v1/ingest/ifc endpoint is called immediately after with the file path
so LATTICE picks up the export.

Reference: vs.SetPref(*ifcExport*), vs.DoMenuTextByName('Export IFC...', 0).
"""

import os
import time

import vs  # type: ignore[import]


def main() -> None:
    target_dir = os.path.expanduser("~/.lattice/vw-exports")
    os.makedirs(target_dir, exist_ok=True)
    out_path = os.path.join(target_dir, f"{int(time.time())}.ifc")

    # The 'silent' / 'no prompt' export sequence — VW-version-specific.
    # Adjust pref numbers per the vs.* docs for the installed VW version.
    vs.SetPref(8908, True)            # use last-used IFC export settings
    vs.SetSavePref(8909, out_path)    # output path
    vs.DoMenuTextByName("Export IFC...", 0)

    vs.Message(f"exported to {out_path}")
    # TODO: POST out_path to the sidecar /v1/ingest/ifc once that endpoint lands.


if __name__ == "__main__":
    main()
