# EVA SC — Chinese web font subset

`eva-sc-400.woff` / `eva-sc-700.woff` are subsets of **Noto Sans CJK SC** Regular / Bold (Google / Adobe, the same design
as Noto Sans SC), licensed under the SIL Open Font License 1.1 (https://openfontlicense.org). Only the Simplified
Chinese characters the website itself uses are included (UI text in `i18n.js`, template names), so each file is ~150 KB
and is downloaded only when a page actually shows Chinese text (CSS `unicode-range`). Other Chinese characters (for
example in a customer's video title) fall back to the device's Chinese fonts, then to Google Fonts' Noto Sans SC.

Rebuild after adding Chinese UI text: `python3 saas/tools/build_cjk_font.py` (needs fonttools and the Noto CJK fonts).
