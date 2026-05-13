"""Botanical prompt engine for SD image generation → TRELLIS pipeline.

Produces prompts optimized for:
  - Single isolated plant subject (full specimen visible)
  - White/light-grey studio background
  - Directional lighting that reads 3D form clearly
  - No background clutter — TRELLIS needs clean silhouettes

Usage:
    from generate_plant_prompt import build_prompt
    p = build_prompt("JUNI_VIR", "Eastern Red Cedar", "Juniperus virginiana", season="summer")
    print(p["sd_prompt"])
    print(p["negative_prompt"])
    print(p["recommended_model"])
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

Season = Literal["spring", "summer", "autumn", "winter", "evergreen"]

# ---------------------------------------------------------------------------
# Per-species trait library
# ---------------------------------------------------------------------------

SPECIES_TRAITS: dict[str, dict] = {
    "JUNI_VIR": {
        "form": "narrow columnar conical",
        "foliage": "dense scale-like evergreen foliage, dark blue-green, aromatic cedar",
        "bark": "reddish-brown fibrous shredding bark",
        "size_hint": "small tree 4-8 meters tall",
        "season": "evergreen",
        "notable": "waxy blue-grey seed cones",
    },
    "PLAT_ACE": {
        "form": "broad spreading rounded crown, massive trunk",
        "foliage": "large maple-like lobed leaves, bright green",
        "bark": "distinctive patchwork camouflage bark, grey-brown-cream exfoliating",
        "size_hint": "large tree 20-35 meters tall",
        "season": "summer",
        "notable": "peeling bark revealing cream patches",
    },
    "QUER_ROB": {
        "form": "broad rounded spreading crown, heavy limbs",
        "foliage": "classic lobed oak leaves, deep green, leathery",
        "bark": "deeply furrowed grey-brown ridged bark",
        "size_hint": "large tree 20-30 meters tall",
        "season": "summer",
        "notable": "dense acorn-bearing crown",
    },
    "ACER_RUB": {
        "form": "oval to rounded crown, upright branching",
        "foliage": "3-5 lobed maple leaves, medium green, silver-white underside",
        "bark": "smooth grey bark, becoming furrowed with age",
        "size_hint": "medium-large tree 12-20 meters",
        "season": "summer",
        "notable": "brilliant scarlet autumn foliage",
    },
    "TAXO_DIS": {
        "form": "conical crown with buttressed flared trunk base",
        "foliage": "feathery light-green needles on horizontal branchlets",
        "bark": "reddish-brown fibrous peeling bark, distinctive flared base",
        "size_hint": "large tree 20-40 meters, distinctive swollen base",
        "season": "summer",
        "notable": "knobby cypress knees, flared buttress roots",
    },
    "MAGN_GRA": {
        "form": "dense pyramidal to oval crown, lower branches sweeping ground",
        "foliage": "large glossy dark-green leathery leaves, rust-brown undersides",
        "bark": "smooth grey bark",
        "size_hint": "large tree 18-25 meters",
        "season": "evergreen",
        "notable": "large white dinner-plate flowers, glossy leaves with brown felt undersides",
    },
    "ILEX_OPA": {
        "form": "dense pyramidal conical, formal",
        "foliage": "spiny glossy dark green leaves",
        "bark": "smooth light grey bark",
        "size_hint": "small-medium tree 6-12 meters",
        "season": "evergreen",
        "notable": "bright red berries on female trees",
    },
    "CORN_FLO": {
        "form": "flat-topped layered horizontal branching",
        "foliage": "oval leaves with parallel veins, medium-green",
        "bark": "grey-brown blocky furrowed bark",
        "size_hint": "small tree 5-10 meters, wide as tall",
        "season": "spring",
        "notable": "large white bracts resembling flowers, layered tiered branching",
    },
    "PRUN_CER": {
        "form": "rounded to vase-shaped crown",
        "foliage": "serrated oval leaves, medium green, bronze tints",
        "bark": "reddish-brown horizontal lenticel-marked smooth bark",
        "size_hint": "small-medium tree 6-12 meters",
        "season": "spring",
        "notable": "profuse white-pink blossom clusters",
    },
    "FAGU_SYL": {
        "form": "massive broad dome, muscular smooth trunk, low branch insertion",
        "foliage": "oval wavy-edged leaves, bright fresh green in spring, rich copper autumn",
        "bark": "smooth silver-grey bark, distinctive and beautiful",
        "size_hint": "very large tree 25-35 meters, broad spreading",
        "season": "summer",
        "notable": "smooth silver-grey bark, dense shade canopy",
    },
}

# Model recommendations per use-case
MODELS = {
    "photorealistic_xl": "JJsLandscape_Render_XL.safetensors",
    "photorealistic_sd15": "landscapeRendering_v10.ckpt",
    "supermix_sd15": "landscapesupermix_v21.safetensors",
    "latte_xl": "lattezenLandscape_v10.safetensors",
}


@dataclass
class PlantPrompt:
    species_code: str
    sd_prompt: str
    negative_prompt: str
    recommended_model: str
    width: int
    height: int
    steps: int
    cfg: float
    sampler: str
    notes: str = ""


def build_prompt(
    species_code: str,
    common_name: str,
    scientific_name: str,
    season: Season | None = None,
) -> PlantPrompt:
    traits = SPECIES_TRAITS.get(species_code, {})
    effective_season = season or traits.get("season", "summer")

    form    = traits.get("form", "tree with natural branching structure")
    foliage = traits.get("foliage", "green leaves")
    bark    = traits.get("bark", "natural bark texture")
    size    = traits.get("size_hint", "medium tree")
    notable = traits.get("notable", "")

    # Season modifier
    season_tag = {
        "spring":     "in spring, fresh bright green new leaves, possibly in bloom",
        "summer":     "in full summer leaf, lush dense canopy",
        "autumn":     "in peak autumn colour, warm golden red foliage",
        "winter":     "in winter, bare branches showing full structure, no leaves",
        "evergreen":  "evergreen, full dense foliage year-round",
    }.get(effective_season, "in full leaf")

    notable_tag = f", {notable}" if notable else ""

    sd_prompt = (
        f"single isolated {common_name} ({scientific_name}) specimen tree, "
        f"{form}{notable_tag}, "
        f"{foliage}, {bark}, "
        f"{size}, {season_tag}, "
        f"full tree visible head to roots, "
        f"pure white seamless studio background, "
        f"professional botanical photography, "
        f"soft diffused side lighting revealing 3D form and volume, "
        f"sharp focus throughout, ultra high detail, 8k, "
        f"natural textures, physically accurate botany, no shadows on background, "
        f"centered composition, square frame, clean silhouette"
    )

    negative_prompt = (
        "blurry, low quality, jpeg artifacts, watermark, logo, text, "
        "multiple trees, forest, landscape scene, sky, ground, soil, pot, "
        "other plants in background, busy background, coloured background, "
        "shadow on background, overexposed, underexposed, flat lighting, "
        "cartoon, illustration, painting, sketch, anime, 3d render, cgi, "
        "cropped tree, partial view, cut off branches, aerial view, "
        "close-up detail only, macro, deformed, unrealistic proportions"
    )

    # Pick model — XL models for best quality on this machine (128GB)
    if "JJsLandscape_Render_XL.safetensors" in MODELS.values():
        model = MODELS["photorealistic_xl"]
        width, height, steps, cfg = 1024, 1024, 35, 7.0
    else:
        model = MODELS["photorealistic_sd15"]
        width, height, steps, cfg = 768, 768, 30, 7.5

    return PlantPrompt(
        species_code=species_code,
        sd_prompt=sd_prompt,
        negative_prompt=negative_prompt,
        recommended_model=model,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        sampler="dpmpp_2m",
        notes=f"{size}, {effective_season} season",
    )


def build_all_prompts() -> list[PlantPrompt]:
    species_list = [
        ("JUNI_VIR", "Eastern Red Cedar",   "Juniperus virginiana"),
        ("PLAT_ACE", "Sycamore",            "Platanus acerifolia"),
        ("QUER_ROB", "English Oak",         "Quercus robur"),
        ("ACER_RUB", "Red Maple",           "Acer rubrum"),
        ("TAXO_DIS", "Bald Cypress",        "Taxodium distichum"),
        ("MAGN_GRA", "Southern Magnolia",   "Magnolia grandiflora"),
        ("ILEX_OPA", "American Holly",      "Ilex opaca"),
        ("CORN_FLO", "Flowering Dogwood",   "Cornus florida"),
        ("PRUN_CER", "Cherry",              "Prunus cerasifera"),
        ("FAGU_SYL", "European Beech",      "Fagus sylvatica"),
    ]
    return [build_prompt(code, common, sci) for code, common, sci in species_list]


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        code = sys.argv[1]
        # Try to find in known species
        for sp_code, traits in SPECIES_TRAITS.items():
            if sp_code == code:
                p = build_prompt(code, code.replace("_", " ").title(), code)
                print(json.dumps(p.__dict__, indent=2))
                break
        else:
            print(f"Unknown species code: {code}. Known: {list(SPECIES_TRAITS)}")
    else:
        for p in build_all_prompts():
            print(f"\n{'='*60}")
            print(f"[{p.species_code}]  model={p.recommended_model}")
            print(f"POSITIVE: {p.sd_prompt[:120]}...")
            print(f"NEGATIVE: {p.negative_prompt[:80]}...")
