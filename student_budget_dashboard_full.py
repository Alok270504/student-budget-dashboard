# ---------------------------------------------------------
# 🎓 Student Budget Dashboard (Full Version)
# ---------------------------------------------------------
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(page_title="Student Budget Dashboard", layout="wide")
st.title("🎓 Student Budget Dashboard")

DATA_DIR = Path("./budget_data")
DATA_DIR.mkdir(exist_ok=True)
F_EXP = DATA_DIR / "expenses.csv"
F_INC = DATA_DIR / "income.csv"

EXPENSE_COLS = ["date", "category", "description", "amount", "payment_method"]
INCOME_COLS  = ["date", "type", "source", "amount"]

def load_csv(path, cols):
    if path.exists():
        try:
            df = pd.read_csv(path)
        except Exception:
            df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(columns=cols)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df

def save_csv(df, path):
    out = df.copy()
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False)

if "expenses" not in st.session_state:
    st.session_state.expenses = load_csv(F_EXP, EXPENSE_COLS)
if "income" not in st.session_state:
    st.session_state.income = load_csv(F_INC, INCOME_COLS)

def _get_dialog():
    dlg = getattr(st, "dialog", None)
    if dlg is None:
        dlg = getattr(st, "experimental_dialog", None)
    return dlg

def show_expense_dialog(category):
    st.session_state._current_category = category
    title = f"Add Expense — {category}"
    def body():
        st.markdown(f"### {title}")
        left, right = st.columns([1,1])
        with left:
            st.markdown("**Single Entry**")
            with st.form(f"exp_single_{category}", clear_on_submit=True):
                d = st.date_input("Date", value=date.today(), key=f"d_{category}")
                desc = st.text_input("Description", key=f"desc_{category}")
                amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0, key=f"amt_{category}")
                pay = st.selectbox("Payment Method", ["UPI","Cash","Card","Bank"], key=f"pay_{category}")
                add = st.form_submit_button("➕ Add")
            if add:
                row = {"date": d, "category": category, "description": desc,
                       "amount": -abs(amt), "payment_method": pay}
                st.session_state.expenses = pd.concat(
                    [st.session_state.expenses, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.expenses, F_EXP)
                st.success("Added expense!")
        with right:
            st.markdown("**Upload CSV/XLSX**")
            up = st.file_uploader("Upload file", type=["csv","xlsx","xls"], key=f"up_{category}")
            if st.button("📥 Import", key=f"imp_{category}"):
                try:
                    df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
                    df["category"] = category
                    df["amount"] = -df["amount"].abs()
                    st.session_state.expenses = pd.concat(
                        [st.session_state.expenses, df], ignore_index=True)
                    save_csv(st.session_state.expenses, F_EXP)
                    st.success(f"Imported {len(df)} rows.")
                except Exception as e:
                    st.error(f"Error: {e}")

    dlg = _get_dialog()
    if dlg:
        @dlg(title)
        def _dlg(): body()
        _dlg()
    else:
        with st.expander(title, expanded=True): body()

def show_income_dialog(kind):
    st.session_state._current_income_type = kind
    title = f"Add {kind}"
    def body():
        st.markdown(f"### {title}")
        left, right = st.columns([1,1])
        with left:
            st.markdown("**Single Entry**")
            with st.form(f"inc_single_{kind}", clear_on_submit=True):
                d = st.date_input("Date", value=date.today(), key=f"id_{kind}")
                src = st.text_input("Source", value=("Stipend" if kind=="Income" else "Parents"), key=f"isrc_{kind}")
                amt = st.number_input("Amount (₹)", min_value=0.0, step=100.0, key=f"iamt_{kind}")
                add = st.form_submit_button("➕ Add")
            if add:
                row = {"date": d, "type": kind, "source": src, "amount": abs(amt)}
                st.session_state.income = pd.concat(
                    [st.session_state.income, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.income, F_INC)
                st.success(f"Added {kind}!")
        with right:
            st.markdown("**Upload CSV/XLSX**")
            up = st.file_uploader("Upload file", type=["csv","xlsx","xls"], key=f"iup_{kind}")
            if st.button("📥 Import", key=f"iimp_{kind}"):
                try:
                    df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
                    df["type"] = kind
                    st.session_state.income = pd.concat(
                        [st.session_state.income, df], ignore_index=True)
                    save_csv(st.session_state.income, F_INC)
                    st.success(f"Imported {len(df)} rows.")
                except Exception as e:
                    st.error(f"Error: {e}")

    dlg = _get_dialog()
    if dlg:
        @dlg(title)
        def _dlg(): body()
        _dlg()
    else:
        with st.expander(title, expanded=True): body()

st.subheader("💸 Add Income / Pocket Money")
colA, colB = st.columns(2)
with colA:
    if st.button("➕ Income", use_container_width=True):
        show_income_dialog("Income")
with colB:
    if st.button("💚 Pocket Money", use_container_width=True):
        show_income_dialog("Pocket Money")

st.markdown("---")
st.subheader("🧾 Add Expenses by Category")
EXPENSE_TYPES = ["Food","Transport","Groceries","Entertainment","Education","Health","Shopping","Bills","Essentials","Other"]
cols_per_row = 5
rows = (len(EXPENSE_TYPES)+cols_per_row-1)//cols_per_row
idx = 0
for _ in range(rows):
    cols = st.columns(cols_per_row)
    for c in cols:
        if idx >= len(EXPENSE_TYPES): break
        cat = EXPENSE_TYPES[idx]
        if c.button(f"➕ {cat}", use_container_width=True, key=f"btn_{cat}"):
            show_expense_dialog(cat)
        idx += 1

st.markdown("---")
st.header("📊 Summary")
exp = st.session_state.expenses.copy()
inc = st.session_state.income.copy()
total_exp = (-exp["amount"]).sum() if not exp.empty else 0
total_inc = inc["amount"].sum() if not inc.empty else 0
m1, m2, m3 = st.columns(3)
m1.metric("Total Income", f"₹{total_inc:,.0f}")
m2.metric("Total Expenses", f"₹{total_exp:,.0f}")
m3.metric("Total Savings", f"₹{(total_inc-total_exp):,.0f}")

if not exp.empty:
    cat = exp.groupby("category")["amount"].sum().abs().sort_values(ascending=False)
    st.subheader("Spend by Category")
    st.bar_chart(cat)
