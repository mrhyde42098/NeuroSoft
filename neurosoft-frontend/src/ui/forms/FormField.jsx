import React from "react";
import { Label } from "../primitives.jsx";

/** Campo de formulario: label + error + children (Input/Sel/etc.). */
export default function FormField({
  label,
  required,
  error,
  className = "",
  children,
}) {
  return (
    <div className={className}>
      {label != null && (
        <Label>
          {label}
          {required ? " *" : ""}
        </Label>
      )}
      {children}
      {error ? (
        <p className="text-xs text-red-500 mt-1" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
