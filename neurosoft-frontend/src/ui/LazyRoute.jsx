/**
 * LazyRoute — React 19 `use()` para rutas con import dinámico.
 * Cachea la promesa del módulo para evitar re-fetch en navegación.
 */
import { use } from "react";

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

export default function LazyRoute({ load, ...props }) {
  const mod = use(load());
  const Component = mod.default;
  return <Component {...props} />;
}
