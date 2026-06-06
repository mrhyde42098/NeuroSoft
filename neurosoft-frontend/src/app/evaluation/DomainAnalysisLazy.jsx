/**
 * DomainAnalysisLazy — wrapper para code-split de recharts.
 */
import React, { lazy, Suspense } from "react";

const DomainAnalysis = lazy(() => import("./DomainAnalysis.jsx"));

export default function DomainAnalysisLazy(props) {
  return (
    <Suspense
      fallback={
        <div
          className="p-6 rounded-md border text-sm"
          style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)", color: "var(--ns-muted)" }}
          role="status"
        >
          Cargando gráficas por dominio…
        </div>
      }
    >
      <DomainAnalysis {...props} />
    </Suspense>
  );
}
