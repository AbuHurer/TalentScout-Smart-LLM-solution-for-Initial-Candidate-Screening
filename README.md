# TalentScout AI - Intelligent Hiring Assistant

## Position: AI/ML Intern Assignment  
**Author:** Mohammed Abu Hurer  
**Tech Stack:** Python, Streamlit, Google Gemini LLM

---

## 📖 Project Overview

TalentScout is an intelligent chatbot designed to streamline the initial recruitment screening process. It autonomously interviews candidates by:

- **Gathering information:** Collecting key details such as Name, Contact, Experience, and Location.
- **Contextual analysis:** Understanding the candidate's declared Tech Stack.
- **Dynamic assessment:** Generating specific, relevant technical questions based on the candidate's expertise  
  (for example, asking about React hooks if the user knows React).

---

## 🚀 Installation & Usage

### Prerequisites

- Python 3.8+
- A Google Gemini API Key (Get it free at [Google AI Studio](https://aistudio.google.com))

### Steps

1. **Clone the repository (or download the files):**
   ```
   git clone https://github.com/AbuHurer/TalentScout-Smart-LLM-solution-for-Initial-Candidate-Screening.git
   cd talentscout
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```
   streamlit run app.py
   ```

### Interact

- The app will open in your browser (usually at `http://localhost:8501`).
- Enter your Google Gemini API Key in the sidebar.
- Begin chatting with TalentScout.

---

## 🧠 Prompt Design Strategy

The core intelligence of TalentScout relies on a **System Prompt** architecture. Instead of hard-coding `if/else` statements for every interaction, we define a persona and a 3-phase state machine within the prompt itself.

### System Prompt Structure

1. **Persona Definition**  
   Establishes the bot as **"TalentScout"**, a friendly recruiter that conducts structured yet conversational interviews.

2. **Phase 1 – Data Extraction**  
   - Explicitly lists the **7 required fields** (e.g., Name, Contact, Email, Experience, Current Role, Location, Tech Stack).
   - The LLM is instructed to ask for these **naturally**, not all at once, to maintain a conversational flow.

3. **Phase 2 – Dynamic Questioning**  
   This is the critical logic block.

   - **Trigger:** Once the model has **all required information**.
   - **Action:** Generate **3 technical questions** based on the declared Tech Stack.
   - **Flow:** Ask questions **one by one** to avoid overwhelming the candidate with a wall of text.

4. **Phase 3 – Termination**  
   - Defines a specific exit phrase, for example: **"End of Interview"**.
   - The Python code listens for this phrase to:
     - Disable the user input box.
     - Save the final interview transcript.

---

## ⚙️ Architecture & State Handling

### Challenge: LLM Forgetting Context Between Streamlit Re-runs

**Problem:**  
Streamlit re-runs the script on each interaction, which can cause the model to lose prior context.

**Solution:**  
Implement a `chat_history` mechanism that:

- Stores the full conversation (user and assistant messages) in `st.session_state`.
- Sends the **entire conversation history** plus the **System Prompt** with every API call.
- Ensures consistent behavior and memory across turns.

### Challenge: Getting AI to Ask Stack-Specific Questions

**Problem:**  
The model may generate generic questions instead of being specific to the candidate’s tech stack.

**Solution:**  

- The prompt explicitly links the **"Tech Stack"** variable to the **"Technical Questions"** phase.
- The LLM is instructed to:
  - Parse the Tech Stack.
  - Create questions that **directly reference** the listed tools/frameworks.
- Empirical tests showed that Google Gemini handles this correlation well **without** external lookup tables.

---

## 🛡️ Data Privacy

In this implementation:

- **No external database** is used. All data lives only in the **session RAM**.
- **Simulated storage:**  
  At the end of the interview, a transcript is generated locally to simulate backend storage or logging.
- **API security:**
  - The API key is captured via a **password input field** in Streamlit.
  - The key is **not logged** or stored in plain text.

---

## 🌟 Future Improvements (Bonus Ideas)

Potential enhancements for future iterations:

- **Sentiment analysis:**  
  Analyze user responses to detect confidence, hesitation, or uncertainty to aid in soft-skill evaluation.

- **Resume parsing:**  
  Allow users to upload a PDF resume and automatically extract:
  - Name
  - Email
  - Experience
  - Skills / Tech Stack  
  to pre-fill interview fields.

- **Voice interface:**  
  Integrate Speech-to-Text (STT) and Text-to-Speech (TTS) to support:
  - Voice-based interviews
  - Audio playback of questions and candidate answers

---

## 🧩 Folder Structure (Example)

```
talentscout/
├─ app.py
├─ requirements.txt
└─ README.md
```

---

## 🤝 Contributions

Contributions, issues, and feature requests are welcome.  
Feel free to fork the repository and submit a pull request.

---

## 📬 Contact

For any queries or collaboration:

- **Author:** Mohammed Abu Hurer  
- **GitHub:** [AbuHurer](https://github.com/AbuHurer)
