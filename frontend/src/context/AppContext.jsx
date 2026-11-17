import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AppContext = createContext(null);

const defaultProcesses = [
  { pid: "P1", arrivalTime: 0, burstTime: 7, priority: 2 },
  { pid: "P2", arrivalTime: 2, burstTime: 4, priority: 1 },
  { pid: "P3", arrivalTime: 4, burstTime: 1, priority: 3 }
];

export function AppProvider({ children }) {
  const [processes, setProcesses] = useState(() => {
    try { return JSON.parse(localStorage.getItem("csv-processes")) || defaultProcesses; }
    catch { return defaultProcesses; }
  });
  const [latestSimulation, setLatestSimulation] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem("csv-latest-simulation")) || null; }
    catch { return null; }
  });
  const [theme, setTheme] = useState(() => localStorage.getItem("csv-theme") || "dark");

  useEffect(() => {
    localStorage.setItem("csv-processes", JSON.stringify(processes));
  }, [processes]);
  useEffect(() => {
    if (latestSimulation) sessionStorage.setItem("csv-latest-simulation", JSON.stringify(latestSimulation));
    else sessionStorage.removeItem("csv-latest-simulation");
  }, [latestSimulation]);
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("csv-theme", theme);
  }, [theme]);

  const value = useMemo(() => ({
    processes, setProcesses, latestSimulation, setLatestSimulation, theme,
    toggleTheme: () => setTheme(t => t === "dark" ? "light" : "dark")
  }), [processes, latestSimulation, theme]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
export const useApp = () => useContext(AppContext);
