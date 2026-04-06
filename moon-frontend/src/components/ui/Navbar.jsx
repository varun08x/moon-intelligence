import React from "react"
export default function Navbar() {
  return (
    <div style={{
      padding: "12px 16px",
      borderBottom: "1px solid #1b2547",
      background: "#0b1020"
    }}>
      <div style={{ fontWeight: 700, letterSpacing: "0.5px" }}>MOON • Frontend</div>
      <div style={{ color: "#8aa0c2", fontSize: 12 }}>3D Lunar Surface + AI Detection</div>
    </div>
  )
}

