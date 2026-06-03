/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ClinicalInterpretationPanel.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Panel de interpretación clínica automatizada del perfil cognitivo.
 *
 * Analiza el conjunto de resultados (índices WISC/WAIS, subtests Z, etc.)
 * y genera:
 *   1. Detección de patrones cognitivos: TDAH, TCL/CDHS, TEA, DCL, etc.
 *   2. Identificación de "islas de habilidad" (TEA / DI)
 *   3. Sugerencias de diagnóstico diferencial
 *   4. Texto clínico borrador para sección de Observaciones
 *   5. Alertas sobre perfil incompleto o datos inconsistentes
 *
 * NO reemplaza el juicio clínico. Es una guía de análisis estructurado.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useState } from "react";
import { Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ── helpers ── */
const round2 = (n) => Math.round(n * 100) / 100;

/* Clasificaciones de CI / índice compuesto (media=100, SD=15) */
const clasificarCI = (ci) => {
  if (ci == null) return null;
  if (ci >= 130) return { label: "Muy superior",    color: "#6d28d9" };
  if (ci >= 120) return { label: "Superior",         color: "#2563eb" };
  if (ci >= 110) return { label: "Alto promedio",    color: "#0d9488" };
  if (ci >= 90)  return { label: "Promedio",         color: "#16a34a" };
  if (ci >= 80)  return { label: "Bajo promedio",    color: "#ca8a04" };
  if (ci >= 70)  return { label: "Bajo",             color: "#ea580c" };
  return              { label: "Extremadamente bajo", color: "#dc2626" };
};

/* ── Análisis de islas de habilidad ──────────────────────────────────── */
function detectarIslasHabilidad(subtests) {
  const validos = subtests.filter(
    (s) => s.puntaje_escalar != null && s.puntaje_escalar !== 9999 && s.puntaje_escalar > 0
  );
  if (validos.length < 4) return null;

  const escalares = validos.map((s) => s.puntaje_escalar);
  const max = Math.max(...escalares);
  const min = Math.min(...escalares);
  const rango = max - min;
  const media = escalares.reduce((a, b) => a + b, 0) / escalares.length;
  const desv = Math.sqrt(
    escalares.reduce((s, e) => s + Math.pow(e - media, 2), 0) / escalares.length
  );

  const fortalezas = validos.filter((s) => s.puntaje_escalar >= 13).map((s) => s.nombre_prueba);
  const debilidades = validos.filter((s) => s.puntaje_escalar <= 7).map((s) => s.nombre_prueba);

  return {
    rango,
    media: round2(media),
    desv: round2(desv),
    max,
    min,
    fortalezas,
    debilidades,
    isHeterogeneo: rango >= 8 || desv >= 3.5,
  };
}

/* ── Análisis de índices WISC/WAIS para detección de patrones ─────── */
function analizarIndices(resultados) {
  /* Busca CI en resultados por nombre_prueba o test_id — soporta WISC-IV y WAIS-III */
  const getCI = (nombres) => {
    for (const n of nombres) {
      const r = resultados.find(
        (r) =>
          r.nombre_prueba?.toLowerCase().includes(n.toLowerCase()) ||
          r.test_id?.toLowerCase().includes(n.toLowerCase())
      );
      if (r?.puntaje_escalar && r.puntaje_escalar !== 9999) return r.puntaje_escalar;
    }
    return null;
  };

  /* WISC-IV: ICV/IRP/IMT/IVP/CIT
   * WAIS-III: ICV/ICP (Comprensión Perceptual)/IMT/IVP/CIT */
  const ICV = getCI(["IndComVer", "ICV", "ComVer", "WAISICV", "Comprensión Verbal"]);
  const IRP = getCI(["IndRazPer", "IRP", "RazPer", "Razonamiento Perceptual"]);
  const ICP = getCI(["IndComPer", "ICP", "ComPer", "WAISIndComPer", "Comprensión Perceptual"]);
  /* Para WAIS-III, "Razonamiento Perceptual" equivale a ICP */
  const IRPo = IRP ?? ICP;  /* IRP o ICP como alternativa */
  const IMT = getCI(["IndMemTra", "IMT", "MemTra", "WAISMT", "Memoria de Trabajo"]);
  const IVP = getCI(["IndVelPro", "IVP", "VelPro", "WAISIVP", "Velocidad de Procesamiento"]);
  const CIT = getCI(["WISCTot", "WAISTot", "CIT", "CI Total"]);
  /* ICG / ICC (alternativas al CIT cuando hay discrepancia) */
  const ICG = getCI(["ICG", "Capacidad General"]);
  const ICC = getCI(["ICC", "Competencia Cognitiva"]);

  return { ICV, IRP: IRPo, IMT, IVP, CIT, ICG, ICC, ICP };
}

/* ── Motor de detección de patrones clínicos ─────────────────────── */
function detectarPatrones(indices, islas, subtests, edad) {
  const patrones = [];
  const { ICV, IRP, IMT, IVP, CIT, ICG, ICC } = indices;
  const disponibles = [ICV, IRP, IMT, IVP].filter((v) => v != null);

  if (disponibles.length < 2) return patrones;

  const promGeneral = disponibles.reduce((a, b) => a + b, 0) / disponibles.length;

  /* ─── 1. TDAH — Déficit selectivo en IMT + IVP (atención ejecutiva) */
  if (IMT != null && IVP != null && ICV != null && IRP != null) {
    const promedioEjec = (IMT + IVP) / 2;
    const promedioCristalizado = (ICV + IRP) / 2;
    const brecha = promedioCristalizado - promedioEjec;
    if (promedioEjec < 90 && promedioCristalizado >= 90 && brecha >= 15) {
      patrones.push({
        tipo: "TDAH / Déficit atencional-ejecutivo",
        nivel: brecha >= 25 ? "alto" : "moderado",
        icono: "flash_on",
        color: "#f59e0b",
        evidencia: [
          `ICV+IRP (cristalizado) = ${Math.round(promedioCristalizado)} · IMT+IVP (ejecutivo) = ${Math.round(promedioEjec)}`,
          `Brecha ejecutiva-cristalizada: ${Math.round(brecha)} puntos (significativa ≥ 15 pts)`,
          IMT < 90 && IVP < 90
            ? `Ambos índices ejecutivos afectados: IMT=${IMT}, IVP=${IVP} — patrón más clásico de TDAH.`
            : `Solo un índice ejecutivo afectado — descartar ansiedad y fatiga.`,
        ],
        sugerencia: "Aplicar SNAP-IV (padres) / ASRS (adultos) + evaluación en múltiples contextos + criterios DSM-5 (6+ síntomas en ≥2 entornos desde la infancia).",
      });
    }
  }

  /* ─── 2. TCL / CDHS — IVP selectivamente muy bajo sin otras afectaciones */
  if (IVP != null && ICV != null && IRP != null && IMT != null) {
    const mediaOtros = (ICV + IRP + IMT) / 3;
    const diferencia = mediaOtros - IVP;
    if (IVP < 85 && diferencia >= 20 && ICV >= 90) {
      patrones.push({
        tipo: "Tempo Cognitivo Lento / CDHS (CDS Barkley 2012)",
        nivel: diferencia >= 30 ? "alto" : "moderado",
        icono: "hourglass_empty",
        color: "#8b5cf6",
        evidencia: [
          `IVP = ${IVP} vs media otros índices = ${Math.round(mediaOtros)} (diferencia ${Math.round(diferencia)} pts)`,
          `ICV = ${ICV} — lenguaje preservado: apoya enlentecimiento selectivo no afásico.`,
          `Patrón compatible con Tempo Cognitivo Lento (ensoñación, pasividad, lentitud sin hiperactividad).`,
        ],
        sugerencia: "Revisar síntomas específicos de CDHS: ensoñación diurna frecuente, confusión mental, hipoactividad. Diferencial con: ansiedad, depresión, trastorno del sueño, hipotiroidismo. CDHS ≠ TDAH (sin hiperactividad).",
      });
    }
  }

  /* ─── 3. TEA — Perfil heterogéneo con islas + ICV bajo vs IRP alto */
  if (islas?.isHeterogeneo && ICV != null) {
    const brechaVerbalPerceptual = IRP != null && IRP >= ICV + 15;
    const perfilMuyHeterogéneo = islas.rango >= 10;
    if (brechaVerbalPerceptual || perfilMuyHeterogéneo) {
      patrones.push({
        tipo: "Perfil heterogéneo — evaluar TEA / perfil disarmónico",
        nivel: "informativo",
        icono: "account_tree",
        color: "#0ea5e9",
        evidencia: [
          `Rango intraindividual: ${islas.rango} pts (max=${islas.max}, min=${islas.min}) | DS=${islas.desv}`,
          brechaVerbalPerceptual
            ? `IRP=${IRP} >> ICV=${ICV} (brecha ${IRP - ICV} pts) — discrepancia verbal vs perceptual frecuente en TEA`
            : null,
          islas.fortalezas.length > 0 ? `Fortalezas: ${islas.fortalezas.slice(0, 4).join(", ")}` : null,
          islas.debilidades.length > 0 ? `Dificultades: ${islas.debilidades.slice(0, 4).join(", ")}` : null,
        ].filter(Boolean),
        sugerencia: "El perfil heterogéneo NO diagnostica TEA. Evaluar: pragmática del lenguaje, conductas repetitivas, procesamiento sensorial, teoría de la mente. M-CHAT-R/F (<3 años) o SRS-2 (>4 años). El CIT puede subestimar la capacidad real — analizar ICG.",
      });
    }
  }

  /* ─── 4. Dificultades de Aprendizaje Específicas — ICV-IRP brecha sin DI */
  if (ICV != null && IRP != null && CIT != null && CIT >= 70) {
    const brechaPerceptualVerbal = ICV < 90 && IRP >= 95 && IRP - ICV >= 15;
    const brechaVerbalPerceptual = IRP < 90 && ICV >= 95 && ICV - IRP >= 15;
    if (brechaPerceptualVerbal) {
      patrones.push({
        tipo: "Posible DEA en lectoescritura / trastorno del lenguaje",
        nivel: "moderado",
        icono: "menu_book",
        color: "#dc8b00",
        evidencia: [
          `ICV = ${ICV} (bajo) vs IRP = ${IRP} (preservado) — brecha ${IRP - ICV} pts`,
          `Dificultad verbal con habilidades visoperceptuales intactas: patrón de dislexia o TDL.`,
          CIT != null ? `CIT = ${CIT} — por encima de rango de discapacidad intelectual.` : null,
        ].filter(Boolean),
        sugerencia: "Evaluar lectura, escritura y conciencia fonológica (PROLEC-R, ENI-2 lectura). Descartar TDL con evaluación de lenguaje formal. Considerar apoyos académicos diferenciados.",
      });
    }
    if (brechaVerbalPerceptual) {
      patrones.push({
        tipo: "Posible DEA no verbal / dificultades visoespaciales",
        nivel: "moderado",
        icono: "grid_view",
        color: "#dc8b00",
        evidencia: [
          `IRP = ${IRP} (bajo) vs ICV = ${ICV} (preservado) — brecha ${ICV - IRP} pts`,
          `Dificultad perceptual-visoespacial con lenguaje intacto: patrón de DEA no verbal (NLD).`,
        ],
        sugerencia: "Evaluar habilidades visoespaciales, motoras y matemáticas. Considerar FCRO (copia/recobro) y pruebas de cálculo. Diferneciar de variante posterior de demencia si es adulto mayor.",
      });
    }
  }

  /* ─── 5. Discapacidad Intelectual — CI total < 70 */
  if (CIT != null && CIT < 70) {
    const ciUsado = ICG ?? CIT;
    patrones.push({
      tipo: "Posible Discapacidad Intelectual",
      nivel: ciUsado < 55 ? "alto" : "moderado",
      icono: "assignment_late",
      color: "#dc2626",
      evidencia: [
        `CI Total = ${CIT}${ICG ? ` | ICG = ${ICG} (uso recomendado si IVP discrepante)` : ""}`,
        `Umbral DSM-5 para DI: CI ≤ ~65-75 en dos pruebas + déficits adaptativos.`,
        `Verificar: ¿aplicación válida? ¿Sin barrera sensorial o idiomática?`,
      ],
      sugerencia: "Diagnóstico requiere: CI < ~70 en dos pruebas independientes Y déficits en conducta adaptativa (Vineland, ABAS). Si IVP es muy discrepante, el ICG puede ser más representativo. Reportar contexto sociocultural.",
    });
  }

  /* ─── 6. DCL / Deterioro cognitivo — Adulto mayor */
  if (edad != null && edad >= 55) {
    const afectados = disponibles.filter((v) => v < 85).length;
    const memoriaAfectada = subtests.some(
      (s) => (s.nombre_prueba?.toLowerCase().includes("recuerdo") ||
               s.nombre_prueba?.toLowerCase().includes("memoria") ||
               s.test_id?.toLowerCase().includes("grober")) &&
              s.puntaje_escalar < 7
    );
    if (afectados >= 2 || (afectados >= 1 && IVP != null && IVP < 80)) {
      patrones.push({
        tipo: afectados >= 3
          ? "Perfil compatible con Deterioro Cognitivo Leve multi-dominio (DCL-md)"
          : memoriaAfectada
          ? "Perfil compatible con DCL amnésico (posible Alzheimer temprano)"
          : "Enlentecimiento cognitivo en adulto mayor — evaluar DCL",
        nivel: afectados >= 3 ? "alto" : "moderado",
        icono: "elderly",
        color: "#ea580c",
        evidencia: [
          `Edad: ${edad} años — grupo de riesgo para DCL`,
          `Índices < 85: ${disponibles.filter((v) => v < 85).length} de ${disponibles.length}`,
          memoriaAfectada ? `Afectación de memoria episódica verbal identificada.` : null,
          IVP != null ? `IVP = ${IVP}${IVP < 80 ? " (enlentecimiento significativo)" : ""}` : null,
          `Descartar: depresión (Yesavage ≥ 5), hipotiroidismo, B12/ácido fólico, medicación.`,
        ].filter(Boolean),
        sugerencia: "Aplicar GDS-15 (Yesavage) + FAQ o Barthel para funcionalidad. MoCA / Grober-Buschke si no se realizaron. Neuroimagen y laboratorios. Seguimiento en 6-12 meses para delimitar progresión.",
      });
    }
  }

  /* ─── 7. TCE / Daño cerebral adquirido — velocidad + ejecutivo + memoria */
  if (IVP != null && IVP < 85 && disponibles.length >= 3) {
    const ejecutivoAfectado = IMT != null && IMT < 85;
    const perfilFocalVP = Math.max(ICV ?? 0, IRP ?? 0) - IVP >= 20;
    const historialTCE = subtests.some(
      (s) => s.test_id?.toLowerCase().includes("tmt") && s.puntaje_escalar < 7
    );
    if (ejecutivoAfectado && perfilFocalVP && (edad == null || edad < 55)) {
      patrones.push({
        tipo: "Perfil sugestivo de secuela neurológica (TCE / ACV / tóxico)",
        nivel: "moderado",
        icono: "emergency",
        color: "#b91c1c",
        evidencia: [
          `IVP = ${IVP} + IMT = ${IMT} — velocidad y memoria de trabajo afectadas.`,
          `Otras habilidades relativamente preservadas (ICV=${ICV ?? "N/D"}, IRP=${IRP ?? "N/D"}).`,
          historialTCE ? `TMT-B bajo en rango — apoya afectación atencional-ejecutiva.` : null,
        ].filter(Boolean),
        sugerencia: "Evaluar antecedentes de TCE, ACV, exposición tóxica o trastorno del sueño. Aplicar PASAT, TMT-B, pruebas de velocidad de procesamiento. Neuroimagen si no se ha realizado.",
      });
    }
  }

  /* ─── 8. Perfil homogéneo promedio-alto — Sin hallazgos clínicos */
  if (promGeneral >= 95 && (!islas || !islas.isHeterogeneo) && CIT != null && CIT >= 90) {
    patrones.push({
      tipo: "Funcionamiento cognitivo en rango esperado",
      nivel: "positivo",
      icono: "check_circle",
      color: "#10b981",
      evidencia: [
        `CI Total = ${CIT}${ICG ? ` | ICG = ${ICG}` : ""} — rango promedio o superior`,
        `Índices cognitivos homogéneos sin discrepancias significativas`,
        `No se detectan patrones sugestivos de trastorno cognitivo mayor`,
      ],
      sugerencia: "Considerar factores emocionales (ansiedad, depresión), contextuales (motivación, sueño) o de dominio específico si persisten quejas cognitivas subjetivas.",
    });
  }

  return patrones;
}

/* ── Generador de texto de observaciones clínicas ────────────────── */
function generarTextoObservaciones(indices, islas, patrones, paciente) {
  const { ICV, IRP, IMT, IVP, CIT, ICG, ICC } = indices;
  const partes = [];

  /* ── Rendimiento general ── */
  if (CIT != null) {
    const cl = clasificarCI(CIT);
    const ciAlt = ICG ? ` El Índice de Capacidad General (ICG=${ICG}, ${clasificarCI(ICG)?.label || ""}) puede ser más representativo cuando existen discrepancias significativas entre índices.` : "";
    partes.push(
      `En la evaluación neuropsicológica, el/la evaluado/a obtuvo un Coeficiente Intelectual Total de ${CIT} puntos ` +
      `(${cl?.label || ""}), ubicándose en rango ${cl?.label?.toLowerCase() || ""} para su grupo normativo de referencia.` +
      ciAlt
    );
  }

  /* ── Análisis de índices ── */
  const lineasIndices = [];
  if (ICV != null) lineasIndices.push(`Comprensión Verbal [ICV=${ICV} — ${clasificarCI(ICV)?.label || ""}]`);
  if (IRP != null) lineasIndices.push(`Razonamiento Perceptual [IRP=${IRP} — ${clasificarCI(IRP)?.label || ""}]`);
  if (IMT != null) lineasIndices.push(`Memoria de Trabajo [IMT=${IMT} — ${clasificarCI(IMT)?.label || ""}]`);
  if (IVP != null) lineasIndices.push(`Velocidad de Procesamiento [IVP=${IVP} — ${clasificarCI(IVP)?.label || ""}]`);
  if (lineasIndices.length > 0) {
    partes.push(`El análisis por índices cognitivos reveló: ${lineasIndices.join("; ")}.`);
  }

  /* ── Heterogeneidad del perfil ── */
  if (islas?.isHeterogeneo) {
    const fortalezasStr = islas.fortalezas.slice(0, 4).join(", ") || "ninguna identificada";
    const debilidadesStr = islas.debilidades.slice(0, 4).join(", ") || "ninguna identificada";
    partes.push(
      `El perfil cognitivo muestra variabilidad intraindividual significativa (rango = ${islas.rango} puntos; ` +
      `DS intra = ${islas.desv}), lo que indica un desarrollo disarmónico de las habilidades. ` +
      `Se identificaron fortalezas en: ${fortalezasStr}; y dificultades relativas en: ${debilidadesStr}. ` +
      `Este patrón heterogéneo debe interpretarse con análisis cualitativo específico por dominio cognitivo.`
    );
  } else if (islas && !islas.isHeterogeneo) {
    partes.push(
      `El perfil cognitivo muestra relativa homogeneidad entre subtests (rango = ${islas.rango} puntos), ` +
      `sin discrepancias intraindividuales de relevancia clínica.`
    );
  }

  /* ── Patrones específicos ── */
  for (const p of patrones) {
    if (p.nivel === "positivo") {
      partes.push(
        `El conjunto de resultados no evidencia patrones sugestivos de trastorno cognitivo mayor. ` +
        `Si persisten quejas subjetivas, se recomienda evaluación de factores emocionales y contextuales.`
      );
      continue;
    }
    if (p.tipo.includes("TDAH")) {
      partes.push(
        `Se identificó una discrepancia significativa entre el rendimiento en habilidades cristalizadas ` +
        `(lenguaje y razonamiento) y los procesos ejecutivo-atencionales (memoria de trabajo y velocidad de procesamiento), ` +
        `patrón consistente con dificultades en atención sostenida, control inhibitorio y regulación del comportamiento.`
      );
    } else if (p.tipo.includes("Tempo") || p.tipo.includes("CDHS")) {
      partes.push(
        `La velocidad de procesamiento se encontró significativamente disminuida en relación con el resto ` +
        `de las habilidades cognitivas evaluadas, sugiriendo un enlentecimiento selectivo que puede manifestarse ` +
        `como dificultad para responder con rapidez en tareas cotidianas, sin reflejar un déficit en la comprensión o el razonamiento.`
      );
    } else if (p.tipo.includes("DCL") || p.tipo.includes("Deterioro")) {
      partes.push(
        `El perfil cognitivo, en el contexto etario del/la evaluado/a, muestra características compatibles ` +
        `con deterioro cognitivo leve. Se recomienda complementar con evaluación funcional, estado de ánimo ` +
        `(GDS-15) y seguimiento longitudinal a los 6-12 meses para definir progresión.`
      );
    } else if (p.tipo.includes("DEA") || p.tipo.includes("lectoescritura")) {
      partes.push(
        `El patrón de rendimiento sugiere posibles dificultades específicas en el procesamiento verbal ` +
        `con habilidades visoperceptuales relativamente preservadas, lo que amerita evaluación específica ` +
        `de lectura, escritura y conciencia fonológica.`
      );
    } else if (p.tipo.includes("secuela") || p.tipo.includes("TCE")) {
      partes.push(
        `El perfil muestra afectación diferencial en velocidad de procesamiento y memoria de trabajo ` +
        `con relativa preservación del lenguaje y el razonamiento, patrón compatible con secuela ` +
        `de lesión cerebral adquirida. Se recomienda evaluar antecedentes de TCE, ACV o exposición tóxica.`
      );
    } else if (p.tipo.includes("Discapacidad")) {
      partes.push(
        `Los resultados indican un CI Total en rango que pudiera ser compatible con discapacidad intelectual. ` +
        `Para confirmar el diagnóstico se requiere: evaluación de conducta adaptativa con escala estandarizada ` +
        `(Vineland-3 o ABAS-3), descarte de barreras sensoriales, lingüísticas o motivacionales, ` +
        `y repetición de la evaluación en condiciones óptimas.`
      );
    }
  }

  if (partes.length === 0) {
    return "Complete la evaluación con al menos 4 subtests o 2 índices compuestos para generar el texto de observaciones automático.";
  }

  return partes.join("\n\n");
}

/* ══════════════════════════════════════════════════════════════════════
 * Componente principal
 * ══════════════════════════════════════════════════════════════════════ */
export default function ClinicalInterpretationPanel({ resultados, edad }) {
  const [textoCopiado, setTextoCopiado] = useState(false);
  const [mostrarTexto, setMostrarTexto] = useState(false);

  const subtests = useMemo(
    () =>
      (resultados || []).filter(
        (r) => r.puntaje_escalar != null && r.puntaje_escalar !== 9999
      ),
    [resultados]
  );

  const indices = useMemo(() => analizarIndices(resultados || []), [resultados]);
  const islas   = useMemo(() => detectarIslasHabilidad(subtests), [subtests]);
  const patrones = useMemo(
    () => detectarPatrones(indices, islas, subtests, edad),
    [indices, islas, subtests, edad]
  );
  const textoObs = useMemo(
    () => generarTextoObservaciones(indices, islas, patrones, { edad }),
    [indices, islas, patrones, edad]
  );

  if (subtests.length < 4 && Object.values(indices).every((v) => v == null)) {
    return null;
  }

  const copiar = () => {
    navigator.clipboard?.writeText(textoObs).then(() => {
      setTextoCopiado(true);
      setTimeout(() => setTextoCopiado(false), 2000);
    });
  };

  /* ── Nivel badge ── */
  const nivelBadge = {
    alto:       { bg: "#fee2e2", text: "#991b1b", label: "Hallazgo importante" },
    moderado:   { bg: "#fef3c7", text: "#92400e", label: "Hallazgo moderado"   },
    informativo:{ bg: "#dbeafe", text: "#1e40af", label: "Informativo"         },
    positivo:   { bg: "#d1fae5", text: "#065f46", label: "Sin hallazgos patológicos" },
  };

  return (
    <Card className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-extrabold flex items-center gap-2">
          <I name="psychology" style={{ color: TEAL }} />
          Interpretación Clínica Asistida
        </h3>
        <span className="text-[9px] italic" style={{ color: "var(--ns-muted)" }}>
          Análisis automático — no reemplaza el juicio clínico
        </span>
      </div>

      {/* ── Islas de habilidad ── */}
      {islas && (
        <div className="rounded-xl p-4 border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          <div className="flex items-center gap-2 mb-2">
            <I name="bar_chart" className="text-base" style={{ color: TEAL }} />
            <span className="text-xs font-bold">Análisis de homogeneidad del perfil</span>
            <span
              className="text-[10px] px-2 py-0.5 rounded-full font-bold"
              style={
                islas.isHeterogeneo
                  ? { background: "#fef3c7", color: "#92400e" }
                  : { background: "#d1fae5", color: "#065f46" }
              }
            >
              {islas.isHeterogeneo ? "Perfil Heterogéneo" : "Perfil Homogéneo"}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div>
              <p className="text-[10px] text-gray-500">Rango</p>
              <p className="text-lg font-extrabold">{islas.rango} pts</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500">Media</p>
              <p className="text-lg font-extrabold">{islas.media}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500">DS Intra</p>
              <p className="text-lg font-extrabold">{islas.desv}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500">Subtests</p>
              <p className="text-lg font-extrabold">{subtests.length}</p>
            </div>
          </div>
          {islas.fortalezas.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              <span className="text-[10px] font-bold text-emerald-700 mr-1">Fortalezas:</span>
              {islas.fortalezas.map((f) => (
                <span key={f} className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">{f}</span>
              ))}
            </div>
          )}
          {islas.debilidades.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              <span className="text-[10px] font-bold text-red-700 mr-1">Dificultades:</span>
              {islas.debilidades.map((d) => (
                <span key={d} className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-800 font-medium">{d}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Patrones clínicos detectados ── */}
      {patrones.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-bold" style={{ color: "var(--ns-muted)" }}>
            Patrones cognitivos identificados
          </p>
          {patrones.map((p, i) => {
            const badge = nivelBadge[p.nivel] || nivelBadge.informativo;
            return (
              <div
                key={i}
                className="rounded-xl p-4 border"
                style={{ borderColor: p.color + "40", background: p.color + "08" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <I name={p.icono} className="text-base" style={{ color: p.color }} />
                  <span className="text-xs font-extrabold" style={{ color: p.color }}>
                    {p.tipo}
                  </span>
                  <span
                    className="ml-auto text-[9px] px-2 py-0.5 rounded-full font-bold"
                    style={{ background: badge.bg, color: badge.text }}
                  >
                    {badge.label}
                  </span>
                </div>
                <ul className="space-y-1 mb-2">
                  {p.evidencia.map((e, j) => (
                    <li key={j} className="text-[11px] flex items-start gap-1" style={{ color: "var(--ns-text)" }}>
                      <span className="text-[10px] mt-0.5">•</span>
                      <span>{e}</span>
                    </li>
                  ))}
                </ul>
                <div
                  className="rounded-lg px-3 py-2 text-[11px] italic"
                  style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}
                >
                  <I name="lightbulb" className="text-xs mr-1" />
                  {p.sugerencia}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Índices rápidos ── */}
      {Object.values(indices).some((v) => v != null) && (
        <div className="rounded-xl p-4 border" style={{ borderColor: "var(--ns-card-b)" }}>
          <p className="text-xs font-bold mb-3" style={{ color: "var(--ns-muted)" }}>
            Resumen de índices compuestos
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {[
              { label: "CIT",  val: indices.CIT,  tooltip: "Coeficiente Intelectual Total" },
              { label: "ICV",  val: indices.ICV,  tooltip: "Índice Comprensión Verbal" },
              { label: "IRP",  val: indices.IRP,  tooltip: "Índice Razonamiento Perceptual" },
              { label: "IMT",  val: indices.IMT,  tooltip: "Índice Memoria de Trabajo" },
              { label: "IVP",  val: indices.IVP,  tooltip: "Índice Velocidad de Procesamiento" },
            ].map(({ label, val, tooltip }) => {
              if (val == null) return null;
              const cl = clasificarCI(val);
              return (
                <div key={label} className="text-center p-2 rounded-lg" title={tooltip}
                  style={{ background: "var(--ns-subtle)" }}>
                  <p className="text-[10px] text-gray-500 font-bold">{label}</p>
                  <p className="text-xl font-extrabold" style={{ color: cl?.color }}>{val}</p>
                  <p className="text-[9px]" style={{ color: cl?.color }}>{cl?.label}</p>
                </div>
              );
            })}
          </div>
          {/* ICG / ICC — alternativas al CIT */}
          {(indices.ICG != null || indices.ICC != null) && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
              <p className="text-[10px] font-bold mb-2" style={{ color: "var(--ns-muted)" }}>
                Índices alternativos (cuando IVP/IMT es discrepante):
              </p>
              <div className="flex gap-3">
                {indices.ICG != null && (() => {
                  const cl = clasificarCI(indices.ICG);
                  return (
                    <div className="text-center p-2 rounded-lg flex-1"
                      title="Índice de Capacidad General — más estable que CIT cuando hay discrepancia de IVP"
                      style={{ background: `${TEAL}10`, border: `1px solid ${TEAL}30` }}>
                      <p className="text-[10px] font-bold" style={{ color: TEAL }}>ICG</p>
                      <p className="text-xl font-extrabold" style={{ color: cl?.color }}>{indices.ICG}</p>
                      <p className="text-[9px]" style={{ color: cl?.color }}>{cl?.label}</p>
                    </div>
                  );
                })()}
                {indices.ICC != null && (() => {
                  const cl = clasificarCI(indices.ICC);
                  return (
                    <div className="text-center p-2 rounded-lg flex-1"
                      title="Índice de Competencia Cognitiva — refleja funciones atencionales y ejecutivas"
                      style={{ background: `${TEAL}10`, border: `1px solid ${TEAL}30` }}>
                      <p className="text-[10px] font-bold" style={{ color: TEAL }}>ICC</p>
                      <p className="text-xl font-extrabold" style={{ color: cl?.color }}>{indices.ICC}</p>
                      <p className="text-[9px]" style={{ color: cl?.color }}>{cl?.label}</p>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Texto clínico borrador ── */}
      <div className="rounded-xl border" style={{ borderColor: "var(--ns-card-b)" }}>
        <button
          className="w-full flex items-center justify-between px-4 py-3 text-xs font-bold"
          onClick={() => setMostrarTexto((v) => !v)}
          style={{ color: "var(--ns-text)" }}
        >
          <span className="flex items-center gap-2">
            <I name="edit_note" className="text-base" style={{ color: TEAL }} />
            Texto borrador para observaciones clínicas
          </span>
          <I name={mostrarTexto ? "expand_less" : "expand_more"} className="text-base" />
        </button>
        {mostrarTexto && (
          <div className="px-4 pb-4 space-y-3">
            <div
              className="rounded-lg p-3 text-[12px] leading-relaxed"
              style={{ background: "var(--ns-subtle)", color: "var(--ns-text)" }}
            >
              {textoObs}
            </div>
            <div className="flex gap-2">
              <button
                onClick={copiar}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all"
                style={{ background: textoCopiado ? "#d1fae5" : TEAL + "15", color: textoCopiado ? "#065f46" : TEAL }}
              >
                <I name={textoCopiado ? "check" : "content_copy"} className="text-sm" />
                {textoCopiado ? "¡Copiado!" : "Copiar texto"}
              </button>
              <p className="text-[10px] self-center italic" style={{ color: "var(--ns-muted)" }}>
                Revise y edite antes de incluir en el informe.
              </p>
            </div>
          </div>
        )}
      </div>

      <p className="text-[9px] italic text-center" style={{ color: "var(--ns-muted)" }}>
        Análisis generado automáticamente con base en los puntajes ingresados.
        Los patrones son sugestivos, no diagnósticos. El profesional debe validar con historia clínica,
        observación conductual y criterios DSM-5/CIE-11.
      </p>
    </Card>
  );
}
