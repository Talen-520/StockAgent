import streamlit as st
from ollama import chat

def main():
    st.title('Chatbot')
    
    st.caption("Welcome! You are using the `deepseek-r1:7b` model.")

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # User input
    if prompt := st.chat_input("Enter your message"):
        st.session_state.chat_history.append({"role": "User", "content": prompt})

        with st.chat_message("User"):
            st.write(prompt)

        # Stream model response
        with st.chat_message("ai"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                response = chat(
                'deepseek-r1:7b', 
                messages=[{"role": "user", "content": prompt}], 
                stream=True, 
                options={'num_ctx': 8192}  
            )
                for chunk in response:
                    if "message" in chunk and "content" in chunk["message"]:
                        full_response += chunk["message"]["content"]
                        response_placeholder.write(full_response)

                st.session_state.chat_history.append({"role": "Model", "content": full_response})
            except Exception as e:
                st.error(f"Failed to get a response from the model: {e}")

if __name__ == "__main__":
    main()