# app.py

import streamlit as st
from database import create_tables, register_user, login_user
from rag import retrieve_relevant_chunks, generate_answer
from pypdf import PdfReader
import io

create_tables()

st.set_page_config(page_title="Structured Questionnaire Tool")

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- FILE PARSING ---------------- #

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf = PdfReader(uploaded_file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text

    else:
        return uploaded_file.read().decode("utf-8")


# ---------------- AUTH ---------------- #

if not st.session_state.user:
    st.title("Login / Register")

    option = st.selectbox("Select Option", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully. Please login.")
            else:
                st.error("Username already exists.")

    if option == "Login":
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- MAIN APP ---------------- #

else:
    st.title("Structured Questionnaire Answering Tool")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.subheader("Upload Questionnaire")
    questionnaire_file = st.file_uploader(
        "Upload Questionnaire (.txt or .pdf)",
        type=["txt", "pdf"]
    )

    st.subheader("Upload Reference Documents")
    reference_files = st.file_uploader(
        "Upload Reference Documents (.txt or .pdf)",
        type=["txt", "pdf"],
        accept_multiple_files=True
    )

    if questionnaire_file and reference_files:
        questionnaire_text = extract_text_from_file(questionnaire_file)

        questions = []
        for line in questionnaire_text.split("\n"):
            clean_line = line.strip()
            if clean_line and any(char.isdigit() for char in clean_line):
                if "." in clean_line:
                    questions.append(clean_line)

        documents = []

        for file in reference_files:
            content = extract_text_from_file(file)
            documents.append((file.name, content))

        if st.button("Generate Answers"):
            results = []

            for question in questions:
                retrieved = retrieve_relevant_chunks(question, documents)
                answer, citations, score, evidence = generate_answer(question, retrieved)

                results.append({
                    "question": question,
                    "answer": answer,
                    "citations": citations,
                    "confidence": round(score, 2),
                    "evidence": evidence
                })

            st.session_state.results = results

    # ---------------- REVIEW ---------------- #

    if "results" in st.session_state:
        total_questions = len(st.session_state.results)
        answered = sum(1 for r in st.session_state.results if r["answer"] != "Not found in references.")

        st.markdown("### Coverage Summary")
        st.write(f"Total Questions: {total_questions}")
        st.write(f"Answered with references: {answered}")
        st.write(f"Not Found: {total_questions - answered}")
        st.subheader("Review & Edit Answers")

        for i, item in enumerate(st.session_state.results):
            st.markdown(f"### Question {i+1}")
            st.write(item["question"])

            edited_answer = st.text_area(
                "Answer",
                value=item["answer"],
                key=f"answer_{i}"
            )

            st.write("Citations:", ", ".join(item["citations"]))
            st.write("Confidence Score:", item["confidence"])
            if item["evidence"]:
                st.markdown("**Evidence Snippets:**")
                for snippet in item["evidence"]:
                    st.info(snippet)

            st.session_state.results[i]["answer"] = edited_answer

        # ---------------- EXPORT ---------------- #

        if st.button("Download Document"):
            output_text = ""

            for item in st.session_state.results:
                output_text += f"{item['question']}\n"
                output_text += f"Answer: {item['answer']}\n"
                output_text += f"Citations: {', '.join(item['citations'])}\n\n"

            st.download_button(
                label="Download Answers",
                data=output_text,
                file_name="answered_questionnaire.txt",
                mime="text/plain"
            )