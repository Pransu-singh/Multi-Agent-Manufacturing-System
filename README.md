# 🏭 Multi-Agent Manufacturing System

A collaborative AI architecture featuring specialization and automated hand-off protocols. This system utilizes a **Researcher Agent** for supplier sourcing and a **Writer Agent** for technical synthesis, demonstrating advanced inter-agent communication.



## 🎯 Project Overview
This project implements a "Producer-Consumer" pattern in AI. By decoupling data discovery from data formatting, the system achieves higher accuracy and better formatting than a single-agent prompt.

- **Researcher Agent:** Scours the web (via DuckDuckGo) to find verified manufacturing suppliers.
- **Writer Agent:** Consumes the researcher's raw findings and formats them into a professional Markdown Procurement Report.
- **Hand-off Protocol:** Uses a sequential state-management flow where Task B's context is explicitly derived from Task A's output.

## 🛠️ Tech Stack (100% Free)
- **Framework:** [CrewAI](https://github.com/joaomdmoura/crewai)
- **LLM:** [Llama 3 (via Groq)](https://groq.com/) - High-speed, free-tier inference.
- **Search Tool:** [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) - No API key required.
- **Language:** Python 3.10+

## ⚙️ Architecture & Logic
The system follows a strict linear workflow to ensure data integrity:

1. **Input:** User provides a manufacturing component (e.g., "Aerospace Grade Titanium").
2. **Search & Source:** Researcher Agent performs real-time web scraping to identify 3 suppliers.
3. **State Handoff:** The raw data is passed to the Writer Agent.
4. **Synthesis:** Writer Agent applies a professional template and performs a risk assessment.
5. **Output:** A structured `procurement_report.md` file is generated.

## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repository
git clone [https://github.com/yourusername/multi-agent-manufacturing.git](https://github.com/yourusername/multi-agent-manufacturing.git)
cd multi_agent_manufacturing

# Install dependencies
pip install crewai langchain-groq langchain-community duckduckgo-search
