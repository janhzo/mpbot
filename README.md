# 🧠 MPBOT: Universal Tender Intelligence Engine

AI-powered multi-agent system for **tender analysis, ranking and prioritization** across any industry.  
**Medical supplies** are used as the proof-of-concept demo.

Anothe one proof-of-concept is insert a digital office ia operator's work together looking for niches and opportunities.

> 💡 Built with [uAgents](https://github.com/fetchai/uAgents) for autonomous collaboration and real-time decision-making.

---

## 🚀 Live Demo — **ASI:One**

**Try it yourself (human-in-the-loop mode):**

1. Open ASI:One Instance Chat Agent
2. Type: `start` or `iniciar`
3. Receive **TOP 5 prioritized tenders**  
4. Reply with a number (e.g., `1`) → *“Marked as reviewed”*

### 🧬 Current demo:
**Medical Supplies (Insumos Médicos)**  
However, MPBOT is fully modular and works for **construction, IT, logistics, education**, etc.

---

## 🧩 Registered Agents on Agentverse

| Agent Name | Role | Address | Port | Inspector |
|-------------|------|----------|-------|------------|
| 🧭 **TenderReader** | Reads tenders from Excel + LLM classification | `agent1qg3cktzapjdru3q6g924ytsghr3ehd4vqyk5ya828c2m93kdexpeyjxy5t4` | 8000 | [Inspector](https://agentverse.ai/inspect/?address=agent1qg3cktzapjdru3q6g924ytsghr3ehd4vqyk5ya828c2m93kdexpeyjxy5t4) |
| 📊 **TenderRanker** | Analyzes & ranks tenders | `agent1q09jyj082tfyta9075vx9pdj0f6xj3zzjpk6529a564ffgu2zwd8203u7xj` | 8001 | [Inspector](https://agentverse.ai/inspect/?address=agent1q09jyj082tfyta9075vx9pdj0f6xj3zzjpk6529a564ffgu2zwd8203u7xj) |
| 🧠 **TenderSupervisor** | Validates, logs & reports results | `agent1q2gmu2xd3yalrue7mwd0wkq35xqw48p70djp5274vxyqvnf7cn735wdyuc5` | 8002 | [Inspector](https://agentverse.ai/inspect/?address=agent1q2gmu2xd3yalrue7mwd0wkq35xqw48p70djp5274vxyqvnf7cn735wdyuc5) |

---

## ⚙️ Core Features

| Feature | Status |
|----------|--------|
| 📄 Excel → LLM classification | ✅ Done |
| 🤝 Real-time agent collaboration | ✅ Done |
| 🧍 Human-in-the-loop (ASI:One) | ✅ Done |
| 📑 Report generation & export | ✅ Done |
| 🏗️ Multi-industry support | ✅ Plug & Play |

---

## 🧪 Proof of Concept — Medical Industry

We selected **medical supplies** as a high-impact real-world demo.

**What it does:**
- Analyzes `data/compras_agiles.xlsx` (Chilean public tenders) or API data.
- Filters only *eligible medical items*
- Ranks tenders by:
  - 📈 Profit margin  
  - 📦 Volume  
  - ⚡ Urgency  
  - 🧩 Competition
- Delivers an actionable **TOP 5** for decision-makers in seconds.

> 🧠 The same logic can be adapted to any sector.

---

## 🧱 Works for Any Industry

| Industry |
|-----------|
| 🏗️ Construction | 
| 💻 IT & Software | 
| 🚚 Logistics | 
| 📚 Education |

Just update:
- Excel file in `/data/`
- LLM prompt in `modules/llm_classifier.py`
- Scoring weights in `modules/analytics.py`

or add API data.
---

## 🧰 Requirements

| Resource | Details |
|-----------|----------|
| Excel File | `data/compras_agiles.xlsx` (included) | (modded add API yourself)
| OpenAI API Key | Required for LLM |
| Python | 3.10+ |

### 🔐 Create `.env` File (MANDATORY)
Create a file in the project root named `.env`:

```bash
OPENAI_API_KEY=sk-your-real-openai-key-here
OPENAI_MODEL=gpt-4o-mini

graph TD
    U[User @ ASI:One] -->|start| A[TenderReader Agent]
    A -->|Excel + LLM Classification| B[TenderRanker Agent]
    B -->|Scores & prioritizes| C[TenderSupervisor Agent]
    C -->|Report + validation| U


📜 License & Credits

Author: @janhzo /Project Zero

@Project0zcl

Framework: Fetch.ai uAgents

License: MIT

Version: 0.2 
