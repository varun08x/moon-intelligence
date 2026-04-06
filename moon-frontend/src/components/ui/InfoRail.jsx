import React, { useContext, useEffect, useMemo, useState } from "react"
import { AppContext } from "../../context/AppContext"
import { getDetections } from "../../services/detectionService"
import { API_BASE } from "../../services/api"

const cards = [
  {
    title: "Mission Brief",
    text:
      "Detect and classify lunar surface hazards (boulders, landslides) from imagery, then map results onto a 3D globe for rapid assessment."
  },
  {
    title: "Pipeline",
    text:
      "Upload image -> AI inference -> Geo-mapping -> Interactive 3D visualization with hotspots and confidence."
  },
  {
    title: "Outputs",
    text:
      "Risk zones, crater/boulder counts, and coordinates ready for mission planning and safety reviews."
  }
]

export default function InfoRail() {
  const { state } = useContext(AppContext)
  const [detections, setDetections] = useState(null)
  const [status, setStatus] = useState("idle")
  const [viewMode, setViewMode] = useState("annotated")
  const [splitView, setSplitView] = useState(false)
  const [healthStatus, setHealthStatus] = useState("unknown")
  const outputLinks = useMemo(() => {
    const annotatedPath = state?.lastResult?.annotated_path
    const threeDPath = state?.lastResult?.three_d_path
    const originalPath =
      state?.lastResult?.frame_path || state?.lastResult?.file_path

    const toUrl = (pathValue, basePath) => {
      if (!pathValue) return null
      if (pathValue.startsWith("http")) return pathValue
      const fileName = pathValue.split(/[/\\]/).pop()
      return `${API_BASE}/${basePath}/${fileName}`
    }

    return {
      annotated: toUrl(annotatedPath, "outputs"),
      threeD: toUrl(threeDPath, "outputs"),
      original: toUrl(originalPath, "uploads")
    }
  }, [
    state?.lastResult?.annotated_path,
    state?.lastResult?.three_d_path,
    state?.lastResult?.file_path,
    state?.lastResult?.frame_path
  ])

  useEffect(() => {
    const uploadId = state?.lastResult?.upload_id
    if (!uploadId) {
      setDetections(null)
      setStatus("idle")
      return
    }

    let isMounted = true
    setStatus("loading")
    getDetections(uploadId)
      .then((res) => {
        if (!isMounted) return
        setDetections(res.detections || [])
        setStatus("ready")
      })
      .catch(() => {
        if (!isMounted) return
        setDetections([])
        setStatus("error")
      })

    return () => {
      isMounted = false
    }
  }, [state?.lastResult?.upload_id])

  useEffect(() => {
    if (state?.lastResult) setViewMode("annotated")
  }, [state?.lastResult])

  useEffect(() => {
    if (state?.lastResult) setSplitView(false)
  }, [state?.lastResult])

  useEffect(() => {
    if (!API_BASE) {
      setHealthStatus("unknown")
      return
    }

    const controller = new AbortController()
    fetch(`${API_BASE}/health`, { signal: controller.signal })
      .then((res) => {
        setHealthStatus(res.ok ? "online" : "offline")
      })
      .catch(() => {
        setHealthStatus("offline")
      })

    return () => controller.abort()
  }, [])

  const hasResult = Boolean(state?.lastResult)
  const hasOriginal = Boolean(outputLinks.original)
  const hasAnnotated = Boolean(outputLinks.annotated)
  const hasThreeD = Boolean(outputLinks.threeD)
  const effectiveMode = hasOriginal && hasAnnotated ? viewMode : hasAnnotated ? "annotated" : "original"
  const primarySrc = effectiveMode === "original" ? outputLinks.original : outputLinks.annotated
  const primaryLabel = effectiveMode === "original" ? "Original" : "Annotated"
  const healthLabel =
    healthStatus === "online" ? "API Online" : healthStatus === "offline" ? "API Offline" : "API Unknown"

  return (
    <aside className="info-rail">
      {hasResult ? (
        <>
          <div className="info-rail-head">
            <div className="info-kicker">Output Ready</div>
            <div className="info-title">Detection Results</div>
            <div className="info-sub">
              Upload ID: {state.lastResult.upload_id}
            </div>
          </div>

          <div className="info-cards">
            <div className="info-card">
              <div className="info-card-title">File</div>
              <div className="info-card-text">
                {state.lastResult.fileName || "Uploaded file"}
              </div>
              <div className="info-card-glow" aria-hidden="true" />
            </div>
            <div className="info-card">
              <div className="info-card-title">Detections</div>
              <div className="info-card-text">
                {status === "loading" && "Fetching results..."}
                {status !== "loading" && `${(detections || []).length} found`}
              </div>
              <div className="info-card-glow" aria-hidden="true" />
            </div>
            <div className="info-card">
              <div className="info-card-title">Counts</div>
              <div className="info-card-text">
                Boulders: {state.lastResult.boulders ?? 0} / Craters:{" "}
                {state.lastResult.craters ?? 0}
              </div>
              <div className="info-card-glow" aria-hidden="true" />
            </div>
          </div>

          {(outputLinks.annotated || outputLinks.threeD || outputLinks.original) && (
            <div className="result-panel">
              <div className="result-title">Outputs</div>
              {hasOriginal && hasAnnotated && (
                <div className="result-controls">
                  <div className="result-toggle" role="tablist" aria-label="Output view">
                    <button
                      type="button"
                      className={`toggle-btn ${effectiveMode === "original" ? "is-active" : ""}`}
                      onClick={() => setViewMode("original")}
                      aria-pressed={effectiveMode === "original"}
                    >
                      Original
                    </button>
                    <button
                      type="button"
                      className={`toggle-btn ${effectiveMode === "annotated" ? "is-active" : ""}`}
                      onClick={() => setViewMode("annotated")}
                      aria-pressed={effectiveMode === "annotated"}
                    >
                      Annotated
                    </button>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={splitView}
                      onChange={(e) => setSplitView(e.target.checked)}
                    />
                    <span className="toggle-track" aria-hidden="true" />
                    <span className="toggle-label">Split View</span>
                  </label>
                </div>
              )}
              <div className="result-grid">
                {splitView && hasOriginal && hasAnnotated ? (
                  <>
                    <a
                      className="result-item"
                      href={outputLinks.original}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <img
                        className="result-image"
                        src={outputLinks.original}
                        alt="Original output"
                      />
                      <div className="result-label">Original</div>
                    </a>
                    <a
                      className="result-item"
                      href={outputLinks.annotated}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <img
                        className="result-image"
                        src={outputLinks.annotated}
                        alt="Annotated output"
                      />
                      <div className="result-label">Annotated</div>
                    </a>
                  </>
                ) : (
                  primarySrc && (
                  <a
                    className="result-item"
                    href={primarySrc}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      className="result-image"
                      src={primarySrc}
                      alt={`${primaryLabel} output`}
                    />
                    <div className="result-label">{primaryLabel}</div>
                  </a>
                ))}
                {hasThreeD && (
                  <a
                    className="result-item"
                    href={outputLinks.threeD}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      className="result-image"
                      src={outputLinks.threeD}
                      alt="3D depth"
                    />
                    <div className="result-label">3D Depth</div>
                  </a>
                )}
              </div>
            </div>
          )}

          <div className="info-badge">
            <div className="pulse-dot" />
            <div>
              <div className="info-badge-title">Status</div>
              <div className="info-badge-text">
                {status === "loading" && `Processing • ${healthLabel}`}
                {status === "ready" && `Complete • ${healthLabel}`}
                {status === "error" && `Fetch failed • ${healthLabel}`}
                {status === "idle" && `Idle • ${healthLabel}`}
              </div>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="info-rail-head">
            <div className="info-kicker">Problem Focus</div>
            <div className="info-title">Lunar Hazard Intelligence</div>
            <div className="info-sub">
              Real-time detection + geospatial context for safer exploration.
            </div>
          </div>

          <div className="info-cards">
            {cards.map((c) => (
              <div key={c.title} className="info-card">
                <div className="info-card-title">{c.title}</div>
                <div className="info-card-text">{c.text}</div>
                <div className="info-card-glow" aria-hidden="true" />
              </div>
            ))}
          </div>

          {(outputLinks.annotated || outputLinks.threeD || outputLinks.original) && (
            <div className="result-panel">
              <div className="result-title">Outputs</div>
              {hasOriginal && hasAnnotated && (
                <div className="result-controls">
                  <div className="result-toggle" role="tablist" aria-label="Output view">
                    <button
                      type="button"
                      className={`toggle-btn ${effectiveMode === "original" ? "is-active" : ""}`}
                      onClick={() => setViewMode("original")}
                      aria-pressed={effectiveMode === "original"}
                    >
                      Original
                    </button>
                    <button
                      type="button"
                      className={`toggle-btn ${effectiveMode === "annotated" ? "is-active" : ""}`}
                      onClick={() => setViewMode("annotated")}
                      aria-pressed={effectiveMode === "annotated"}
                    >
                      Annotated
                    </button>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={splitView}
                      onChange={(e) => setSplitView(e.target.checked)}
                    />
                    <span className="toggle-track" aria-hidden="true" />
                    <span className="toggle-label">Split View</span>
                  </label>
                </div>
              )}
              <div className="result-grid">
                {splitView && hasOriginal && hasAnnotated ? (
                  <>
                    <a
                      className="result-item"
                      href={outputLinks.original}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <img
                        className="result-image"
                        src={outputLinks.original}
                        alt="Original output"
                      />
                      <div className="result-label">Original</div>
                    </a>
                    <a
                      className="result-item"
                      href={outputLinks.annotated}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <img
                        className="result-image"
                        src={outputLinks.annotated}
                        alt="Annotated output"
                      />
                      <div className="result-label">Annotated</div>
                    </a>
                  </>
                ) : (
                  primarySrc && (
                  <a
                    className="result-item"
                    href={primarySrc}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      className="result-image"
                      src={primarySrc}
                      alt={`${primaryLabel} output`}
                    />
                    <div className="result-label">{primaryLabel}</div>
                  </a>
                ))}
                {hasThreeD && (
                  <a
                    className="result-item"
                    href={outputLinks.threeD}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      className="result-image"
                      src={outputLinks.threeD}
                      alt="3D depth"
                    />
                    <div className="result-label">3D Depth</div>
                  </a>
                )}
              </div>
            </div>
          )}

          <div className="info-badge">
            <div className="pulse-dot" />
            <div>
              <div className="info-badge-title">System Status</div>
              <div className="info-badge-text">{healthLabel}</div>
            </div>
          </div>
        </>
      )}
    </aside>
  )
}
