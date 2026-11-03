#!/usr/bin/env python3
"""Deploy step (GitHub Actions, `production` environment): Stripe TEST-mode webhook endpoint + its signing secret.

    stripe_webhook.py placeholder          make sure Modal secret `eva-stripe-webhook` exists (so the API can deploy)
    stripe_webhook.py sync API_URL         one endpoint for API_URL/api/stripe/webhook; secret stored ONLY in Modal Secrets

The signing secret is shown by Stripe once, at creation. It goes straight from Stripe's response into the Modal secret
manager (`modal secret create eva-stripe-webhook ...`) and is masked in the GitHub log; it is never printed, written to
disk, or stored in R2. The endpoint is tagged metadata[secret_store]=modal:eva-stripe-webhook only after the secret was
stored, so an interrupted run is repaired on the next deploy (untagged endpoint → replaced, new secret stored).
Refuses live keys.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))
import stripe_lite as S

NAME, TAG = "eva-stripe-webhook", "modal:eva-stripe-webhook"


def modal_secret(value):
    subprocess.run(["modal", "secret", "create", NAME, f"STRIPE_WEBHOOK_SECRET={value}", "--force"], check=True,
                   stdout=subprocess.DEVNULL)   # the CLI echoes key names only; output suppressed anyway


def exists():
    r = subprocess.run(["modal", "secret", "list"], capture_output=True, text=True, check=True)
    return NAME in r.stdout


def main():
    if S.mode() != "test": sys.exit("refusing: STRIPE_SECRET_KEY is not a test-mode key")
    if sys.argv[1] == "placeholder":
        if not exists(): modal_secret("unset"); print("created placeholder", NAME)
        else: print(NAME, "exists")
        return
    url = sys.argv[2].rstrip("/") + "/api/stripe/webhook"
    eps = [e for e in S.call("GET", "/webhook_endpoints?limit=100").get("data", []) if e["url"] == url]
    good = [e for e in eps if (e.get("metadata") or {}).get("secret_store") == TAG and set(S.EVENTS) <= set(e.get("enabled_events", []))]
    if good and exists():
        for e in eps:
            if e["id"] != good[0]["id"]: S.call("DELETE", f"/webhook_endpoints/{e['id']}")
        print("webhook kept", good[0]["id"]); return
    for e in eps: S.call("DELETE", f"/webhook_endpoints/{e['id']}")
    ep = S.call("POST", "/webhook_endpoints", {"url": url, "enabled_events": S.EVENTS, "description": "EVA Video Studio MVP (test)"})
    print(f"::add-mask::{ep['secret']}", flush=True)
    modal_secret(ep["secret"])
    S.call("POST", f"/webhook_endpoints/{ep['id']}", {"metadata": {"secret_store": TAG}})
    print("webhook created", ep["id"], "livemode", ep.get("livemode"), "- signing secret stored in Modal secret", NAME)


if __name__ == "__main__":
    main()
