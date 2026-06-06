const owner = context.repo.owner;
const repo = context.repo.repo;

for (const name of ["roadmap", "enhancement", "bug"]) {
  try {
    await github.rest.issues.createLabel({
      owner,
      repo,
      name,
      color: name === "roadmap" ? "1d76db" : "0e8a16",
    });
  } catch (e) {
    if (e.status !== 422) throw e;
  }
}

const planned = [
  {
    title: "[roadmap]: E2E Playwright paciente -> evaluacion -> informe Pro",
    labels: ["roadmap"],
    body: [
      "Flujo critico de regresion antes de releases beta.",
      "",
      "- [ ] Crear paciente sintetico",
      "- [ ] Aplicar subtest WISC con baremo conocido",
      "- [ ] Generar informe Pro y validar CI esperado",
      "",
      "Ref: docs/ESTADO_VIVO.md",
    ].join("\n"),
  },
  {
    title: "[roadmap]: Etiquetas/tags en panel de pacientes",
    labels: ["roadmap"],
    body: [
      "Quick win pendiente del roadmap 2026. Permitir filtrar pacientes por etiquetas",
      "clinicas (TDAH, adulto mayor, remision EPS, etc.).",
      "",
      "Prioridad: P1",
    ].join("\n"),
  },
  {
    title: "[feature]: Placeholders visuales de estimulos WISC/WAIS en evaluacion",
    labels: ["enhancement"],
    body: [
      "Mejorar fidelidad del flujo de aplicacion mostrando estimulos desde",
      "stimuli_manifest.json. Sin copiar material con copyright en el repo.",
      "",
      "Ref: docs/stimuli/STIMULI_INVENTORY.md",
    ].join("\n"),
  },
];

const { data: existing } = await github.rest.issues.listForRepo({
  owner,
  repo,
  state: "all",
  per_page: 100,
});
const titles = new Set(existing.map((i) => i.title));

for (const issue of planned) {
  if (titles.has(issue.title)) {
    core.info(`Issue ya existe: ${issue.title}`);
    continue;
  }
  await github.rest.issues.create({
    owner,
    repo,
    title: issue.title,
    body: issue.body,
    labels: issue.labels,
  });
  core.info(`Issue creado: ${issue.title}`);
}
