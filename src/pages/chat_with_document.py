import streamlit as st
from langchain.document_loaders import PyPDFLoader
from ollama import chat
import io

# Function to extract text from PDF using LangChain's PyPDFLoader
def extract_text_from_pdf(uploaded_file):
    # Save the uploaded file to a temporary location
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Use PyPDFLoader to load the PDF
    loader = PyPDFLoader("temp.pdf")
    pages = loader.load()
    
    # Combine text from all pages
    text = " ".join([page.page_content for page in pages])
    print(text)
    return text

def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Function to handle user input and model response
def handle_user_input(prompt, pdf_text):
    if prompt:
        st.session_state.chat_history.append({"role": "User", "content": prompt})

        with st.chat_message("User"):
            st.write(prompt)
        
        # Include the PDF text in the prompt if available
        prompt = f"PDF Text: {pdf_text}\n\nUser Question: {prompt}" if pdf_text else prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the provided PDF text to answer the user's questions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        with st.chat_message("Model"):
            response_placeholder = st.empty()  
            full_response = ""

            # Use the Ollama chat function
            response = chat('deepseek-r1:7b', messages=messages, stream=True, options={'num_ctx': 8192})
            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    full_response += chunk["message"]["content"]
                    response_placeholder.write(full_response)  

        st.session_state.chat_history.append({"role": "Model", "content": full_response})

def main():
    st.title('Chat with PDF using Ollama')

    with st.sidebar:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        "[View the source code](https://github.com/Talen-520/StockAgent)]"

    pdf_text = ""
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF file uploaded and processed successfully!")

    initialize_session_state()
    display_chat_history()

    user_input = st.chat_input("Ask a question about the PDF")
    handle_user_input(user_input, pdf_text)

if __name__ == "__main__":
    main()