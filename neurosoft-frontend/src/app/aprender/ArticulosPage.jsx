/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/ArticulosPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 — Artículos clínicos cortos.
 *
 * Listado + viewer markdown simple (renderer ad-hoc para evitar dep externa).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Btn, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { ARTICULOS } from "../../data/aprenderContent.js";

/* Renderer markdown muy básico (h1/h2/h3, párrafos, listas, citas) — sin librería externa. */
function renderMarkdown(md) {
  if (!md) return null;
  const lines = md.split("\n");
  const out = [];
  let i = 0;
  let listBuffer = [];
  const flushList = (key) => {
    if (listBuffer.length) {
      out.push(<ul key={`ul-${key}`} className="list-disc pl-6 mb-3 space-y-1">{listBuffer}</ul>);
      listBuffer = [];
    }
  };
  while (i < lines.length) {
    const ln = lines[i];
    if (/^\|.+\|$/.test(ln.trim()) && i + 1 < lines.length && /^\|[\s\-:|]+\|$/.test(lines[i + 1]?.trim())) {
      flushList(i);
      const headerCells = ln.trim().slice(1, -1).split("|").map((c) => c.trim());
      i += 2;
      const rows = [];
      while (i < lines.length && /^\|.+\|$/.test(lines[i].trim())) {
        rows.push(lines[i].trim().slice(1, -1).split("|").map((c) => c.trim()));
        i++;
      }
      out.push(
        <table key={`tbl-${i}`} className="w-full text-xs mb-4 border-collapse">
          <thead>
            <tr>{headerCells.map((h, j) => <th key={j} className="border px-2 py-1 text-left font-bold" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri}>{row.map((cell, ci) => <td key={ci} className="border px-2 py-1" style={{ borderColor: "var(--ns-card-b)" }}>{cell}</td>)}</tr>
            ))}
          </tbody>
        </table>
      );
      continue;
    }
    if (/^# /.test(ln)) {
      flushList(i);
      out.push(<h1 key={i} className="ns-serif text-2xl font-bold mt-6 mb-3">{ln.replace(/^# /, "")}</h1>);
    } else if (/^## /.test(ln)) {
      flushList(i);
      out.push(<h2 key={i} className="ns-serif text-xl font-bold mt-5 mb-2" style={{ color: TEAL }}>{ln.replace(/^## /, "")}</h2>);
    } else if (/^### /.test(ln)) {
      flushList(i);
      out.push(<h3 key={i} className="font-bold text-base mt-4 mb-1.5">{ln.replace(/^### /, "")}</h3>);
    } else if (/^- /.test(ln) || /^\* /.test(ln)) {
      listBuffer.push(<li key={i} className="text-sm leading-relaxed" dangerouslySetInnerHTML={{
        __html: ln.replace(/^[-*] /, "").replace(/</g, "&lt;").replace(/>/g, "&gt;")
          .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
          .replace(/`(.+?)`/g, '<code class="ns-mono text-xs bg-gray-100 px-1 rounded">$1</code>'),
      }} />);
    } else if (/^> /.test(ln)) {
      flushList(i);
      out.push(<blockquote key={i} className="border-l-2 pl-3 italic my-3 text-sm" style={{ borderColor: TEAL, color: "var(--ns-muted)" }}>{ln.replace(/^> /, "")}</blockquote>);
    } else if (ln.trim() === "") {
      flushList(i);
      // párrafo break
    } else {
      flushList(i);
      const html = ln.replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.+?)`/g, '<code class="ns-mono text-xs bg-gray-100 px-1 rounded">$1</code>')
        .replace(/\*(.+?)\*/g, "<em>$1</em>");
      out.push(<p key={i} className="text-sm leading-relaxed mb-3" style={{ color: "var(--ns-text)" }}
        dangerouslySetInnerHTML={{ __html: html }} />);
    }
    i++;
  }
  flushList("end");
  return out;
}

export default function ArticulosPage() {
  const [sel, setSel] = useState(null);

  if (sel) {
    return (
      <>
        <TopBar title={sel.titulo}>
          <Btn variant="ghost" onClick={() => setSel(null)} className="text-xs">
            <I name="arrow_back" className="mr-1" />Volver
          </Btn>
        </TopBar>
        <main className="p-8 max-w-3xl mx-auto">
          <article>
            <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>{sel.categoria}</p>
            <p className="text-xs mb-4" style={{ color: "var(--ns-muted)" }}>
              {sel.autor} · {sel.fecha} · {sel.tiempo_lectura_min} min de lectura
            </p>
            <div className="prose-clinical">
              {renderMarkdown(sel.contenido_md)}
            </div>
            {sel.referencias?.length > 0 && (
              <div className="mt-8 pt-5 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-2">Referencias citadas</p>
                <ul className="space-y-1 text-xs ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                  {sel.referencias.map((r, i) => <li key={i}>· {r}</li>)}
                </ul>
              </div>
            )}
          </article>
        </main>
      </>
    );
  }

  return (
    <>
      <TopBar title="Artículos clínicos" />
      <main className="p-8 max-w-7xl mx-auto space-y-5">
        <div className="flex items-center gap-3 mb-2">
          <I name="article" style={{ color: TEAL, fontSize: 28 }} />
          <div>
            <h2 className="ns-serif text-xl font-bold">Artículos editoriales</h2>
            <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
              {ARTICULOS.length} artículos · contenido revisado con referencias clínicas verificadas
            </p>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ARTICULOS.map(a => (
            <button key={a.id} onClick={() => setSel(a)}
              className="text-left p-5 rounded border transition-all hover:shadow-md flex flex-col h-full"
              style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
              <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>{a.categoria.replace(/_/g, " ")}</p>
              <h3 className="ns-serif font-bold text-base mb-2 leading-tight">{a.titulo}</h3>
              <p className="text-xs leading-relaxed mb-3 flex-1" style={{ color: "var(--ns-muted)" }}>
                {a.resumen}
              </p>
              <div className="flex items-center justify-between text-[10px]" style={{ color: "var(--ns-muted)" }}>
                <span>{a.fecha}</span>
                <span><I name="schedule" className="text-xs" />{a.tiempo_lectura_min} min</span>
              </div>
            </button>
          ))}
        </div>
      </main>
    </>
  );
}
