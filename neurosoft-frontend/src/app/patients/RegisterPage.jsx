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
    estrato: null, ocupacion: "", acompanante: "", grupo_etnico: "",
    profesional_id: "",
    fecha_atencion: new Date().toISOString().split("T")[0],
    motivo_consulta: "", remite: "", eps: "", orden_medica_no: "",
    discapacidad: "", codigo_rips: "", cups: "", finalidad_consulta: "",
    numero_sesiones: 1, donante: false,
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const set = (k, val) => sF((o) => ({ ...o, [k]: val }));
  const [profs, setProfs] = useState([]);

  useEffect(() => {
    api.get("/api/v1/config/profesionales").then(d => setProfs(d || [])).catch(() => toast.error("Error cargando profesionales"));
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
      [
        "lugar_nacimiento", "telefono", "correo", "direccion", "localidad",
        "ocupacion", "acompanante", "remite", "eps", "orden_medica_no",
        "discapacidad", "motivo_consulta", "codigo_rips",
      ].forEach(k => { if (body[k] === "") delete body[k]; });
      await api.post("/api/v1/patients/", body);
      setMsg("ok");
      setTimeout(() => setPage("patients"), 1200);
    } catch (e) { setMsg(_parseError(e)); }
    setSaving(false);
  };

  const secs = ["Identificación", "Contacto y Demografía", "Datos de Consulta"];
  const reqErr = (field) => msg && msg !== "ok" && msg.includes(_fieldNames[field] || field);
  const errCls = (field) => reqErr(field) ? "!border-red-400 !bg-red-50/50" : "";

  const cupsOpts = [
    "940681 - Eval NPs Infantil", "940682 - Eval NPs Adulto",
    "940683 - Terapia NPs", "940686 - Rehab NPs", "940680 - Otra",
  ];
  const finOpts = ["Diagnóstico", "Terapéutico", "Seguimiento", "Rehabilitación"];

  return (
    <>
      <TopBar title="Registro de Paciente">
        <div className="text-right text-xs">
          <p className="font-bold">{user?.nombre_completo}</p>
          <p className="text-gray-400">Fecha: {f.fecha_atencion}</p>
        </div>
      </TopBar>
      <main className="p-8 max-w-6xl mx-auto space-y-6">
        <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? () => setMsg("") : null} />
        <div className="flex gap-2">
          {secs.map((s, i) => (
            <button key={s} onClick={() => setSec(i)}
              className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all ${
                sec === i ? "text-white shadow-lg" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
              }`}
              style={sec === i ? { background: TEAL } : {}}>
              <span className="mr-1.5">{i + 1}.</span>{s}
            </button>
          ))}
        </div>

        {sec === 0 && (
          <Card className="p-8 space-y-8">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="badge" style={{ color: TEAL }} />Identificación del Paciente
            </h3>
            <div className="grid grid-cols-6 gap-4">
              <div><Label>Tipo Doc. *</Label>
                <Sel value={f.tipo_documento} onChange={(e) => set("tipo_documento", e.target.value)}>
                  <option>CC</option><option>TI</option><option>RC</option>
                  <option>CE</option><option>PA</option><option>MS</option><option>NV</option>
                </Sel>
              </div>
              <div className="col-span-2"><Label>Número Documento *</Label>
                <Input className={errCls("numero_documento")} value={f.numero_documento} onChange={(e) => set("numero_documento", e.target.value)} placeholder="1234567890" />
              </div>
              <div><Label>Sexo *</Label>
                <Sel value={f.sexo} onChange={(e) => set("sexo", e.target.value)}>
                  <option value="H">Masculino</option><option value="M">Femenino</option>
                </Sel>
              </div>
              <div className="col-span-2"><Label>Fecha Nacimiento *</Label>
                <Input className={errCls("fecha_nacimiento")} type="date" value={f.fecha_nacimiento} onChange={(e) => set("fecha_nacimiento", e.target.value)} />
                {edad !== null && (
                  <span className="inline-block mt-1 px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-xs font-bold">
                    {edad} años — {edad < 6 ? "Preescolar" : edad < 18 ? "Infantil" : edad < 50 ? "Adulto Joven" : "Adulto Mayor"}
                  </span>
                )}
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div><Label>Primer Nombre *</Label><Input className={errCls("primer_nombre")}   value={f.primer_nombre}   onChange={(e) => set("primer_nombre", e.target.value)} /></div>
              <div><Label>Segundo Nombre</Label><Input value={f.segundo_nombre}    onChange={(e) => set("segundo_nombre", e.target.value)} /></div>
              <div><Label>Primer Apellido *</Label><Input className={errCls("primer_apellido")} value={f.primer_apellido} onChange={(e) => set("primer_apellido", e.target.value)} /></div>
              <div><Label>Segundo Apellido</Label><Input value={f.segundo_apellido}  onChange={(e) => set("segundo_apellido", e.target.value)} /></div>
            </div>
            <div className="grid grid-cols-4 gap-4">
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
              <div><Label>Lugar de Nacimiento</Label><Input value={f.lugar_nacimiento} onChange={(e) => set("lugar_nacimiento", e.target.value)} placeholder="Ciudad, Depto" /></div>
            </div>
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
            <div className="grid grid-cols-5 gap-4">
              <div><Label>Ciudad</Label><Input value={f.ciudad} onChange={(e) => set("ciudad", e.target.value)} /></div>
              <div><Label>Localidad</Label><Input value={f.localidad} onChange={(e) => set("localidad", e.target.value)} placeholder="Ej: Usaquén" /></div>
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
            <div className="grid grid-cols-3 gap-4">
              <div><Label>Acompañante</Label><Input value={f.acompanante} onChange={(e) => set("acompanante", e.target.value)} placeholder="Nombre del acompañante" /></div>
              <div><Label>Discapacidad</Label><Input value={f.discapacidad} onChange={(e) => set("discapacidad", e.target.value)} placeholder="Ej: Ninguna" /></div>
              <div><Label>EPS</Label><Input value={f.eps} onChange={(e) => set("eps", e.target.value)} placeholder="Ej: Compensar" /></div>
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
                  {cupsOpts.map(o => <option key={o}>{o}</option>)}
                </Sel>
              </div>
              <div><Label>Código RIPS (CIE-10)</Label><Input value={f.codigo_rips} onChange={(e) => set("codigo_rips", e.target.value)} placeholder={ripsAuto || "F809"} /></div>
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

        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            {sec > 0 && (
              <Btn v="outline" onClick={() => setSec(s => s - 1)}>
                <I name="chevron_left" className="text-sm" />Anterior
              </Btn>
            )}
            {sec < 2 && (
              <Btn v="outline" onClick={() => setSec(s => s + 1)}>
                Siguiente<I name="chevron_right" className="text-sm" />
              </Btn>
            )}
          </div>
          <div className="flex gap-4">
            <Btn v="outline" onClick={() => setPage("patients")}>Cancelar</Btn>
            <Btn onClick={save} disabled={saving}>{saving ? "Guardando..." : "Guardar Paciente"}</Btn>
          </div>
          {/* Aviso de privacidad — Ley 1581 */}
          <div className="flex items-center gap-2 mt-2">
            <I name="privacy_tip" className="text-xs shrink-0" style={{color:TEAL}}/>
            <p className="text-[10px] leading-relaxed" style={{color:"var(--ns-muted)"}}>
              Los datos del paciente se tratarán conforme a la{" "}
              <button type="button" onClick={()=>setPrivOpen(true)} className="underline underline-offset-2 font-semibold" style={{color:TEAL}}>
                Política de Privacidad · Ley 1581 de 2012
              </button>. El paciente debe haber firmado el consentimiento informado antes de iniciar la evaluación.
            </p>
          </div>
        </div>
      </main>
      <PrivacyPolicyModal open={privOpen} onClose={()=>setPrivOpen(false)}/>
    </>
  );
}
