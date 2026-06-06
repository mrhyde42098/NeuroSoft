/** Limpia la BD E2E antes de levantar uvicorn (evita beta con password obsoleta). */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BACKEND = path.resolve(__dirname, "../../neurosoft-backend");

export default async function globalSetup() {
  const rel = process.env.NEUROSOFT_DB_PATH || "data/e2e_test.db";
  const base = path.join(BACKEND, rel);
  for (const suffix of ["", "-wal", "-shm"]) {
    try {
      fs.unlinkSync(base + suffix);
    } catch {
      /* ok si no existe */
    }
  }
}
