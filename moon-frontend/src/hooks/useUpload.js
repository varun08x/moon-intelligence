import { useState } from "react"

export default function useUpload() {
  const [file, setFile] = useState(null)
  return { file, setFile }
}
