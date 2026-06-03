# Política de Retención de Historia Clínica

**Normograma aplicable:** Resolución 1995 de 1999, art. 28 · Ley 962 de 2005, art. 28 · Ley 1098 de 2006 (protección al menor) · Ley 1581 de 2012, art. 11 · Estatuto Tributario, art. 654.

---

## 1. Plazos de retención

| Documento | Plazo | Norma |
|---|---|---|
| HC adulto (≥18a en atención) | **15 años** desde la última atención | Res 1995/1999 art 28 |
| HC menor (<18a en atención) | **15 años** desde la atención **O** hasta cumplir 25 años, lo que sea MAYOR | Res 1995/1999 + Ley 1098/2006 |
| Consentimiento informado | Mismo plazo que la HC a la que está asociado | Por extensión normativa |
| Bitácora de acceso / auditoría clínica | **5 años** desde su generación | Ley 1581/2012 + circular SIC |
| Factura electrónica | **5 años** | Estatuto Tributario art 654 |

## 2. Cálculo

Implementado en `app/infrastructure/retencion.py`. Funciones expuestas:

- `fecha_caducidad_hc(fecha_atencion, fecha_nacimiento, fecha_actual) → date | None`
- `fecha_caducidad_logs_acceso(fecha_evento) → date | None`
- `fecha_caducidad_factura(fecha_emision) → date | None`
- `estado_retencion(...) → EstadoRetencion` (con `estado ∈ {vigente, proximo_a_caducar, caducada}`)
- `resumen_inventario(patients, fecha_actual) → dict` con estadísticas

### Estados

- **vigente**: ≥ 2 años restantes
- **proximo_a_caducar**: < 2 años restantes (alerta al responsable)
- **caducada**: plazo cumplido (puede proceder disposición final)

## 3. Endpoint de consulta

```
GET /api/v1/admin/retencion
  → Resumen global del inventario de HCs (solo admin).
GET /api/v1/admin/retencion/paciente/{patient_id}
  → Estado de un paciente específico.
```

Respuesta de ejemplo:

```json
{
  "fecha_referencia": "2026-06-01",
  "total_pacientes": 124,
  "vigentes": 119,
  "proximo_a_caducar": 4,
  "caducadas": 1,
  "por_poblacion": { "adulto": 105, "menor": 18, "desconocida": 1 },
  "normograma_aplicado": { "resolucion_1995_1999_art28": 15, ... },
  "proximo_a_caducar_detalle": [ ... ],
  "caducadas_detalle": [ ... ]
}
```

## 4. Disposición final (NO automática)

NeuroSoft **NO borra automáticamente** HCs caducadas. La disposición final es responsabilidad del responsable del tratamiento y debe seguir este procedimiento:

1. Acta de disposición donde conste: N° de HCs, fechas, justificación, método (eliminación, anonimización irreversible, archivo histórico).
2. Autorización del Comité de Ética institucional (si aplica) o del responsable médico.
3. Notificación a pacientes cuyos datos serán objeto de disposición (si están vivos y localizables).
4. Conservación de la **acta de disposición** por 20 años como evidencia.

## 5. Limitaciones del módulo

- Si el paciente no tiene `fecha_nacimiento`, se aplica el mínimo legal (15 años) sin protección reforzada al menor.
- Si el paciente fue atendido siendo menor pero se desconoce su fecha de nacimiento actual, se usa 15 años desde la última atención.
- El módulo NO consulta historias externas; solo aplica a las HCs registradas en este sistema.

## 6. Auditoría

Cualquier consulta al endpoint de retención queda registrada en la bitácora de auditoría (acción `read:retencion`) conforme a Ley 1581/2012.

---

**Autor:** NeuroSoft App · 2026
