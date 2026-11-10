/* Plans page — CONCEPT ONLY. No checkout, no Stripe: every subscription/pack button is disabled ("Coming soon").
   The live $9.99 / 100-credit top-up is the existing flow (account.html#billing), unchanged. */
(function () {
  const $ = s => document.querySelector(s);
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v);
    kids.forEach(k => e.append(k)); return e; };
  const PLANS = [
    { id: "creator", name: "Creator", month: 19.99, credits: 200, blurb: "For a few polished shorts every month." },
    { id: "pro", name: "Pro", month: 39.99, credits: 450, blurb: "For weekly creators and small brands.", popular: true },
    { id: "studio", name: "Studio", month: 79.99, credits: 1000, blurb: "For teams and agencies publishing daily." }];
  const PACKS = [{ price: 9.99, credits: 100, live: true }, { price: 24.99, credits: 270 }, { price: 49.99, credits: 560 }];
  const YEAR_OFF = 0.20, HD = [43, 52];                       // HD export cost today: 10 s → 43, 30 s → 52 credits
  const money = n => "$" + n.toFixed(2), cents = n => (n * 100).toFixed(1).replace(/\.0$/, "") + "¢";
  const yearMonthly = m => Math.floor(m * (1 - YEAR_OFF) * 100) / 100;      // 19.99 → 15.99
  let period = "month";
  function render() {
    $("#pGrid").replaceChildren(...PLANS.map(p => {
      const y = period === "year", per = y ? yearMonthly(p.month) : p.month;
      const hd = `about ${Math.floor(p.credits / HD[1])}–${Math.floor(p.credits / HD[0])} HD exports a month`;
      return el("article", { class: "p-card" + (p.popular ? " pop" : ""), "data-plan": p.id }, [
        p.popular ? el("span", { class: "p-badge", text: "Most popular" }) : "",
        el("h3", { text: p.name }), el("p", { class: "hint", text: p.blurb }),
        el("div", { class: "p-price" }, [el("b", { text: money(per) }), el("span", { text: "/month" })]),
        el("p", { class: "p-bill", text: y ? `${money(+(per * 12).toFixed(2))} billed yearly · save ${money(+(p.month * 12 - per * 12).toFixed(2))}` : "Billed monthly · cancel any time" }),
        el("ul", {}, [el("li", {}, [el("b", { text: p.credits.toLocaleString() + " credits" }), document.createTextNode(y ? " added every month" : " every month")]),
          el("li", { text: hd }), el("li", { text: `${cents(per / p.credits)} per credit` }), el("li", { text: "All available templates" })]),
        el("button", { class: "btn", type: "button", disabled: "", "aria-disabled": "true", text: "Coming soon" })]);
    }));
    document.querySelectorAll(".p-toggle button").forEach(b => b.setAttribute("aria-checked", String(b.dataset.period === period)));
  }
  document.querySelectorAll(".p-toggle button").forEach(b => b.onclick = () => { period = b.dataset.period; render(); });
  $("#pPacks").replaceChildren(...PACKS.map(k => el("div", { class: "p-pack" + (k.live ? " live" : "") }, [
    el("b", { text: `${k.credits} credits` }), el("span", { class: "p-pp", text: money(k.price) }), el("span", { class: "hint", text: `${cents(k.price / k.credits)} per credit` }),
    k.live ? el("a", { class: "btn small", href: "account.html#billing", text: "Buy now" })
           : el("button", { class: "btn small ghost", type: "button", disabled: "", text: "Coming soon" })])));
  render();
  if (window.EVA && EVA.header) EVA.header();
})();
