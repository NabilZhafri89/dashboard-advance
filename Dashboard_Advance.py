import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import numpy as np
from datetime import datetime



st.set_page_config(page_title="Dashboard Advance", layout="wide")

st.markdown("""
<style>
section[data-testid="stSidebar"] { 
  position: relative; 
}

.sidebar-bottom {
  position: sticky;
  bottom: 12px;
  margin-top: 24px;
  z-index: 999;
}

.update-card {
  background: #966fd6;
  color: white;
  padding: 14px 16px;
  border-radius: 14px;
  box-shadow: none;
  border: none;
}

.update-card .title {
  font-weight: 700;
  margin-bottom: 6px;
}

.update-card .date {
  font-size: 16px;
  font-weight: 800;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
h1 {
  color: #00ff00;   /* hijau terang */
  font-weight: 700;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* PAGE BACKGROUND */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #e6e6fa !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p {
    color: white !important;
}


/* Placeholder text (kalau ada) */
section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {
    color: #536878 !important;
}

/* Dropdown list item text */
div[role="listbox"] span {
    color: #536878 !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* SIDEBAR BACKGROUND */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #B58CFF 0%,
        #8EA2FF 50%,
        #7B9CFF 100%
    ) !important;
}


}

/* Sidebar header */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Selectbox / input background */
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stMultiSelect {
    background-color: rgba(255,255,255,0.15);
    border-radius: 10px;
}



</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>



/* KPI CARD (st.metric) */
div[data-testid="stMetric"]{
  background: linear-gradient(
     135deg,
     #7B9CFF 0%,
     #B58CFF 100%
  );
  border-radius: 14px;
  padding: 20px 22px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}



/* KPI label */
div[data-testid="stMetric"] label{
  color: #f0f8ff;
  font-size: 14px;
}

/* KPI value */
div[data-testid="stMetric"] [data-testid="stMetricValue"]{
  color: #f8f8ff;
  font-weight: 700;
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>


  /* shadow sahaja, no border */
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);

  overflow: visible;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* BUANG SHADOW CHART */
div[data-testid="stPlotlyChart"] {
    box-shadow: none !important;
}

/* BUANG SHADOW KPI CARD */
div[data-testid="stMetric"] {
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* BUANG SEMUA GARISAN <hr> */
hr {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Tukar warna tajuk st.title() */
div[data-testid="stAppViewContainer"] div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stAppViewContainer"] h1 {
  color: #4b0082 !important;
}
</style>
""", unsafe_allow_html=True)
# -------------------------
# File paths
# -------------------------
BASE_FOLDER = Path(__file__).parent



CSV_BEKALAN = BASE_FOLDER / "GL Advance bekalan.csv"
CSV_DIRI    = BASE_FOLDER / "GL Advance diri.csv"
CSV_PTJ     = BASE_FOLDER / "DimPTJ.csv"   # PTJ file
CSV_STAF_DIRI = BASE_FOLDER / "LIST ID STAF ADVANCE DIRI.csv"

from datetime import datetime
import os


def file_token(p: Path) -> float:
    return os.path.getmtime(p) if p.exists() else 0.0

def get_last_modified_date(*paths):
    latest_ts = max(os.path.getmtime(p) for p in paths if os.path.exists(p))
    return datetime.fromtimestamp(latest_ts).strftime("%d %b %Y")

last_update = get_last_modified_date(CSV_BEKALAN, CSV_DIRI)


# -------------------------
# Helper: PTJ + HQ / Negeri / Cawangan logic
# -------------------------
def apply_ptj_hq_logic(df: pd.DataFrame, df_ptj: pd.DataFrame) -> pd.DataFrame:
    # 1) Normalise join keys: Funds Center & PTJ NO -> integer strings
    df["Funds Center Key"] = (
        pd.to_numeric(df["Funds Center"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )

    df_ptj["PTJ NO Key"] = (
        pd.to_numeric(df_ptj["PTJ NO"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )

    # 2) Take only needed columns from DimPTJ
    df_ptj_small = df_ptj[["PTJ NO Key", "PTJ", "BAHAGIAN/UNIT", "SEKTOR"]]

    # 3) Merge mapping onto GL data
    df = df.merge(
        df_ptj_small,
        left_on="Funds Center Key",
        right_on="PTJ NO Key",
        how="left"
    )

    # 4) Define list of Funds Centers that are BRANCHES (states/towns)
    BRANCH_FUNDS = {
        "10200012",  # KELANTAN
        "10200006",  # WPKL
        "10200009",  # JOHOR
        "10200010",  # PAHANG
        "10200008",  # MELAKA
        "10200030",  # SABAH
        "10200003",  # PULAU PINANG
        "10200004",  # PERAK
        "10200021",  # MIRI
        "10200001",  # PERLIS
        "10200002",  # KEDAH
        "10200032",  # SANDAKAN
        "10200007",  # N.SEMBILAN
        "10200020",  # SARAWAK
        "10200011",  # TERENGGANU
        "10200023",  # SIBU
        "10200005",  # SL-SELANGOR
        "10200031",  # TAWAU
        "10200022",  # BINTULU
    }

    is_branch = df["Funds Center Key"].isin(BRANCH_FUNDS)

    # 5) For NON-branch funds centers → force HQ / Ibu Pejabat
    df.loc[~is_branch, "PTJ"] = "HQ"
    df.loc[~is_branch, "BAHAGIAN/UNIT"] = "Ibu Pejabat"

    # 6) Drop helper keys
    df = df.drop(columns=["Funds Center Key", "PTJ NO Key"], errors="ignore")

    return df


# -------------------------
# Loaders
# -------------------------

def load_ptj():
    return pd.read_csv(CSV_PTJ)


def load_staf_diri():
    df = pd.read_csv(CSV_STAF_DIRI)

    # Keep only needed columns
    keep_cols = ["Document Number", "Supplier"]
    df = df[keep_cols].copy()

    # Normalise Document Number for joining
    df["Document Number Key"] = (
        df["Document Number"].astype(str).str.replace(r"\.0$", "", regex=True)
    )

    return df


def load_staff_master():
    df = pd.read_csv(BASE_FOLDER / "ID NAMA STAF.csv")

    # Clean column: convert No Staf to string without decimals
    df["NoStafKey"] = df["No Staf"].astype(str).str.replace(r"\.0$", "", regex=True)

    return df



def load_bekalan():
    df = pd.read_csv(CSV_BEKALAN)
    df_ptj = load_ptj()
    df_staff_master = load_staff_master()   # <-- NEW (to get Nama)

    # 1. Exclude specific document numbers
    exclude_list = ["390000008", "390000004"]
    df = df[~df["Invoice reference"].astype(str).isin(exclude_list)]

    # 2. Exclude rows where Posting Date is null
    df = df[df["Posting Date"].notna()]

    # 3. Add Detail column (A73102 → Bekalan)
    df["Detail"] = df["G/L Account"].apply(
        lambda x: "Bekalan" if str(x) == "A73102" else ""
    )

    # 4. CLEAN Supplier ID → SupplierKey (same logic as Pendahuluan Diri)
    df["SupplierKey"] = (
        df["Supplier"]
        .astype(str)
        .str.replace("E", "", regex=False)
        .str.lstrip("0")
    )

    # 5. Merge to get Nama Staf
    df = df.merge(
        df_staff_master[["NoStafKey", "Nama"]],
        left_on="SupplierKey",
        right_on="NoStafKey",
        how="left"
    )

    # 6. Apply PTJ + HQ logic
    df = apply_ptj_hq_logic(df, df_ptj)

    # 7. Remove helper columns
    df = df.drop(columns=[c for c in ["SupplierKey", "NoStafKey"] if c in df.columns])

    return df



def load_diri():
    df = pd.read_csv(CSV_DIRI)
    df_ptj = load_ptj()
    df_staf_map = load_staf_diri()       # mapping Document Number → Supplier (ID staf)
    df_staff_master = load_staff_master()  # master Nama staf

    # 1) Exclude rows with null Posting Date
    if "Posting Date" in df.columns:
        df = df[df["Posting Date"].notna()]

    # 2) Contra logic: build key = Reference + ABS(Amount)
    amount_abs = df["Amount in local currency"].astype(float).abs().round(2)

    df["ContraKey"] = (
        df["Reference"].astype(str).str.strip()
        + "|"
        + amount_abs.astype(str)
    )

    grp = df.groupby("ContraKey")["Amount in local currency"].agg(["min", "max"])
    keys_to_remove = grp[(grp["min"] < 0) & (grp["max"] > 0)].index

    # Remove all fully-contra rows
    df = df[~df["ContraKey"].isin(keys_to_remove)].copy()

    # 3) Merge LIST ID STAF ADVANCE DIRI to get Supplier by Document Number
    df["Document Number Key"] = (
        df["Document Number"].astype(str).str.replace(r"\.0$", "", regex=True)
    )

    df = df.merge(
        df_staf_map[["Document Number Key", "Supplier"]],
        on="Document Number Key",
        how="left"
    )

    # 4) Clean Supplier ID: remove 'E' + leading zeros → SupplierKey
    df["SupplierKey"] = (
        df["Supplier"]
        .astype(str)
        .str.replace("E", "", regex=False)
        .str.lstrip("0")
    )

    # 5) Merge master staff (ID NAMA STAF.csv) to get Nama
    df = df.merge(
        df_staff_master[["NoStafKey", "Nama"]],
        left_on="SupplierKey",
        right_on="NoStafKey",
        how="left"
    )

    # 6) Label & apply PTJ/HQ logic
    df["Detail"] = "Pendahuluan Diri"
    df = apply_ptj_hq_logic(df, df_ptj)

    # 7) Buang helper columns
    drop_cols = [c for c in ["ContraKey", "Document Number Key", "SupplierKey", "NoStafKey"]
                 if c in df.columns]
    df = df.drop(columns=drop_cols)

    return df


#Untuk date today#

def add_tempoh_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Posting Date" not in df.columns:
        return df

    # Today = whenever user opens the dashboard
    today = pd.Timestamp.today().normalize()

    # Ensure Posting Date is a clean datetime
    # - Works whether it's already datetime or a string like "2025-11-13"
    # - Strip spaces and coerce errors to NaT
    posting = pd.to_datetime(
        df["Posting Date"].astype(str).str.strip(),
        errors="coerce",
        dayfirst=False,          # your data is YYYY-MM-DD (e.g. 2025-11-13)
        infer_datetime_format=True,
    )

    # Days difference
    days = (today - posting.dt.normalize()).dt.days

    # Buckets:
    # > 90 days    → ">90 Hari"
    # > 60 days    → ">60 Hari" (61–90)
    # > 30 days    → ">30 Hari" (31–60)
    # > 14 days    → ">14 Hari" (15–30)
    # ≤ 14 days    → "<14 Hari"
    conditions = [
        days > 90,
        (days > 60) & (days <= 90),
        (days > 30) & (days <= 60),
        (days > 14) & (days <= 30),
        days <= 14,
    ]
    choices = [">90 Hari", ">60 Hari", ">30 Hari", ">14 Hari", "<14 Hari"]

    df["Tempoh"] = np.select(conditions, choices, default=None)

    return df



# -------------------------
# UI
# -------------------------
st.title("Dashboard Pendahuluan Diri dan Bekalan")

# -------------------------
# SLICER – Jenis Pendahuluan
# -------------------------
# -------------------------
# SIDEBAR – SLICER
# SIDEBAR – SLICERS
# -------------------------
# -------------------------
# SIDEBAR – SLICERS
# -------------------------
with st.sidebar:
    st.header("Tapisan")

    all_data = pd.concat([load_bekalan(), load_diri()], ignore_index=True)
    all_data = add_tempoh_column(all_data)

    jenis_list = ["All"] + sorted(all_data["Detail"].dropna().unique().tolist())
    selected_jenis = st.selectbox("Jenis Pendahuluan", jenis_list)

    if selected_jenis != "All":
        data_for_ptj = all_data[all_data["Detail"] == selected_jenis]
    else:
        data_for_ptj = all_data

    ptj_list = ["All"] + sorted(data_for_ptj["BAHAGIAN/UNIT"].dropna().unique().tolist())
    selected_ptj = st.selectbox("PTJ", ptj_list)

    data_for_tempoh = data_for_ptj.copy()
    if selected_ptj != "All":
        data_for_tempoh = data_for_tempoh[data_for_tempoh["BAHAGIAN/UNIT"] == selected_ptj]

    tempoh_list = ["All"] + sorted(data_for_tempoh["Tempoh"].dropna().unique().tolist())
    selected_tempoh = st.selectbox("Tempoh", tempoh_list)

    # ===== TARIKH KEMASKINI (BWH SEKALI) =====
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sidebar-bottom">
          <div class="update-card">
            <div class="title">Tarikh Kemaskini:</div>
            <div class="date">{last_update}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )




# -------------------------
# Pendauluan Bekalan (TOP)
# -------------------------

# -------------------------
# UI
# -------------------------

# --- Load & apply filters for BOTH datasets first ---
# --- Load & apply filters for BOTH datasets first ---
df_bekalan = load_bekalan()
df_diri = load_diri()

# Add Tempoh column BEFORE any filters
df_bekalan = add_tempoh_column(df_bekalan)
df_diri = add_tempoh_column(df_diri)


# Apply PTJ filter
if selected_ptj != "All":
    df_bekalan = df_bekalan[df_bekalan["BAHAGIAN/UNIT"] == selected_ptj]
    df_diri = df_diri[df_diri["BAHAGIAN/UNIT"] == selected_ptj]

# Apply Jenis Pendahuluan filter
if selected_jenis != "All":
    df_bekalan = df_bekalan[df_bekalan["Detail"] == selected_jenis]
    df_diri = df_diri[df_diri["Detail"] == selected_jenis]

# Apply Tempoh filter
if selected_tempoh != "All":
    df_bekalan = df_bekalan[df_bekalan["Tempoh"] == selected_tempoh]
    df_diri = df_diri[df_diri["Tempoh"] == selected_tempoh]
# -------------------------
# KPI CARDS
# -------------------------
total_bekalan = df_bekalan["Amount in local currency"].sum() if not df_bekalan.empty else 0
total_diri = df_diri["Amount in local currency"].sum() if not df_diri.empty else 0

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Jumlah Tunggakan Pendahuluan Bekalan (RM)",
        f"{total_bekalan:,.2f}"
    )

with col2:
    st.metric(
        "Jumlah Tunggakan Pendahuluan Diri (RM)",
        f"{total_diri:,.2f}"
    )

st.markdown("---")

# -------------------------
# VERTICAL BAR CHART – JUMLAH MENGIKUT PTJ (SHORTFORM)
# -------------------------
df_bekalan_bar = df_bekalan.copy()
df_diri_bar = df_diri.copy()

df_bekalan_bar["Jenis"] = "Bekalan"
df_diri_bar["Jenis"] = "Pendahuluan Diri"

df_all_bar = pd.concat([df_bekalan_bar, df_diri_bar], ignore_index=True)

if not df_all_bar.empty:
    df_bar_agg = (
        df_all_bar
        .dropna(subset=["PTJ"])
        .groupby("PTJ", as_index=False)["Amount in local currency"]
        .sum()
    )

    df_bar_agg["is_HQ"] = (df_bar_agg["PTJ"] == "HQ").astype(int)
    df_bar_agg = df_bar_agg.sort_values(
        by=["is_HQ", "Amount in local currency"],
        ascending=[False, False]
    )

    def format_number(n):
        n = float(n)
        if abs(n) >= 1_000_000:
            return f"{n/1_000_000:.1f} M"
        elif abs(n) >= 1_000:
            return f"{n/1_000:.1f} K"
        else:
            return f"{n:,.0f}"

    df_bar_agg["Label"] = df_bar_agg["Amount in local currency"].apply(format_number)

    fig = px.bar(
        df_bar_agg,
        x="PTJ",
        y="Amount in local currency",
        text="Label"
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=df_bar_agg["PTJ"].tolist(),
        showgrid=False,
        automargin=True
    )

    # Warna bar (turquoise) + buang outline
    fig.update_traces(
        marker_color="#bf94e4",
        marker_line_width=0,
        marker_cornerradius="50%",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        title=dict(
            text="Jumlah Baki Pendahuluan Mengikut PTJ",
            x=0.0,
            xanchor="left",
            font=dict(size=18)
        ),
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        margin=dict(l=0, r=60, t=60, b=0)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

else:
    st.info("Tiada data untuk dipaparkan dalam carta bagi kombinasi tapisan semasa.")







st.markdown("---")


# -------------------------
# TABLE – Pendahuluan Bekalan (TOP)
# -------------------------
st.subheader("Pendahuluan Bekalan – Raw Data")

# (Optional) Tempoh already added above, but safe to call again
df_bekalan = add_tempoh_column(df_bekalan)

hide_cols_bekalan = [
    c for c in [
        "Funds Center",
        "G/L Account",
        "Ref.key (header) 1",
        "Supplier",
        "Detail",
        "PTJ",
        "BAHAGIAN/UNIT",
        "SEKTOR",          # hide SEKTOR
    ]
    if c in df_bekalan.columns
]

# Create display copy AFTER deciding which columns to hide
df_bekalan_display = df_bekalan.drop(columns=hide_cols_bekalan).copy()

# Format Posting Date → DDMMYYYY
df_bekalan_display["Posting Date"] = pd.to_datetime(
    df_bekalan_display["Posting Date"], errors="coerce"
).dt.strftime("%d/%m/%Y")

# Format Amount → currency
df_bekalan_display["Amount in local currency"] = (
    df_bekalan_display["Amount in local currency"]
    .astype(float)
    .map("{:,.2f}".format)
)



st.dataframe(df_bekalan_display, use_container_width=True)

st.markdown("---")

# -------------------------
# TABLE – Pendahuluan Diri (BOTTOM)
# -------------------------
st.subheader("Pendahuluan Diri – Raw Data")

# (Optional) Tempoh already added above, but safe to call again
df_diri = add_tempoh_column(df_diri)

hide_cols_diri = [
    c for c in [
        "Funds Center",
        "G/L Account",
        "Document Header Text",
        "Supplier",
        "Detail",
        "PTJ",
        "BAHAGIAN/UNIT",
        "SEKTOR",          # hide SEKTOR
    ]
    if c in df_diri.columns
]

# Create display copy AFTER deciding which columns to hide
df_diri_display = df_diri.drop(columns=hide_cols_diri).copy()

# Format Posting Date → DDMMYYYY
df_diri_display["Posting Date"] = pd.to_datetime(
    df_diri_display["Posting Date"], errors="coerce"
).dt.strftime("%d/%m/%Y")

# Format Amount → currency
df_diri_display["Amount in local currency"] = (
    df_diri_display["Amount in local currency"]
    .astype(float)
    .map("{:,.2f}".format)
)

st.dataframe(df_diri_display, use_container_width=True)


