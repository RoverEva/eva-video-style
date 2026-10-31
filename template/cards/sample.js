/* EVA Card System previews: one shared sample content set, so the four template styles and nine layouts compare line by line.
 * Presenter frames: put 30 fps JPGs in template/cards/media/eva (not in the repo); stills use frame 0. */
window.CS = {
  setup(C, end) { C.src0 = -100; C.end = end || 20; C.evaDir = '../media/eva'; C.face = { x: .52, y: .36, h: .52 }; },
  HERO: { kicker: 'EVA CARD SYSTEM', words: ['BIG IDEAS'], sub: 'SIMPLE STEPS' },
  HERO2: { words: ['BIG', 'IDEAS'], sub: 'SIMPLE STEPS' },
  STEPS: [{ title: 'Idea', sub: 'Find the opportunity', icon: 'idea' }, { title: 'Plan', sub: 'Set your strategy', icon: 'plan' },
          { title: 'Build', sub: 'Take action', icon: 'build' }, { title: 'Grow', sub: 'Scale your impact', icon: 'grow' }],
  SEVEN: [{ title: 'Idea', icon: 'idea' }, { title: 'Plan', icon: 'plan' }, { title: 'Build', icon: 'build' }, { title: 'Grow', icon: 'grow' },
          { title: 'Audience', icon: 'audience' }, { title: 'Launch', icon: 'rocket' }, { title: 'Success', icon: 'success' }],
  STATEMENT: { script: 'Turn', words: ['IDEAS'], sub: 'INTO RESULTS' },
  FEATURE: { n: 1, title: 'Idea', body: 'Find a real problem and a unique opportunity.', icon: 'idea' },
};
