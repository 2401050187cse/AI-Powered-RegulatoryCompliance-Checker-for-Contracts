import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ========================= LOAD ENV =========================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("DEFAULT_RECEIVER_EMAIL")

# ========================= LANGCHAIN =========================
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# ========================= PAGE CONFIG =========================
st.set_page_config(
    page_title="AI-Powered Regulatory Compliance Checker",
    layout="wide",
)

# ========================= PATHS =========================
UPLOAD_DIR = "uploads"
UPDATED_DIR = "updated_contracts"
FAISS_INDEX_PATH = "faiss_index"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(UPDATED_DIR, exist_ok=True)

# ========================= SESSION STATE =========================
if "contract_text" not in st.session_state:
    st.session_state.contract_text = ""
if "amended_text" not in st.session_state:
    st.session_state.amended_text = ""
if "amended_file_path" not in st.session_state:
    st.session_state.amended_file_path = ""

# ========================= EMBEDDINGS =========================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ========================= LOAD VECTOR STORE =========================
@st.cache_resource
def load_or_build_vector_store():
    """Load existing FAISS index or build from Dataset files"""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import TextLoader
        from pathlib import Path
        
        # Try loading existing index first
        if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
            try:
                st.info("📦 Loading existing FAISS index...")
                vector_store = FAISS.load_local(
                    FAISS_INDEX_PATH,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                st.success("✅ FAISS index loaded!")
                return vector_store
            except Exception as e:
                st.warning(f"Could not load existing index: {e}. Building new one...")
        
        # Build new index from Dataset
        st.info("🔄 Building FAISS index from Dataset...")
        
        dataset_path = Path("Dataset/contracts")
        docs = []
        
        if dataset_path.exists():
            for txt_file in dataset_path.glob("*.txt"):
                try:
                    loader = TextLoader(str(txt_file), encoding="utf-8")
                    docs.extend(loader.load())
                except Exception as e:
                    st.warning(f"Could not load {txt_file}: {e}")
        
        if not docs:
            st.error("❌ No documents found in Dataset/contracts")
            return None
        
        # Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)
        st.info(f"📚 Split into {len(chunks)} chunks")
        
        # Build FAISS index
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)
        st.success("✅ FAISS index built and saved!")
        
        return vector_store
    except Exception as e:
        st.error(f"❌ Error with vector store: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Initialize vector store
vector_store = load_or_build_vector_store()

# ========================= LLM =========================
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.3
)

# ========================= EMAIL FUNCTION =========================
def convert_txt_to_pdf(txt_content: str, pdf_path: str) -> bool:
    """Convert text content to PDF file"""
    try:
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*72, bottomMargin=0.5*72)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = styles['Heading1']
        story.append(Paragraph("AMENDED CONTRACT", title_style))
        story.append(Spacer(1, 12))
        
        # Split content into paragraphs and create paragraphs with better styling
        paragraphs = txt_content.split("\n")
        for para_text in paragraphs:
            clean_text = para_text.strip()
            if clean_text:
                try:
                    story.append(Paragraph(clean_text, styles['Normal']))
                except:
                    # Fallback for problematic text
                    story.append(Paragraph(clean_text.replace('<', '&lt;').replace('>', '&gt;'), styles['Normal']))
            story.append(Spacer(1, 6))
        
        doc.build(story)
        st.info(f"📄 PDF created: {pdf_path}")
        return True
    except Exception as e:
        st.error(f"❌ PDF conversion failed: {str(e)}")
        return False

def send_email_with_attachment(recipient_email: str, subject: str, file_path: str) -> bool:
    """Send email with file attachment"""
    try:
        st.info(f"📧 Email Config - Sender: {EMAIL_SENDER}")
        st.info(f"📧 Email Config - Receiver: {recipient_email}")
        
        if not EMAIL_SENDER or not EMAIL_PASSWORD:
            st.error("❌ Email configuration not set. Check .env file")
            st.error(f"   SENDER_EMAIL = {EMAIL_SENDER}")
            st.error(f"   SENDER_PASSWORD = {EMAIL_PASSWORD}")
            return False
        
        if not os.path.exists(file_path):
            st.error(f"❌ PDF file not found at: {file_path}")
            st.info(f"📁 Current directory: {os.getcwd()}")
            st.info(f"📁 Files in {UPDATED_DIR}: {os.listdir(UPDATED_DIR) if os.path.exists(UPDATED_DIR) else 'Directory not found'}")
            return False
        
        st.info(f"✅ PDF file found: {file_path}")
        file_size = os.path.getsize(file_path)
        st.info(f"📊 File size: {file_size} bytes")
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = recipient_email
        msg["Subject"] = subject
        
        body = "Your amended contract is attached below."
        msg.attach(MIMEText(body, "plain"))
        
        # Attach file
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
        
        st.info("🔌 Connecting to Gmail SMTP server...")
        # Send email via Gmail with proper timeout handling
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        server.starttls()
        st.info("✅ SMTP connection secured")
        
        st.info("🔐 Authenticating...")
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        st.info("✅ Authentication successful")
        
        st.info("📤 Sending email...")
        server.send_message(msg)
        st.info("✅ Email submitted to server")
        server.quit()
        st.info("✅ Connection closed cleanly")
        
        st.success(f"✅✅✅ Email sent successfully to {recipient_email}!")
        return True
        
    except socket.timeout:
        st.error("❌ SMTP Connection Timeout: The connection took too long")
        st.warning("💡 Try again in a few seconds, or check your internet connection")
        return False
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"❌ Authentication failed: {str(e)}")
        st.error("   Use Gmail App Password (not your Gmail password)")
        st.error("   1. Go to https://myaccount.google.com/apppasswords")
        st.error("   2. Generate a new app password")
        st.error("   3. Use that in .env as SENDER_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP Error: {str(e)}")
        st.warning("💡 This may be a temporary Gmail issue. Try again in a moment.")
        return False
    except Exception as e:
        st.error(f"❌ Email send failed: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

# ========================= RAG FUNCTION =========================
def run_rag(query: str) -> str:
    if vector_store is None:
        return "Error: Vector store not loaded. Please check FAISS index."
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(query)

    if not docs:
        return "No relevant regulatory information found."

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a regulatory compliance expert.

Context:
{context}

Question:
{query}

Provide a clear, professional answer.
"""

    response = llm.invoke(prompt)
    return response.content

# ========================= SIDEBAR =========================
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Upload Contract",
        "RAG Compliance Analysis",
        "Risk Assessment",
        "Amendment Generator",
        "AI Chatbot"
    ]
)

# ==========================================================
# DASHBOARD
# ==========================================================
if page == "Dashboard":
    st.title("⚖ AI-Powered Regulatory Compliance Checker")

    col1, col2, col3 = st.columns(3)
    col1.metric("Uploaded Contracts", len(os.listdir(UPLOAD_DIR)))
    col2.metric("Regulatory Index", "FAISS")
    col3.metric("AI Model", "Groq LLaMA 3.1")

    st.markdown("""
### System Capabilities
✔ Upload legal contracts  
✔ RAG-based regulation matching  
✔ Compliance risk analysis  
✔ Automated contract amendments  
✔ AI chatbot support  
""")

# ==========================================================
# UPLOAD CONTRACT
# ==========================================================
elif page == "Upload Contract":
    st.title("📄 Upload Contract")

    uploaded_file = st.file_uploader("Upload Contract (TXT)", type=["txt"])

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")
        st.session_state.contract_text = text

        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        st.success("✅ Contract uploaded successfully")
        st.text_area("Contract Preview", text[:2000], height=300)

# ==========================================================
# RAG COMPLIANCE ANALYSIS
# ==========================================================
elif page == "RAG Compliance Analysis":
    st.title("📘 RAG Compliance Analysis")

    if not st.session_state.contract_text:
        st.warning("Upload a contract first")
        st.stop()

    with st.spinner("Analyzing contract against regulations..."):
        result = run_rag(
            "Analyze this contract for compliance issues and missing regulatory clauses"
        )

    st.subheader("Compliance Findings")
    st.info(result)

# ==========================================================
# RISK ASSESSMENT (AI BASED – CORRECT)
# ==========================================================
elif page == "Risk Assessment":
    st.title("⚠ Compliance Risk Assessment")

    if not st.session_state.contract_text:
        st.warning("Upload a contract first")
        st.stop()

    with st.spinner("Assessing risks..."):
        risk = run_rag(
            "Assess legal, financial, and operational risks in this contract"
        )

    st.subheader("Risk Report")
    st.warning(risk)

# ==========================================================
# AMENDMENT GENERATOR
# ==========================================================
elif page == "Amendment Generator":
    st.title("🛠 Contract Amendment Generator")

    if not st.session_state.contract_text:
        st.warning("Upload a contract first")
        st.stop()

    if st.button("Generate Amendments"):
        with st.spinner("Generating compliant clauses..."):
            amendments = run_rag(
                "Generate missing compliance clauses to amend this contract"
            )

        amended_text = (
            st.session_state.contract_text
            + "\n\n--- AMENDMENTS ---\n"
            + amendments
        )

        file_name = f"amended_{int(datetime.now().timestamp())}.txt"
        file_path = os.path.join(UPDATED_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(amended_text)

        # Store in session state for email sending
        st.session_state.amended_text = amended_text
        st.session_state.amended_file_path = file_path

        st.success("✅ Amended contract generated")

    # Show download and email buttons if contract is amended
    if st.session_state.amended_text:
        st.markdown("---")
        st.subheader("📥 Download & Email Options")
        
        # Email input
        email_input = st.text_input(
            "Enter email address to receive PDF",
            value=EMAIL_RECEIVER or "",
            placeholder="your-email@gmail.com"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "⬇️ Download Only",
                st.session_state.amended_text,
                file_name=f"amended_{int(datetime.now().timestamp())}.txt",
                use_container_width=True
            )
        
        with col2:
            if st.button("📧 Email Only", use_container_width=True):
                if email_input and "@" in email_input:
                    with st.spinner("Converting to PDF and sending email..."):
                        # Convert TXT to PDF
                        pdf_file_name = f"amended_{int(datetime.now().timestamp())}.pdf"
                        pdf_file_path = os.path.join(UPDATED_DIR, pdf_file_name)
                        
                        if convert_txt_to_pdf(st.session_state.amended_text, pdf_file_path):
                            # Send email with PDF
                            send_email_with_attachment(email_input, "Amended Contract", pdf_file_path)
                        else:
                            st.error("Failed to convert to PDF")
                else:
                    st.warning("Please enter a valid email address")
        
        with col3:
            if st.button("⬇️📧 Download & Email", use_container_width=True):
                if email_input and "@" in email_input:
                    with st.spinner("Preparing PDF and sending email..."):
                        # Convert TXT to PDF
                        pdf_file_name = f"amended_{int(datetime.now().timestamp())}.pdf"
                        pdf_file_path = os.path.join(UPDATED_DIR, pdf_file_name)
                        
                        if convert_txt_to_pdf(st.session_state.amended_text, pdf_file_path):
                            # Send email with PDF
                            if send_email_with_attachment(email_input, "Amended Contract", pdf_file_path):
                                st.balloons()
                                st.success("✅ PDF downloaded and email sent!")
                        else:
                            st.error("Failed to convert to PDF")
                else:
                    st.warning("Please enter a valid email address")

# ==========================================================
# AI CHATBOT
# ==========================================================
elif page == "AI Chatbot":
    st.title("🤖 AI Compliance Chatbot")

    question = st.text_input("Ask a compliance-related question")

    if st.button("Ask"):
        if question.strip() == "":
            st.warning("Enter a question")
        else:
            with st.spinner("Thinking..."):
                answer = run_rag(question)

            st.success("AI Response")
            st.write(answer)
