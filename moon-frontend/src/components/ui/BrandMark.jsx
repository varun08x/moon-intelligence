import React from "react"

export default function BrandMark() {
  return (
    <div className="brand-mark">
      <div className="brand-icon" aria-hidden="true">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="14" cy="14" r="12.5" stroke="#E7EDF7" strokeWidth="2" />
          <path d="M18.5 6.5C15.2 8.2 13.2 11.8 13.2 15.8C13.2 19.2 14.6 22.2 16.8 24.3" stroke="#A7FF83" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
      <div className="brand-text">
        <div className="brand-name">LUNAR FORGE</div>
        <div className="brand-tag">Moon Intelligence</div>
      </div>
    </div>
  )
}
