import React from "react"
import DragDrop from "./DragDrop"
import Button from "../ui/Button"

export default function UploadBox() {
  return (
    <div style={{ marginBottom: 16 }}>
      <h3 style={{ margin: "0 0 8px" }}>Upload Crater Image</h3>
      <DragDrop />
      <div style={{ marginTop: 12 }}>
        <Button label="Analyze" />
      </div>
    </div>
  )
}

