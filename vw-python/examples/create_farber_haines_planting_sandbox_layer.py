"""Create a safe Farber-Haines planting sandbox design layer.

Run inside Vectorworks with `_Farber-Haines [2521].vwx` open.

What it does:
- duplicates all top-level objects from `L2.01 [Planting Plan]`
- inserts them into a new design layer
- preserves layer scale and elevation

Why:
- lets us test Plant Style Manager, 3D graphics, pricing, and IFC export setup
  without touching the architect's source layer

Important:
- if you use this sandbox for pricing scripts, set their `CONFIG["target_layers"]`
  to the sandbox layer name so you do not double-count the original layer
"""

from __future__ import annotations

from typing import Any

import vs  # type: ignore


CONFIG = {
    "source_layer_name": "L2.01 [Planting Plan]",
    "target_layer_name": "ZZ_ESTIMATION__L2.01_PLANTING_PLAN",
    "make_target_active": True,
}


def alert(message: str) -> None:
    vs.AlrtDialog(message)


def get_layer(name: str) -> Any:
    handle = vs.GetObject(name)
    if handle and vs.GetTypeN(handle) == 31:
        return handle
    return None


def layer_name(layer_handle: Any) -> str:
    try:
        return str(vs.GetLName(layer_handle) or "").strip()
    except Exception:
        return ""


def layer_scale(layer_handle: Any) -> float:
    try:
        return float(vs.GetLScale(layer_handle) or 1.0)
    except Exception:
        return 1.0


def layer_elevation(layer_handle: Any) -> tuple[float, float]:
    try:
        base_elev, thickness = vs.GetLayerElevation(layer_handle)
        return float(base_elev or 0.0), float(thickness or 0.0)
    except Exception:
        return 0.0, 0.0


def duplicate_object(handle: Any) -> None:
    dup_handle = vs.CreateDuplicateObject(handle, None)
    if dup_handle:
        vs.SetSelect(dup_handle)


def build_constraints(handle: Any) -> None:
    try:
        vs.BuildConstraintModelForObject(handle, False)
    except Exception:
        pass


def main() -> None:
    source_name = str(CONFIG["source_layer_name"])
    target_name = str(CONFIG["target_layer_name"])

    source_layer = get_layer(source_name)
    if not source_layer:
        alert(f"Source design layer not found: {source_name}")
        return

    if get_layer(target_name):
        alert(
            "Sandbox layer already exists.\n\n"
            f"Layer: {target_name}\n"
            "Delete it first if you want a clean rebuild."
        )
        return

    original_active = vs.ActLayer()
    original_active_name = layer_name(original_active)
    source_scale = layer_scale(source_layer)
    source_base_elev, source_thickness = layer_elevation(source_layer)

    vs.Layer(source_name)
    source_first_object = vs.FActLayer()
    target_layer = vs.CreateLayer(target_name, 1)
    if not target_layer:
        alert(f"Could not create sandbox layer: {target_name}")
        if original_active:
            vs.ActLayer()
        return

    try:
        vs.SetLScale(target_layer, source_scale)
    except Exception:
        pass
    try:
        vs.SetLayerElevation(target_layer, source_base_elev, source_thickness)
    except Exception:
        pass

    duplicated = 0
    if source_first_object and source_layer != vs.ActLayer():
        vs.BeginMultipleDuplicate()

        def _dup(handle: Any) -> None:
            nonlocal duplicated
            duplicate_object(handle)
            duplicated += 1

        vs.ForEachObjectInList(_dup, 0, 0, source_first_object)
        vs.EndMultipleDuplicate()

    vs.ForEachObjectInLayer(build_constraints, 0, 2, 0)

    if not CONFIG["make_target_active"] and original_active_name:
        try:
            vs.Layer(original_active_name)
        except Exception:
            pass

    alert(
        "Planting sandbox layer created.\n\n"
        f"Source: {source_name}\n"
        f"Sandbox: {target_name}\n"
        f"Objects duplicated: {duplicated}\n\n"
        "Set the estimate scripts' CONFIG['target_layers'] to the sandbox "
        "layer name before running pricing on this copy."
    )


if __name__ == "__main__":
    main()
