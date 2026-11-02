import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { authFetch } from "../services/auth"

const API = "http://127.0.0.1:8010"

export default function Setup(){

  const [packs,setPacks]=useState([])
  const [loading,setLoading]=useState(false)

  /* ======================
     CARGAR PACKS REALES
  ====================== */

  useEffect(()=>{

    authFetch(`${API}/workflows/packs`)
      .then(res => res.json())
      .then(setPacks)
      .catch(()=>{
        setPacks([
          { slug:"hotel", name:"Hotel Edition", color:"#5b8cff" },
          { slug:"bar", name:"Bar Edition", color:"#7c5cff" },
          { slug:"office", name:"Office Edition", color:"#00b894" }
        ])
      })

  },[])

  /* ======================
     INSTALAR
  ====================== */

  const choose = async (slug)=>{

    try{
      setLoading(true)

      await authFetch(`${API}/setup/install`,{
        method:"POST",
        headers:{
          "Content-Type":"application/json"
        },
        body: JSON.stringify({ slug })
      })

      window.location.reload()

    }catch(e){
      console.error(e)
      alert("Error instalando pack")
    }finally{
      setLoading(false)
    }
  }

  /* ====================== */

  return(
    <div style={styles.page}>

      {/* Glow fondo */}
      <div style={styles.glow}/>

      <motion.div
        initial={{opacity:0, scale:.95}}
        animate={{opacity:1, scale:1}}
        transition={{duration:.4}}
        style={styles.card}
      >

        <h1 style={styles.title}>Nexus</h1>
        <p style={styles.subtitle}>
          Elegí la edición para comenzar
        </p>

        <div style={styles.grid}>
          {packs.map(p=>(
            <button
              key={p.slug}
              disabled={loading}
              onClick={()=>choose(p.slug)}
              style={{
                ...styles.packBtn,
                background:p.color
              }}
            >
              ⚡ {p.name}
            </button>
          ))}
        </div>

        {loading && (
          <div style={styles.loading}>
            Instalando pack...
          </div>
        )}

      </motion.div>
    </div>
  )
}

/* ======================
   STYLES
====================== */

const styles={

  page:{
    height:"100vh",
    background:"#0f1115",
    display:"flex",
    alignItems:"center",
    justifyContent:"center",
    fontFamily:"sans-serif",
    color:"white",
    position:"relative",
    overflow:"hidden"
  },

  glow:{
    position:"absolute",
    width:600,
    height:600,
    borderRadius:"50%",
    background:"radial-gradient(circle, rgba(124,92,255,.35), transparent 60%)",
    filter:"blur(80px)"
  },

  card:{
    background:"rgba(255,255,255,.06)",
    backdropFilter:"blur(20px)",
    padding:"60px 70px",
    borderRadius:26,
    border:"1px solid rgba(255,255,255,.08)",
    display:"flex",
    flexDirection:"column",
    gap:24,
    alignItems:"center",
    zIndex:2
  },

  title:{
    fontSize:42,
    fontWeight:700,
    margin:0
  },

  subtitle:{
    opacity:.6,
    margin:0
  },

  grid:{
    display:"flex",
    gap:14,
    flexWrap:"wrap",
    justifyContent:"center"
  },

  packBtn:{
    border:"none",
    padding:"14px 22px",
    borderRadius:14,
    fontSize:15,
    fontWeight:600,
    color:"white",
    cursor:"pointer",
    transition:"all .2s",
    minWidth:160
  },

  loading:{
    fontSize:13,
    opacity:.7
  }
}