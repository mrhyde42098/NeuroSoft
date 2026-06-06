/** Ejecuta global-setup (limpia BD E2E) desde CI o local. */
import globalSetup from "./global-setup.js";

await globalSetup();
