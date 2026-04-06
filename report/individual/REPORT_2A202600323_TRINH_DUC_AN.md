# Individual Report: Lab 3 - Chatbot vs ReAct Agent

**Student Name:** Trịnh Đức An  
**Student ID:** 2A202600323  
**Date:** 06-04-2026  
**Role:** Agent v1 & v2 — LangGraph + Prompt Engineering 

---

## I. Technical Contribution

**Modules Implemented:** `src/agent_v1.py` & `src/agent_v2.py`.

**Evidence of Code Quality & Architecture Design:**
- **StateGraph Implementation:** Built a robust conversational flow using LangGraph's `StateGraph(MessagesState)`. Both agents share the identical graph structure (`__start__ → llm → [tools | __end__]`) to ensure a proper scientific ablation study. This proves that performance differences stem directly from Prompt Engineering (the system prompt), not architectural disparities.
- **Dynamic Prompt Injection & Guardrails:** In `agent_v2.py`, I designed the `_system_v2()` function to dynamically inject the current month's promotions using `datetime.now().month` and the `PROMOTIONS` dictionary. Implemented strict operational boundaries (Guardrails) in `v2` to reject interactions outside the VinFast ecosystem (e.g., Toyota inquiries) and to enforce exact loan terms.
- **Code Clarity:** Maintained clean, modular Python codebase by separating tool logic (`src/tools.py`) from graph/routing logic, leveraging `make_logged_tool_node` for seamless telemetry integration, and employing functional separation for readability.

---

## II. Debugging Case Study

**Failure Mode Analyzed:** Boundary Hallucination and Invalid Tool Usage (Test Case T04 & T05).

**Observation via Telemetry/Logs (`logs/vinfast_20260406_090834.log`):**
During the evaluation of Agent v1 on Test Case T04 ("Toyota Camry bản hybrid giá bao nhiêu?"), the telemetry log `LLM ra | gọi công cụ: ['check_price']` revealed a critical flaw. Because `SYSTEM_V1` only instructed the agent to "use available tools", the LLM blindly hallucinated and attempted to call `check_price(model="Toyota Camry")`. This resulted in returning an internal tool error string, confusing the AI further.
Similarly, in T05, when asked to calculate a loan term of "50 tháng" (an invalid duration), Agent v1 silently self-corrected the user's input to "48 months" to force the tool to work, severely violating business policy.

**Resolution:**
I resolved this by heavily engineering the system prompt in `agent_v2.py`. I introduced explicit **Negative Constraints**: 
*"Nếu người dùng hỏi chủ đề không thuộc VinFast... Không gọi công cụ. Trả lời ngắn... nhắc họ đặt câu hỏi về giá... các dòng VF3, VF8 Plus..."* 
and strict parameter enforcement rules: 
*"Nếu khách yêu cầu số tháng KHÁC (vd 50)... Vẫn phải gọi tính toán với đúng months khách nói... để công cụ trả lỗi"*.
Post-resolution logs confirm that v2 successfully intercepts the Toyota query without invoking the tool at all, and correctly passes "50" to the finance tool to trigger and display a policy-compliant rejection message.

---

## III. Personal Insights

**Deep Reflection: LLM Chatbots vs ReAct Agents based on Lab Results**
Before this lab, I mistakenly assumed that simply providing an LLM with external tools (creating a ReAct Agent) was sufficient to create a bulletproof system. Observing `agent_v1` fail taught me a crucial pivot: **Tools without context and guardrails are dangerous.**

A standard LLM Chatbot relies purely on its pre-trained parametric memory, inevitably breaking down and hallucinating precise prices or promotion parameters it hasn't memorized. A ReAct Agent solves this by utilizing the "Reason → Act → Observe" loop to fetch ground-truth API data. However, the "Reason" step is entirely governed by the System Prompt. 

In our experiment, `agent_v1` proved that just giving the agent the `calculate_monthly_payment` tool doesn't impart the business logic of *when* to subtract the promotion discount before performing the calculation. The true capability of a ReAct Agent only materializes when the LLM is provided with a rigorous "Standard Operating Procedure" (the meticulously structured `_system_v2`). The ReAct architecture does not eliminate the need for Prompt Engineering; rather, it demands significantly more precise Prompt Architecting to choreograph the interaction between the LLM and its external tools.

---

## IV. Future Improvements

**Scaling to a Production-Level RAG and Multi-Agent System:**
1. **Robust RAG Integration (Data Layer):** Transition from hardcoded `CATALOG` mock dictionaries to a Vector Database (e.g., Qdrant or Pinecone). By equipping the agent with a proper `retriever_tool`, it could fetch real-time specifications, pricing, and massive user manuals, allowing it to scale dynamically to thousands of automotive models and technical documents.
2. **Multi-Agent Supervisor Architecture:** As user queries grow in complexity (e.g., navigating a deeply technical car breakdown vs. pursuing a standard sales inquiry), a single monolithic prompt becomes bloated and unstable. We should implement a **Supervisor Node (Multi-Agent framework)** that classifies the intent and routes the query to specialized sub-agents: a `FinancialSalesAgent` (managing quotes) and a `TechnicalSupportAgent` (handling manual RAG).
3. **Stateful Persistence:** Integrate a storage checkpoint mechanism (`MemorySaver` or `AsyncPostgresSaver`) directly into the LangGraph to persist conversation states (thread memory) reliably across prolonged customer sessions, moving beyond the transient local array structure.
