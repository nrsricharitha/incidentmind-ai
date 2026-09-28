# Demo Guide — 60–90 Second Hackathon Presentation

## Overview
This guide provides the exact script, timing, and actions for demonstrating **IncidentMind AI** to hackathon judges or attendees.

---

## Elevator Pitch (15 Seconds)
> *"Modern AI incident response assistants usually answer one question: **'What is broken right now?'** But every time a new incident occurs, they start from zero with no memory of what worked last week or last month.*
>
> *IncidentMind AI changes that by integrating **Hindsight Long-Term Memory** into the **Microsoft Agent Framework** and **Groq LLM**. It investigates incidents, resolves them, retains that operational experience into a persistent memory bank, and immediately recalls it when similar incidents strike in the future."*

---

## Step-by-Step Demo Walkthrough

### Phase 1: Day 1 Incident (30 Seconds)
1. Open the application at `http://localhost:8501`.
2. Select **`🎬 Demo Mode`** in the left sidebar.
3. Click the primary button: **`▶️ 1. Start Day 1 (INC-1001)`**.
4. **Point out to judges:**
   - Raw logs show `payment-api` failing with `connection pool exhausted` and `database connection acquisition timeout`.
   - The agent executes deterministic log analysis and simulated health inspection.
   - It searches operational runbooks and matches `DB-POOL-004` (*Database Connection Pool Exhaustion*).
   - Notice the status: **Hindsight memory is queried, but because this is Day 1, no prior memory exists yet**.
   - The agent assesses the root cause and generates safe remediation actions.
5. Click **`✅ Click to 'Resolve & Remember' Day 1 into Hindsight`**.
   - Show the success banner: The resolution is now permanently retained in Hindsight memory bank `incidentmind-demo`.

---

### Phase 2: Proving Memory Persistence Across Sessions (15 Seconds)
6. Click **`🔄 2. Start New Agent Session`**.
7. **Explain to judges:**
   - *"We just wiped the agent's short-term conversational context. There is no conversation history in memory. In a normal chatbot, that experience would be permanently lost."*

---

### Phase 3: Day 30 Incident & Memory Recall (30 Seconds)
8. Click **`⏩ 3. Simulate 30 Days Later (INC-1042)`**.
9. **Highlight the Memory Transformation:**
   - A new incident has struck 30 days later with similar symptoms (`database connection timeout`, latency spike).
   - **Look at the Hindsight Memory Panel:**
     - The agent retrieved memory from `INC-1001`!
     - It displays the recalled failure mode, previous resolution, and runbook applied.
   - **Look at the Recommendation:**
     - The agent notes: `[HINDSIGHT EXPERIENCE APPLIED] High similarity with past incident INC-1001.`
     - It cross-references current evidence with past experience rather than starting from scratch!

---

### Phase 4: Additional Exploration (Optional)
- **Hindsight Memory Sandbox**: Navigate to `🧠 Hindsight Memory` to run arbitrary natural language queries against the bank.
- **Runbook Explorer**: Show the structured SOP catalog in `📖 Runbooks`.
- **System Information**: Demonstrate live truthful connectivity to Groq and Hindsight under `⚙️ System Information`.
