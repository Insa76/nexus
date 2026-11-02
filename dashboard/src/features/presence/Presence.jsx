import { useEffect, useRef } from "react"
import face from "../../assets/face-mask.png"
import { NexusState } from "../../nexusState"

export default function Presence() {

  const ref = useRef()
  const particlesRef = useRef([])
  const animationRef = useRef()
  const audioLevelRef = useRef(0)

  useEffect(() => {

    const canvas = ref.current
    const ctx = canvas.getContext("2d")

    /* =========================
       CANVAS SCALE SAFE
    ========================= */

    function resize() {
      const DPR = window.devicePixelRatio || 1

      canvas.width = window.innerWidth * DPR
      canvas.height = window.innerHeight * DPR

      canvas.style.width = "100vw"
      canvas.style.height = "100vh"

      ctx.setTransform(1,0,0,1,0,0)
      ctx.scale(DPR, DPR)
    }

    resize()
    window.addEventListener("resize", resize)

    /* =========================
       VARIABLES
    ========================= */

    const particles = particlesRef.current
    let mouse = { x: window.innerWidth/2, y: window.innerHeight/2 }
    let t = 0

    /* =========================
       AUDIO REACTIVE
    ========================= */

    navigator.mediaDevices?.getUserMedia({ audio: true })
      .then(stream => {

        const audioCtx = new AudioContext()
        const analyser = audioCtx.createAnalyser()
        const source = audioCtx.createMediaStreamSource(stream)

        analyser.fftSize = 256
        source.connect(analyser)

        const data = new Uint8Array(analyser.frequencyBinCount)

        function readAudio() {
          analyser.getByteFrequencyData(data)
          const avg = data.reduce((a,b)=>a+b,0) / data.length
          audioLevelRef.current = avg / 255
          requestAnimationFrame(readAudio)
        }

        readAudio()

      })
      .catch(() => {
        audioLevelRef.current = 0
      })

    /* =========================
       MOUSE TRACK
    ========================= */

    window.addEventListener("mousemove", e => {
      mouse.x = e.clientX
      mouse.y = e.clientY
    })

    /* =========================
       CARGAR MÁSCARA
    ========================= */

    const img = new Image()
    img.src = face

    img.onload = () => {

      particles.length = 0

      const off = document.createElement("canvas")
      const octx = off.getContext("2d")

      const size = 500
      off.width = size
      off.height = size

      octx.drawImage(img, 0, 0, size, size)
      const data = octx.getImageData(0, 0, size, size).data

      const gap = 4

      for (let y = 0; y < size; y += gap) {
        for (let x = 0; x < size; x += gap) {

          const i = (y * size + x) * 4

          if (data[i + 3] > 120) {

            particles.push({
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              tx: window.innerWidth/2 - size/2 + x,
              ty: window.innerHeight/2 - size/2 + y,
              vx: 0,
              vy: 0
            })
          }
        }
      }

      animate()
    }

    /* =========================
       COLOR DINÁMICO
    ========================= */

    function color() {
      switch (NexusState.mode) {
        case "listening": return "rgba(0,200,255,0.9)"
        case "thinking": return "rgba(255,170,0,0.95)"
        case "speaking": return "rgba(124,92,255,1)"
        case "error": return "rgba(255,50,80,0.9)"
        default: return "rgba(124,92,255,0.55)"
      }
    }

    /* =========================
       LOOP PRINCIPAL
    ========================= */

    function animate() {

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      t += 0.02
      const breathe = Math.sin(t) * 2

      ctx.shadowBlur = 24
      ctx.shadowColor = "#7c5cff"

      const mx = (mouse.x - window.innerWidth/2) * 0.03
      const my = (mouse.y - window.innerHeight/2) * 0.03

      for (const p of particles) {

        const dx = p.tx + mx - p.x
        const dy = p.ty + my - p.y

        p.vx += dx * 0.02
        p.vy += dy * 0.02

        const audioBoost = audioLevelRef.current * 8

        p.vx += (Math.random() - 0.5) * audioBoost
        p.vy += (Math.random() - 0.5) * audioBoost

        p.vx *= 0.86
        p.vy *= 0.86

        p.x += p.vx
        p.y += p.vy + breathe

        ctx.fillStyle = color()
        ctx.fillRect(p.x, p.y, 2, 2)
      }

      animationRef.current = requestAnimationFrame(animate)
    }

    /* =========================
       CLEANUP
    ========================= */

    return () => {
      cancelAnimationFrame(animationRef.current)
      window.removeEventListener("resize", resize)
    }

  }, [])

  return (
    <canvas
      ref={ref}
      style={{
        position: "fixed",
        inset: 0,
        pointerEvents: "none",
        zIndex: 0,
        opacity: 0.45,
        transition: "opacity .4s ease"
      }}
    />
  )
}