import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from gtts import gTTS
import tempfile

# Load Environment Variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)


# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI News Analyst",
    page_icon="📰",
    layout="wide"
)
st.markdown("""
<style>
/* Hide Streamlit Header */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Hide Toolbar */
[data-testid="stToolbar"] {
    display: none;
}

/* Hide Footer */
footer {
    visibility: hidden;
}

/* Remove Top Space */
.block-container {
    padding-top: 0rem;
}
/* Main App */
.stApp {
    background: linear-gradient(
    135deg,
    #020617,
    #0F172A,
    #1E293B,
    #334155
);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827;
}

/* Cards */
div[data-testid="stVerticalBlock"] {
    border-radius: 15px;
}

/* Buttons */
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 8px 20px;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #1D4ED8;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* Headings */
h1,h2,h3 {
    color: #F8FAFC;
}

/* Paragraphs */
/* Text */
p,
span,
label,
li,
ul,
ol {
    color: #E2E8F0 !important;
}

/* Markdown */
.stMarkdown,
.stMarkdown p,
.stMarkdown li,
.stMarkdown ul,
.stMarkdown ol,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    color: white !important;
}

/* Links */
a {
    color: #60A5FA;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown(
    """
    <h2 style="
        color:#00F5FF;
        font-size:32px;
        font-weight:700;
        text-shadow:0 0 15px #00F5FF;
    ">
        📰 News Topics
    </h2>
    """,
    unsafe_allow_html=True,
)

category = st.sidebar.radio(
    "📰 Select Topic",
    [
        "Polity",
        "Economy",
        "International Relations",
        "Defence",
        "Environment",
        "Science & Technology",
        "Agriculture",
        "Judiciary",
        "Education",
        "Health"
    ]
)


refresh = st.sidebar.button("🔄 Refresh News")


# -----------------------------
# Main Title
# -----------------------------
st.title("Tejas AI")
col1, col2 = st.columns([6,1])

with col1:
    st.caption("AI-powered India News Brief")

with col2:
    st.caption("👨‍💻 Developed By Atish Singh")

search = st.text_input(
    "",
    placeholder="🔍 Search any topic (RBI, GST, ISRO, India-China...)"
)

st.divider()
st.divider()

# -----------------------------
# Fetch News from NewsAPI
# -----------------------------
import requests

search_query = {
    "Polity": '"India" AND (Parliament OR Constitution OR Government OR Supreme Court)',
    "Economy": '"India" AND (RBI OR Economy OR GDP OR Inflation OR Budget)',
    "International Relations": '"India" AND (Foreign Policy OR Diplomacy OR G20 OR BRICS)',
    "Defence": '"India" AND (Army OR Navy OR Air Force OR Defence)',
    "Environment": '"India" AND (Climate OR Environment OR Pollution)',
    "Science & Technology": '"India" AND (ISRO OR AI OR Technology)',
    "Agriculture": '"India" AND (Agriculture OR Farmers OR Crops)',
    "Judiciary": '"India" AND (Supreme Court OR High Court OR Judiciary)',
    "Education": '"India" AND (Education OR UGC OR NEP)',
    "Health": '"India" AND (Health OR AIIMS OR Medical)'
}

# Use search box if user typed something
if search.strip():
    query = f'"{search}" AND India'
else:
    query = search_query[category]

url = (
    f"https://newsapi.org/v2/everything?"
    f"q={query}"
    f"&language=en"
    f"&sortBy=publishedAt"
    f"&pageSize=20"
    f"&apiKey={NEWS_API_KEY}"
)
response = requests.get(url)
news_data = response.json()


if news_data["status"] != "ok":
    st.error("Unable to fetch news.")
    st.stop()
articles = news_data.get("articles", [])


# -----------------------------
# News Section
# -----------------------------
st.subheader("📰 Latest News")

if articles:

    for article in articles:

        with st.container(border=True):

            left, right = st.columns([3, 1])

            with left:

                st.markdown(f"### {article['title']}")

                st.caption(
                    f"🏢 {article['source']['name']} | 📅 {article['publishedAt'][:10]}"
                )

            with right:

                if article["urlToImage"]:
                    st.image(article["urlToImage"], width=180)

            with st.spinner("Analyzing with NVIDIA AI..."):

                response = client.chat.completions.create(
                    model="meta/llama-3.1-8b-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
You are Tejas AI.

Explain the following Indian news in a simple UPSC-friendly manner.

Title:
{article['title']}

Description:
{article['description']}

Return ONLY in the format below.

🧠 Brief
<blank line>
Write one short paragraph (4-5 simple sentences).

📌 Key Points

• Every bullet must contain NEW information not already stated in the Brief.
• Do NOT repeat any sentence from the Brief.
• Mention names, dates, organisations, schemes, committees, laws and important facts.
• Do not write multiple bullets on one line
• One fact per bullet

Example:

- Point one
- Point two
- Point three



🎯 Why it Matters

Write 3 short bullet points and Do not write multiple bullets on one line


Return only this format.
"""
                        }
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
            st.markdown(response.choices[0].message.content)

            st.write("")

else:
    st.warning("No news available.")

st.divider()

st.divider()



