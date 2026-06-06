/* ═══════════════════════════════════════════════════════════════════════
 * src/data/stimuli.jsx — Estimulos visuales nativos (SVG) por subprueba
 * Aislado en .jsx porque contiene markup JSX inline.
 * ─────────────────────────────────────────────────────────────────────── */

import React from "react";
import { CubosPoster } from "./PatronesCubos.jsx";
import FCRODisplay from "./FCRODisplay.jsx";

export const NativeStimuli={
  NiWiscDC:()=><CubosPoster test="wisc"/>,
  AdWAISCC:()=><CubosPoster test="wais"/>,
  NiWiscMat:()=>(
    /* Matriz 3x3 con un ítem en blanco */
    <svg viewBox="0 0 220 220" className="w-full h-full"><g stroke="#1e293b" strokeWidth="1.5" fill="none">
      {[0,1,2].map(r=>[0,1,2].map(c=>{const x=10+c*70,y=10+r*70;const full=!(r===2&&c===2);if(!full)return<rect key={`${r}${c}`} x={x} y={y} width="60" height="60" fill="#fff" strokeDasharray="4 3"/>;
        return<g key={`${r}${c}`}><rect x={x} y={y} width="60" height="60" fill="#fff"/>
          {r===0&&<circle cx={x+30} cy={y+30} r={10+c*5} fill="#0D9488"/>}
          {r===1&&<rect x={x+15+c*3} y={y+15+c*3} width={30-c*6} height={30-c*6} fill="#1E293B"/>}
          {r===2&&c===0&&<polygon points={`${x+30},${y+10} ${x+50},${y+50} ${x+10},${y+50}`} fill="#ef4444"/>}
          {r===2&&c===1&&<polygon points={`${x+30},${y+10} ${x+50},${y+50} ${x+10},${y+50}`} fill="#f59e0b"/>}
        </g>;
      }))}
      <text x="175" y="195" fontSize="18" fontWeight="bold" fill="#64748b">?</text>
    </g></svg>
  ),
  NiTMTA:()=>(
    /* TMT-A: ejemplo genérico con 5 círculos numerados 1-5 */
    <svg viewBox="0 0 260 180" className="w-full h-full">
      {[{x:30,y:60,n:1},{x:90,y:30,n:2},{x:160,y:80,n:3},{x:220,y:40,n:4},{x:180,y:140,n:5}].map(p=>
        <g key={p.n}><circle cx={p.x} cy={p.y} r="18" fill="#fff" stroke="#0D9488" strokeWidth="2"/><text x={p.x} y={p.y+5} textAnchor="middle" fontSize="16" fontWeight="bold" fill="#0D9488">{p.n}</text></g>)}
      <text x="130" y="172" textAnchor="middle" fontSize="10" fill="#64748b">Ejemplo ilustrativo — no reemplaza el protocolo impreso</text>
    </svg>
  ),
  NiTMTB:()=>(
    /* TMT-B: alternancia 1-A-2-B-3 */
    <svg viewBox="0 0 260 180" className="w-full h-full">
      {[{x:30,y:60,l:"1"},{x:90,y:30,l:"A"},{x:160,y:80,l:"2"},{x:220,y:40,l:"B"},{x:180,y:140,l:"3"}].map((p,i)=>
        <g key={i}><circle cx={p.x} cy={p.y} r="18" fill="#fff" stroke={/^\d+$/.test(p.l)?"#0D9488":"#943700"} strokeWidth="2"/><text x={p.x} y={p.y+5} textAnchor="middle" fontSize="16" fontWeight="bold" fill={/^\d+$/.test(p.l)?"#0D9488":"#943700"}>{p.l}</text></g>)}
      <text x="130" y="172" textAnchor="middle" fontSize="10" fill="#64748b">Alternancia número-letra · ejemplo ilustrativo</text>
    </svg>
  ),
  NiFigHum:()=>(
    /* Figura humana — referencia para recordar criterios de evaluación */
    <svg viewBox="0 0 180 240" className="w-full h-full"><g stroke="#1e293b" strokeWidth="2" fill="none">
      <circle cx="90" cy="40" r="28" fill="#FDFBF7"/>
      <circle cx="82" cy="36" r="2" fill="#1e293b"/><circle cx="98" cy="36" r="2" fill="#1e293b"/>
      <path d="M80 48 Q90 54 100 48" fill="none"/>
      <path d="M90 68 L90 150"/>
      <path d="M90 85 L55 115 M90 85 L125 115"/>
      <path d="M90 150 L70 220 M90 150 L110 220"/>
      <text x="90" y="235" textAnchor="middle" fontSize="9" fill="#64748b">Referencia · evalúa según criterios Koppitz/Goodenough</text>
    </g></svg>
  ),
  NiFCROCop:()=><FCRODisplay/>,
  NiFCRORec:()=><FCRODisplay/>,
  AdFCRORec:()=><FCRODisplay/>,
  MMSE:()=>(
    /* Pentágonos del MMSE */
    <svg viewBox="0 0 220 140" className="w-full h-full"><g stroke="#1e293b" strokeWidth="2" fill="#fff">
      <polygon points="60,20 100,20 115,60 80,90 45,60"/>
      <polygon points="110,50 150,50 165,90 130,120 95,90"/>
      <text x="110" y="135" textAnchor="middle" fontSize="10" fill="#64748b">Ítem visuoconstructivo — pentágonos superpuestos</text>
    </g></svg>
  ),

  /* ═══ Claves WISC-IV / Clave de Números WAIS-III / SDMT ═══ */
  NiWiscCl:()=><DigitSymbolKey/>,
  AdSDWais:()=><DigitSymbolKey/>,
  SDMT:()=><DigitSymbolKey/>,

  /* ═══ Búsqueda de Símbolos WISC-IV ═══ */
  NiWiscBusSim:()=>(
    <svg viewBox="0 0 320 180" className="w-full h-full">
      <text x="10" y="14" fontSize="9" fill="#64748b">Indique si el símbolo objetivo aparece en el grupo</text>
      {[0,1,2].map(row=>{const y=30+row*45;return(<g key={row}>
        <rect x="10" y={y} width="40" height="36" fill="#fff" stroke="#1e293b" strokeWidth="1.5" rx="4"/>
        <text x="30" y={y+24} textAnchor="middle" fontSize="22" fontWeight="bold" fill={["#dc2626","#0D9488","#7c3aed"][row]}>{["★","◆","●"][row]}</text>
        <line x1="55" y1={y+18} x2="65" y2={y+18} stroke="#94a3b8" strokeWidth="1.5"/>
        {[0,1,2,3].map(col=>{const x=70+col*50;const sym=[["▲","★","●","◆"],["◆","■","◇","○"],["☆","●","★","▼"]][row][col];const isTarget=sym===["★","◆","●"][row];return(<g key={col}><rect x={x} y={y} width="40" height="36" fill="#fff" stroke="#1e293b" strokeWidth="1" rx="4"/><text x={x+20} y={y+24} textAnchor="middle" fontSize="20" fill={isTarget?"#0D9488":"#1e293b"}>{sym}</text></g>)})}
        <rect x="270" y={y} width="40" height="36" fill="#f1f5f9" stroke="#1e293b" strokeWidth="1" rx="4"/>
        <text x="290" y={y+22} textAnchor="middle" fontSize="11" fill="#64748b">SI / NO</text>
      </g>)})}
    </svg>
  ),

  /* ═══ Matrices WAIS-III ═══ */
  AdMatr:()=>(
    <svg viewBox="0 0 220 220" className="w-full h-full"><g stroke="#1e293b" strokeWidth="1.5" fill="none">
      {[0,1,2].map(r=>[0,1,2].map(c=>{const x=10+c*70,y=10+r*70;const isMissing=r===2&&c===2;if(isMissing)return<rect key={`${r}${c}`} x={x} y={y} width="60" height="60" fill="#fff" strokeDasharray="4 3"/>;
        return<g key={`${r}${c}`}><rect x={x} y={y} width="60" height="60" fill="#fff"/>
          <polygon points={`${x+30},${y+15} ${x+45},${y+30} ${x+30},${y+45} ${x+15},${y+30}`} fill={["#0D9488","#1E293B","#dc2626"][c]} transform={`rotate(${r*30} ${x+30} ${y+30})`}/>
        </g>;
      }))}
      <text x="175" y="195" fontSize="18" fontWeight="bold" fill="#64748b">?</text>
    </g></svg>
  ),

  /* ═══ Figuras Incompletas WISC-IV / WAIS-III ═══ */
  NiWisFigInc:()=><FiguresIncompleteGrid/>,
  AdWAISFI:()=><FiguresIncompleteGrid/>,

  /* ═══ Conceptos con Dibujos WISC-IV ═══ */
  NiWiscConD:()=>(
    <svg viewBox="0 0 320 180" className="w-full h-full">
      <text x="10" y="14" fontSize="9" fill="#64748b">Elija un dibujo de cada fila que comparta categoría</text>
      <g transform="translate(10, 30)">
        <rect x="0" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="40" y="40" textAnchor="middle" fontSize="32">🐶</text>
        <rect x="100" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="140" y="40" textAnchor="middle" fontSize="32">🚗</text>
        <rect x="200" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="240" y="40" textAnchor="middle" fontSize="32">🐱</text>
      </g>
      <g transform="translate(10, 105)">
        <rect x="0" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="40" y="40" textAnchor="middle" fontSize="32">🍎</text>
        <rect x="100" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="140" y="40" textAnchor="middle" fontSize="32">🐦</text>
        <rect x="200" y="0" width="80" height="60" fill="#fff" stroke="#1e293b"/>
        <text x="240" y="40" textAnchor="middle" fontSize="32">⚽</text>
      </g>
    </svg>
  ),

  /* ═══ Reconocimiento Expresiones Faciales (Ekman 6 básicas) ═══ */
  NiRecEmo:()=><EkmanFaces/>,

  /* ═══ Stroop infantil/adulto ═══ */
  NiSt_Edades:()=><StroopReference/>,
  StroopAM:()=><StroopReference/>,
  StroopAJ:()=><StroopReference/>,

  /* ═══ Cancelación de Dibujos ENI-2 / CARAS-R ═══ */
  NiENICDib:()=><CancellationGrid target="🌟"/>,
  NiTestPC_R:()=><FaceDiscriminationRow/>,

  /* ═══ Palabras en Contexto WISC-IV ═══ */
  NiWisPalCon:()=><WordContextGrid/>,

  /* ═══ Integración de Objetos (estilo rompecabezas) ═══ */
  NiIntObj:()=><ObjectIntegration/>,

  /* ═══ Denominación 48 ítems (galería de dibujos propios) ═══ */
  Denom48:()=><Denomination48/>,
};

/* ═══════════════════════════════════════════════════════════════════════
 * Componentes auxiliares
 * ═══════════════════════════════════════════════════════════════════════ */

const SYMBOLS = ["─","▲","○","◆","✕","☐","▼","△","■"];

function DigitSymbolKey() {
  return (
    <svg viewBox="0 0 360 130" className="w-full h-full">
      <text x="10" y="14" fontSize="9" fill="#64748b">Plantilla pareo dígito↔símbolo (clave de referencia)</text>
      <g transform="translate(10, 24)">
        {[1,2,3,4,5,6,7,8,9].map((d,i)=>(
          <g key={d}><rect x={i*38} y="0" width="36" height="28" fill="#0D9488" rx="4"/>
            <text x={i*38+18} y="20" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#fff">{d}</text></g>
        ))}
      </g>
      <g transform="translate(10, 56)">
        {SYMBOLS.map((s,i)=>(
          <g key={i}><rect x={i*38} y="0" width="36" height="28" fill="#fff" stroke="#1e293b" rx="4"/>
            <text x={i*38+18} y="22" textAnchor="middle" fontSize="20" fill="#1e293b">{s}</text></g>
        ))}
      </g>
      <text x="10" y="96" fontSize="9" fill="#64748b">Ítems de práctica:</text>
      <g transform="translate(10, 100)">
        {[3,7,1,5,9].map((d,i)=>(
          <g key={i}><rect x={i*60} y="0" width="28" height="22" fill="#fff" stroke="#0D9488" strokeWidth="1.5" rx="3"/>
            <text x={i*60+14} y="17" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#0D9488">{d}</text>
            <rect x={i*60+30} y="0" width="28" height="22" fill="#fff" stroke="#94a3b8" strokeDasharray="3 2" rx="3"/></g>
        ))}
      </g>
    </svg>
  );
}

function FiguresIncompleteGrid() {
  return (
    <svg viewBox="0 0 320 180" className="w-full h-full">
      <text x="10" y="14" fontSize="9" fill="#64748b">¿Qué detalle importante falta en cada dibujo?</text>
      <g transform="translate(10, 30)">
        <rect x="10" y="20" width="50" height="8" fill="#a16207"/>
        <rect x="14" y="28" width="6" height="34" fill="#a16207"/>
        <rect x="50" y="28" width="6" height="34" fill="#a16207"/>
        <rect x="10" y="0" width="50" height="22" fill="#fbbf24" stroke="#a16207"/>
        <text x="35" y="80" textAnchor="middle" fontSize="9" fill="#64748b">Silla</text>
      </g>
      <g transform="translate(95, 30)">
        <circle cx="35" cy="35" r="28" fill="#fde68a" stroke="#a16207"/>
        <circle cx="45" cy="28" r="3" fill="#1e293b"/>
        <path d="M25 42 Q35 50 45 42" fill="none" stroke="#1e293b" strokeWidth="2"/>
        <text x="35" y="80" textAnchor="middle" fontSize="9" fill="#64748b">Cara</text>
      </g>
      <g transform="translate(180, 30)">
        <circle cx="35" cy="35" r="28" fill="#fff" stroke="#1e293b"/>
        {[0,3,6,9].map(h=>(
          <text key={h} x={35+22*Math.sin(h*Math.PI/2)} y={37-22*Math.cos(h*Math.PI/2)} textAnchor="middle" fontSize="8" fill="#1e293b">{h===0?12:h}</text>
        ))}
        <line x1="35" y1="35" x2="35" y2="18" stroke="#1e293b" strokeWidth="2"/>
        <text x="35" y="80" textAnchor="middle" fontSize="9" fill="#64748b">Reloj</text>
      </g>
      <g transform="translate(265, 30)">
        <circle cx="20" cy="20" r="10" fill="none" stroke="#1e293b" strokeWidth="2"/>
        <circle cx="40" cy="20" r="10" fill="none" stroke="#1e293b" strokeWidth="2"/>
        <line x1="20" y1="30" x2="40" y2="60" stroke="#1e293b" strokeWidth="2"/>
        <line x1="40" y1="30" x2="20" y2="60" stroke="#1e293b" strokeWidth="2"/>
        <text x="30" y="80" textAnchor="middle" fontSize="9" fill="#64748b">Tijera</text>
      </g>
      <text x="160" y="170" textAnchor="middle" fontSize="8" fill="#64748b" fontStyle="italic">Apoyo visual ilustrativo · no sustituye el cuadernillo</text>
    </svg>
  );
}

function EkmanFaces() {
  const emotions = [
    { label: "Alegría", color: "#10b981", smile: "happy" },
    { label: "Tristeza", color: "#3b82f6", smile: "sad" },
    { label: "Ira", color: "#dc2626", smile: "angry" },
    { label: "Miedo", color: "#f59e0b", smile: "fear" },
    { label: "Sorpresa", color: "#8b5cf6", smile: "surprise" },
    { label: "Asco", color: "#84cc16", smile: "disgust" },
  ];
  return (
    <svg viewBox="0 0 360 180" className="w-full h-full">
      <text x="180" y="14" textAnchor="middle" fontSize="9" fill="#64748b">Reconocimiento de expresiones faciales · 6 emociones básicas (Ekman)</text>
      {emotions.map((e,i)=>{
        const col=i%3, row=Math.floor(i/3);
        const cx=60+col*120, cy=50+row*70;
        return (
          <g key={i}>
            <circle cx={cx} cy={cy} r="26" fill="#fde68a" stroke={e.color} strokeWidth="2"/>
            {e.smile==="surprise"
              ? <><circle cx={cx-9} cy={cy-6} r="4" fill="#1e293b"/><circle cx={cx+9} cy={cy-6} r="4" fill="#1e293b"/></>
              : e.smile==="angry"
                ? <><line x1={cx-14} y1={cy-10} x2={cx-4} y2={cy-6} stroke="#1e293b" strokeWidth="2"/><line x1={cx+14} y1={cy-10} x2={cx+4} y2={cy-6} stroke="#1e293b" strokeWidth="2"/></>
                : <><circle cx={cx-8} cy={cy-6} r="2" fill="#1e293b"/><circle cx={cx+8} cy={cy-6} r="2" fill="#1e293b"/></>
            }
            {e.smile==="happy" && <path d={`M${cx-10} ${cy+6} Q${cx} ${cy+16} ${cx+10} ${cy+6}`} stroke="#1e293b" strokeWidth="2" fill="none"/>}
            {e.smile==="sad" && <path d={`M${cx-10} ${cy+12} Q${cx} ${cy+4} ${cx+10} ${cy+12}`} stroke="#1e293b" strokeWidth="2" fill="none"/>}
            {e.smile==="angry" && <path d={`M${cx-10} ${cy+10} L${cx+10} ${cy+10}`} stroke="#1e293b" strokeWidth="2"/>}
            {e.smile==="fear" && <ellipse cx={cx} cy={cy+10} rx="6" ry="4" fill="#1e293b"/>}
            {e.smile==="surprise" && <circle cx={cx} cy={cy+10} r="4" fill="#1e293b"/>}
            {e.smile==="disgust" && <path d={`M${cx-8} ${cy+12} Q${cx} ${cy+6} ${cx+8} ${cy+12}`} stroke="#1e293b" strokeWidth="2" fill="none"/>}
            <text x={cx} y={cy+50} textAnchor="middle" fontSize="9" fontWeight="bold" fill={e.color}>{e.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

function StroopReference() {
  return (
    <svg viewBox="0 0 360 130" className="w-full h-full">
      <text x="60" y="14" textAnchor="middle" fontSize="9" fill="#64748b">Lámina 1 · Lectura</text>
      <text x="180" y="14" textAnchor="middle" fontSize="9" fill="#64748b">Lámina 2 · Color</text>
      <text x="300" y="14" textAnchor="middle" fontSize="9" fill="#64748b">Lámina 3 · Interferencia</text>
      <g transform="translate(10, 24)">
        {["ROJO","AZUL","VERDE"].map((w,i)=>(
          <text key={i} x="50" y={20+i*30} textAnchor="middle" fontSize="14" fontWeight="bold" fill="#1e293b">{w}</text>
        ))}
      </g>
      <g transform="translate(140, 24)">
        {[{c:"#dc2626"},{c:"#2563eb"},{c:"#10b981"}].map((b,i)=>(
          <rect key={i} x="20" y={i*30+5} width="60" height="20" fill={b.c}/>
        ))}
      </g>
      <g transform="translate(260, 24)">
        {[{w:"ROJO",c:"#2563eb"},{w:"AZUL",c:"#10b981"},{w:"VERDE",c:"#dc2626"}].map((p,i)=>(
          <text key={i} x="40" y={20+i*30} textAnchor="middle" fontSize="14" fontWeight="bold" fill={p.c}>{p.w}</text>
        ))}
      </g>
      <text x="180" y="125" textAnchor="middle" fontSize="8" fill="#64748b" fontStyle="italic">Resistencia a la interferencia: nombrar el COLOR DE LA TINTA, no la palabra</text>
    </svg>
  );
}

function CancellationGrid({ target = "★" }) {
  /* Hoja con N targets dispersos entre distractores. Layout determinístico
   * basado en posición (para no causar re-renders aleatorios). */
  const distractors = ["○","△","◇","■","□","▽"];
  const cells = [];
  for (let r=0; r<6; r++) for (let c=0; c<10; c++) {
    const seed = (r*10+c)*7919 % 17;
    const isTarget = seed < 3; // ~18% targets
    cells.push({ r, c, sym: isTarget ? target : distractors[seed % distractors.length] });
  }
  return (
    <svg viewBox="0 0 360 180" className="w-full h-full">
      <text x="180" y="12" textAnchor="middle" fontSize="9" fill="#64748b">Tache cada {target} entre los distractores · trabaje de izquierda a derecha</text>
      {cells.map((c,i)=>(
        <text key={i} x={20+c.c*32} y={32+c.r*22} textAnchor="middle" fontSize="14" fill={c.sym===target?"#0D9488":"#475569"}>{c.sym}</text>
      ))}
    </svg>
  );
}

function FaceDiscriminationRow() {
  return (
    <svg viewBox="0 0 360 100" className="w-full h-full">
      <text x="180" y="12" textAnchor="middle" fontSize="9" fill="#64748b">Tache la cara diferente de la fila</text>
      {[0,1,2,3,4].map(i=>{
        const cx=40+i*70, cy=55;
        const odd = i===2;
        return (
          <g key={i}>
            <circle cx={cx} cy={cy} r="22" fill="#fde68a" stroke="#a16207" strokeWidth="1.5"/>
            <circle cx={cx-7} cy={cy-5} r="2" fill="#1e293b"/>
            <circle cx={cx+7} cy={cy-5} r="2" fill="#1e293b"/>
            {odd
              ? <path d={`M${cx-7} ${cy+8} Q${cx} ${cy+2} ${cx+7} ${cy+8}`} stroke="#1e293b" strokeWidth="2" fill="none"/>
              : <path d={`M${cx-7} ${cy+5} Q${cx} ${cy+12} ${cx+7} ${cy+5}`} stroke="#1e293b" strokeWidth="2" fill="none"/>
            }
          </g>
        );
      })}
    </svg>
  );
}

/* ═══ Palabras en Contexto WISC-IV — cuadrícula 2×2 de imágenes para pareo ═══ */
function WordContextGrid() {
  const rows = [
    { word: "VEHÍCULO", imgs: ["🚗","🍎","🐶","⚽"] },
    { word: "INSTRUMENTO", imgs: ["🎸","🚲","🌺","🍕"] },
    { word: "HERRAMIENTA", imgs: ["🔨","🎈","🐱","☁️"] },
  ];
  return (
    <svg viewBox="0 0 360 200" className="w-full h-full">
      <text x="180" y="13" textAnchor="middle" fontSize="9" fill="#64748b">Elija la imagen que corresponde a la palabra</text>
      {rows.map((row, ri) => {
        const y = 22 + ri * 58;
        return (
          <g key={ri}>
            <rect x="4" y={y} width="78" height="44" fill="#0D9488" rx="6"/>
            <text x="43" y={y+27} textAnchor="middle" fontSize="9" fontWeight="bold" fill="#fff">{row.word}</text>
            {row.imgs.map((img, ci) => (
              <g key={ci}>
                <rect x={90+ci*66} y={y} width="58" height="44" fill="#fff" stroke="#cbd5e1" strokeWidth="1" rx="4"/>
                <text x={90+ci*66+29} y={y+29} textAnchor="middle" fontSize="26">{img}</text>
              </g>
            ))}
          </g>
        );
      })}
      <text x="180" y="196" textAnchor="middle" fontSize="8" fill="#64748b" fontStyle="italic">Apoyo ilustrativo · no sustituye el cuadernillo editorial</text>
    </svg>
  );
}

/* ═══ Integración de Objetos — fragmentos desordenados para reconocer ═══ */
function ObjectIntegration() {
  const _objects = [
    { label: "Mariposa", parts: [[{x:90,y:40,r:28,fill:"#f59e0b"},{x:130,y:40,r:28,fill:"#f59e0b"},{cx:110,cy:40,label:"●"}] ] },
  ];
  const items = [
    { label: "Mariposa",  color: "#f59e0b" },
    { label: "Guitarra",  color: "#0D9488" },
    { label: "Tijera",    color: "#7c3aed" },
    { label: "Ancla",     color: "#dc2626" },
  ];
  return (
    <svg viewBox="0 0 360 200" className="w-full h-full">
      <text x="180" y="13" textAnchor="middle" fontSize="9" fill="#64748b">¿Qué objeto forman estas piezas?</text>
      {items.map((item, i) => {
        const col = i % 2, row = Math.floor(i / 2);
        const ox = 20 + col * 180, oy = 24 + row * 90;
        return (
          <g key={i}>
            <rect x={ox} y={oy} width="150" height="78" fill="var(--ns-subtle,#f8fafc)" stroke="#e2e8f0" strokeWidth="1" rx="8"/>
            {/* fragmento A */}
            <rect x={ox+10} y={oy+10} width="40" height="40" fill={item.color} rx="6" opacity="0.7"/>
            <text x={ox+30} y={oy+35} textAnchor="middle" fontSize="20" fill="#fff">?</text>
            {/* fragmento B — rotado */}
            <rect x={ox+60} y={oy+25} width="34" height="34" fill={item.color} rx="6" opacity="0.5" transform={`rotate(45 ${ox+77} ${ox+42})`}/>
            {/* fragmento C */}
            <rect x={ox+105} y={oy+10} width="36" height="36" fill={item.color} rx="18" opacity="0.8"/>
            <text x={ox+75} y={oy+70} textAnchor="middle" fontSize="8" fill="#64748b">{item.label}</text>
          </g>
        );
      })}
      <text x="180" y="196" textAnchor="middle" fontSize="8" fill="#64748b" fontStyle="italic">Apoyo ilustrativo · identifique el objeto a partir de sus partes</text>
    </svg>
  );
}

/* ═══ Denominación 48 ítems — galería de dibujos esquemáticos propios ═══ */
function Denomination48() {
  /* 48 ítems agrupados en 6 categorías semánticas (8 c/u).
   * Se representa como galería emoji sobre grid 8×6.
   * Dibujos propios: emojis son ideogramas de dominio público / Unicode. */
  const items = [
    /* Animales */ "🐘","🦁","🦢","🦋","🐢","🦎","🦀","🦈",
    /* Frutas/veg */ "🍇","🥝","🌽","🥕","🍄","🌰","🧅","🫑",
    /* Herramientas */ "⚙️","🔧","🪚","🔩","🧲","🪣","🔭","🪛",
    /* Cuerpo */ "👁️","👂","🦷","🫀","🧠","🦴","👃","🫁",
    /* Transporte */ "🚁","🛶","🚂","🛸","🚑","🚜","🛺","🚀",
    /* Objetos hogar */ "🪑","🛁","🪟","🧹","🪴","🕯️","🧺","🪞",
  ];
  return (
    <svg viewBox="0 0 360 240" className="w-full h-full">
      <text x="180" y="12" textAnchor="middle" fontSize="9" fill="#64748b">Nombrar cada dibujo · 48 ítems — tiempo libre</text>
      {items.map((item, i) => {
        const col = i % 8, row = Math.floor(i / 8);
        const x = 6 + col * 43, y = 18 + row * 36;
        return (
          <g key={i}>
            <rect x={x} y={y} width="39" height="32" fill="#fff" stroke="#e2e8f0" rx="4"/>
            <text x={x+19} y={y+23} textAnchor="middle" fontSize="18">{item}</text>
          </g>
        );
      })}
      <text x="180" y="234" textAnchor="middle" fontSize="7" fill="#64748b" fontStyle="italic">Apoyo orientativo · los ítems de calificación provienen del BNT/ENI estandarizado</text>
    </svg>
  );
}
