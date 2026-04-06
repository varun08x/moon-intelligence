import React, { useState } from "react"
import { Canvas } from "@react-three/fiber"
import * as THREE from "three"
import MoonSphere from "./MoonSphere"
import MoonControls from "./MoonControls"
import MoonMarkers from "./MoonMarkers"

const sampleDetections = []

export default function MoonCanvas() {
  const [isInteracting, setIsInteracting] = useState(false)

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <Canvas
        camera={{ position: [0, 0, 3], fov: 35 }}
        gl={{
          antialias: true,
          alpha: true,
          outputColorSpace: THREE.SRGBColorSpace,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.35
        }}
        dpr={[1, 2]}
      >
        <color attach="background" args={["#000"]} />
        <ambientLight intensity={0.35} />
        <hemisphereLight intensity={0.25} color="#ffffff" groundColor="#0a0a0a" />
        <directionalLight position={[4, 2.5, 2]} intensity={2.6} color="#ffffff" />
        <directionalLight position={[-3, -1, -2]} intensity={0.6} color="#c9d6ff" />
        <pointLight position={[0, 3, 3]} intensity={0.35} />
        <MoonSphere isInteracting={isInteracting} />
        <MoonMarkers detections={sampleDetections} />
        <MoonControls
          onStart={() => setIsInteracting(true)}
          onEnd={() => setIsInteracting(false)}
        />
      </Canvas>
    </div>
  )
}
