import { createFileRoute } from "@tanstack/react-router";
import {
  Box,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  Cpu,
  Download,
  ExternalLink,
  ImageIcon,
  Loader2,
  RefreshCw,
  Settings,
  Upload,
  X,
  Zap,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export const Route = createFileRoute("/genai/trellis")({
  component: TrellisPage,
});

const SIDECAR =
  (
    import.meta as ImportMeta & { env: { VITE_PIXELTABLE_SERVICE_URL?: string } }
  ).env?.VITE_PIXELTABLE_SERVICE_URL ?? "http://127.0.0.1:7770";

const SUPERSPLAT_BASE = "https://supersplat.playcanvas.com";

type JobStatus =
  | "idle"
  | "uploading"
  | "starting"
  | "processing"
  | "succeeded"
  | "failed"
  | "cancelled";

interface TrellisJob {
  job_id: string;
  status: JobStatus;
  input_filename?: string;
  output_glb_url?: string;
  output_ply_url?: string;
  output_video_url?: string;
  error_message?: string;
  duration_seconds?: number;
  created_at?: string;
}

interface GenParams {
  seed: number;
  ssGuidance: number;
  ssSteps: number;
  slatGuidance: number;
  slatSteps: number;
  meshSimplify: number;
  textureSize: number;
}

const DEFAULT_PARAMS: GenParams = {
  seed: 0,
  ssGuidance: 7.5,
  ssSteps: 12,
  slatGuidance: 3.0,
  slatSteps: 12,
  meshSimplify: 0.95,
  textureSize: 1024,
};

// ── Three.js GLB Viewer ──────────────────────────────────────────────────────

function GlbViewer({ url }: { url: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const frameRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !url) return;

    const w = canvas.clientWidth;
    const h = canvas.clientHeight;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(w, h, false);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    rendererRef.current = renderer;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111827);

    const camera = new THREE.PerspectiveCamera(45, w / h, 0.01, 1000);
    camera.position.set(0, 0.5, 2);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 2.0);
    dirLight.position.set(2, 4, 3);
    scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight(0x88aaff, 0.5);
    fillLight.position.set(-2, 0, -1);
    scene.add(fillLight);

    // Load GLB
    const loader = new GLTFLoader();
    loader.load(
      url,
      (gltf) => {
        const model = gltf.scene;
        // Centre and normalise scale
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 1.5 / maxDim;
        model.scale.setScalar(scale);
        const centre = box.getCenter(new THREE.Vector3());
        model.position.sub(centre.multiplyScalar(scale));
        scene.add(model);
      },
      undefined,
      (err) => console.warn("GLB load error:", err),
    );

    // Render loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Resize
    const ro = new ResizeObserver(() => {
      const nw = canvas.clientWidth;
      const nh = canvas.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh, false);
    });
    ro.observe(canvas);

    return () => {
      cancelAnimationFrame(frameRef.current);
      ro.disconnect();
      controls.dispose();
      renderer.dispose();
    };
  }, [url]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full rounded-lg"
      style={{ display: "block" }}
    />
  );
}

// ── Params Panel ─────────────────────────────────────────────────────────────

function ParamsPanel({
  params,
  onChange,
  disabled,
}: {
  params: GenParams;
  onChange: (p: GenParams) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = useState(false);

  const set = (key: keyof GenParams) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    onChange({ ...params, [key]: Number.isNaN(v) ? params[key] : v });
  };

  return (
    <div className="rounded-lg border border-purple-500/20 bg-gray-800/50">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-gray-300 hover:text-white transition-colors"
      >
        <span className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-purple-400" />
          Generation Parameters
        </span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {open && (
        <div className="border-t border-purple-500/10 px-4 pb-4 pt-3 grid grid-cols-2 gap-3">
          {(
            [
              ["seed", "Seed", 0, 999999, 1],
              ["ssGuidance", "SS Guidance", 1, 20, 0.5],
              ["ssSteps", "SS Steps", 1, 50, 1],
              ["slatGuidance", "SLAT Guidance", 1, 10, 0.5],
              ["slatSteps", "SLAT Steps", 1, 50, 1],
              ["meshSimplify", "Mesh Simplify", 0.5, 1, 0.01],
              ["textureSize", "Texture Size", 512, 2048, 256],
            ] as const
          ).map(([key, label, min, max, step]) => (
            <div key={key}>
              <label className="block text-xs text-gray-400 mb-1">
                {label}: <span className="text-purple-300">{params[key as keyof GenParams]}</span>
              </label>
              <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={params[key as keyof GenParams]}
                onChange={set(key as keyof GenParams)}
                disabled={disabled}
                className="w-full accent-purple-500 disabled:opacity-50"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Status Badge ──────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: JobStatus }) {
  const cfg: Record<JobStatus, { label: string; color: string; icon: React.ReactNode }> = {
    idle:       { label: "Idle",       color: "text-gray-400  bg-gray-700/50  border-gray-600",       icon: null },
    uploading:  { label: "Uploading",  color: "text-blue-300  bg-blue-900/30  border-blue-500/30",    icon: <Loader2 className="w-3 h-3 animate-spin" /> },
    starting:   { label: "Starting",   color: "text-yellow-300 bg-yellow-900/20 border-yellow-500/30",icon: <Loader2 className="w-3 h-3 animate-spin" /> },
    processing: { label: "Processing", color: "text-orange-300 bg-orange-900/20 border-orange-500/30",icon: <Cpu className="w-3 h-3 animate-pulse" /> },
    succeeded:  { label: "Succeeded",  color: "text-green-300  bg-green-900/20  border-green-500/30", icon: <CheckCircle className="w-3 h-3" /> },
    failed:     { label: "Failed",     color: "text-red-300    bg-red-900/20    border-red-500/30",   icon: <X className="w-3 h-3" /> },
    cancelled:  { label: "Cancelled",  color: "text-gray-400   bg-gray-800/50   border-gray-600",     icon: <X className="w-3 h-3" /> },
  };
  const { label, color, icon } = cfg[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${color}`}>
      {icon}
      {label}
    </span>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

function TrellisPage() {
  const [dragOver, setDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [params, setParams] = useState<GenParams>(DEFAULT_PARAMS);
  const [job, setJob] = useState<TrellisJob | null>(null);
  const [status, setStatus] = useState<JobStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [recentJobs, setRecentJobs] = useState<TrellisJob[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load recent jobs on mount
  useEffect(() => {
    fetch(`${SIDECAR}/v1/trellis/jobs`)
      .then((r) => r.json())
      .then((d) => setRecentJobs(d.jobs ?? []))
      .catch(() => {});
  }, []);

  // Poll for job status
  useEffect(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (!job || status === "succeeded" || status === "failed" || status === "cancelled") return;

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${SIDECAR}/v1/trellis/jobs/${job.job_id}`);
        if (!res.ok) return;
        const data: TrellisJob = await res.json();
        setJob(data);
        setStatus(data.status);
        if (data.status === "succeeded" || data.status === "failed" || data.status === "cancelled") {
          clearInterval(pollRef.current!);
        }
      } catch {
        // keep polling
      }
    }, 4000);

    return () => clearInterval(pollRef.current!);
  }, [job?.job_id, status]);

  const acceptFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) {
      setError("Please upload an image file (JPEG, PNG, WebP).");
      return;
    }
    setFile(f);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreviewUrl(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f) acceptFile(f);
    },
    [acceptFile],
  );

  const onFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) acceptFile(f);
    },
    [acceptFile],
  );

  const handleSubmit = async () => {
    if (!file) return;
    setError(null);
    setJob(null);
    setStatus("uploading");

    const form = new FormData();
    form.append("file", file);
    form.append("seed", String(params.seed));
    form.append("ss_guidance_strength", String(params.ssGuidance));
    form.append("ss_sampling_steps", String(params.ssSteps));
    form.append("slat_guidance_strength", String(params.slatGuidance));
    form.append("slat_sampling_steps", String(params.slatSteps));
    form.append("mesh_simplify_ratio", String(params.meshSimplify));
    form.append("texture_size", String(params.textureSize));

    try {
      const res = await fetch(`${SIDECAR}/v1/trellis/jobs`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail ?? `Server error ${res.status}`);
      }
      const d = await res.json();
      setJob({ job_id: d.job_id, status: d.status, input_filename: file.name });
      setStatus(d.status);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setStatus("idle");
    }
  };

  const handleCancel = async () => {
    if (!job) return;
    await fetch(`${SIDECAR}/v1/trellis/jobs/${job.job_id}`, { method: "DELETE" });
    setStatus("cancelled");
    setJob((j) => j ? { ...j, status: "cancelled" } : j);
  };

  const openSuperSplat = () => {
    const plyUrl = job?.output_ply_url;
    if (!plyUrl) return;
    window.open(`${SUPERSPLAT_BASE}/?url=${encodeURIComponent(plyUrl)}`, "_blank");
  };

  const isRunning = status === "starting" || status === "processing" || status === "uploading";
  const succeeded = status === "succeeded" && job?.output_glb_url;

  return (
    <div className="min-h-[calc(100vh-80px)] bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center">
              <Box className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">TRELLIS Image → 3D</h1>
              <p className="text-sm text-gray-400">Microsoft TRELLIS via Replicate · Gaussian splat output via SuperSplat</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowHistory((h) => !h)}
            className="flex items-center gap-2 rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-gray-300 hover:text-white transition-colors"
          >
            <Clock className="w-4 h-4" />
            History
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* ── Left panel: upload + params ── */}
          <div className="lg:col-span-2 space-y-4">

            {/* Dropzone */}
            <div
              onDrop={onDrop}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => !isRunning && fileInputRef.current?.click()}
              className={`relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed transition-all cursor-pointer select-none
                ${dragOver
                  ? "border-purple-400 bg-purple-900/20"
                  : previewUrl
                  ? "border-purple-500/40 bg-gray-800/50"
                  : "border-gray-600 bg-gray-800/30 hover:border-purple-500/50 hover:bg-gray-800/50"
                } ${isRunning ? "pointer-events-none opacity-70" : ""}`}
              style={{ minHeight: 220 }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="sr-only"
                onChange={onFileChange}
              />

              {previewUrl ? (
                <>
                  <img
                    src={previewUrl}
                    alt="Input preview"
                    className="max-h-48 max-w-full rounded-lg object-contain"
                  />
                  {!isRunning && (
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setPreviewUrl(null); setFile(null); }}
                      className="absolute top-2 right-2 w-6 h-6 rounded-full bg-gray-700/80 flex items-center justify-center text-gray-300 hover:text-white"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                  <p className="mt-2 text-xs text-gray-400">{file?.name}</p>
                </>
              ) : (
                <>
                  <Upload className="w-10 h-10 text-purple-400/60 mb-3" />
                  <p className="text-sm font-medium text-gray-300">Drop an image here</p>
                  <p className="text-xs text-gray-500 mt-1">or click to browse · JPEG · PNG · WebP</p>
                </>
              )}
            </div>

            {/* Params */}
            <ParamsPanel params={params} onChange={setParams} disabled={isRunning} />

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-900/20 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            {/* Submit / Cancel */}
            {isRunning ? (
              <button
                type="button"
                onClick={handleCancel}
                className="w-full flex items-center justify-center gap-2 rounded-lg border border-red-500/30 bg-red-900/20 px-4 py-3 text-sm font-medium text-red-300 hover:bg-red-900/40 transition-colors"
              >
                <X className="w-4 h-4" />
                Cancel Job
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!file || isRunning}
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:text-gray-500 px-4 py-3 text-sm font-semibold text-white transition-colors"
              >
                <Zap className="w-4 h-4" />
                Generate 3D with TRELLIS
              </button>
            )}
          </div>

          {/* ── Right panel: 3D viewer / status ── */}
          <div className="lg:col-span-3 space-y-4">

            {/* Status bar */}
            {job && (
              <div className="flex items-center justify-between rounded-xl border border-gray-700 bg-gray-800/50 px-4 py-3">
                <div className="flex items-center gap-3">
                  <StatusBadge status={status} />
                  <span className="text-sm text-gray-300 font-mono">{job.job_id}</span>
                </div>
                {(status === "starting" || status === "processing") && (
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    Polling every 4s…
                  </div>
                )}
                {status === "succeeded" && job.duration_seconds && (
                  <span className="text-xs text-green-400">
                    {job.duration_seconds.toFixed(0)}s
                  </span>
                )}
              </div>
            )}

            {/* 3D viewer */}
            {succeeded && job.output_glb_url ? (
              <div
                className="rounded-xl border border-purple-500/20 bg-gray-800/60 overflow-hidden"
                style={{ height: 420 }}
              >
                <GlbViewer url={job.output_glb_url} />
              </div>
            ) : (
              <div
                className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-700 bg-gray-800/20 text-gray-600"
                style={{ height: 420 }}
              >
                {isRunning ? (
                  <div className="flex flex-col items-center gap-3">
                    <div className="relative w-16 h-16">
                      <div className="absolute inset-0 rounded-full border-2 border-purple-500/20" />
                      <div className="absolute inset-0 rounded-full border-2 border-t-purple-500 animate-spin" />
                      <Box className="absolute inset-0 m-auto w-6 h-6 text-purple-400" />
                    </div>
                    <p className="text-sm text-gray-400">
                      {status === "uploading" ? "Uploading…" : status === "starting" ? "Starting TRELLIS…" : "Generating 3D mesh…"}
                    </p>
                    <p className="text-xs text-gray-500">This typically takes 2–4 minutes</p>
                  </div>
                ) : (
                  <>
                    <Box className="w-16 h-16 mb-4 opacity-20" />
                    <p className="text-sm">Upload an image and click Generate</p>
                  </>
                )}
              </div>
            )}

            {/* Output actions */}
            {succeeded && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {/* Download GLB */}
                <a
                  href={job.output_glb_url}
                  download="trellis-mesh.glb"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 rounded-lg border border-blue-500/30 bg-blue-900/20 px-4 py-3 text-sm font-medium text-blue-300 hover:bg-blue-900/40 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download GLB
                </a>

                {/* Download PLY */}
                {job.output_ply_url && (
                  <a
                    href={job.output_ply_url}
                    download="trellis-splat.ply"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 rounded-lg border border-teal-500/30 bg-teal-900/20 px-4 py-3 text-sm font-medium text-teal-300 hover:bg-teal-900/40 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download .ply
                  </a>
                )}

                {/* Open in SuperSplat */}
                {job.output_ply_url && (
                  <button
                    type="button"
                    onClick={openSuperSplat}
                    className="flex items-center justify-center gap-2 rounded-lg border border-purple-500/40 bg-purple-600/20 px-4 py-3 text-sm font-semibold text-purple-300 hover:bg-purple-600/30 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Open in SuperSplat
                  </button>
                )}
              </div>
            )}

            {/* Error detail */}
            {status === "failed" && job?.error_message && (
              <div className="rounded-lg border border-red-500/30 bg-red-900/20 px-4 py-3 text-sm text-red-300">
                <span className="font-medium">Generation failed: </span>
                {job.error_message}
              </div>
            )}

            {/* Preview video */}
            {succeeded && job.output_video_url && (
              <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
                <p className="px-4 py-2 text-xs font-medium text-gray-400 border-b border-gray-700">Turntable Preview</p>
                <video
                  src={job.output_video_url}
                  autoPlay
                  loop
                  muted
                  playsInline
                  className="w-full"
                />
              </div>
            )}

            {/* SuperSplat instructions */}
            {succeeded && job.output_ply_url && (
              <div className="rounded-xl border border-gray-700/50 bg-gray-800/30 px-4 py-3 text-xs text-gray-400 space-y-1">
                <p className="font-medium text-gray-300 flex items-center gap-2">
                  <ImageIcon className="w-3.5 h-3.5 text-purple-400" />
                  SuperSplat Gaussian Splat Viewer
                </p>
                <p>
                  Click <span className="text-purple-300 font-medium">Open in SuperSplat</span> to load your Gaussian splat in the
                  PlayCanvas SuperSplat editor — an open-source browser-based 3DGS viewer. If the auto-load doesn't work,
                  download the <code className="bg-gray-700 px-1 rounded">.ply</code> and drag it into{" "}
                  <a href="https://supersplat.playcanvas.com" target="_blank" rel="noopener noreferrer" className="text-purple-300 underline">
                    supersplat.playcanvas.com
                  </a>.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ── History panel ── */}
        {showHistory && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/50">
            <div className="flex items-center justify-between px-5 py-3 border-b border-gray-700">
              <h2 className="text-sm font-semibold text-gray-300">Recent Jobs</h2>
              <button
                type="button"
                onClick={() =>
                  fetch(`${SIDECAR}/v1/trellis/jobs`)
                    .then((r) => r.json())
                    .then((d) => setRecentJobs(d.jobs ?? []))
                }
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-white"
              >
                <RefreshCw className="w-3 h-3" />
                Refresh
              </button>
            </div>
            {recentJobs.length === 0 ? (
              <p className="px-5 py-8 text-sm text-center text-gray-600">No jobs yet.</p>
            ) : (
              <div className="divide-y divide-gray-700/50">
                {recentJobs.map((j) => (
                  <div
                    key={j.job_id}
                    className="flex items-center justify-between px-5 py-3 hover:bg-gray-700/30 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <StatusBadge status={j.status as JobStatus} />
                      <div>
                        <p className="text-sm text-gray-200 font-mono">{j.job_id}</p>
                        <p className="text-xs text-gray-500">{j.input_filename}</p>
                      </div>
                    </div>
                    {j.output_glb_url && (
                      <button
                        type="button"
                        onClick={() => {
                          setJob(j);
                          setStatus(j.status as JobStatus);
                          setShowHistory(false);
                        }}
                        className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
                      >
                        <Box className="w-3 h-3" />
                        View
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
