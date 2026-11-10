/* Shared 5-second sample for new template demos (templatechoose_demo.mp4, AI presenter). Put the presenter as 30 fps JPGs in
 * media/eva and, for cut-out templates, the AI cut-out (scripts/matte.py) in media/cut. */
window.S5 = {
  END: 5.05, FRAMES: 150,
  setup(C) { C.src0 = 0; C.end = this.END; C.evaDir = '../media/eva'; C.face = { x: .5, y: .2, h: .36 }; },
  cut(t) { const q = window.EV && EV.params, d = (q && q.get('cut')) || '../media/cut', n = +((q && q.get('cutN')) || this.FRAMES);
    return `${d}/f_${String(Math.max(0, Math.min(n - 1, Math.round(t * 30)))).padStart(5, '0')}.webp`; },
};
