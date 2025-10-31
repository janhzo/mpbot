# 🤖 MPBot01 – Multi-Agent System (Demo)

## 🇬🇧 English Version

### Overview
**MPBot01** is a modular multi-agent demo system designed for intelligent data extraction, classification, and analysis using a coordinated architecture.  
It demonstrates how multiple autonomous agents can collaborate to process, analyze, and summarize structured data (such as procurement records).

---

## 📁 Project Structure

mpbot01/
│
├── agents/ ← All uAgents (independent intelligent agents)
│ ├── agente_consultor.py ← Handles consultation, queries, and coordination
│ ├── agente_analista.py ← Performs data analysis and report generation
│ └── agente_supervisor.py ← Oversees agents and workflow consistency
│
├── modules/ ← Reusable logic and helper modules
│ ├── init.py ← Enables module imports
│ ├── excel_reader.py ← Handles Excel data extraction
│ ├── llm_classifier.py ← AI-based text classification using LLMs
│ ├── analytics.py ← Statistical and data processing utilities
│ └── utils.py ← Logging, file management, and shared helpers
│
├── data/ ← Input and output data
│ ├── compras_agiles.xlsx ← Sample dataset for testing
│ └── reports/ ← Auto-generated analysis reports (.txt)
│
├── config.py ← Global configuration and constants
├── requirements.txt ← Python dependencies
├── README.md ← This documentation file

