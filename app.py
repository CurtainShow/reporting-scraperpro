import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math

st.set_page_config(page_title="ScraperPro Viewer", layout="wide", page_icon="🛒")

FILIALES = ["cz", "de", "hr", "hu", "it", "pl", "pt", "si", "sk"]

FLAG = {
    "co_uk": "🇬🇧", "cz": "🇨🇿", "de": "🇩🇪", "hr": "🇭🇷",
    "hu": "🇭🇺", "it": "🇮🇹", "pl": "🇵🇱", "pt": "🇵🇹",
    "si": "🇸🇮", "sk": "🇸🇰",
}

STOCK_COLOR = {
    "high":   ("#d4edda", "#155724"),
    "low":    ("#fff3cd", "#856404"),
    "zero":   ("#f8d7da", "#721c24"),
    "none":   ("#e9ecef", "#6c757d"),
}

CSS = """
<style>
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; }

.card {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 16px 18px 14px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
}

/* ── Header ── */
.card-header { display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
.product-name { font-size:1rem; font-weight:700; color:#212529; margin-bottom:6px; }

.badge {
    display:inline-block; padding:3px 9px; border-radius:20px;
    font-size:.72rem; font-weight:600; margin:2px;
}
.badge-mig  { background:#d0e8ff; color:#0a58ca; }
.badge-attr { background:#f0e6ff; color:#6f42c1; }
.badge-pid  { background:#e8f5e9; color:#2e7d32; }

/* ── Match banner ── */
.match-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, #fff8e1, #fffde7);
    border: 1.5px solid #ffe082;
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.match-label {
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #9e6f00;
    white-space: nowrap;
}
.match-sku {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #ffffff;
    border: 1px solid #ffe082;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: .82rem;
    font-weight: 600;
    color: #333;
}
.match-sku .country { font-size: .85rem; }
.no-match {
    font-size: .75rem;
    color: #aaa;
    font-style: italic;
}

/* ── Filiales grid ── */
.filiale-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(155px, 1fr));
    gap: 8px;
    margin-top: 4px;
}
.filiale-cell {
    border-radius: 8px;
    padding: 8px 10px;
    font-size: .8rem;
    line-height: 1.55;
    border: 1px solid transparent;
}
.filiale-cell.ref-cell {
    border: 2px solid #adb5bd !important;
    background: #f8f9fa !important;
    position: relative;
}
.ref-label {
    position: absolute;
    top: -9px; left: 8px;
    background: #fff;
    border: 1px solid #adb5bd;
    border-radius: 4px;
    font-size: .62rem;
    font-weight: 700;
    color: #6c757d;
    padding: 0 5px;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.filiale-flag { font-size: 1rem; }
.filiale-name { font-weight: 700; font-size: .8rem; }
.price-gross  { font-size: .92rem; font-weight: 700; color: #1a1a2e; }
.price-net    { font-size: .73rem; color: #666; }
.delivery     { font-size: .7rem; color: #777; font-style: italic; margin-top: 2px; }
.stock-badge  {
    display: inline-block;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: .68rem;
    font-weight: 600;
}
.unavailable  { background: #f5f5f5; color: #bbb; }

/* ── Button ── */
.url-btn {
    display: inline-block;
    margin-top: 12px;
    padding: 6px 16px;
    background: #0d6efd;
    color: #fff !important;
    font-size: .78rem;
    font-weight: 600;
    border-radius: 6px;
    text-decoration: none;
    transition: background .15s;
}
.url-btn:hover { background: #0b5ed7; }
</style>
"""


def stock_style(val):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return STOCK_COLOR["none"]
    if math.isnan(v):
        return STOCK_COLOR["none"]
    if v > 10:
        return STOCK_COLOR["high"]
    if v > 0:
        return STOCK_COLOR["low"]
    return STOCK_COLOR["zero"]


def stock_label(val):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if math.isnan(v):
        return "N/A"
    return f"{int(v)} en stock"


def render_card(row: pd.Series) -> str:
    name    = row.get("product_name", "—")
    mig     = row.get("MIG", "—")
    attr    = row.get("attributes", "—")
    pid     = row.get("pid", "—")
    url     = row.get("url", "")
    sku_ita = row.get("SKU_ManITA", "")
    sku_es  = row.get("SKU_ManES", "")

    # ── Match banner ─────────────────────────────────────────────────────────
    has_ita = pd.notna(sku_ita) and str(sku_ita).strip() not in ("", "nan")
    has_es  = pd.notna(sku_es)  and str(sku_es).strip()  not in ("", "nan")

    if has_ita or has_es:
        sku_items = ""
        if has_ita:
            sku_items += f'<span class="match-sku"><span class="country">🇮🇹</span>{sku_ita}</span>'
        if has_es:
            sku_items += f'<span class="match-sku"><span class="country">🇪🇸</span>{sku_es}</span>'
        match_block = f"""
        <div class="match-banner">
            <span class="match-label">✅ Match</span>
            {sku_items}
        </div>"""
    else:
        match_block = '<div class="match-banner"><span class="match-label">Match</span><span class="no-match">Aucun SKU correspondant</span></div>'

    # ── co_uk reference cell (first in grid) ─────────────────────────────────
    ref_gross    = row.get("price_gross", "—")
    ref_net      = row.get("price_net", "—")
    ref_currency = row.get("price_currency", "GBP")
    ref_stock    = row.get("stock", None)
    ref_delivery = row.get("delivery_label", "—")
    bg_r, fg_r   = stock_style(ref_stock)

    ref_cell = f"""
    <div class="filiale-cell ref-cell" style="background:#f8f9fa;">
        <span class="ref-label">Référence</span>
        <span class="filiale-flag">{FLAG['co_uk']}</span>
        <span class="filiale-name"> CO_UK</span><br>
        <span class="price-gross">{ref_gross} {ref_currency}</span><br>
        <span class="price-net">net {ref_net}</span><br>
        <span class="stock-badge" style="background:{bg_r};color:{fg_r};">{stock_label(ref_stock)}</span>
        <div class="delivery">{ref_delivery}</div>
    </div>"""

    # ── Other filiales ────────────────────────────────────────────────────────
    cells = ref_cell
    for f in FILIALES:
        gross    = row.get(f"price_gross_{f}")
        net      = row.get(f"price_net_{f}")
        currency = row.get(f"price_currency_{f}", "")
        delivery = row.get(f"delivery_label_{f}", "—")
        stk      = row.get(f"stock_{f}")
        bg2, fg2 = stock_style(stk)

        if pd.isna(gross):
            cells += f"""
            <div class="filiale-cell unavailable">
                <span class="filiale-flag">{FLAG[f]}</span>
                <span class="filiale-name"> {f.upper()}</span><br>
                <em style="font-size:.73rem;">Non disponible</em>
            </div>"""
        else:
            cells += f"""
            <div class="filiale-cell" style="background:{bg2}18;border-color:{bg2};">
                <span class="filiale-flag">{FLAG[f]}</span>
                <span class="filiale-name"> {f.upper()}</span><br>
                <span class="price-gross">{gross} {currency}</span><br>
                <span class="price-net">net {net}</span><br>
                <span class="stock-badge" style="background:{bg2};color:{fg2};">{stock_label(stk)}</span>
                <div class="delivery">{delivery}</div>
            </div>"""

    # ── Button ────────────────────────────────────────────────────────────────
    btn = f'<a class="url-btn" href="{url}" target="_blank">🔗 Voir le produit</a>' if url else ""

    return f"""
    <div class="card">
        <div class="card-header">
            <div>
                <div class="product-name">{name}</div>
                <div>
                    <span class="badge badge-mig">MIG {mig}</span>
                    <span class="badge badge-attr">{attr}</span>
                    <span class="badge badge-pid">PID {pid}</span>
                </div>
            </div>
        </div>
        {match_block}
        <div class="filiale-grid">{cells}</div>
        {btn}
    </div>
    """


# ── UI ───────────────────────────────────────────────────────────────────────

st.title("🛒 ScraperPro — Viewer")

uploaded = st.file_uploader(
    "Charger le fichier CSV agrégé (séparateur `;`)",
    type=["csv"],
    help="aggregated_result_with_sku.csv ou tout fichier au même format",
)

if uploaded is None:
    st.info("Chargez un fichier CSV pour commencer.")
    st.stop()


@st.cache_data(show_spinner="Chargement du fichier…")
def load(file):
    return pd.read_csv(file, sep=";", dtype=str, encoding="utf-8-sig")


df = load(uploaded)

num_cols = (
    ["price_gross", "price_net", "stock"]
    + [f"price_gross_{f}" for f in FILIALES]
    + [f"price_net_{f}"   for f in FILIALES]
    + [f"stock_{f}"       for f in FILIALES]
)
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ── Filtres ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtres")
    search         = st.text_input("🔍 Recherche (nom, MIG, SKU…)")
    migs           = sorted(df["MIG"].dropna().unique().tolist()) if "MIG" in df.columns else []
    sel_mig        = st.multiselect("MIG", migs)
    filiale_stock  = st.selectbox("Filiale avec stock disponible", ["(toutes)"] + FILIALES)
    only_matched   = st.checkbox("Uniquement les produits avec SKU ITA/ES")
    st.markdown("---")
    per_page       = st.select_slider("Cartes par page", options=[10, 20, 50, 100], value=20)

# ── Filtrage ──────────────────────────────────────────────────────────────────
filtered = df.copy()

if search:
    mask = filtered.apply(
        lambda r: r.astype(str).str.contains(search, case=False, na=False).any(), axis=1
    )
    filtered = filtered[mask]

if sel_mig:
    filtered = filtered[filtered["MIG"].isin(sel_mig)]

if filiale_stock != "(toutes)":
    col = f"stock_{filiale_stock}"
    if col in filtered.columns:
        filtered = filtered[filtered[col] > 0]

if only_matched:
    mask = filtered["SKU_ManITA"].notna() & (filtered["SKU_ManITA"].astype(str).str.strip() != "")
    filtered = filtered[mask]

total       = len(filtered)
total_pages = max(1, math.ceil(total / per_page))

# ── Pagination ────────────────────────────────────────────────────────────────
col_info, col_page = st.columns([3, 1])
with col_info:
    st.markdown(f"**{total}** résultats &nbsp;|&nbsp; page **{min(1, total_pages)}/{total_pages}**",
                unsafe_allow_html=True)
with col_page:
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1,
                           label_visibility="collapsed")

start = (page - 1) * per_page
chunk = filtered.iloc[start: start + per_page]

# ── Rendu ─────────────────────────────────────────────────────────────────────
if total == 0:
    st.warning("Aucun résultat pour ces filtres.")
else:
    all_cards = "\n".join(render_card(row) for _, row in chunk.iterrows())
    html_page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">{CSS}</head>
<body style="background:transparent;margin:0;padding:4px 0;">{all_cards}</body>
</html>"""
    components.html(html_page, height=per_page * 400, scrolling=True)
