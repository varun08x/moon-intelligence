import React from "react"

function latLonToVector3(lat, lon, radius = 1.05) {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)

  const x = -radius * Math.sin(phi) * Math.cos(theta)
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)

  return [x, y, z]
}

export default function MoonMarkers({ detections = [] }) {
  return (
    <>
      {detections.map((d, i) => {
        const [x, y, z] = latLonToVector3(d.lat, d.lon)
        const color = d.type === "landslide" ? "yellow" : "red"

        return (
          <mesh key={i} position={[x, y, z]}>
            <sphereGeometry args={[0.02, 16, 16]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.5} />
          </mesh>
        )
      })}
    </>
  )
}

