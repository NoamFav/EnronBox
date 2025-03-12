---
theme: ~/tokyo_night.json
author: Noam Favier
date: MMMM dd, YYYY
paging: Slide %d / %d
---

# **Project Proposal: Voice-Driven AI Coding Assistant**

# **Group 3**

# **Umbrella Topic: NLP**

---

# **Table of Contents**

- [**Project Proposal: Voice-Driven AI Coding Assistant**](#project-proposal-voice-driven-ai-coding-assistant)
  - [**1. Project Overview**](#1-project-overview)
    - [**Introduction**](#introduction)
    - [**Key Objectives**](#key-objectives)
  - [**2. Key Features & Capabilities**](#2-key-features-capabilities)
    - [**1️⃣ Voice-Controlled AI Pair Programming**](#1️⃣-voice-controlled-ai-pair-programming)
    - [**2️⃣ AI That Learns & Adapts**](#2️⃣-ai-that-learns-adapts)
    - [**3️⃣ Memory & Context Awareness**](#3️⃣-memory-context-awareness)
    - [**4️⃣ AI-Powered Debugging & Code Review**](#4️⃣-ai-powered-debugging-code-review)
    - [**5️⃣ IDE & Editor Control**](#5️⃣-ide-editor-control)
  - [**3. Expanded Tech Stack & Architecture**](#3-expanded-tech-stack-architecture)
  - [**5. Future Considerations & Scalability**](#5-future-considerations-scalability)
  - [**6. Next Steps – Where to Start**](#6-next-steps-where-to-start)

## **1. Project Overview**

### **Introduction**

The **Voice-Driven AI Coding Assistant** is a highly advanced, **fully offline, real-time AI companion** designed to enhance software development workflows by integrating **speech-to-text (STT), natural language understanding (NLU), local LLM reasoning, and memory-based adaptation** into a developer’s workflow.

Unlike existing AI tools such as **GitHub Copilot, OpenAI GPT models, or even the advanced Claude**, this assistant is not simply a **code generator**. Instead, it acts as a **true AI pair programmer**, capable of understanding the intention of the developer, tracking project context, and actively assisting in real-time via **voice control and inline interaction**.

---

### **Key Objectives**

- **Real-Time Voice Interaction**: Allows developers to control their coding environment through hands-free, natural voice control.
- **Context-Aware Code Assistance**: Track project structure, active files, function calls, and dependencies to provide highly relevant suggestions.
- **Adaptive Learning**: Improve over time by learning from the user’s coding habits, refactoring tendencies, and preferred patterns.
- **Fully Offline and Free**: Avoid reliance on cloud-based APIs to maintain privacy and eliminate cost constraints. **Note that this may enforce hardware limitations on the user's side.**
- **Seamless IDE Integration**: Work directly within **Neovim, VS Code, IntelliJ**, and other commonly used development environments.
- **Interactive Debugging and Refactoring**: Proactively assist in debugging, code reviews, and error correction.
- **Personalized Code Recommendations**: Based on previous user interactions, dynamically refine suggestions and interventions.

---

## **2. Key Features & Capabilities**

### **1️⃣ Voice-Controlled AI Pair Programming**

- Iris (name of the AI) **tracks project activity silently** and **listens for activation commands** (e.g., “Iris, how do I fix this bug?”).
- Instead of generating large code chunks, it **guides** the user through changes step by step.
- Iris can differentiate between general queries (e.g., _“How do I optimize this function?”_), and direct coding actions (e.g., _“Rename variable `playerSpeed` to `velocity`”_).
- Example Interaction:

  - Developer: _"Iris, my ledge climbing logic isn’t working. It lets me jump instead of climbing."_
  - Iris: _"It looks like your ground collision check is allowing jumps too close to ledges. Want me to highlight where this happens?"_
  - Developer: _"Yeah, show me."_
  - Iris: _(Highlights relevant function.)_ _"Here is the logic controlling ground detection. You might want to check if the ledge’s position is being considered."_
  - Developer: _"I see. How do I fix it?"_
  - Iris: _"You can add a check for the ledge’s position in the collision function. Want me to guide you through it?"_
  - Developer: _"Yes, please."_
  - Iris: _(Suggests adding a conditional check for the ledge’s position in the collision function.)_ _"This should prevent the jump action when near a ledge."_
  - Developer: _"Okay, let me try that."_

- Another Example:

  - Developer: _"Iris, I need to refactor this function to handle multiple edge cases."_
  - Iris: _"I suggest breaking it down into smaller functions. Want me to guide you through the process?"_
  - Developer: _"Yes, please."_
  - Iris: _(Suggests breaking down the function into smaller, more manageable parts.)_

- After some time, Iris will not need to ask for confirmation and will directly implement the changes based on the developer's preferences. The developer can always revert the changes if they don't like them by telling Iris to do so. You can, of course, force Iris to ask for confirmation if you want to.
- Additionally, Iris may even take over parts of the codebase that the developer is not interested in working on, such as writing boilerplate code or fixing simple bugs. And can even work on its own when asked to do so. Like implementing a feature or fixing a bug.

- Example:

  - Developer: _"Iris, can you implement the player movement logic?"_
  - Iris: _"Sure, I will implement the player movement logic. Do you want me to follow a specific pattern?"_
  - Developer: _"Yes, I prefer the state pattern."_
  - Iris: _(Implements the player movement logic using the state pattern.)_

---

### **2️⃣ AI That Learns & Adapts**

- Tracks user coding habits and **suggests improvements based on prior edits**.
- Recognizes frequently used functions, coding patterns, and naming conventions.
- Adjusts its behavior based on **user confirmations and rejections**. Making the confirmation non-mandatory after some time.
- Example:
  - If the user **prefers a certain loop structure**, AI adapts to match that style automatically.
  - If the developer **often writes logs before exceptions**, AI suggests doing so proactively.
  - Iris remembers **project-specific logic** and **avoids redundant suggestions**.

---

### **3️⃣ Memory & Context Awareness**

- **Stores project context** (recent functions, active files, past discussions) in an **SQLite/Redis database**.
- Unlike traditional AI assistants, it **remembers past queries and feedback**, reducing redundant suggestions.
- Uses **semantic search embeddings (FAISS/ChromaDB)** to recall past discussions on similar issues.
- Example:
  - Developer: _"What was that function I used for vector normalization?"_
  - Iris: _"You used `normalizeVector()` in `movement.cs` yesterday. Want me to open it?"_
  - Developer: _"No, just remind me how it works."_
  - Iris: _(Provides a summary of function usage.)_

---

### **4️⃣ AI-Powered Debugging & Code Review**

- Iris proactively detects **common logic errors**, missing conditions, and performance inefficiencies.
- Can **interrupt the user** if a serious issue is detected.
- Example:
  - Iris: _"You’re modifying a list while iterating through it. That could cause a runtime error. Want me to suggest a safer approach?"_
  - Developer: _"Yeah, what do you suggest?"_
  - Iris: _(Proposes using a separate list to store modifications before applying them.)_

---

### **5️⃣ IDE & Editor Control**

- Iris can **open files, highlight code, refactor functions, and navigate projects**.
- Seamless integration with **Neovim (Lua API) & VS Code (Extension API)**.
- Example:

  - Developer: _"Iris, open `player_movement.cs` and jump to the function handling wall jumps."_
  - Iris: _(Opens file, highlights relevant function.)_ _"Here’s the function `handleWallJump()`."_

- Another Example:
  - Developer: _"Iris, rename the `playerSpeed` variable to `velocity` across the project."_
  - Iris: _(Searches for all instances of `playerSpeed` and renames them to `velocity`.)_

---

## **3. Expanded Tech Stack & Architecture**

| **Component**                            | **Technology / Tools**                                    | **Reason**                                                  |
| ---------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------- |
| **Speech-to-Text (STT)**                 | **Vosk (Offline STT), DeepSpeech, Whisper (Self-Hosted)** | Free, local speech recognition                              |
| **Natural Language Understanding (NLU)** | **Custom NLP Model (spaCy, Rasa NLU, Transformers)**      | Detects coding commands, questions, and interactions        |
| **Local LLM (AI Brain)**                 | **Mistral-7B, Llama-2 (Self-Hosted on GGUF/TensorRT)**    | Generates intelligent responses, understands code reasoning |
| **Memory & Context Tracking**            | **SQLite/Redis, FAISS (for embeddings)**                  | Stores past interactions, learns coding habits              |
| **Codebase Understanding**               | **LSP (OmniSharp, Rust Analyzer, Pyright, Clangd, etc.)** | Hooks into active code for deep understanding               |
| **Editor Integration**                   | **Neovim (via Lua API) / VS Code (via Extension API)**    | Directly controls code navigation & editing                 |
| **Text-to-Speech (TTS)**                 | **Coqui TTS, Piper, ElevenLabs**                          | AI responds with natural voice feedback                     |
| **OS-Level Integration**                 | **Rust, Python, Zig or C++**                              | Manages system-wide keybinds, file handling, and API calls  |

---

## **5. Future Considerations & Scalability**

- **Online Coding Mode**: Enable AI-assisted **live collaboration** with other developers.
- **Automated Project Summarization**: AI generates **documentation & project reports** dynamically.
- **Offline LLM Training**: Fine-tune Llama-3/Mistral on **personal datasets** to further optimize responses.
- **Interactive UI Overlay**: Small **visual assistant overlay** for **better interaction within IDEs**.
- **Automated Feature implementation**: Iris can **implement features** on its own when asked to do so.
- **Fully automatic coding**: Iris can take over projects like AI training or testing, where she oversees the project and makes changes as needed.

---

## **6. Planning & Timeline**

- **Week 1-5**: Set up STT pipeline, basic NLU understanding, and local LLM reasoning.
- **Week 6-7**: Implement memory system, context tracking, and SQLite/Redis integration.
- **Week 8-12**: Develop AI-powered debugging, code review, and editor control features.
- **Week 13-15**: Integrate with Neovim, VS Code, and other IDEs for seamless interaction.
- **Week 16-18**: Finalize voice-controlled pair programming, adaptive learning, and memory recall.

---

## **7. Next Steps – Where to Start**

1️⃣ **Speech-to-Text (STT) pipeline:** Get voice input working locally with Vosk or DeepSpeech.  
2️⃣ **Basic AI understanding & Neovim integration:** Hook into the LSP for code awareness.  
3️⃣ **Memory system & AI adaptation:** Implement long-term learning via SQLite/Redis.

🚀 This project has massive potential, making it one of the **first true AI-driven voice coding assistants** that is fully offline and learns over time!

---

## Note

As the project is originally focused on the NLP part, we will be focusing on building the NLP and STT part of the project. The other parts of the project will be implemented but not from scratch. We will be using pre-trained models and tools to implement them. Making the project more focused on the NLP part. While still having the other parts of the project implemented.
The end goal of Iris is to go beyond the scope of the project in the end and create a tool that can be used by developers to help them in their daily tasks.
The language used will be determined based on the team’s competencies and the tools used.

# Thank you for reading! 🚀
