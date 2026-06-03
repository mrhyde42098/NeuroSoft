/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/BlockStimulus.jsx — Estímulos SVG de Diseño con Cubos
 * Patrones A-E para WISC-IV / WAIS-III.
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";

/* ═══ Block Design Visual Stimuli — SVG patterns for WISC-IV / WAIS-III ═══ */
const BlockStimulus=({pattern,size=120})=>{const grid=pattern==="A"?[[0,1],[1,0]]:pattern==="B"?[[1,0],[0,1]]:pattern==="C"?[[0,0],[1,1]]:pattern==="D"?[[1,1,0,0],[1,1,0,0],[0,0,1,1],[0,0,1,1]]:pattern==="E"?[[1,0,0,1],[0,1,1,0],[0,1,1,0],[1,0,0,1]]:[[1,1],[1,1]];const n=grid.length;const cell=size/n;return<svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rounded-lg" style={{background:"#fff",border:"1px solid #ddd"}}>{grid.map((row,r)=>row.map((c,i)=>{const x=i*cell,y=r*cell;if(c===1)return<g key={`${r}-${i}`}><polygon points={`${x},${y} ${x+cell},${y} ${x+cell},${y+cell}`} fill="#e11d48"/><polygon points={`${x},${y} ${x+cell},${y+cell} ${x},${y+cell}`} fill="#fff"/><rect x={x} y={y} width={cell} height={cell} fill="none" stroke="#1e293b" strokeWidth="1"/></g>;return<rect key={`${r}-${i}`} x={x} y={y} width={cell} height={cell} fill={c===0?"#fff":"#e11d48"} stroke="#1e293b" strokeWidth="1"/>}))}</svg>};

export default BlockStimulus;
