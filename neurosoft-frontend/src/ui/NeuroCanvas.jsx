/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/NeuroCanvas.jsx — Animación de red neuronal viva
 * ───────────────────────────────────────────────────────────────────────
 * Canvas 2D con neuronas que pulsan, sinapsis curvadas que disparan
 * señales y partículas neurotransmisoras. Usado como decoración del
 * panel izquierdo del LoginPage. Reacciona suavemente al cursor.
 *
 * Props:
 *   • mouseRef.current: { x, y } — coordenadas del cursor relativas al
 *     contenedor padre. Se setea desde un onMouseMove externo.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef } from "react";
import { TEAL_LIGHT } from "./tokens.js";

export default function NeuroCanvas({ mouseRef }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const cv = canvasRef.current;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    let W, H, raf;
    const dpr = window.devicePixelRatio || 1;
    const resize = () => {
      W = cv.parentElement.clientWidth;
      H = cv.parentElement.clientHeight;
      cv.width = W * dpr;
      cv.height = H * dpr;
      ctx.scale(dpr, dpr);
    };
    resize();
    window.addEventListener("resize", resize);

    /* Neurons — organic positions with gentle drift */
    const N = 35;
    const neurons = [];
    for (let i = 0; i < N; i++) {
      const layer = i < 8 ? 0 : i < 20 ? 1 : 2;
      const cx = W / 2, cy = H / 2;
      const angle = Math.random() * Math.PI * 2;
      const dist = layer === 0 ? Math.random() * 80 + 20
        : layer === 1 ? Math.random() * 160 + 100
        : Math.random() * Math.min(W, H) * 0.45 + 180;
      neurons.push({
        x:  cx + Math.cos(angle) * dist, y:  cy + Math.sin(angle) * dist,
        ox: cx + Math.cos(angle) * dist, oy: cy + Math.sin(angle) * dist,
        r: layer === 0 ? 3 + Math.random() * 2.5
          : layer === 1 ? 2 + Math.random() * 1.5
          : 1 + Math.random(),
        phase: Math.random() * Math.PI * 2,
        speed: 0.3 + Math.random() * 0.5,
        drift: 8 + Math.random() * 15,
        driftPhase: Math.random() * Math.PI * 2,
        pulsePhase: Math.random() * Math.PI * 2,
        layer,
        glow: layer === 0 ? 1 : layer === 1 ? 0.6 : 0.3,
      });
    }
    /* Synapses */
    const synapses = [];
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const dx = neurons[i].ox - neurons[j].ox;
        const dy = neurons[i].oy - neurons[j].oy;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < 220 && Math.random() < 0.55) {
          synapses.push({ a: i, b: j, d, fireTime: -99, fireDir: 1 });
        }
      }
    }
    const signals = [];
    let lastFire = 0;
    const particles = [];
    for (let i = 0; i < 60; i++) {
      particles.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
        r: 0.5 + Math.random() * 1.2,
        alpha: 0.1 + Math.random() * 0.3,
        phase: Math.random() * Math.PI * 2,
      });
    }
    let t = 0;
    const draw = () => {
      t += 0.016;
      ctx.clearRect(0, 0, W, H);
      const bg = ctx.createRadialGradient(W * 0.4, H * 0.4, 0, W * 0.5, H * 0.5, Math.max(W, H) * 0.7);
      bg.addColorStop(0, "#0f2a3d");
      bg.addColorStop(0.5, "#0a2530");
      bg.addColorStop(1, "#061218");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);

      const orb1X = W * 0.3 + Math.sin(t * 0.2) * 50, orb1Y = H * 0.3 + Math.cos(t * 0.15) * 40;
      const orb2X = W * 0.7 + Math.sin(t * 0.18 + 2) * 60, orb2Y = H * 0.7 + Math.cos(t * 0.22 + 1) * 50;
      [
        [[orb1X, orb1Y, 180], "rgba(13,148,136,0.04)"],
        [[orb2X, orb2Y, 150], "rgba(103,232,249,0.03)"],
      ].forEach(([p, c]) => {
        const g = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], p[2]);
        g.addColorStop(0, c);
        g.addColorStop(1, "transparent");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      });

      const mx = mouseRef?.current?.x ?? -999, my = mouseRef?.current?.y ?? -999;
      neurons.forEach((n) => {
        n.x = n.ox + Math.sin(t * n.speed + n.driftPhase) * n.drift + Math.cos(t * n.speed * 0.7 + n.phase) * n.drift * 0.5;
        n.y = n.oy + Math.cos(t * n.speed * 0.8 + n.driftPhase) * n.drift + Math.sin(t * n.speed * 0.6 + n.phase) * n.drift * 0.3;
        if (mx > 0) {
          const dx = mx - n.x, dy = my - n.y, dd = Math.sqrt(dx * dx + dy * dy);
          if (dd < 200) {
            const f = ((200 - dd) / 200) * 12;
            n.x += (dx / dd) * f * 0.3;
            n.y += (dy / dd) * f * 0.3;
          }
        }
      });

      synapses.forEach((s) => {
        const a = neurons[s.a], b = neurons[s.b];
        const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy);
        const alpha = Math.max(0, (180 - d) / 180) * 0.25;
        if (alpha <= 0) return;
        const mx2 = (a.x + b.x) / 2 + Math.sin(t * 0.5 + s.d) * 8;
        const my2 = (a.y + b.y) / 2 + Math.cos(t * 0.3 + s.d) * 8;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.quadraticCurveTo(mx2, my2, b.x, b.y);
        ctx.strokeStyle = `rgba(13,148,136,${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      });

      if (t - lastFire > 0.8 + Math.random() * 2) {
        lastFire = t;
        const si = Math.floor(Math.random() * synapses.length);
        signals.push({ synapse: si, progress: 0, speed: 0.8 + Math.random() * 0.6 });
      }
      for (let i = signals.length - 1; i >= 0; i--) {
        const sig = signals[i];
        sig.progress += sig.speed * 0.016;
        if (sig.progress > 1) {
          const s = synapses[sig.synapse], dest = neurons[s.b];
          for (let j = 0; j < 4; j++) {
            particles.push({
              x: dest.x, y: dest.y,
              vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2,
              r: 1 + Math.random(), alpha: 0.8, phase: 0, life: 1,
            });
          }
          signals.splice(i, 1);
          continue;
        }
        const s = synapses[sig.synapse], a = neurons[s.a], b = neurons[s.b];
        const pp = sig.progress;
        const mx2 = (a.x + b.x) / 2 + Math.sin(t * 0.5 + s.d) * 8;
        const my2 = (a.y + b.y) / 2 + Math.cos(t * 0.3 + s.d) * 8;
        const tp = 1 - pp;
        const sx = tp * tp * a.x + 2 * tp * pp * mx2 + pp * pp * b.x;
        const sy = tp * tp * a.y + 2 * tp * pp * my2 + pp * pp * b.y;
        const sg = ctx.createRadialGradient(sx, sy, 0, sx, sy, 8);
        sg.addColorStop(0, "rgba(103,232,249,0.9)");
        sg.addColorStop(0.4, "rgba(13,148,136,0.4)");
        sg.addColorStop(1, "transparent");
        ctx.fillStyle = sg;
        ctx.fillRect(sx - 10, sy - 10, 20, 20);
        ctx.beginPath();
        ctx.arc(sx, sy, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(103,232,249,0.95)";
        ctx.fill();
      }

      neurons.forEach((n) => {
        const pulse = 0.7 + Math.sin(t * 2 + n.pulsePhase) * 0.3;
        if (n.layer < 2) {
          const glow = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 6);
          glow.addColorStop(0, `rgba(13,148,136,${0.15 * n.glow * pulse})`);
          glow.addColorStop(1, "transparent");
          ctx.fillStyle = glow;
          ctx.fillRect(n.x - n.r * 6, n.y - n.r * 6, n.r * 12, n.r * 12);
        }
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * pulse, 0, Math.PI * 2);
        const nGrad = ctx.createRadialGradient(n.x - n.r * 0.3, n.y - n.r * 0.3, 0, n.x, n.y, n.r);
        nGrad.addColorStop(0, n.layer === 0 ? `rgba(103,232,249,${0.95 * pulse})` : `rgba(13,148,136,${0.7 * pulse})`);
        nGrad.addColorStop(1, n.layer === 0 ? `rgba(13,148,136,${0.6 * pulse})` : `rgba(13,148,136,${0.3 * pulse})`);
        ctx.fillStyle = nGrad;
        ctx.fill();
      });

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.phase += 0.02;
        if (p.life !== undefined) {
          p.life -= 0.02;
          p.alpha = p.life;
          if (p.life <= 0) { particles.splice(i, 1); continue; }
        }
        if (p.x < -10) p.x = W + 10;
        if (p.x > W + 10) p.x = -10;
        if (p.y < -10) p.y = H + 10;
        if (p.y > H + 10) p.y = -10;
        const pa = p.alpha * (0.5 + Math.sin(p.phase) * 0.5);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(103,232,249,${pa})`;
        ctx.fill();
      }

      const bcx = W * 0.5, bcy = H * 0.45;
      ctx.save();
      ctx.globalAlpha = 0.03 + Math.sin(t * 0.5) * 0.01;
      ctx.beginPath();
      ctx.moveTo(bcx, bcy - 70);
      ctx.bezierCurveTo(bcx + 50, bcy - 70, bcx + 75, bcy - 40, bcx + 70, bcy - 10);
      ctx.bezierCurveTo(bcx + 68, bcy + 10, bcx + 60, bcy + 25, bcx + 45, bcy + 35);
      ctx.bezierCurveTo(bcx + 35, bcy + 45, bcx + 20, bcy + 55, bcx, bcy + 60);
      ctx.bezierCurveTo(bcx - 20, bcy + 55, bcx - 35, bcy + 45, bcx - 45, bcy + 35);
      ctx.bezierCurveTo(bcx - 60, bcy + 25, bcx - 68, bcy + 10, bcx - 70, bcy - 10);
      ctx.bezierCurveTo(bcx - 75, bcy - 40, bcx - 50, bcy - 70, bcx, bcy - 70);
      ctx.strokeStyle = TEAL_LIGHT;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(bcx, bcy - 65);
      ctx.quadraticCurveTo(bcx + 5, bcy, bcx, bcy + 55);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(bcx - 30, bcy - 50);
      ctx.quadraticCurveTo(bcx - 10, bcy - 15, bcx - 35, bcy + 20);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(bcx + 30, bcy - 50);
      ctx.quadraticCurveTo(bcx + 10, bcy - 15, bcx + 35, bcy + 20);
      ctx.stroke();
      ctx.restore();

      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />;
}

/* ─── Sonidos UI sutiles (clicks, hovers, success) ───────────────── */
const _audioCtx = typeof window !== "undefined"
  ? new (window.AudioContext || window.webkitAudioContext)()
  : null;

const _playTone = (freq = 800, dur = 0.08, vol = 0.03, type = "sine") => {
  if (!_audioCtx) return;
  try {
    if (_audioCtx.state === "suspended") _audioCtx.resume();
    const o = _audioCtx.createOscillator();
    const g = _audioCtx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, _audioCtx.currentTime);
    o.frequency.exponentialRampToValueAtTime(freq * 1.2, _audioCtx.currentTime + dur * 0.3);
    g.gain.setValueAtTime(vol, _audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, _audioCtx.currentTime + dur);
    o.connect(g);
    g.connect(_audioCtx.destination);
    o.start();
    o.stop(_audioCtx.currentTime + dur);
  } catch {}
};

export const sfx = {
  hover:   () => _playTone(600, 0.04, 0.015),
  click:   () => _playTone(800, 0.06, 0.025),
  success: () => {
    _playTone(523, 0.12, 0.03);
    setTimeout(() => _playTone(659, 0.12, 0.03), 120);
    setTimeout(() => _playTone(784, 0.15, 0.03), 240);
  },
  error: () => _playTone(220, 0.2, 0.03, "triangle"),
  type:  () => _playTone(1200 + Math.random() * 400, 0.02, 0.008),
};
