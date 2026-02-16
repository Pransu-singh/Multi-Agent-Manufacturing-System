# 🏭 Multi-Agent Manufacturing System (AAI-32)

AI-powered collaborative manufacturing assistant built using **Multi-Agent Architecture**.  
This project demonstrates how specialized AI agents cooperate to perform supplier sourcing, analysis, and structured report generation.

---

## 📌 Project Information

- **Division:** D7  
- **Group:** Group 09D7  
- **Project No:** AAI-32  
- **Problem Statement:** Multi-Agent Manufacturing System  

---

## 🚀 Overview

The **Multi-Agent Manufacturing System** is a web-based AI platform where multiple intelligent agents collaborate to solve manufacturing-related tasks such as:

✔ Supplier sourcing  
✔ Cost comparison  
✔ Data analysis  
✔ Report generation  

Instead of using a single AI model, this system uses **specialized agents** with clearly defined roles, enabling modular, scalable, and realistic AI workflows.

---

## 🧠 System Architecture

The system consists of the following agents:

| Agent | Role |
|------|------|
| **Coordinator Agent** | Manages workflow & task routing |
| **Researcher Agent** | Collects manufacturing/supplier data |
| **Analyst Agent** *(optional)* | Evaluates and compares options |
| **Writer Agent** | Generates structured reports |

---

## 🔄 Workflow

- User Query  
- ↓  
- Coordinator Agent  
- ↓  
- Researcher Agent → Data Collection  
- ↓  
- Analyst Agent → Evaluation / Comparison  
- ↓  
- Writer Agent → Structured Output  
- ↓  
- User Dashboard  



---

## ✨ Features

### 👤 User Features

- Ask manufacturing-related questions  
- Supplier sourcing  
- Cost comparison  
- AI-generated reports  
- Query history  
- Download reports (PDF / CSV)  

---

### 🛠 Admin Features

- User management  
- Query monitoring  
- Report management  
- Agent performance tracking  
- System configuration  

---

## 🖥 Web Interface

The platform includes:

- ✅ Landing Page  
- ✅ Login / Signup  
- ✅ User Dashboard  
- ✅ Query History  
- ✅ Reports Page  
- ✅ Admin Dashboard  

---

## 🧰 Tech Stack

### 🔹 Backend

- Python  
- FastAPI / Flask  
- LangChain / CrewAI  

---

### 🔹 Frontend

- HTML / CSS / JavaScript  
*(or React for modern UI)*  

---

### 🔹 AI / LLM

- OpenAI API / Groq / Gemini (Free Tier)

---

### 🔹 Database

- SQLite / PostgreSQL  

---

### 🔹 Deployment

- Render / Railway / Replit (Free Tier)

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/multi-agent-manufacturing.git
cd multi-agent-manufacturing

python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate

# Linux / Mac:
source venv/bin/activate

pip install -r requirements.txt
# Clone repository
git clone https://github.com/Pransu-singh/Multi-Agent-Manufacturing-System.git

# Navigate into project
cd multi-agent-manufacturing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # (Linux/Mac)
venv\Scripts\activate     # (Windows)

# Install dependencies
pip install -r requirements.txt

📁 Project Structure
multi-agent-manufacturing/
│
├── backend/
│   ├── agents/
│   ├── tools/
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   └── styles.css
│
├── database/
├── requirements.txt
└── README.md

