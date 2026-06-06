/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/RegisterPage.jsx — Alta de paciente (3 secciones)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError, _fieldNames } from "../../api/client.js";
import { useAuth, useToast } from "../../contexts.jsx";
import {
  Btn, Card, I, Input, Label, MsgBanner, Sel, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import PrivacyPolicyModal from "../legal/PrivacyPolicyModal.jsx";
import ConsentModal from "./ConsentModal.jsx";
import { ASEGURADORES_COLOMBIA, REGIMENES } from "../../data/aseguradoresColombia.js";
import { CUPS_PSICOLOGIA } from "../../data/cupsPsicologia.js";

const BTN_FOOT = "!min-h-[44px] !py-2.5 !px-5 !text-sm";

function FieldBlock({ title, icon, children }) {
  return (
    <div
      className="rounded-2xl p-5 border space-y-4"
      style={{ borderColor: `${TEAL}28`, background: `${TEAL}06` }}
    >
      <p className="text-xs font-bold flex items-center gap-2" style={{ color: TEAL }}>
        {icon && <I name={icon} className="text-sm" />}{title}
      </p>
      {children}
    </div>
  );
}

/* Catálogos de apoyo para los desplegables del registro */
const TIPOS_DOC = [
  { v: "CC", l: "CC — Cédula de ciudadanía" },
  { v: "TI", l: "TI — Tarjeta de identidad" },
  { v: "RC", l: "RC — Registro civil" },
  { v: "CE", l: "CE — Cédula de extranjería" },
  { v: "PA", l: "PA — Pasaporte" },
  { v: "PEP", l: "PEP — Permiso especial de permanencia" },
  { v: "PT", l: "PT — Permiso por protección temporal" },
  { v: "MS", l: "MS — Menor sin identificación" },
  { v: "AS", l: "AS — Adulto sin identificación" },
  { v: "NV", l: "NV — Certificado de nacido vivo" },
  { v: "DE", l: "DE — Documento extranjero" },
];
const CIUDADES_CO = [
  "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Cúcuta",
  "Bucaramanga", "Pereira", "Santa Marta", "Ibagué", "Manizales",
  "Villavicencio", "Pasto", "Neiva", "Armenia", "Soacha", "Soledad",
  "Valledupar", "Montería", "Sincelejo", "Popayán", "Tunja", "Riohacha",
  "Florencia", "Yopal", "Quibdó", "Mocoa", "San Andrés", "Leticia",
  "Arauca", "Inírida", "Mitú", "Puerto Carreño",
];
const LOCALIDADES_BOGOTA = [
  "Usaquén", "Chapinero", "Santa Fe", "San Cristóbal", "Usme", "Tunjuelito",
  "Bosa", "Kennedy", "Fontibón", "Engativá", "Suba", "Barrios Unidos",
  "Teusaquillo", "Los Mártires", "Antonio Nariño", "Puente Aranda",
  "La Candelaria", "Rafael Uribe Uribe", "Ciudad Bolívar", "Sumapaz",
];
/* Diagnósticos CIE-10 frecuentes en neuropsicología (códigos oficiales) */
const CIE10_FRECUENTES = [
  { c: "F90", n: "TDAH" }, { c: "F84", n: "Trastorno del espectro autista" },
  { c: "F70", n: "Discapacidad intelectual leve" }, { c: "F81", n: "Trastorno del aprendizaje" },
  { c: "F060", n: "Trastorno mental orgánico" }, { c: "F32", n: "Episodio depresivo" },
  { c: "F41", n: "Trastorno de ansiedad" }, { c: "F432", n: "Trastorno de adaptación" },
  { c: "F431", n: "Estrés postraumático" }, { c: "G3184", n: "Deterioro cognitivo leve" },
  { c: "G30", n: "Enfermedad de Alzheimer" }, { c: "F03", n: "Demencia no especificada" },
  { c: "F09", n: "Trastorno mental orgánico no especificado" }, { c: "Z04", n: "Examen/observación (peritaje)" },
  { c: "F809", n: "Trastorno del desarrollo del habla/lenguaje" }, { c: "F880", n: "Otros trastornos del desarrollo psicológico" },
  { c: "G319", n: "Enfermedad degenerativa del SNC no especificada" },
];

export default function RegisterPage({ setPage }) {
  const { user } = useAuth();
  const toast = useToast();
  const [sec, setSec] = useState(0);
  const [privOpen, setPrivOpen] = useState(false);
  const [f, sF] = useState({
    tipo_documento: "CC", numero_documento: "",
    primer_nombre: "", segundo_nombre: "", primer_apellido: "", segundo_apellido: "",
    fecha_nacimiento: "", sexo: "H",
    escolaridad: "Secundaria Completa", lateralidad: "Diestro",
    estado_civil: "", lugar_nacimiento: "",
    telefono: "", correo: "", direccion: "", ciudad: "Bogotá", localidad: "",
    pais: "Colombia", pais_modo: "co",
    estrato: null, ocupacion: "", acompanante: "", grupo_etnico: "",
    profesional_id: "",
    fecha_atencion: new Date().toISOString().split("T")[0],
    motivo_consulta: "", remite: "",     eps: "", regimen: "", orden_medica_no: "", autorizacion_eps: "",
    telefono_acompanante: "", necesidades_accesibilidad: "",
    discapacidad: "", codigo_rips: "", cups: "", finalidad_consulta: "",
    numero_sesiones: 1, donante: false,
    via_atencion: "mixto",
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [showConsent, setShowConsent] = useState(false);
  const [savedPatientId, setSavedPatientId] = useState(null);
  const [savedPatientName, setSavedPatientName] = useState("");
  const [savedPatientEmail, setSavedPatientEmail] = useState("");
  const [postSaveDest, setPostSaveDest] = useState(null);
  const set = (k, val) => sF((o) => ({ ...o, [k]: val }));
  const [profs, setProfs] = useState([]);

  useEffect(() => {
    api.get("/api/v1/config/profesionales").then(d => setProfs(d || [])).catch(() => toast.error("Error cargando profesionales"));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const edad = f.fecha_nacimiento
    ? Math.floor((new Date() - new Date(f.fecha_nacimiento)) / (365.25 * 86400000))
    : null;
  const ripsAuto = edad !== null
    ? (edad < 6 ? "F880" : (edad < 18 ? "F809" : (edad < 50 ? "F060" : "G319")))
    : "";
  useEffect(() => {
    if (ripsAuto && !f.codigo_rips) set("codigo_rips", ripsAuto);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ripsAuto]);

  const save = async () => {
    const errs = [];
    if (!f.primer_nombre   || f.primer_nombre.trim().length   < 2) errs.push("Primer nombre: debe tener al menos 2 caracteres");
    if (!f.primer_apellido || f.primer_apellido.trim().length < 2) errs.push("Primer apellido: debe tener al menos 2 caracteres");
    if (!f.numero_documento|| f.numero_documento.trim().length< 4) errs.push("Número de documento: debe tener al menos 4 caracteres");
    if (!f.fecha_nacimiento) errs.push("Fecha de nacimiento: es obligatorio");
    if (!f.sexo)             errs.push("Sexo: es obligatorio");
    if (!f.escolaridad)      errs.push("Escolaridad: es obligatorio");
    if (f.fecha_nacimiento && f.fecha_atencion &&
        new Date(f.fecha_nacimiento) >= new Date(f.fecha_atencion)) {
      errs.push("Fecha de nacimiento: debe ser anterior a la fecha de atención");
    }
    if (errs.length > 0) {
      setMsg(errs.join(". "));
      setSec(0);
      return;
    }
    setSaving(true);
    setMsg("");
    try {
      const body = { ...f };
      if (!body.estrato)             delete body.estrato;
      if (!body.profesional_id)      delete body.profesional_id;
      if (!body.estado_civil)        delete body.estado_civil;
      if (!body.grupo_etnico)        delete body.grupo_etnico;
      if (!body.finalidad_consulta)  delete body.finalidad_consulta;
      if (!body.cups)                delete body.cups;
      if (!body.regimen) delete body.regimen;
      const paisModo = body.pais_modo;
      delete body.pais_modo;
      if (paisModo === "ext" && !body.pais?.trim()) {
        setMsg("País: indique el país de residencia");
        setSec(1);
        setSaving(false);
        return;
      }
      if (paisModo === "co" || !body.pais || body.pais === "Colombia") delete body.pais;
      [
        "lugar_nacimiento", "telefono", "correo", "direccion", "localidad",
        "ocupacion", "acompanante", "telefono_acompanante", "remite", "eps",
        "orden_medica_no", "autorizacion_eps", "necesidades_accesibilidad",
        "discapacidad", "motivo_consulta", "codigo_rips",
      ].forEach(k => { if (body[k] === "") delete body[k]; });
      const created = await api.post("/api/v1/patients/", body);
      setMsg("ok");
      const dest = {
        neuro: "evaluation",
        clinica: "therapy",
        rehab: "rehab",
        mixto: "patients",
      }[f.via_atencion] || "patients";
      const nombre = created.nombre_completo
        || `${created.primer_nombre || f.primer_nombre} ${created.primer_apellido || f.primer_apellido}`.trim();
      setSavedPatientId(created.id);
      setSavedPatientName(nombre);
      setSavedPatientEmail(created.correo || f.correo || "");
      setPostSaveDest(dest);
      setShowConsent(true);
    } catch (e) { setMsg(_parseError(e)); }
    setSaving(false);
  };

  const secs = ["Identificación", "Contacto y Demografía", "Datos de Consulta", "Vía de atención"];
  const VIA_OPTS = [
    { id: "neuro", label: "Evaluación neuropsicológica", desc: "Batería NPS, informes y baremos", icon: "psychology" },
    { id: "clinica", label: "Psicoterapia clínica", desc: "Sesiones SOAP, planes terapéuticos", icon: "self_improvement" },
    { id: "rehab", label: "Rehabilitación cognitiva", desc: "Plan y actividades de rehab", icon: "fitness_center" },
    { id: "mixto", label: "Mixto / por definir", desc: "Decidir módulo después del intake", icon: "hub" },
  ];
  const reqErr = (field) => msg && msg !== "ok" && msg.includes(_fieldNames[field] || field);
  const errCls = (field) => reqErr(field) ? "!border-red-400 !bg-red-50/50" : "";

  const finOpts = ["Diagnóstico", "Terapéutico", "Seguimiento", "Rehabilitación"];
  const esColombia = f.pais_modo === "co";

  const openConsent = () => {
    if (savedPatientId) {
      setShowConsent(true);
      return;
    }
    toast.info("Guarde el paciente primero para imprimir o enviar el consentimiento con sus datos.");
  };

  const closeConsent = () => {
    setShowConsent(false);
    if (postSaveDest) {
      setPage(postSaveDest);
      setPostSaveDest(null);
    }
  };

  return (
    <>
      <TopBar title="Registro de Paciente">
        <div className="text-right text-xs">
          <p className="font-bold">{user?.nombre_completo}</p>
          <p className="text-gray-400">Fecha: {f.fecha_atencion}</p>
        </div>
      </TopBar>
      <main className="p-8 max-w-7xl mx-auto space-y-6">
        <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? () => setMsg("") : null} />
        <div className="flex flex-wrap gap-2">
          {secs.map((s, i) => (
            <button key={s} onClick={() => setSec(i)}
              className="px-5 py-2.5 rounded-full text-xs font-bold transition-all border"
              style={sec === i
                ? { background: TEAL, color: "#fff", borderColor: TEAL, boxShadow: "0 4px 14px rgba(13,148,136,0.25)" }
                : { background: "var(--ns-card)", color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}>
              <span className="mr-1.5 opacity-80">{i + 1}.</span>{s}
            </button>
          ))}
        </div>

        {sec === 0 && (
          <Card className="p-8 space-y-6">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="badge" style={{ color: TEAL }} />Identificación del Paciente
            </h3>
            <FieldBlock title="Documento de identidad" icon="fingerprint">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div><Label>Tipo Doc. *</Label>
                  <Sel value={f.tipo_documento} onChange={(e) => set("tipo_documento", e.target.value)}>
                    {TIPOS_DOC.map(t => <option key={t.v} value={t.v}>{t.l}</option>)}
                  </Sel>
                </div>
                <div><Label>Número Documento *</Label>
                  <Input className={errCls("numero_documento")} value={f.numero_documento} onChange={(e) => set("numero_documento", e.target.value)} placeholder="1234567890" />
                </div>
                <div><Label>Sexo *</Label>
                  <Sel value={f.sexo} onChange={(e) => set("sexo", e.target.value)}>
                    <option value="H">Masculino</option><option value="M">Femenino</option>
                  </Sel>
                </div>
              </div>
            </FieldBlock>
            <FieldBlock title="Nombres y apellidos" icon="person">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div><Label>Primer Nombre *</Label><Input className={errCls("primer_nombre")} value={f.primer_nombre} onChange={(e) => set("primer_nombre", e.target.value)} /></div>
                <div><Label>Segundo Nombre</Label><Input value={f.segundo_nombre} onChange={(e) => set("segundo_nombre", e.target.value)} /></div>
                <div><Label>Primer Apellido *</Label><Input className={errCls("primer_apellido")} value={f.primer_apellido} onChange={(e) => set("primer_apellido", e.target.value)} /></div>
                <div><Label>Segundo Apellido</Label><Input value={f.segundo_apellido} onChange={(e) => set("segundo_apellido", e.target.value)} /></div>
              </div>
            </FieldBlock>
            <FieldBlock title="Edad y perfil demográfico" icon="cake">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label>Fecha Nacimiento *</Label>
                  <Input className={errCls("fecha_nacimiento")} type="date" value={f.fecha_nacimiento} onChange={(e) => set("fecha_nacimiento", e.target.value)} />
                  {edad !== null && (
                    <span className="inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold"
                      style={{ background: `${TEAL}18`, color: TEAL }}>
                      {edad} años — {edad < 6 ? "Preescolar" : edad < 18 ? "Infantil" : edad < 50 ? "Adulto Joven" : "Adulto Mayor"}
                    </span>
                  )}
                </div>
                <div><Label>Escolaridad *</Label>
                  <Sel value={f.escolaridad} onChange={(e) => set("escolaridad", e.target.value)}>
                    {["Preescolar","Primaria Incompleta","Primaria Completa","Secundaria Incompleta","Secundaria Completa","Técnico","Tecnólogo","Universitaria","Profesional","Especialización","Maestría","Doctorado","Analfabeta","No Aplica"].map(o => <option key={o}>{o}</option>)}
                  </Sel>
                </div>
                <div><Label>Lateralidad</Label>
                  <Sel value={f.lateralidad} onChange={(e) => set("lateralidad", e.target.value)}>
                    <option>Diestro</option><option>Zurdo</option><option>Ambidiestro</option><option>No Definida</option>
                  </Sel>
                </div>
                <div><Label>Estado Civil</Label>
                  <Sel value={f.estado_civil} onChange={(e) => set("estado_civil", e.target.value)}>
                    <option value="">-- Seleccionar --</option>
                    {["Soltero(a)","Casado(a)","Unión Libre","Divorciado(a)","Viudo(a)","Separado(a)","Menor de Edad"].map(o => <option key={o}>{o}</option>)}
                  </Sel>
                </div>
                <div className="sm:col-span-2"><Label>Lugar de Nacimiento</Label><Input value={f.lugar_nacimiento} onChange={(e) => set("lugar_nacimiento", e.target.value)} placeholder="Ciudad, departamento o país" /></div>
              </div>
            </FieldBlock>
          </Card>
        )}

        {sec === 1 && (
          <Card className="p-8 space-y-8">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="location_on" className="text-teal-600" />Contacto y Demografía
            </h3>
            <div className="grid grid-cols-4 gap-4">
              <div><Label>Teléfono</Label><Input value={f.telefono} onChange={(e) => set("telefono", e.target.value)} placeholder="3001234567" /></div>
              <div><Label>Correo Electrónico</Label><Input type="email" value={f.correo} onChange={(e) => set("correo", e.target.value)} placeholder="correo@email.com" /></div>
              <div className="col-span-2"><Label>Dirección</Label><Input value={f.direccion} onChange={(e) => set("direccion", e.target.value)} placeholder="Calle 123 # 45-67" /></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <div><Label>País</Label>
                <Sel value={esColombia ? "Colombia" : "__otro__"} onChange={(e) => {
                  if (e.target.value === "Colombia") {
                    sF((o) => ({ ...o, pais_modo: "co", pais: "Colombia", ciudad: "Bogotá" }));
                  } else {
                    sF((o) => ({ ...o, pais_modo: "ext", pais: "", ciudad: "", localidad: "" }));
                  }
                }}>
                  <option value="Colombia">Colombia</option>
                  <option value="__otro__">Otro país</option>
                </Sel>
              </div>
              {esColombia ? (
                <>
                  <div><Label>Ciudad</Label>
                    <Sel value={CIUDADES_CO.includes(f.ciudad) ? f.ciudad : "__otra__"} onChange={(e) => { const v = e.target.value; set("ciudad", v === "__otra__" ? "" : v); if (v !== "Bogotá") set("localidad", ""); }}>
                      {CIUDADES_CO.map(c => <option key={c}>{c}</option>)}
                      <option value="__otra__">Otra ciudad…</option>
                    </Sel>
                    {!CIUDADES_CO.includes(f.ciudad) && <Input className="mt-1" value={f.ciudad} onChange={(e) => set("ciudad", e.target.value)} placeholder="Escriba la ciudad" />}
                  </div>
                  <div><Label>Localidad / Barrio</Label>
                    {f.ciudad === "Bogotá"
                      ? <Sel value={f.localidad} onChange={(e) => set("localidad", e.target.value)}>
                          <option value="">-- Seleccionar --</option>
                          {LOCALIDADES_BOGOTA.map(l => <option key={l}>{l}</option>)}
                        </Sel>
                      : <Input value={f.localidad} onChange={(e) => set("localidad", e.target.value)} placeholder="Barrio / localidad" />}
                  </div>
                </>
              ) : (
                <>
                  <div><Label>País (texto)</Label><Input value={f.pais} onChange={(e) => set("pais", e.target.value)} placeholder="Ej: Ecuador" /></div>
                  <div><Label>Ciudad / Localidad</Label><Input value={f.ciudad} onChange={(e) => set("ciudad", e.target.value)} placeholder="Ciudad o barrio" /></div>
                </>
              )}
              <div><Label>Estrato</Label>
                <Sel value={f.estrato || ""} onChange={(e) => set("estrato", e.target.value ? parseInt(e.target.value, 10) : null)}>
                  <option value="">--</option>
                  {[1, 2, 3, 4, 5, 6].map(n => <option key={n} value={n}>{n}</option>)}
                </Sel>
              </div>
              <div><Label>Ocupación</Label><Input value={f.ocupacion} onChange={(e) => set("ocupacion", e.target.value)} placeholder="Ej: Estudiante" /></div>
              <div><Label>Grupo Étnico</Label>
                <Sel value={f.grupo_etnico} onChange={(e) => set("grupo_etnico", e.target.value)}>
                  <option value="">-- Ninguno --</option>
                  {["Indígena","Rom (Gitano)","Raizal","Palenquero","Negro/Afrocolombiano","Mestizo","Otro"].map(o => <option key={o}>{o}</option>)}
                </Sel>
              </div>
            </div>
            <FieldBlock title="Afiliación, acompañante y accesibilidad" icon="health_and_safety">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div><Label>Régimen</Label>
                  <Sel value={f.regimen} onChange={(e) => set("regimen", e.target.value)}>
                    <option value="">-- Seleccionar --</option>
                    {REGIMENES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
                  </Sel>
                </div>
                <div><Label>EPS / Asegurador</Label>
                  <Sel value={f.eps} onChange={(e) => set("eps", e.target.value)}>
                    <option value="">-- Seleccionar --</option>
                    {ASEGURADORES_COLOMBIA
                      .filter(a => !f.regimen || a.regimen === f.regimen)
                      .map(a => <option key={a.codigo} value={a.nombre}>{a.nombre}</option>)}
                    <option value="Particular">Particular / Sin afiliación</option>
                  </Sel>
                </div>
                <div><Label>Nº autorización EPS</Label>
                  <Input value={f.autorizacion_eps} onChange={(e) => set("autorizacion_eps", e.target.value)} placeholder="Si la EPS lo exige" />
                </div>
                <div><Label>CUPS (si ya lo tiene)</Label>
                  <Sel value={f.cups} onChange={(e) => set("cups", e.target.value)}>
                    <option value="">-- Seleccionar --</option>
                    {CUPS_PSICOLOGIA.map(o => <option key={o.codigo} value={`${o.codigo} - ${o.nombre}`}>{o.codigo} — {o.nombre}</option>)}
                  </Sel>
                </div>
                <div><Label>Nombre acompañante</Label>
                  <Input value={f.acompanante} onChange={(e) => set("acompanante", e.target.value)} placeholder="Familiar o cuidador principal" />
                </div>
                <div><Label>Teléfono acompañante</Label>
                  <Input value={f.telefono_acompanante} onChange={(e) => set("telefono_acompanante", e.target.value)} placeholder="300…" />
                </div>
                <div className="sm:col-span-2"><Label>Necesidades de accesibilidad</Label>
                  <Input value={f.necesidades_accesibilidad} onChange={(e) => set("necesidades_accesibilidad", e.target.value)}
                    placeholder="Ej: baja visión, silla de ruedas, intérprete, tiempo extra en pruebas…" />
                </div>
                <div><Label>Discapacidad (registro)</Label>
                  <Input value={f.discapacidad} onChange={(e) => set("discapacidad", e.target.value)} placeholder="Ninguna / tipo si aplica" />
                </div>
              </div>
            </FieldBlock>
          </Card>
        )}

        {sec === 3 && (
          <Card className="p-8 space-y-6">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="route" style={{ color: TEAL }} />Vía de atención
            </h3>
            <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
              Define el flujo inicial tras guardar. Puedes cambiar de módulo en cualquier momento desde el panel del paciente.
            </p>
            <div className="grid sm:grid-cols-2 gap-3">
              {VIA_OPTS.map((v) => (
                <button
                  key={v.id}
                  type="button"
                  onClick={() => set("via_atencion", v.id)}
                  className="text-left p-4 rounded-xl border-2 transition-all"
                  style={{
                    borderColor: f.via_atencion === v.id ? TEAL : "var(--ns-card-b)",
                    background: f.via_atencion === v.id ? `${TEAL}08` : "var(--ns-card)",
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <I name={v.icon} style={{ color: TEAL }} />
                    <span className="font-bold text-sm">{v.label}</span>
                  </div>
                  <p className="text-xs" style={{ color: "var(--ns-muted)" }}>{v.desc}</p>
                </button>
              ))}
            </div>
          </Card>
        )}

        {sec === 2 && (
          <Card className="p-8 space-y-8">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="medical_information" className="text-orange-600" />Datos de Consulta
            </h3>
            <div className="grid grid-cols-4 gap-4">
              <div><Label>Fecha Atención *</Label><Input type="date" value={f.fecha_atencion} onChange={(e) => set("fecha_atencion", e.target.value)} /></div>
              <div><Label>Profesional</Label>
                <Sel value={f.profesional_id} onChange={(e) => set("profesional_id", e.target.value)}>
                  <option value="">-- Seleccionar --</option>
                  {profs.map(p => <option key={p.id} value={p.id}>{p.nombre_completo}</option>)}
                </Sel>
              </div>
              <div><Label>Remite</Label><Input value={f.remite} onChange={(e) => set("remite", e.target.value)} placeholder="Ej: Neuropediatría" /></div>
              <div><Label>Orden Médica No.</Label><Input value={f.orden_medica_no} onChange={(e) => set("orden_medica_no", e.target.value)} /></div>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div><Label>Finalidad Consulta</Label>
                <Sel value={f.finalidad_consulta} onChange={(e) => set("finalidad_consulta", e.target.value)}>
                  <option value="">-- Seleccionar --</option>
                  {finOpts.map(o => <option key={o}>{o}</option>)}
                </Sel>
              </div>
              <div><Label>CUPS</Label>
                <Sel value={f.cups} onChange={(e) => set("cups", e.target.value)}>
                  <option value="">-- Seleccionar --</option>
                  {CUPS_PSICOLOGIA.map(o => <option key={o.codigo} value={`${o.codigo} - ${o.nombre}`}>{o.codigo} — {o.nombre}</option>)}
                </Sel>
              </div>
              <div><Label>Código RIPS (CIE-10)</Label>
                <Input list="cie10-frecuentes" value={f.codigo_rips} onChange={(e) => set("codigo_rips", e.target.value)} placeholder={ripsAuto || "F809"} />
                <datalist id="cie10-frecuentes">
                  {CIE10_FRECUENTES.map(d => <option key={d.c} value={d.c}>{d.c} — {d.n}</option>)}
                </datalist>
              </div>
              <div><Label>No. Sesiones</Label><Input type="number" min="1" value={f.numero_sesiones} onChange={(e) => set("numero_sesiones", parseInt(e.target.value, 10) || 1)} /></div>
            </div>
            <div><Label>Motivo de Consulta</Label>
              <Txta value={f.motivo_consulta} onChange={(e) => set("motivo_consulta", e.target.value)} placeholder="Describa el motivo de consulta..." className="min-h-[80px]" />
            </div>
            <div className="flex items-center gap-3">
              <input type="checkbox" checked={f.donante} onChange={(e) => set("donante", e.target.checked)} className="w-4 h-4 rounded" />
              <span className="text-sm font-medium text-gray-600">Donante de órganos</span>
            </div>
          </Card>
        )}

        <div
          className="sticky bottom-0 z-20 -mx-8 px-8 py-4 mt-6 border-t space-y-3"
          style={{
            background: "var(--ns-bg)",
            borderColor: "var(--ns-card-b)",
            boxShadow: "0 -10px 30px rgba(0,0,0,0.05)",
          }}
        >
          <div
            className="flex flex-wrap items-start gap-2 p-3 rounded-xl border text-xs leading-relaxed"
            style={{ background: `${TEAL}08`, borderColor: `${TEAL}25`, color: "var(--ns-muted)" }}
          >
            <I name="verified_user" className="text-sm shrink-0 mt-0.5" style={{ color: TEAL }} />
            <div className="flex-1 min-w-0">
              <p>
                Los datos se tratan conforme a la{" "}
                <button type="button" onClick={() => setPrivOpen(true)} className="underline underline-offset-2 font-semibold" style={{ color: TEAL }}>
                  Política de Privacidad · Ley 1581
                </button>.
                El consentimiento informado debe firmarse antes de la evaluación.
              </p>
            </div>
            <Btn v="outline" className={`${BTN_FOOT} shrink-0`} onClick={openConsent}>
              <I name="draw" className="text-sm" />Consentimiento
            </Btn>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {sec > 0 && (
                <Btn v="outline" className={BTN_FOOT} onClick={() => setSec((s) => s - 1)}>
                  <I name="chevron_left" className="text-sm" />Anterior
                </Btn>
              )}
              {sec < secs.length - 1 && (
                <Btn v="outline" className={BTN_FOOT} onClick={() => setSec((s) => s + 1)}>
                  Siguiente<I name="chevron_right" className="text-sm" />
                </Btn>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              <Btn v="outline" className={BTN_FOOT} onClick={() => setPage("patients")}>Cancelar</Btn>
              <Btn className={BTN_FOOT} onClick={save} disabled={saving}>
                {saving ? "Guardando..." : "Guardar Paciente"}
              </Btn>
            </div>
          </div>
        </div>
      </main>
      <PrivacyPolicyModal open={privOpen} onClose={() => setPrivOpen(false)} />
      {showConsent && savedPatientId && (
        <ConsentModal
          patientId={savedPatientId}
          patientName={savedPatientName}
          patientEmail={savedPatientEmail}
          onClose={closeConsent}
        />
      )}
    </>
  );
}
