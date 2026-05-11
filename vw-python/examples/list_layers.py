"""List every design layer in the active Vectorworks document and report visibility.

Run via VW: Tools -> Plug-Ins -> Run Script... -> pick this file.

Reference (vs.* API): scope `vw-dev-scripting` in the local knowledge index,
or https://developer.vectorworks.net/.
"""

import vs  # type: ignore[import]


def main() -> None:
    rows = []
    layer = vs.FActLayer()  # first design layer
    while layer:
        name = vs.GetLName(layer)
        visible = vs.GetLVisibility(layer)
        rows.append((name, visible))
        layer = vs.NextLayer(layer)

    for name, visible in rows:
        vs.Message(f"{name}\t{'visible' if visible == 0 else 'hidden'}")


if __name__ == "__main__":
    main()
