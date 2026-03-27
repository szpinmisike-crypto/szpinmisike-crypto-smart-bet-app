import streamlit as st
import json
import os

st.set_page_config(page_title="Smart Bet Tracker PRO", layout="centered")

DATA_FILE = "data.json"

# -----------------------
# LOAD / SAVE
# -----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"bankroll": 10000, "history": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -----------------------
# SESSION STATE
# -----------------------
if "bankroll" not in st.session_state:
    st.session_state.bankroll = data["bankroll"]

if "history" not in st.session_state:
    st.session_state.history = data["history"]

# -----------------------
# HEADER
# -----------------------
st.title("💰 Smart Bet Tracker PRO")

st.subheader(f"Bankroll: {int(st.session_state.bankroll)} Ft")

# -----------------------
# SETTINGS
# -----------------------
st.sidebar.title("⚙️ Beállítások")

risk_mode = st.sidebar.selectbox(
    "Kockázat szint",
    ["Biztonságos (1%)", "Normál (2%)", "Agresszív (5%)"]
)

if "1%" in risk_mode:
    risk = 0.01
elif "2%" in risk_mode:
    risk = 0.02
else:
    risk = 0.05

stop_loss = st.sidebar.number_input("Stop Loss", value=-2000)
take_profit = st.sidebar.number_input("Take Profit", value=3000)

# -----------------------
# STREAK ANALYSIS
# -----------------------
wins = 0
losses = 0

for h in reversed(st.session_state.history):
    if h["result"] == "Nyertem":
        if losses > 0:
            break
        wins += 1
    else:
        if wins > 0:
            break
        losses += 1

# -----------------------
# SMART BET LOGIC
# -----------------------
base_bet = st.session_state.bankroll * risk

# adaptív mód
if losses >= 3:
    recommended_bet = base_bet * 0.5
    st.warning("⚠️ Vesztes széria → tét csökkentve")
elif wins >= 3:
    recommended_bet = base_bet * 1.5
    st.success("🔥 Nyerő széria → tét növelve")
else:
    recommended_bet = base_bet

st.info(f"Ajánlott tét: {int(recommended_bet)} Ft")

# -----------------------
# ADD ROUND
# -----------------------
st.divider()
st.subheader("➕ Új kör")

bet_input = st.number_input("Tét", value=int(recommended_bet))
result = st.radio("Eredmény", ["Nyertem", "Vesztettem"])

if st.button("Mentés"):
    if result == "Nyertem":
        st.session_state.bankroll += bet_input
    else:
        st.session_state.bankroll -= bet_input

    st.session_state.history.append({
        "bet": bet_input,
        "result": result,
        "bankroll": st.session_state.bankroll
    })

    save_data({
        "bankroll": st.session_state.bankroll,
        "history": st.session_state.history
    })

    st.success("Mentve!")

# -----------------------
# LIMIT CHECK
# -----------------------
profit = st.session_state.bankroll - 10000

if profit <= stop_loss:
    st.error("🛑 Stop Loss elérve! Állj meg!")
if profit >= take_profit:
    st.success("💰 Cél elérve! Érdemes kiszállni!")

# -----------------------
# STATS
# -----------------------
st.divider()
st.subheader("📊 Statisztika")

if st.session_state.history:
    bankrolls = [h["bankroll"] for h in st.session_state.history]
    st.line_chart(bankrolls)

    wins_total = sum(1 for h in st.session_state.history if h["result"] == "Nyertem")
    total = len(st.session_state.history)

    st.write(f"Win rate: {round((wins_total/total)*100,1)}%")
    st.write(f"Körök száma: {total}")

# -----------------------
# RESET
# -----------------------
st.divider()
if st.button("🔄 Reset"):
    st.session_state.bankroll = 10000
    st.session_state.history = []
    save_data({"bankroll": 10000, "history": []})
    st.warning("Adatok törölve!")
