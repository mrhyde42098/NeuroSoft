/* ═══════════════════════════════════════════════════════════════════════
 * AvdDineroActivity.jsx — AVD cognitiva: Manejo de dinero
 * ───────────────────────────────────────────────────────────────────────
 * Escenarios ecológicos de manejo de dinero:
 *   1. Calcular vuelto de una compra
 *   2. Planificar presupuesto semanal (asignación de montos)
 *   3. Leer precio de productos y elegir el más económico
 *
 * Evidencia: transferencia ecológica en rehabilitación cognitiva de TCE
 * y demencia leve (Logsdon et al.; Sohlberg & Mateer).
 *
 * Props: { params, onFinish, onCancel }
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Btn, Card, I, Input } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ── Escenarios ── */
const SCENARIOS = [
  /* Tipo: vuelto */
  {
    type: "vuelto",
    desc: "Usted va a la tienda y compra:",
    items: [{ name: "Leche x2", price: 4200 }, { name: "Pan", price: 1800 }, { name: "Jabón", price: 3500 }],
    paid: 15000,
    question: "¿Cuánto vuelto debe recibir?",
    answer: 5500,
    currency: "COP",
  },
  {
    type: "vuelto",
    desc: "Compra en la farmacia:",
    items: [{ name: "Paracetamol", price: 8900 }, { name: "Alcohol", price: 6200 }],
    paid: 20000,
    question: "¿Cuánto debe recibir de vuelto?",
    answer: 4900,
    currency: "COP",
  },
  /* Tipo: comparar precios */
  {
    type: "comparar",
    question: "¿Cuál opción le conviene más por la misma cantidad?",
    options: [
      { label: "Tienda A — 500g por $3.200", unitCost: 6.4 },
      { label: "Tienda B — 250g por $1.400", unitCost: 5.6 },
      { label: "Supermercado — 1kg por $6.800", unitCost: 6.8 },
    ],
    bestIdx: 1,
    explain: "Tienda B tiene el menor costo por gramo ($5,6/g).",
  },
  {
    type: "comparar",
    question: "¿Cuál oferta es más económica para llenar el tanque de 40 litros?",
    options: [
      { label: "Estación A — $9.800/litro", unitCost: 9800 },
      { label: "Estación B — $10.200/litro con 5% dcto", unitCost: 9690 },
      { label: "Estación C — $9.950/litro", unitCost: 9950 },
    ],
    bestIdx: 1,
    explain: "Estación B con descuento queda a $9.690/litro — la más económica.",
  },
  /* Tipo: presupuesto */
  {
    type: "presupuesto",
    ingresos: 800000,
    gastos: [
      { nombre: "Arriendo", monto: 400000 },
      { nombre: "Servicios", monto: 80000 },
      { nombre: "Mercado", monto: 200000 },
      { nombre: "Transporte", monto: 60000 },
    ],
    question: "¿Cuánto dinero libre le queda al mes?",
    answer: 60000,
  },
];

function fmt(n) {
  return "$" + n.toLocaleString("es-CO");
}

export default function AvdDineroActivity({ params = {}, onFinish, onCancel }) {
  const maxScenarios = Math.min(params.scenarios ?? 5, SCENARIOS.length);
  const scenarios    = SCENARIOS.slice(0, maxScenarios);

  const [idx,     setIdx]     = useState(0);
  const [answer,  setAnswer]  = useState("");
  const [choice,  setChoice]  = useState(null);
  const [checked, setChecked] = useState(false);
  const [results, setResults] = useState([]);
  const [started, setStarted] = useState(false);
  const [done,    setDone]    = useState(false);

  const sc = scenarios[idx];

  function check() {
    let correct = false;
    if (sc.type === "vuelto" || sc.type === "presupuesto") {
      const num = parseInt(answer.replace(/[^0-9]/g, ""), 10);
      correct = num === sc.answer;
    } else if (sc.type === "comparar") {
      correct = choice === sc.bestIdx;
    }
    setChecked(true);
    const newResults = [...results, { idx, correct, type: sc.type }];
    setResults(newResults);
  }

  function next() {
    if (idx + 1 >= maxScenarios) {
      setDone(true);
    } else {
      setIdx(i => i + 1);
      setAnswer("");
      setChoice(null);
      setChecked(false);
    }
  }

  if (!started) {
    return (
      <Card className="p-8 max-w-lg mx-auto space-y-5 text-center">
        <I name="payments" style={{ color: TEAL, fontSize: 48 }}/>
        <h2 className="text-xl font-extrabold">Manejo de Dinero</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Situaciones reales de la vida cotidiana: calcular vueltos,
          comparar precios y planificar presupuesto.
          Estas habilidades son parte fundamental de la independencia funcional.
        </p>
        <p className="text-sm font-bold" style={{ color: TEAL }}>{maxScenarios} situaciones</p>
        <Btn onClick={() => setStarted(true)}>Comenzar</Btn>
        <button onClick={onCancel} className="block mx-auto text-xs mt-2" style={{ color: "var(--ns-muted)" }}>Cancelar</button>
      </Card>
    );
  }

  if (done) {
    const correct = results.filter(r => r.correct).length;
    const pct = Math.round((correct / maxScenarios) * 100);
    return (
      <Card className="p-8 max-w-lg mx-auto space-y-5 text-center">
        <I name="account_balance_wallet" fill style={{ color: TEAL, fontSize: 48 }}/>
        <h2 className="text-xl font-extrabold">Completado</h2>
        <p className="text-5xl font-extrabold" style={{ color: pct >= 80 ? "#10b981" : pct >= 60 ? "#f59e0b" : "#dc2626" }}>
          {correct}/{maxScenarios}
        </p>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>{pct}% de aciertos</p>
        {pct < 80 && (
          <p className="text-xs p-3 rounded-xl" style={{ background: "#fef3c7", color: "#92400e" }}>
            <I name="lightbulb" className="text-sm mr-1"/>
            Estrategia: anote el total a pagar antes de dar el dinero.
            Para comparar precios, calcule el costo por unidad (precio ÷ cantidad).
          </p>
        )}
        <div className="space-y-1 text-left">
          {results.map((r, i) => (
            <div key={i} className={`flex items-center gap-2 p-2 rounded-lg text-xs ${r.correct ? "bg-green-50" : "bg-red-50"}`}>
              <I name={r.correct ? "check_circle" : "cancel"} fill className={r.correct ? "text-green-600" : "text-red-500"}/>
              <span>Situación {i + 1} ({r.type})</span>
            </div>
          ))}
        </div>
        <Btn onClick={() => onFinish({ correct, total: maxScenarios, pct_aciertos: pct })}>
          Guardar resultados
        </Btn>
      </Card>
    );
  }

  return (
    <Card className="p-6 max-w-lg mx-auto space-y-5">
      {/* Progreso */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-extrabold">Situación {idx + 1} / {maxScenarios}</p>
        <span className="text-xs px-3 py-1 rounded-full font-bold"
          style={{ background: `${TEAL}18`, color: TEAL }}>
          {sc.type === "vuelto" ? "Vuelto" : sc.type === "comparar" ? "Comparar precios" : "Presupuesto"}
        </span>
      </div>

      {/* Contenido según tipo */}
      {sc.type === "vuelto" && (
        <div className="space-y-3">
          <p className="text-sm font-bold">{sc.desc}</p>
          <div className="p-4 rounded-xl space-y-2" style={{ background: "var(--ns-subtle)" }}>
            {sc.items.map((item, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span>{item.name}</span>
                <span className="font-bold">{fmt(item.price)}</span>
              </div>
            ))}
            <div className="border-t pt-2 flex justify-between text-sm">
              <span className="font-bold">Total</span>
              <span className="font-bold" style={{ color: TEAL }}>
                {fmt(sc.items.reduce((s, i) => s + i.price, 0))}
              </span>
            </div>
          </div>
          <p className="text-sm">Pagó con: <strong>{fmt(sc.paid)}</strong></p>
          <p className="text-sm font-bold">{sc.question}</p>
          {!checked ? (
            <Input
              type="number" placeholder="Ingrese el monto en pesos"
              value={answer} onChange={e => setAnswer(e.target.value)}
            />
          ) : (
            <div className={`p-3 rounded-xl text-sm font-bold ${results[results.length-1]?.correct ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
              {results[results.length-1]?.correct
                ? `✓ Correcto — ${fmt(sc.answer)}`
                : `✗ La respuesta correcta es ${fmt(sc.answer)}`}
            </div>
          )}
        </div>
      )}

      {sc.type === "comparar" && (
        <div className="space-y-3">
          <p className="text-sm font-bold">{sc.question}</p>
          <div className="space-y-2">
            {sc.options.map((opt, i) => {
              let bg = "var(--ns-card)", border = "var(--ns-card-b)", color = "var(--ns-text)";
              if (checked && i === sc.bestIdx) { bg = "#ecfdf5"; border = "#10b981"; color = "#064e3b"; }
              if (checked && choice === i && i !== sc.bestIdx) { bg = "#fef2f2"; border = "#dc2626"; color = "#7f1d1d"; }
              if (!checked && choice === i) { bg = `${TEAL}18`; border = TEAL; }
              return (
                <button key={i} onClick={() => !checked && setChoice(i)} disabled={checked}
                  className="w-full p-3 rounded-xl text-sm text-left border-2 transition-all"
                  style={{ background: bg, borderColor: border, color }}>
                  {opt.label}
                  {checked && i === sc.bestIdx && <I name="check_circle" fill className="ml-2 text-green-600"/>}
                </button>
              );
            })}
          </div>
          {checked && (
            <p className="text-xs p-3 rounded-xl" style={{ background: "#eff6ff", color: "#1e40af" }}>
              <I name="lightbulb" className="text-sm mr-1"/>{sc.explain}
            </p>
          )}
        </div>
      )}

      {sc.type === "presupuesto" && (
        <div className="space-y-3">
          <p className="text-sm font-bold">Ingreso mensual: <span style={{ color: TEAL }}>{fmt(sc.ingresos)}</span></p>
          <div className="p-4 rounded-xl space-y-2" style={{ background: "var(--ns-subtle)" }}>
            {sc.gastos.map((g, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span>{g.nombre}</span>
                <span className="font-bold text-red-600">−{fmt(g.monto)}</span>
              </div>
            ))}
            <div className="border-t pt-2 flex justify-between text-sm">
              <span className="font-bold">Total gastos</span>
              <span className="font-bold text-red-600">
                −{fmt(sc.gastos.reduce((s, g) => s + g.monto, 0))}
              </span>
            </div>
          </div>
          <p className="text-sm font-bold">{sc.question}</p>
          {!checked ? (
            <Input
              type="number" placeholder="Ingrese el monto en pesos"
              value={answer} onChange={e => setAnswer(e.target.value)}
            />
          ) : (
            <div className={`p-3 rounded-xl text-sm font-bold ${results[results.length-1]?.correct ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
              {results[results.length-1]?.correct
                ? `✓ Correcto — ${fmt(sc.answer)}`
                : `✗ La respuesta correcta es ${fmt(sc.answer)}`}
            </div>
          )}
        </div>
      )}

      {/* Acciones */}
      {!checked ? (
        <Btn onClick={check} disabled={
          (sc.type !== "comparar" && !answer) ||
          (sc.type === "comparar" && choice === null)
        }>
          Verificar respuesta
        </Btn>
      ) : (
        <Btn onClick={next}>
          {idx + 1 < maxScenarios ? "Siguiente situación" : "Ver resultados"}
        </Btn>
      )}

      <button onClick={onCancel} className="w-full text-xs" style={{ color: "var(--ns-muted)" }}>
        Salir de la actividad
      </button>
    </Card>
  );
}
