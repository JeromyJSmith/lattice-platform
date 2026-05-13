<!-- spec-verified: browser-use/browser-harness 2026-05-13 -->
# Capability Matrix — browser-harness

| Capability ID | Harness | Value | Risk | Decision | Proof run | Registry state after proof | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `browser-harness-new-tab` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); print(page_info())'` | TBD-browser-harness-new-tab |
| `browser-harness-goto-url` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab(); goto_url("https://example.com"); print(page_info())'` | TBD-browser-harness-goto-url |
| `browser-harness-page-info` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); print(page_info())'` | TBD-browser-harness-page-info |
| `browser-harness-click-at-xy` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab(...); capture_screenshot("/tmp/t.png"); click_at_xy(800, 400)'` | TBD-browser-harness-click-at-xy |
| `browser-harness-type-text` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab(...); js("document.body.innerHTML=\\"<input id=x></input>\\""); focus via js; type_text("hello"); js("document.getElementById(\'x\').value")'` | TBD-browser-harness-type-text |
| `browser-harness-fill-input` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab(...); js("document.body.innerHTML=\\"<input id=x></input>\\""); fill_input("#x", "text"); js("document.getElementById(\'x\').value")'` | TBD-browser-harness-fill-input |
| `browser-harness-press-key` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); press_key("Enter")'` | TBD-browser-harness-press-key |
| `browser-harness-scroll` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); scroll(400, 300, dy=500)'` | TBD-browser-harness-scroll |
| `browser-harness-capture-screenshot` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); path=capture_screenshot("/tmp/test.png"); import os; print(f"PNG exists: {os.path.exists(path)}")'` | TBD-browser-harness-capture-screenshot |
| `browser-harness-list-tabs` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'tabs=list_tabs(); print(f"Found {len(tabs)} tabs")'` | TBD-browser-harness-list-tabs |
| `browser-harness-current-tab` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'tab=current_tab(); print(tab["url"], tab["title"])'` | TBD-browser-harness-current-tab |
| `browser-harness-switch-tab` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); t=current_tab(); new_tab("https://google.com"); switch_tab(t)'` | TBD-browser-harness-switch-tab |
| `browser-harness-wait` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'import time; t=time.time(); wait(0.5); print(f"Slept: {time.time()-t > 0.4}")'` | TBD-browser-harness-wait |
| `browser-harness-wait-for-load` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); success=wait_for_load(timeout=10); print(f"Loaded: {success}")'` | TBD-browser-harness-wait-for-load |
| `browser-harness-wait-for-element` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); found=wait_for_element("body", timeout=5); print(f"Element found: {found}")'` | TBD-browser-harness-wait-for-element |
| `browser-harness-wait-for-network-idle` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); wait_for_load(); idle=wait_for_network_idle(timeout=5); print(f"Network idle: {idle}")'` | TBD-browser-harness-wait-for-network-idle |
| `browser-harness-js` | `meta-harness` | `high` | `medium` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("about:blank"); result=js("1+1"); print(f"JS eval: {result==2}")'` | TBD-browser-harness-js; **core dependency for sfa_browser_bonsai_v1.py** |
| `browser-harness-dispatch-key` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab(...); js("document.body.innerHTML=\\"<input id=x></input>\\""); dispatch_key("#x", "Enter")'` | TBD-browser-harness-dispatch-key |
| `browser-harness-upload-file` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'import tempfile; new_tab(...); f=tempfile.mktemp(); open(f, "w").write("test"); upload_file("input[type=file]", f)'` | TBD-browser-harness-upload-file |
| `browser-harness-http-get` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'text=http_get("https://example.com"); print(f"HTTP OK: {len(text) > 0}")'` | TBD-browser-harness-http-get |
| `browser-harness-cdp` | `meta-harness` | `high` | `medium` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'new_tab("https://example.com"); r=cdp("Page.getLayoutMetrics"); print(f"Layout: {bool(r)}")'` | TBD-browser-harness-cdp |
| `browser-harness-drain-events` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'events=drain_events(); print(f"Events buffered: {len(events)}")'` | TBD-browser-harness-drain-events |
| `browser-harness-iframe-target` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'tid=iframe_target("example.com"); print(f"Iframe found: {tid is not None}")'` | TBD-browser-harness-iframe-target |
| `browser-harness-ensure-real-tab` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `browser-harness -c 'tab=ensure_real_tab(); print(f"Real tab: {tab is not None and not tab[\"url\"].startswith(\"chrome://\")}")'` | TBD-browser-harness-ensure-real-tab |
| `browser-harness-agent-helpers-canvas` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `Artifact: read agent-workspace/agent_helpers.py after agent execution; verify custom helper present and invoked. (Proof run: agent writes helper during browser task)` | TBD-browser-harness-agent-helpers-canvas |
| `browser-harness-interaction-skills` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `Artifact: read interaction-skills/*.md directory; catalog coverage per mechanic (dialogs, dropdowns, iframes, etc.). Count >= 17 skill files.` | TBD-browser-harness-interaction-skills |
| `browser-harness-domain-skills` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `BH_DOMAIN_SKILLS=1 browser-harness -c 'goto_url("https://github.com/browser-use/browser-harness"); skills=goto_url(...); print(f"Skills returned: {bool(skills.get(\"domain_skills\"))}")'` | TBD-browser-harness-domain-skills |
| `browser-harness-cdp-attach-to-running-chrome` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `Manual: user enables chrome://inspect/#remote-debugging checkbox; agent runs browser-harness -c 'page_info()' without starting Chrome; verify connection succeeds.` | TBD-browser-harness-cdp-attach-to-running-chrome |
| `browser-harness-coordinate-first-clicks` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `Artifact: in helpers.py, verify click_at_xy uses Input.dispatchMouseEvent (compositor-level) and passes through iframes/shadow/cross-origin without DOM fallback.` | TBD-browser-harness-coordinate-first-clicks |
| `browser-harness-start-remote-daemon` | `meta-harness` | `high` | `low` | `defer` | `none` | `DEFERRED` | `(Deferred to Phase 2; requires BROWSER_USE_API_KEY provisioning)` | TBD-browser-harness-start-remote-daemon |
| `browser-harness-list-cloud-profiles` | `meta-harness` | `medium` | `low` | `defer` | `none` | `DEFERRED` | `(Deferred to Phase 2; requires BROWSER_USE_API_KEY provisioning)` | TBD-browser-harness-list-cloud-profiles |
| `browser-harness-list-local-profiles` | `meta-harness` | `medium` | `low` | `defer` | `none` | `DEFERRED` | `(Deferred to Phase 2; requires BROWSER_USE_API_KEY provisioning)` | TBD-browser-harness-list-local-profiles |
| `browser-harness-sync-local-profile` | `meta-harness` | `medium` | `low` | `defer` | `none` | `DEFERRED` | `(Deferred to Phase 2; requires BROWSER_USE_API_KEY provisioning)` | TBD-browser-harness-sync-local-profile |
| `browser-harness-multi-named-sessions` | `meta-harness` | `high` | `low` | `candidate` | `none` | `DEFERRED` | `BU_NAME=work browser-harness -c 'print(page_info())' & BU_NAME=research browser-harness -c 'print(page_info())'` — verify both run in parallel without socket collision | TBD-browser-harness-multi-named-sessions |

## Notes on decision policy

**Core helpers + patterns (rows 1-28)**: Marked `candidate` because browser-harness is mature and well-tested (30+ functions, clear CDP interface, no breaking changes expected). Each core helper is low-risk (read-only by default; `js()` is `medium` risk due to arbitrary JS execution but is essential for in-browser work). These are candidates for ACTIVE once proof runs confirm they wire correctly into the harness.

**`browser-harness-js` specifically** (row 17): This is the headline capability for the planned `sfa_browser_bonsai_v1.py` work (WebGPU + Bonsai in-browser execution). Medium risk (arbitrary JS in user's tab) but high value (enables full DOM introspection and transformers.js integration). Marked `candidate`; proof run will execute a simple JS expression and verify return value.

**Remote-browser surfaces (rows 29-32)**: Deferred to `phase-2-headless-pipelines` with reason `out-of-scope-for-current-phase`. Require `BROWSER_USE_API_KEY` environment variable provisioning and Browser Use Cloud account setup, neither of which is in scope for the current meta-harness proof cycle. Can be wired as ACTIVE once the API key is provisioned and cloud browser pools are budgeted.

## First proof targets

The in-flight `sfa_browser_bonsai_v1.py` will exercise these three capabilities in proof order:

1. **`browser-harness-new-tab`** — Create a new tab to hold the Bonsai instance.
2. **`browser-harness-js`** — Execute transformers.js / WebGPU JavaScript inside the tab, invoke inference, return results. **Core substrate.**
3. **`browser-harness-capture-screenshot`** — Screenshot the tab after inference to verify output (optional but useful for QA).

These three alone unlock the browser-based in-band inference harness. Remaining core helpers (click, scroll, type, wait, etc.) are validation targets for Phase 2 browser-automation scenarios (headless tasks, scraping, form-filling).
