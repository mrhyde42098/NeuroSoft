import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App.jsx'

/* §splash: oculta el splash inline tan pronto como React monte algo en #root.
 * Defensa en profundidad — el CSS también lo oculta automáticamente, pero
 * setear display:none explícito garantiza que no se solape en pywebview. */
function hideSplash() {
  try {
    const s = document.getElementById('ns-splash');
    if (s) s.style.display = 'none';
  } catch {}
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

/* Tras el primer commit de React, escondemos el splash. */
requestAnimationFrame(hideSplash);
