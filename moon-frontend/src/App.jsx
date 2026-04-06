import React from "react"
import "./styles/globals.css"
import MoonCanvas from "./components/moon/MoonCanvas"
import BrandMark from "./components/ui/BrandMark"
import TopNav from "./components/ui/TopNav"
import InfoRail from "./components/ui/InfoRail"
import UploadRail from "./components/ui/UploadRail"

export default function App() {
  return (
    <div className="app-shell">
      <div className="moon-bg">
        <MoonCanvas />
      </div>
      <header className="top-bar">
        <BrandMark />
        <TopNav />
      </header>
      <UploadRail />
      <InfoRail />
    </div>
  )
}
