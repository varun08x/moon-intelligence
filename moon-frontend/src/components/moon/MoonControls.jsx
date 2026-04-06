import React from "react"
import { OrbitControls } from "@react-three/drei"

export default function MoonControls({ onStart, onEnd }) {
  return (
    <OrbitControls
      enableZoom={false}
      enablePan={false}
      enableDamping={true}
      dampingFactor={0.08}
      rotateSpeed={0.55}
      minDistance={3}
      maxDistance={3}
      minPolarAngle={0}
      maxPolarAngle={Math.PI}
      onStart={onStart}
      onEnd={onEnd}
    />
  )
}
