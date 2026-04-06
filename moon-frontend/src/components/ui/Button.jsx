import React from "react"
export default function Button({ label = "Action", onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: "#7dff7a",
        color: "#0b1020",
        border: "none",
        padding: "10px 14px",
        borderRadius: 10,
        fontWeight: 700,
        cursor: "pointer"
      }}
    >
      {label}
    </button>
  )
}

