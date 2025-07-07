import streamlit as st
import pandas as pd
import altair as alt

# Load your Excel data
@st.cache_data
def load_data():
    df = pd.read_excel("Clarkson-Columbia.xlsx", header=1)
    return df

df = load_data()

st.title("🎯 University Decision Matrix: Clarkson vs Columbia")
st.markdown("Customize weights and explore your smartest fit")

# --- Sliders for weight customization ---
st.sidebar.header("🎛️ Adjust Category Weights")

weights = []
for i, category in enumerate(df["Category"]):
    raw_weight = df.loc[i, "Weight (%)"]
    default_weight = int(raw_weight) if pd.notna(raw_weight) else 0
    weight = st.sidebar.slider(label=category, min_value=0, max_value=30, value=default_weight, step=1)
    weights.append(weight)

df["Custom Weight (%)"] = weights

# --- Live weighted score calculation ---
df["Clarkson Score"] = df["Clarkson"] * df["Custom Weight (%)"] / 100
df["Columbia Score"] = df["Columbia (No EYUF)"] * df["Custom Weight (%)"] / 100
df["EYUF Score"] = df["Columbia (With EYUF)"] * df["Custom Weight (%)"] / 100

total_scores = {
    "Clarkson": round(df["Clarkson Score"].sum(), 2),
    "Columbia (No EYUF)": round(df["Columbia Score"].sum(), 2),
    "Columbia (With EYUF)": round(df["EYUF Score"].sum(), 2)
}

# --- Show inputs and calculations ---
st.subheader("📊 Matrix Input + Live Scores")
st.dataframe(df[["Category", "Custom Weight (%)", "Clarkson", "Columbia (No EYUF)", "Columbia (With EYUF)",
                 "Clarkson Score", "Columbia Score", "EYUF Score"]])

# --- Visual bar chart ---
st.subheader("📈 Comparison Chart")
chart_df = pd.DataFrame.from_dict(total_scores, orient="index", columns=["Score"]).reset_index()
chart_df.columns = ["Option", "Score"]

bar = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X("Option", sort="-y"),
    y="Score",
    color="Option"
).properties(width=600)

st.altair_chart(bar)

# --- Recommendation & Reasoning ---
best = chart_df.loc[chart_df["Score"].idxmax()]

st.success(f"✅ Based on your custom weights, the best fit is **{best['Option']}** with a score of {best['Score']}.")

# Show top contributing factor
top_factor_idx = df[best['Option'] + " Score"].idxmax()
top_factor = df.loc[top_factor_idx, "Category"]
top_reason = df.loc[top_factor_idx, "Reasoning / Notes"]

st.markdown(f"📌 **Top factor influencing this decision:** `{top_factor}`")
st.markdown(f"🧠 *Why:* {top_reason}")

# --- Optional: show reasoning table ---
with st.expander("📝 See full reasoning for all categories"):
    st.dataframe(df[["Category", "Reasoning / Notes"]])
