import React from "react"
import { Line } from "@react-three/drei"
import * as THREE from "three"

export default function MoonGrid() {
  const lines = []
  const radius = 1.01

  for (let lat = -80; lat <= 80; lat += 20) {
    const points = []
    for (let lon = 0; lon <= 360; lon += 5) {
      const phi = (90 - lat) * (Math.PI / 180)
      const theta = lon * (Math.PI / 180)
      const x = radius * Math.sin(phi) * Math.cos(theta)
      const y = radius * Math.cos(phi)
      const z = radius * Math.sin(phi) * Math.sin(theta)
      points.push(new THREE.Vector3(x, y, z))
    }
    lines.push(points)
  }

  return (
    <>
      {lines.map((points, i) => (
        <Line key={i} points={points} color="lime" lineWidth={1} />
      ))}
    </>
  )
}

