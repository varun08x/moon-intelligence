import React from "react"

const items = [
  { label: "Explore", href: "#explore" },
  { label: "Features", href: "#features" },
  { label: "Models", href: "#models" },
  { label: "Docs", href: "#docs" },
  { label: "Contact", href: "#contact" }
]

export default function TopNav() {
  return (
    <nav className="top-nav">
      {items.map((item) => (
        <a key={item.label} href={item.href} className="top-nav-link">
          {item.label}
        </a>
      ))}
    </nav>
  )
}
