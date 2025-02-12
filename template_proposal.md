---
theme: ~/tokyo_night.json
author: Noam Favier
date: MMMM dd, YYYY
paging: Slide %d / %d
---

# Group Number: 3

# Group Members:

- Noam Favier
- David Brune
- Remi Heijmans
- Jiang Geer
- Giorgos de Jonge
- Esteban Naranjo Amortegui
- Octavian Rujan

# Anticipated role distribution: Not defined yet

# Natural Language Processing (NLP)

# Iris: An NLP-Driven AI Coding Assistant with Context-Aware Reasoning

---

## 1 Motivation and problem statement

The way developers write code has changed recently because to AI-driven coding tools like OpenAI Codex and GitHub Copilot. However, there is minimal interaction or adaptive learning based on a developer's workflow; instead, these tools mostly provide static code suggestions. Additionally, they are unable to have conversations in plain language, which makes complicated coding tasks like context recall, multistep refactoring, and debugging less intuitive.

Iris, our suggested AI coding assistant, overcomes these drawbacks by integrating contextual memory, local large-scale language models (LLMs), and natural language processing (NLP) to produce a completely offline, conversation-based coding assistant. Iris can function as a true AI programmer by responding to natural language queries, remembering previous interactions, and assisting with real-time feature implementation and debugging thanks to the NLP core's conversational interaction, intent recognition, and contextual suggestions.

The focus of our project will be on developing an NLP pipeline for speech-to-text conversion, intent classification, and multi-turn dialogue management. By adopting local LLMs for reasoning and memory-based context tracking, we will ensure that Iris remains adaptable and highly personalized to each developer’s workflow. Additionally, the project will emphasize privacy and offline capabilities, making it an innovative alternative to existing cloud-based solutions. Moreover, Iris would be given a voice, allowing developers to interact with it hands-free, further enhancing productivity and accessibility.

This work is highly relevant in an era where software complexity continues to grow, and hands-free, voice-driven coding environments can significantly boost productivity while reducing cognitive load.

---

## 2 Research questions

1. How can NLP techniques be applied to intent classification and dialogue management for a coding assistant?
2. What methods can be used to ensure accurate contextual understanding and recall in multi-turn interactions within a coding environment?
3. How can speech recognition and NLP-based dialogue systems be optimized for real-time, hands-free developer interactions?

---

## 3 Chosen approaches

The core of our project lies in combining NLP for conversation and dialogue management with LLMs for code reasoning and context-aware suggestions. We will build the following key components:

---

### Speech-to-Text (STT)

For offline speech recognition, Vosk or DeepSpeech will be utilized. These technologies will be tailored to identify terminology unique to coding and will be integrated with our NLP pipeline for additional processing. Developer commands will be transformed into actionable text by the STT module so that the NLU engine may examine it.

---

### Natural Language Understanding (NLU)

Our NLU engine will classify developer queries and extract relevant intents using frameworks like spaCy and transformer-based models. The main tasks of the NLU system are:

1. Intent Detection: Classifies commands (e.g., code navigation, debugging, feature implementation).
   - Example: “Iris, highlight all occurrences of playerSpeed in this file.” → Intent: Code Search
2. Entity Recognition and Context Extraction: Identifies specific parts of the code or coding concepts mentioned in the query.
   - Example: “What’s the function for normalizing a vector?” → Entity: normalizeVector()
3. Dialogue Management: Handles multi-turn interactions and provides suggestions or clarifications when commands are ambiguous. This module will manage the flow of conversation to ensure accurate, contextually aware responses.

---

### Local Large Language Model (LLM)

For reasoning and code understanding, we will integrate a self-hosted LLM (e.g., Mistral-7B or Llama-3) to generate intelligent responses. While the NLP pipeline handles conversation flow and command classification, the LLM will reason about the codebase context and provide relevant suggestions or generate code snippets.

---

### Memory and Context Tracking

To ensure Iris remains contextually aware, we will implement a memory system using SQLite/Redis for short-term memory and FAISS for semantic search and long-term recall. This allows Iris to store and retrieve information about recent interactions, active files, and project-specific logic.

---

### Editor and IDE Integration

Iris will integrate with Neovim ,VS Code and IntelliJ, allowing it to perform tasks such as opening files, navigating to functions, refactoring code, and suggesting improvements. This integration will be managed through Lua (Neovim), TypeScript (VS Code extensions), and Java (IntelliJ plugins).

---

### Text-to-Speech (TTS)

For audio feedback and responses, we will use TTS engines like Mozilla TTS or Google TTS. This will enable Iris to provide spoken feedback, code suggestions, and debugging tips to the developer.

---

### Validation and Evaluation

We will validate the system with experiments that measure:

- STT accuracy (transcription accuracy for coding commands)
- Intent classification accuracy (precision, recall, F1 score)
- Dialogue coherence and context recall (multi-turn dialogue success rate)

---

## 4 Experiments

We plan to conduct the following experiments to answer our research questions:

1. Speech-to-Text Accuracy
   - Measure transcription accuracy for coding-specific vocabulary and multi-word commands.
   - Evaluate performance in noisy environments (e.g., background typing noise).
2. Intent Classification and Context Extraction
   - Test the accuracy of intent detection across a set of predefined commands.
   - Evaluate how well the system extracts entities (e.g., variable names, function calls) and recalls project context.
3. Dialogue Coherence and Multi-Turn Interaction
   - Simulate multi-turn dialogues and measure the system’s ability to handle context changes and clarifications.
   - Track success rates for context recall and adaptive responses.

---

## 5 Related work

Several existing tools, such as OpenAI Codex, GitHub Copilot, Claude, and TabNine, provide AI-driven code suggestions, but their primary focus is on code generation rather than natural language interaction.

Recent advancements in NLP for conversational AI (e.g., BERT, Dialogue Transformers) have demonstrated significant improvements in intent recognition and dialogue management. Research on semantic search for codebases (e.g., CodeBERT) offers a promising direction for building context-aware assistants.

Our approach differentiates itself by combining voice-driven interaction, multi-turn NLP dialogue, and offline LLM-based reasoning, creating a fully adaptive coding assistant that is privacy-focused and highly interactive.

---

## 6 Relation of proposal to courses in your curriculum

This project relates to Theoretical computer science, Machine Learning, and Human-Computer Interaction, applying advanced concepts from all three to build a novel developer tool. The focus on NLP and dialogue systems makes it directly relevant to current coursework and research in conversational AI.

---

## 7 Planning : To be defined

---

## 8 Minimal passing requirements

The minimal passing requirement is a working STT and NLP pipeline that handles intent detection, multi-turn dialogue, and context tracking. Integration with at least one IDE and successful validation of NLP experiments is essential. Advanced reasoning and debugging features are secondary but desirable.

---

## 9 References

1. **Vosk Speech Recognition** – Open-source offline STT toolkit

   - Alpha Cephei. "Vosk Speech Recognition Toolkit." Available at: [https://alphacephei.com/vosk/](https://alphacephei.com/vosk/)

2. **Mozilla DeepSpeech** – End-to-End Deep Learning for Speech Recognition

   - Hannun, A., et al. "Deep Speech: Scaling up end-to-end speech recognition." _arXiv preprint arXiv:1412.5567_, 2014.
   - GitHub: [https://github.com/mozilla/DeepSpeech](https://github.com/mozilla/DeepSpeech)

3. **spaCy** – Industrial-Strength NLP in Python

   - Honnibal, M., & Montani, I. “spaCy: Industrial-strength Natural Language Processing in Python.” Available at: https://spacy.io

4. **Rasa NLU** – Conversational AI framework

   - Bocklisch, T., et al. "Rasa: Open source language understanding and dialogue management." _arXiv preprint arXiv:1712.05181_, 2017.

5. **Transformer Models (e.g., BERT, GPT)**

   - Devlin, J., et al. "BERT: Pre-training of deep bidirectional transformers for language understanding." _arXiv preprint arXiv:1810.04805_, 2018.
   - Brown, T., et al. "Language models are few-shot learners." _arXiv preprint arXiv:2005.14165_, 2020.

6. **FAISS** – Facebook AI Similarity Search

   - Johnson, J., Douze, M., & Jégou, H. "Billion-scale similarity search with GPUs." _arXiv preprint arXiv:1702.08734_, 2017.

7. **CodeBERT** – A Pre-trained Model for Programming Language and Natural Language

   - Feng, Z., et al. "CodeBERT: A Pre-trained Model for Programming and Natural Languages." _arXiv preprint arXiv:2002.08155_, 2020.

8. **Mistral-7B** and **Llama-2** Documentation

   - Touvron, H., et al. "LLaMA: Open and Efficient Foundation Language Models." _arXiv preprint arXiv:2307.09288_, 2023.
   - Mistral AI. "Mistral-7B: A new generation of open-weight language models." Available at: [https://mistral.ai](https://mistral.ai)

9. **Neovim API Documentation**

   - "Neovim Lua API Documentation." Available at: [https://neovim.io](https://neovim.io)

10. **Visual Studio Code Extension API Documentation**

    - "Visual Studio Code Extension Documentation." Available at: [https://code.visualstudio.com/docs/extensions/overview](https://code.visualstudio.com/docs/extensions/overview)
