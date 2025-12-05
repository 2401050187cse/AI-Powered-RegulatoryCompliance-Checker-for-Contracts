import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from sklearn.linear_model import LinearRegression

# ---------------- BASIC UI ----------------
st.title("Hello Streamlit 👋")
st.write("This is my first Streamlit app!")

st.text_input("Enter Something")

st.title("Main Title")
st.header("Header")
st.subheader("Subheader")
st.text("Simple text")
st.markdown("**Bold**  *Italic*  `Code`")

# ---------------- USER INPUT ----------------
name1 = st.text_input("Enter your name:")
age = st.number_input("Enter age:", min_value=0, max_value=100)
hobby1 = st.selectbox("Choose a hobby", ["Coding", "Cricket", "Music"])
agree = st.checkbox("I agree to terms")

if agree:
    st.success(f"Hello {name1}, Age: {age}, Hobby: {hobby1}")

# ---------------- IMAGE ----------------
st.image(
    "https://images.unsplash.com/photo-1677442136019-21780ecad995",
    caption="Artificial Intelligence"
)

# ---------------- LAYOUT ----------------
col1, col2, col3 = st.columns(3)
col1.button("Button 1")
col2.button("Button 2")
col3.button("Button 3")

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["Tab A", "Tab B"])
with tab1:
    st.write("Content for A")
with tab2:
    st.write("Content for B")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Sidebar Menu")
option = st.sidebar.radio("Choose", ["Option 1", "Option 2"])
st.sidebar.write("Selected:", option)

# ---------------- DATA + CHARTS ----------------
df = pd.DataFrame({
    "A": np.random.randn(10),
    "B": np.random.randn(10)
})

st.dataframe(df)
st.table(df.head())

st.line_chart(df)
st.bar_chart(df)
st.area_chart(df)

# ---------------- MATPLOTLIB ----------------
fig, ax = plt.subplots()
ax.hist(df["A"], bins=5)
st.pyplot(fig)

# ---------------- SESSION STATE ----------------
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write("Counter:", st.session_state.count)

# ---------------- FILE UPLOAD ----------------
upload_file = st.file_uploader("Upload a CSV", type="csv")
if upload_file:
    df2 = pd.read_csv(upload_file)
    st.dataframe(df2)

# ---------------- FORM ----------------
with st.form("my_form"):
    fname = st.text_input("Name")
    fhobby = st.selectbox("Choose a hobby", ["Coding", "Cricket", "Music"])
    fagree = st.checkbox("I agree to terms")
    submit = st.form_submit_button("Submit")

if submit:
    st.success(f"Hello {fname}")

# ---------------- API CALL ----------------
try:
    response = requests.get("https://api.github.com/users/streamlit")
    st.json(response.json())
except:
    st.error("API not reachable")

# ---------------- MACHINE LEARNING ----------------
X = np.array(df["A"]).reshape(-1,1)
y = df["B"]

model = LinearRegression().fit(X, y)
st.write("Model Coefficient:", model.coef_)
