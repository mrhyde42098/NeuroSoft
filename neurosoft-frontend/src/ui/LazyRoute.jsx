/**
 * LazyRoute — React 19 `use()` para rutas con import dinámico.
 * Cachea la promesa del módulo para evitar re-fetch en navegación.
 */
import { use } from "react";
import RouteErrorBoundary from "./RouteErrorBoundary.jsx";

const _cache = new Map();

/** Devuelve una función load() estable para pasar a LazyRoute. */
export function pageLoader(importFn) {
  return () => {
    if (!_cache.has(importFn)) {
      _cache.set(importFn, importFn());
    }
    return _cache.get(importFn);
  };
}

export default function LazyRoute({ load, feature, ...props }) {
  const mod = use(load());
  const Component = mod.default;
  const page = <Component {...props} />;
  if (!feature) return page;
  return <RouteErrorBoundary feature={feature}>{page}</RouteErrorBoundary>;
}
