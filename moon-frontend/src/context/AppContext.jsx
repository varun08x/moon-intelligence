import React, { createContext, useMemo, useState } from "react"

export const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [state, setState] = useState({ lastResult: null })
  const value = useMemo(() => ({ state, setState }), [state])
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}
