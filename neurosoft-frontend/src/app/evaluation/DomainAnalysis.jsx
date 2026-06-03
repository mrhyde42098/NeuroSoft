/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/DomainAnalysis.jsx — Agrupacion por dominio cognitivo
 * Radar + barras con Z promedio y % bajo el promedio por dominio.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { _useMemo } from "react";
import {
  ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Tooltip,
} from "recharts";
import { Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* Custom tooltip for radar chart */
function RadarTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const z = payload[0].value;
  let interp = "Promedio";
  if (z <= -2) interp = "Muy Bajo";
  else if (z <= -1) interp = "Bajo";
  else if (z >= 2) interp = "Muy Superior";
  else if (z >= 1) interp = "Superior";
  return (
    <div className="bg-white border rounded-xl shadow-lg p-3 text-xs max-w-[200px]">
      <p className="font-bold text-gray-800 mb-1">{label}</p>
      <p className="font-mono" style={{ color: TEAL }}>Z = {z > 0 ? "+" : ""}{z.toFixed(2)}</p>
      <p className="text-[10px] text-gray-500 mt-1">{interp}</p>
    </div>
  );
}

/* ══════════════ EVAL RESULTS ══════════════ */
/* ─── Análisis por dominios cognitivos (F.2) ───
 * Agrupa subtests por dominio, calcula promedio Z, % bajo el promedio, etc.
 * Muestra radar + lista con barritas. */
export default function DomainAnalysis({subtests}){
  if(!subtests||subtests.length===0)return null;
  const DOMAIN_CANON=[
    ["Atención","atenci"],
    ["Memoria","memoria"],
    ["Lenguaje","lengu"],
    ["Funciones Ejecutivas","ejec"],
    ["Visoespacial","visoesp|visoconstr|viso-"],
    ["Velocidad de Procesamiento","velocidad|proces"],
    ["Habilidades Académicas","académ|academ"],
    ["Emocional","emoc|afect"],
  ];
  const canonFor=(s)=>{
    const t=(s||"").toLowerCase();
    for(const[nom,pat]of DOMAIN_CANON){if(new RegExp(pat).test(t))return nom}
    return s||"Otros";
  };
  const groups={};
  subtests.forEach(r=>{
    const d=canonFor(r.dominio_cognitivo);
    if(!groups[d])groups[d]={nombre:d,tests:[],z_sum:0,z_n:0,bajo:0,alto:0};
    groups[d].tests.push(r);
    if(Number.isFinite(r.z_equivalente)){
      groups[d].z_sum+=r.z_equivalente;groups[d].z_n+=1;
      if(r.z_equivalente<=-1)groups[d].bajo+=1;
      if(r.z_equivalente>=1) groups[d].alto+=1;
    }
  });
  const rows=Object.values(groups).map(g=>({
    ...g,
    z_prom: g.z_n>0?+(g.z_sum/g.z_n).toFixed(2):null,
    pct_bajo: g.z_n>0?Math.round((g.bajo/g.z_n)*100):0,
  })).sort((a,b)=>(a.z_prom??9)-(b.z_prom??9));
  if(rows.length<2)return null;
  const radarData=rows.filter(r=>r.z_prom!==null).map(r=>({dominio:r.nombre,z:+(r.z_prom).toFixed(2)}));

  /* Color scale for Z scores */
  const zColor = (z) => {
    if (z === null || z === undefined) return "#94A3B8";
    if (z <= -2) return "#7F1D1D";   // very low - dark red
    if (z <= -1) return "#DC2626";   // low - red
    if (z < 0)   return "#D97706";   // below avg - amber
    if (z < 1)   return "#0D9488";   // avg - teal
    if (z < 2)   return "#059669";   // high - green
    return "#047857";                // very high - emerald
  };

  /* Animated bar width calculation */
  const barWidth = (z) => {
    const pct = Math.min(100, Math.max(0, ((z ?? 0) + 3) / 6 * 100));
    return `${pct.toFixed(1)}%`;
  };

  return(<Card className="p-6 space-y-4">
    <h3 className="text-sm font-extrabold flex items-center gap-2"><I name="bubble_chart" style={{color:TEAL}}/>Análisis por Dominios Cognitivos</h3>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Radar */}
      {radarData.length>=3&&<div className="p-3 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radarData} outerRadius={100}>
            <PolarGrid stroke="#e5e7eb" strokeDasharray="3 3"/>
            <PolarAngleAxis dataKey="dominio" tick={{fontSize:10,fill:"#374151",fontWeight:600}}/>
            <PolarRadiusAxis angle={90} domain={[-3,3]} tick={{fontSize:9}} tickCount={7}/>
            <Radar dataKey="z" stroke={TEAL} fill={TEAL} fillOpacity={0.35} name="Z promedio"
                   isAnimationActive={true} animationDuration={900} animationEasing="ease-out"/>
            <Tooltip content={<RadarTooltip/>}/>
          </RadarChart>
        </ResponsiveContainer>
      </div>}
      {/* Lista */}
      <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
        {rows.map((g,idx)=>{
          const c = zColor(g.z_prom);
          const delay = idx * 80; /* staggered animation */
          return(
            <div key={g.nombre}
                 className="p-3 rounded-xl border transition-all duration-300 hover:shadow-md"
                 style={{borderColor:"var(--ns-card-b)", animationDelay:`${delay}ms`}}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold">{g.nombre}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full"
                      style={{color:c, background:`${c}15`}}>
                  Z̄ = {g.z_prom===null?"—":(g.z_prom>0?"+":"")+g.z_prom.toFixed(2)}
                </span>
              </div>
              <div className="h-2.5 rounded-full overflow-hidden mb-1.5" style={{background:"var(--ns-subtle)"}}>{/* §dark-mode-fix */}
                <div className="h-full rounded-full transition-all duration-700 ease-out"
                     style={{width:barWidth(g.z_prom), background:c}}/>
              </div>
              <div className="flex justify-between text-[10px]" style={{color:"var(--ns-muted)"}}>
                <span>{g.tests.length} subtest{g.tests.length!==1?"s":""}</span>
                {g.bajo>0&&<span className="text-red-600 font-semibold">{g.bajo} bajo{g.bajo!==1?"s":""} ({g.pct_bajo}%)</span>}
                {g.alto>0&&<span className="text-emerald-600 font-semibold">{g.alto} alto{g.alto!==1?"s":""}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
    <p className="text-[9px] italic" style={{color:"var(--ns-muted)"}}>
      Agrupación automática por dominio cognitivo. Z promedio por dominio y % de subtests bajo el promedio (≤ -1 SD).
      Colores: <span style={{color:"#DC2626"}}>rojo</span> = bajo, <span style={{color:"#D97706"}}>naranja</span> = límite, <span style={{color:"#0D9488"}}>teal</span> = promedio, <span style={{color:"#059669"}}>verde</span> = superior.
    </p>
  </Card>);
}
