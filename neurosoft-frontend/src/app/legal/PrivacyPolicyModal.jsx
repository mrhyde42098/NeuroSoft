/* ═══════════════════════════════════════════════════════════════════════
 * src/app/legal/PrivacyPolicyModal.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Modal de Política de Privacidad y Tratamiento de Datos Personales
 * Cumplimiento: Ley 1581 de 2012, Decreto 1377 de 2013 (Colombia)
 * Uso: <PrivacyPolicyModal open={bool} onClose={fn} />
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef } from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";

/* ─── Secciones de la política ────────────────────────────── */
const SECCIONES = [
  {
    icon: "business",
    titulo: "1. Responsable del Tratamiento",
    texto: `NeuroSoft es el responsable del tratamiento de los datos personales recopilados a través de esta aplicación. Los datos institucionales (nombre, NIT, dirección, email de contacto) se configuran en el módulo de Configuración y son utilizados exclusivamente para identificar al prestador de servicios en los informes clínicos generados.

Para ejercer sus derechos o resolver inquietudes sobre privacidad, puede comunicarse al correo electrónico registrado en la configuración de la institución.`,
  },
  {
    icon: "database",
    titulo: "2. Datos Personales que se Tratan",
    texto: `NeuroSoft recopila y trata las siguientes categorías de datos personales:

• Datos de identificación del paciente: nombres, apellidos, fecha de nacimiento, documento de identidad, escolaridad, lateralidad y datos de contacto del acudiente (en casos pediátricos).

• Datos clínicos y de salud: antecedentes personales y familiares, motivo de consulta, resultados de evaluaciones neuropsicológicas (puntajes, interpretaciones), observaciones conductuales y diagnósticos de impresión (CIE-10/DSM-5).

• Datos del profesional: nombre, registro profesional, título, especialidad y firma digital, usados para firmar informes.

• Datos de uso del sistema: registros de auditoría (acciones realizadas, fecha/hora), útiles para la trazabilidad clínica requerida por la Resolución 1995 de 1999 (Historia Clínica).`,
  },
  {
    icon: "verified_user",
    titulo: "3. Finalidad del Tratamiento",
    texto: `Los datos personales son tratados con las siguientes finalidades:

• Gestión de la historia clínica electrónica del paciente conforme a la Resolución 1995 de 1999.
• Generación de informes neuropsicológicos en formato PDF.
• Programación y seguimiento de citas y sesiones de rehabilitación cognitiva.
• Comparación longitudinal de resultados para seguimiento del progreso clínico.
• Cumplimiento de obligaciones legales aplicables a los prestadores de servicios de salud.

NeuroSoft NO utiliza los datos clínicos de los pacientes para entrenar modelos de inteligencia artificial, ni los comparte con terceros sin consentimiento explícito del titular.`,
  },
  {
    icon: "lock",
    titulo: "4. Almacenamiento y Seguridad",
    texto: `Todos los datos son almacenados localmente en la base de datos de la institución (SQLite), que reside en el equipo o servidor del prestador de servicios. NeuroSoft, como software, no transmite datos clínicos a servidores externos salvo que el profesional utilice explícitamente la función de compartir informes vía enlace (telemedicina), en cuyo caso el enlace es cifrado y de tiempo limitado.

Se recomienda al prestador de servicios:
• Realizar copias de seguridad periódicas desde el módulo "Respaldo".
• Mantener el sistema operativo y el software actualizados.
• Restringir el acceso a usuarios autorizados con contraseña segura.
• Considerar el cifrado del disco o la carpeta de datos según lo exige la normativa aplicable.`,
  },
  {
    icon: "person_check",
    titulo: "5. Derechos del Titular (ARCO)",
    texto: `Conforme a la Ley 1581 de 2012, los titulares de datos personales tienen los siguientes derechos:

• Acceso: Conocer los datos personales que se tienen sobre usted.
• Rectificación: Solicitar la corrección de datos inexactos o incompletos.
• Cancelación/Supresión: Solicitar la eliminación de sus datos cuando no sean necesarios para la finalidad para la que fueron recabados, o cuando haya revocado su consentimiento.
• Oposición: Oponerse al tratamiento de sus datos en los casos previstos por la ley.

Para ejercer estos derechos, el titular o su representante legal debe dirigirse directamente al profesional o institución que administra el sistema NeuroSoft.`,
  },
  {
    icon: "description",
    titulo: "6. Base Legal y Normativa Aplicable",
    texto: `El tratamiento de datos personales en NeuroSoft se rige por:

• Ley 1581 de 2012 — Régimen General de Protección de Datos Personales (Colombia).
• Decreto 1377 de 2013 — Reglamentación de la Ley 1581.
• Resolución 1995 de 1999 — Normas para el manejo de la Historia Clínica.
• Resolución 2654 de 2019 — Telesalud y telemedicina.
• Ley 23 de 1981 — Ética médica.
• Código Deontológico y Bioético de Psicología (Ley 1090 de 2006).

El consentimiento informado para la evaluación y el tratamiento de datos de salud debe ser obtenido por el profesional previamente al inicio de cualquier proceso de evaluación, conforme al módulo de Consentimiento Informado integrado en NeuroSoft.`,
  },
  {
    icon: "update",
    titulo: "7. Vigencia y Actualizaciones",
    texto: `Esta política de privacidad puede ser actualizada en versiones posteriores del software para reflejar cambios normativos o funcionales. Se recomienda revisar esta sección en cada actualización de la aplicación.

La conservación de la historia clínica se rige por los plazos establecidos en la normativa vigente (mínimo 20 años para adultos; hasta los 25 años de edad para menores). El profesional es responsable de garantizar la conservación y confidencialidad de los datos durante este periodo.`,
  },
];

/* ─── Componente principal ─────────────────────────────────── */
export default function PrivacyPolicyModal({ open, onClose }) {
  const scrollRef = useRef(null);

  /* Cerrar con Escape */
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  /* Bloquear scroll del body cuando está abierto */
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-3xl overflow-hidden shadow-2xl animate-[fadeIn_0.2s_ease-out]"
        style={{ background: "var(--ns-card)", color: "var(--ns-text)" }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-8 py-6 border-b shrink-0"
          style={{
            borderColor: "var(--ns-card-b)",
            background: `linear-gradient(135deg,${NAVY}f0,${TEAL}30)`,
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center"
              style={{ background: `${TEAL}20` }}
            >
              <I name="policy" fill className="text-xl" style={{ color: TEAL }} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                Política de Privacidad y Protección de Datos
              </h2>
              <p className="text-xs" style={{ color: "#94a3b8" }}>
                Ley 1581 de 2012 · Decreto 1377 de 2013 · Colombia
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-white/10 transition-colors text-white/60 hover:text-white"
          >
            <I name="close" className="text-xl" />
          </button>
        </div>

        {/* Aviso de clasificación */}
        <div
          className="px-8 py-3 flex items-center gap-2 text-xs font-semibold shrink-0 border-b"
          style={{
            background: `${TEAL}10`,
            borderColor: `${TEAL}30`,
            color: TEAL,
          }}
        >
          <I name="info" className="text-sm" />
          Este software trata datos de salud (datos sensibles). Su tratamiento requiere consentimiento
          explícito del titular conforme al Art. 6 de la Ley 1581 de 2012.
        </div>

        {/* Cuerpo scrolleable */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
          {SECCIONES.map((sec, idx) => (
            <section key={idx}>
              <div className="flex items-center gap-2 mb-3">
                <I
                  name={sec.icon}
                  fill
                  className="text-base shrink-0"
                  style={{ color: TEAL }}
                />
                <h3 className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>
                  {sec.titulo}
                </h3>
              </div>
              <div
                className="text-xs leading-relaxed whitespace-pre-line pl-6"
                style={{ color: "var(--ns-muted)" }}
              >
                {sec.texto}
              </div>
              {idx < SECCIONES.length - 1 && (
                <div className="mt-6 border-b" style={{ borderColor: "var(--ns-card-b)" }} />
              )}
            </section>
          ))}

          {/* Pie legal */}
          <div
            className="mt-4 p-4 rounded-2xl text-[10px] text-center leading-relaxed"
            style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}
          >
            NeuroSoft es una herramienta de apoyo clínico. No sustituye el juicio profesional ni
            la relación clínica. El profesional de la salud es el responsable del tratamiento de
            los datos de sus pacientes conforme a la normativa vigente.
            <br />
            <span className="font-bold" style={{ color: TEAL }}>
              NeuroSoft App
            </span>
          </div>
        </div>

        {/* Footer con botón cerrar */}
        <div
          className="px-8 py-4 border-t flex items-center justify-between shrink-0"
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}
        >
          <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
            Versión del documento: 2.1 · Última actualización: mayo 2025
          </p>
          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-full text-sm font-bold text-white transition-all hover:-translate-y-0.5 active:scale-95"
            style={{
              background: TEAL,
              boxShadow: "0 6px 16px -4px rgba(13,148,136,0.4)",
            }}
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
