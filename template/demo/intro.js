/* Shared timing for the Eva Video Style demo reel: one 15 s self-intro (AI presenter), every template shows the same lines its own way. */
window.IN = {
  T: { hi: .1, meet: .9, oss: 1.9, cine: 3.87, fut: 4.73, soc: 5.87, tpl: 7.73, pick: 8.97, apply: 9.87, ai: 10.67, less: 12.1, more: 12.9, tryit: 13.77 },
  END: 15.033, B: [0, 3.87, 7.73, 12.07, 15.033],
  setup(C) { C.src0 = 0; C.end = this.END; C.evaDir = '../media/eva'; C.face = { x: .51, y: .25, h: .42 }; },
  SHOTS: ['../media/web/f_00000.jpg', '../media/web/f_00150.jpg', '../media/web/f_00300.jpg', '../media/wb/f_00600.jpg', '../media/wb/f_01200.jpg', '../media/wb/f_02400.jpg', '../media/fly/f_00100.jpg', '../media/whis/f_00200.jpg', '../media/sent/f_00400.jpg', '../media/match/f_00200.jpg'],
  STYLES: ['CINEMATIC', 'FUTURISTIC TECH', 'SOCIAL MEDIA', 'MINIMALIST'],
};
