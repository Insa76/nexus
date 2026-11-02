import { useEffect, useState } from "react"
import axios from "axios"

import Login from "./pages/Login"
import Register from "./pages/Register"
import Dashboard from "./pages/Dashboard"
import Users from "./pages/Users"
import Setup from "./pages/Setup"




import Builder from "./pages/Builder";
import Wallboard from "./features/wallboard/Wallboard"
import AssistantMode from "./features/ai/AssistantMode"
import Navbar from "./components/Navbar"

const API = "http://127.0.0.1:8000"

// ✅ AXIOS CONFIG CON TOKEN
const api = axios.create({
  baseURL: API
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem("token")


  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default function App() {

  const [installed, setInstalled] = useState(true)
  const [kiosk, setKiosk] = useState(false)

  const [stats, setStats] = useState({})
  const [jobs, setJobs] = useState({})
  const [logs, setLogs] = useState([])
  const [plugins, setPlugins] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [market, setMarket] = useState([])

  // ======================
  // KIOSK MODE
  // ======================
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)

    if (params.get("kiosk")) {
      setKiosk(true)
      document.body.style.margin = "0"
      document.body.style.overflow = "hidden"
      document.body.style.cursor = "none"
    }
  }, [])

  // ======================
  // SETUP CHECK (SAFE)
  // ======================
  useEffect(() => {
    api.get("/setup")
      .then(r => setInstalled(r.data?.installed ?? true))
      .catch(() => setInstalled(true)) // fallback
  }, [])

  // ======================
  // DASHBOARD LOADER (SAFE MODE)
  // ======================
  const load = async () => {

    const token = localStorage.getItem("token")
     if (!token) return

    try {
      const safe = async (fn, fallback) => {
        try {
          const r = await fn()
          return r.data
        } catch {
          return fallback
        }
      }

      const [
        s,
        l,
        p,
        sug,
        j
      ] = await Promise.all([
        safe(() => api.get("/dashboard/stats"), {}),
        safe(() => api.get("/dashboard/logs"), { logs: [] }),
        safe(() => api.get("/dashboard/plugins"), { plugins: [] }),
        safe(() => api.get("/dashboard/suggestions"), { suggestions: [] }),
        safe(() => api.get("/jobs/"), {})
      ])

      setStats(s)
      setLogs(l.logs || [])
      setPlugins(p.plugins || [])
      setSuggestions(sug.suggestions || [])
      setJobs(j || {})

    } catch (e) {
      console.log("dashboard load fail", e)
    }
  }

  useEffect(() => {

  const start = () => {
    const token = localStorage.getItem("token")
    if (!token) return

    load()
    const i = setInterval(load, 5000)
    return () => clearInterval(i)
  }

  // pequeña espera para asegurar login
  setTimeout(start, 300)

}, [])

  // ======================
  // AUTH
  // ======================
  const token = localStorage.getItem("token")

  if (window.location.pathname === "/login") return <Login />
  if (window.location.pathname === "/register") return <Register />

  if (!token) {
    window.location.href = "/login"
    return null
  }

  if (window.location.pathname === "/assistant") return <AssistantMode />
  if (window.location.pathname === "/wallboard") return <Wallboard />
  if (window.location.pathname === "/users") return <Users />
  if (window.location.pathname === "/builder") return <Builder />

  if (!installed) return <Setup />

  return <Dashboard />
}