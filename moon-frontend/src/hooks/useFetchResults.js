import { useState } from "react"

export default function useFetchResults() {
  const [results, setResults] = useState(null)
  return { results, setResults }
}
