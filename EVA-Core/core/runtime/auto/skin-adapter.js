/* Shared EVA automatic-edit adapter.
 *
 * A template package owns only its visual configuration and a tiny registration
 * wrapper. The presenter, transcript cards, section timing and QA behavior stay
 * in EVA Core. Existing hand-authored scenes.js files are packaged separately
 * and are never rewritten by this adapter.
 */
(function (root) {
  const C = EV, K0 = K;

  const px = value => `${Math.round(value)}px`;
  const add = (parent, style) => C.el(parent, 'div', 'abs', style);

  function buildPattern(L, cfg) {
    const visual = cfg.visual || {};
    const pattern = visual.pattern || 'grid';
    const ink = visual.ink || '#ffffff';
    const accent = visual.accent || '#d4ff2e';
    const nodes = [];

    if (pattern === 'paper') {
      for (let i = 0; i < 15; i++) nodes.push(add(L, {
        left: '0px', top: px(70 + i * 70), width: '1920px', height: '1px',
        background: ink, opacity: '.10'
      }));
      nodes.push(add(L, { left: '120px', top: '0px', width: '2px', height: '1080px', background: accent, opacity: '.45' }));
    } else if (pattern === 'sunburst' || pattern === 'comic') {
      for (let i = 0; i < 18; i++) nodes.push(add(L, {
        left: '958px', top: '-180px', width: '4px', height: '1440px',
        transformOrigin: '2px 720px', transform: `rotate(${i * 20}deg)`,
        background: i % 2 ? accent : ink, opacity: pattern === 'comic' ? '.20' : '.16'
      }));
    } else if (pattern === 'bubbles' || pattern === 'learning') {
      for (let i = 0; i < 18; i++) {
        const r = 18 + (i * 23) % 92;
        nodes.push(add(L, {
          left: px((i * 173 + 47) % 1820), top: px((i * 97 + 31) % 980),
          width: px(r), height: px(r), borderRadius: '50%', border: `3px solid ${i % 3 ? ink : accent}`,
          opacity: '.20'
        }));
      }
    } else if (pattern === 'hud' || pattern === 'tech' || pattern === 'future') {
      for (let i = 0; i < 11; i++) nodes.push(add(L, {
        left: px(55 + i * 170), top: px(70 + (i % 4) * 220), width: px(115 + (i % 3) * 40), height: px(70 + (i % 2) * 55),
        border: `1px solid ${i % 2 ? accent : ink}`, opacity: '.18', boxShadow: `0 0 18px ${accent}33`
      }));
    } else if (pattern === 'news' || pattern === 'editorial') {
      nodes.push(add(L, { left: '70px', top: '90px', width: '1780px', height: '3px', background: accent, opacity: '.65' }));
      nodes.push(add(L, { left: '70px', top: '985px', width: '1780px', height: '1px', background: ink, opacity: '.28' }));
      for (let i = 0; i < 8; i++) nodes.push(add(L, {
        left: px(80 + i * 230), top: '120px', width: '1px', height: '820px', background: ink, opacity: '.08'
      }));
    } else if (pattern === 'wave') {
      for (let i = 0; i < 12; i++) nodes.push(add(L, {
        left: px(-100 + i * 180), top: px(760 + (i % 3) * 55), width: '430px', height: '110px',
        border: `3px solid ${i % 2 ? accent : ink}`, borderRadius: '50%', opacity: '.14', transform: `rotate(${i % 2 ? -8 : 8}deg)`
      }));
    } else if (pattern === 'luxury') {
      nodes.push(add(L, { left: '80px', top: '80px', width: '1760px', height: '920px', border: `1px solid ${accent}`, opacity: '.42' }));
      nodes.push(add(L, { left: '110px', top: '110px', width: '1700px', height: '860px', border: `1px solid ${ink}`, opacity: '.12' }));
      for (let i = 0; i < 5; i++) nodes.push(add(L, {
        left: px(950 + i * 150), top: px(130 + i * 115), width: px(520 - i * 55), height: px(520 - i * 55),
        border: `1px solid ${accent}`, borderRadius: '50%', opacity: '.14'
      }));
    } else if (pattern === 'video-wall' || pattern === 'footage') {
      for (let i = 0; i < 15; i++) nodes.push(add(L, {
        left: px(45 + (i % 5) * 380), top: px(55 + Math.floor(i / 5) * 340), width: '330px', height: '275px',
        background: `linear-gradient(${125 + i * 11}deg, ${ink}22, ${accent}44)`, border: `1px solid ${ink}33`,
        borderRadius: '18px', opacity: '.55', transform: `rotate(${(i % 3) - 1}deg)`
      }));
    } else {
      for (let i = 0; i < 18; i++) {
        nodes.push(add(L, { left: px(i * 120), top: '0px', width: '1px', height: '1080px', background: ink, opacity: '.08' }));
        if (i < 10) nodes.push(add(L, { left: '0px', top: px(i * 120), width: '1920px', height: '1px', background: ink, opacity: '.08' }));
      }
    }

    const label = add(L, {
      left: '78px', top: '54px', color: ink, font: `700 20px/1.1 ${visual.font || 'Inter, sans-serif'}`,
      letterSpacing: '5px', textTransform: 'uppercase', opacity: '.62'
    });
    label.textContent = `${cfg.id} · ${cfg.label || cfg.id}`;
    return { nodes, label, pattern };
  }

  function updatePattern(state, t, localTime) {
    const phase = localTime == null ? t : localTime;
    state.nodes.forEach((node, i) => {
      if (state.pattern === 'sunburst' || state.pattern === 'comic') {
        node.style.transform = `rotate(${i * 20 + phase * (i % 2 ? 1.4 : -1.1)}deg)`;
      } else if (state.pattern === 'bubbles' || state.pattern === 'learning') {
        node.style.transform = `translateY(${(Math.sin(phase * .8 + i) * 14).toFixed(2)}px)`;
      } else if (state.pattern === 'video-wall' || state.pattern === 'footage') {
        node.style.transform = `translateX(${((phase * (i % 2 ? -13 : 11)) % 45).toFixed(2)}px) rotate(${(i % 3) - 1}deg)`;
      } else if (state.pattern === 'hud' || state.pattern === 'tech' || state.pattern === 'future') {
        node.style.opacity = (.12 + .08 * (1 + Math.sin(phase * 1.3 + i)) / 2).toFixed(3);
      }
    });
  }

  function register(cfg) {
    if (!cfg || !/^T\d{2}$/.test(cfg.id)) throw new Error('invalid template adapter config');
    if (!cfg.window || !cfg.side || !cfg.theme) throw new Error(`${cfg.id}: incomplete template adapter config`);
    root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
    root.EVA_TEMPLATE_SKINS[cfg.id] = {
      win: cfg.window,
      side: cfg.side,
      theme: cfg.theme,
      themeOver: cfg.theme_over,
      cls: cfg.class,
      ring: () => ({
        color: (cfg.ring && cfg.ring.color) || (cfg.visual && cfg.visual.accent) || '#ffffff',
        width: (cfg.ring && cfg.ring.width) == null ? 5 : cfg.ring.width,
        glow: cfg.ring && cfg.ring.glow,
        shadow: (cfg.ring && cfg.ring.shadow) == null ? .25 : cfg.ring.shadow
      }),
      bg: (cfg.visual && cfg.visual.background) || '#11131a',
      build: L => buildPattern(L, cfg),
      update: (state, t, localTime) => updatePattern(state, t, localTime)
    };
  }

  root.EVA_SKIN_ADAPTER = { register };
})(window);
