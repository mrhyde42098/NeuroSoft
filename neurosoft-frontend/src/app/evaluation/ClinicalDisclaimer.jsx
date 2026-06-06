/* src/app/evaluation/ClinicalDisclaimer.jsx — Disclaimer clínico para informes y UI */
import React from "react";
import SectionCard from "../../ui/SectionCard.jsx";

export default function ClinicalDisclaimer({ modo = "banner", className = "" }) {
  const contenido = {
    es: {
      titulo: "Aviso Clínico",
      texto: "NeuroSoft es una herramienta de apoyo a la decisión clínica. Los puntajes estandarizados se calculan con base en normas psicométricas publicadas, pero la interpretación final, el diagnóstico y las recomendaciones son responsabilidad exclusiva del profesional de la salud evaluador. Este software no sustituye el juicio clínico.",
      corto: "Herramienta de apoyo clínico. No sustituye juicio profesional.",
    }
  };

  const t = contenido.es;

  if (modo === "banner") {
    return (
      <SectionCard
        title={t.titulo}
        icon="medical_services"
        eyebrow="Responsabilidad profesional"
        className={className}
      >
        <p className="text-xs leading-relaxed" style={{ color: "var(--ns-text)" }}>{t.texto}</p>
      </SectionCard>
    );
  }

  if (modo === "footer") {
    return (
      <div className={`text-center border-t pt-2 mt-4 ${className}`} style={{ borderColor: "var(--ns-card-b)" }}>
        <p className="text-[9px] text-gray-400 italic">{t.corto}</p>
      </div>
    );
  }

  if (modo === "pdf") {
    return (
      <div className={`text-[8px] text-gray-500 italic leading-tight ${className}`}>
        {t.texto}
      </div>
    );
  }

  return null;
}
