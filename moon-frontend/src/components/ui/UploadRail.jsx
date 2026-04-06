import React, { useContext, useRef, useState } from "react"
import { detectImage } from "../../services/detectionService"
import { AppContext } from "../../context/AppContext"

export default function UploadRail() {
  const inputRef = useRef(null)
  const { setState } = useContext(AppContext)
  const [file, setFile] = useState(null)
  const [fileName, setFileName] = useState("")
  const [status, setStatus] = useState("idle")
  const [message, setMessage] = useState("")

  const onPick = () => inputRef.current?.click()
  const onChange = (e) => {
    const file = e.target.files?.[0]
    setFile(file || null)
    setFileName(file ? file.name : "")
    setMessage("")
    setStatus("idle")
  }

  const onAnalyze = async () => {
    if (!file) {
      setStatus("error")
      setMessage("Please select a file first.")
      return
    }

    try {
      setStatus("loading")
      setMessage("Uploading...")
      const result = await detectImage(file)
      setState((prev) => ({ ...prev, lastResult: { ...result, fileName } }))
      setStatus("success")
      setMessage(`Uploaded. ID: ${result.upload_id}`)
    } catch (err) {
      setStatus("error")
      setMessage("Upload failed. Check backend is running.")
    }
  }

  return (
    <aside className="upload-rail">
      <div className="upload-head">
        <div className="upload-kicker">Submit Data</div>
        <div className="upload-title">Upload Image or Video</div>
        <div className="upload-sub">
          Add lunar surface footage for AI analysis.
        </div>
      </div>

      <div className="upload-drop" onClick={onPick} role="button" tabIndex={0}>
        <div className="upload-icon">+</div>
        <div className="upload-text">Click to add photo or video</div>
        <div className="upload-hint">JPG, PNG, MP4, MOV</div>
        <input
          ref={inputRef}
          className="upload-input"
          type="file"
          accept="image/*,video/*"
          onChange={onChange}
        />
      </div>

      {fileName ? (
        <div className="upload-file">Selected: {fileName}</div>
      ) : (
        <div className="upload-file upload-empty">No file selected</div>
      )}

      {message ? (
        <div className={`upload-file ${status === "error" ? "upload-empty" : ""}`}>
          {message}
        </div>
      ) : null}

      <button className="upload-cta" type="button" onClick={onAnalyze}>
        {status === "loading" ? "Uploading..." : "Analyze Now"}
      </button>
    </aside>
  )
}
