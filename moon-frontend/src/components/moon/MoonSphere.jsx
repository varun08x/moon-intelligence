import React, { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import { useGLTF } from "@react-three/drei"

export default function MoonSphere({ isInteracting }) {
  const groupRef = useRef(null)
  const gltf = useGLTF("/models/moon.glb")

  useFrame((_, delta) => {
    if (groupRef.current && !isInteracting) {
      groupRef.current.rotation.y += delta * 0.20
    }
  })

  return (
    <group ref={groupRef}>
      <primitive object={gltf.scene} scale={1} />
    </group>
  )
}

useGLTF.preload("/models/moon.glb")
