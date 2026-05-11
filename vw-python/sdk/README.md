# Vectorworks Python API — Where it lives

You don't install this. The `vs.*` module is bundled with Vectorworks itself — every supported VW version ships a Python interpreter and the `vs` module pre-imported. Run scripts via `Tools → Plug-Ins → Run Script…`.

For autocomplete in external editors, copy `vs.pyi` from the VW install (`<VW>/Python/lib/site-packages/vs.pyi`) into this directory. The `.gitignore` excludes it because it's tied to a specific VW version.
