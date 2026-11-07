#!/usr/bin/env python3
"""Offline check of the Stripe step in browser_e2e.py against mock Checkout layouts (no network, no Stripe):
A  accordion visible → must click it, then fill;  B  card already active + a HIDDEN "Pay with card" button → must NOT
click it, fill directly;  C  card fields inside an iframe;  D  nothing usable → must fail fast and save diagnostics."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from playwright.sync_api import sync_playwright
import browser_e2e as E

FIELDS = """<input id="cardNumber" placeholder="1234"><input id="cardExpiry"><input id="cardCvc">
<input id="billingName"><input id="billingPostalCode">"""
SUBMIT = """<button type="submit" onclick="top.paid={n:(document.getElementById('cardNumber')||frames[0].document.getElementById('cardNumber')).value,
 e:(document.getElementById('cardExpiry')||frames[0].document.getElementById('cardExpiry')).value}">Pay</button>"""
PAGES = {
 "A": f"""<input id="email" type="email"><button data-testid="card-accordion-item-button" onclick="window.clicked=1;document.getElementById('f').style.display='block'">Pay with card</button>
      <div id="f" style="display:none">{FIELDS}</div>{SUBMIT}""",
 "B": f"""<input id="email" type="email"><button data-testid="card-accordion-item-button" style="display:none" onclick="window.clicked=1">Pay with card</button>
      {FIELDS}{SUBMIT}""",
 "C": f"""<input id="email" type="email"><iframe srcdoc='{FIELDS.replace(chr(10), " ")}' style="width:600px;height:80px"></iframe>{SUBMIT}""",
 "D": """<input id="email" type="email"><button data-testid="card-accordion-item-button" style="display:none">Pay with card</button>""",
}


def main():
    out = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch()
        for k, html in PAGES.items():
            pg = b.new_page(); pg.set_content(f"<html><body>{html}</body></html>")
            if k == "D":
                try: E.stripe_pay(pg, out, "t@example.com", redact=["SECRETTOKEN"], timeout=5); sys.exit("D should fail")
                except RuntimeError as e: assert (out / "stripe_fail.png").exists() and (out / "stripe_fail.html").exists(); print("D: failed as expected:", e)
                continue
            st = E.stripe_pay(pg, out, "t@example.com", timeout=10)
            paid = pg.evaluate("() => window.paid"); clicked = pg.evaluate("() => window.clicked || 0")
            assert paid and paid["n"] == "4242 4242 4242 4242" and paid["e"] == "12 / 34", (k, paid)
            assert (k == "A") == (clicked == 1), (k, clicked)       # A clicks, B never clicks the hidden accordion
            assert st.startswith("A" if k == "A" else "B"), (k, st)
            print(f"{k}: {st}; paid with test card; accordion clicked={clicked}")
        b.close()
    print("stripe checkout UI tests: ok")


if __name__ == "__main__":
    main()
