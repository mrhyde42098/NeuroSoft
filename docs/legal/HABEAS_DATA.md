# Anexo: Tratamiento de Datos Personales — NeuroSoft

> Documento operacional para responsables del tratamiento que desplieguen
> NeuroSoft en Colombia.

## 1. Marco legal aplicable

NeuroSoft procesa datos sensibles de salud según las siguientes normas:

| Norma | Alcance |
|---|---|
| **Ley 1581 de 2012** ("Habeas Data") | Régimen general de protección de datos personales en Colombia. |
| **Decreto 1377 de 2013** | Reglamenta la Ley 1581: consentimiento, política de tratamiento, autorizaciones. |
| **Decreto 1074 de 2015** (arts. 2.2.2.25.x) | Registro Nacional de Bases de Datos (RNBD) ante la SIC. |
| **Resolución 1995 de 1999** (MinSalud) | Manejo de la historia clínica: es **obligatorio conservarla** (mín. 15 años en archivo central) y **no se puede eliminar**. |
| **Resolución 2275 de 2023** (MinSalud) | Estructura de los Registros Individuales de Prestación de Servicios (RIPS). |
| **Ley 23 de 1981** + **Resolución 8430 de 1993** | Ética médica y consentimiento informado. |

La condición del responsable es la del **profesional clínico o institución
prestadora de salud** que instala NeuroSoft; NO es el proveedor del software.

## 2. Categorías de datos tratados

NeuroSoft almacena:

1. **Identificación del paciente**: nombre completo, tipo y número de
   documento, fecha de nacimiento, sexo, dirección, teléfono, correo,
   EPS/afiliación, acudiente cuando aplica.
2. **Historia clínica** (datos sensibles, Art. 6 Ley 1581):
   desarrollo, antecedentes personales/familiares, escolaridad, consumo,
   motivos de consulta, diagnósticos presuntivos.
3. **Evaluaciones neuropsicológicas**: puntajes brutos, escalares, Z,
   interpretaciones, protocolos aplicados, versión del baremo usado.
4. **Evolución terapéutica**: sesiones, objetivos, actividades, planes.
5. **Documentos y firmas**: firma digital del profesional (imagen base64),
   consentimientos informados cuando se adjuntan.
6. **Auditoría**: identificador del actor, fecha/hora, acción realizada
   sobre cada entidad (crear/actualizar/archivar/restaurar).

NeuroSoft **no** exfiltra datos a servidores externos: el despliegue es
on-premise y la única salida por defecto es el envío opcional de
recordatorios por SMTP configurado por el operador.

## 3. Principios que aplica la plataforma

La Ley 1581 establece ocho principios rectores. NeuroSoft los soporta así:

| Principio | Implementación técnica |
|---|---|
| Legalidad | El flujo obliga a registrar autorización del paciente antes de crear la HC. |
| Finalidad | Los datos se usan solo para evaluación, diagnóstico, informe y reportes RIPS obligatorios. |
| Libertad | El operador debe permitir al titular revocar o pedir actualización; ver sección 4. |
| Veracidad/Calidad | Validaciones de PD (rechazo de negativos, advertencias fuera de baremo). |
| Transparencia | Acceso al propio expediente disponible vía endpoint por paciente. |
| Acceso restringido | JWT, roles (admin / clínico / recepción), auditoría completa. |
| Seguridad | WAL mode, backup a disco, bcrypt, rate limit, CORS estricto, PII redactor en logs. |
| Confidencialidad | Los logs redactan PII; los reports se guardan localmente; no hay telemetría. |

## 4. Derechos del titular (ARCO+revocación)

El paciente puede ejercer:

- **Acceso** a sus datos → endpoint `GET /api/v1/patients/{id}/export`
  (entrega JSON completo para revisión).
- **Rectificación** → endpoints PATCH sobre paciente e historia clínica.
- **Actualización** → idem.
- **Cancelación / archivo** → `POST /api/v1/patients/{id}/archive`
  (soft-delete: marca `archived_at`, `archived_by`, `archived_reason`;
  la HC se preserva por la Res. 1995).
- **Revocación de autorización** → el operador debe dejar constancia
  escrita y detener usos ulteriores. NeuroSoft permite registrar la
  revocación en las notas de la HC, pero el operador debe canalizar el
  flujo legal.
- **Consulta de quejas** → la SIC es la autoridad (www.sic.gov.co).

## 5. Obligaciones del operador

El profesional/clínica que instala NeuroSoft debe:

1. **Registrar la base de datos en el RNBD** (Superintendencia de
   Industria y Comercio) si procesa datos de más de 100.000 titulares
   o pertenece a una entidad con patrimonio > 100.000 UVT.
2. **Publicar política de tratamiento** visible en el sitio web o
   consultorio, y obtener **autorización previa, expresa e informada**
   del titular antes del primer registro.
3. **Designar responsable de datos personales** (oficial de protección
   o encargado) y vía de contacto (correo/formulario).
4. **Mantener el servidor on-premise con cifrado en reposo**:
   - Disco cifrado con BitLocker (Windows), LUKS (Linux) o FileVault (macOS).
   - Backup cifrado (ver sección 6).
5. **Limitar accesos por rol**: crear una cuenta por profesional; no
   compartir el usuario `admin`.
6. **Registrar incidentes**: notificar a la SIC cualquier vulneración
   dentro de los **15 días hábiles** siguientes al incidente (Art. 22
   Ley 1581).
7. **Cumplir la Resolución 1995 de 1999**: la HC clínica se conserva
   como mínimo 15 años en archivo central y **no puede eliminarse**
   físicamente. NeuroSoft soporta esto con soft-delete (archivo lógico
   con trazabilidad de quién y cuándo lo archivó).

## 6. Backups y retención

Recomendaciones operativas:

- **Backup automático diario** con `APScheduler` (activo por defecto).
- **Backup manual** antes de actualizaciones de versión:
  `POST /api/v1/backup/` → `data/backups/`.
- **Ubicación**: al menos dos copias: disco local cifrado + almacenamiento
  externo cifrado (disco USB cifrado, S3/Wasabi con cifrado en reposo).
- **Retención**:
  - BD operativa: indefinida mientras el paciente esté activo.
  - HC de pacientes archivados: 15 años mínimo (Res. 1995).
  - Backups: política recomendada 7 diarios + 4 semanales + 12 mensuales.
- **Restauración**: endpoint `POST /api/v1/backup/restore` con validación
  por magic bytes y backup de seguridad automático antes de reemplazar.

## 7. Logs y auditoría

- Toda operación CRUD sobre entidades clínicas queda en `audit_log`
  con actor, acción, entidad, timestamp y resumen.
- Los logs de aplicación pasan por un filtro PII que redacta emails,
  teléfonos colombianos, JWT tokens y pares clave=valor sensibles antes
  de llegar al handler (consola, archivo o agente de telemetría).
- Los logs **no deben exportarse a servicios SaaS externos** sin un
  acuerdo de transmisión internacional de datos compatible con la
  Ley 1581 (el país destino debe tener nivel adecuado de protección,
  según el listado de la SIC).

## 8. Subcontratación / encargados del tratamiento

Si el operador delega operación técnica (hosting, soporte) a un tercero:

- Debe firmar un **acuerdo de transmisión o transferencia** (según
  Art. 25 del Decreto 1377) que obligue al encargado a cumplir la Ley
  1581 y reportar incidentes al responsable.
- El encargado no puede usar los datos para fines distintos a los del
  responsable ni transferirlos a terceros sin autorización.

## 9. Uso clínico — descargo de responsabilidad

NeuroSoft es una **herramienta de apoyo** para el profesional. No es
un dispositivo médico certificado ante INVIMA ni sustituye el juicio
clínico. Las calificaciones, interpretaciones y alertas son insumos
que el profesional debe validar antes de emitir diagnóstico o
recomendación terapéutica.

Cualquier decisión tomada con base en los reportes generados por
NeuroSoft es responsabilidad exclusiva del profesional que la emite.

## 10. Contacto

Responsable del tratamiento: **[Completar: nombre de la clínica /
profesional / correo de contacto]**.

Este documento debe personalizarse antes de desplegar NeuroSoft en
producción y publicarse junto con la política de tratamiento y el
formato de autorización del paciente.
