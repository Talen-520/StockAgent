import streamlit as st
import requests
import json  # Import the json module for safe parsing

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3.2"  # TODO: update this for whatever model you wish to use

# Define the system prompt
system_prompt = "You are a helpful assistant."

def chat_with_llama(prompt):
    try:
        full_prompt = f"{system_prompt}\n\nUser: {prompt}"
        
        payload = {
            "model": model,  
            "prompt": full_prompt,    
            "stream": True  # Enable streaming
        }
        
        # Send the request to the Ollama API
        response = requests.post('http://127.0.0.1:11434/api/generate', json=payload, stream=True)
        response.raise_for_status()
        
        # Process the streamed response
        for chunk in response.iter_lines():
            if chunk:
                data = chunk.decode('utf-8')
                yield data  # Yield each chunk of the response

    except requests.exceptions.RequestException as e:
        yield f"Error: {e}"

def main():
    st.title('Ollama Chat')
    st.write(f"Welcome to the Ollama Chat! Ask me anything. You are running the `{model}` model.")
    st.markdown(
    """
    **Command Available:**  
    - `clear` - clear chat history
    """
    )
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Enter your message")

    if user_input:
        if user_input.lower() in ['clear', 'reset']:
            st.session_state.chat_history = []
            st.rerun()  
        elif user_input.lower() in ['list']:
            st.info(f"Current model: {model}", icon="ℹ️")
        else:
            st.session_state.chat_history.append({"role": "User", "content": user_input})

            with st.chat_message("User"):
                st.write(user_input)

            # Stream the response from the model
            with st.chat_message("Model"):
                response_placeholder = st.empty()  # Placeholder to display streamed response
                full_response = ""
                for chunk in chat_with_llama(user_input):
                    try:
                        # Parse the JSON chunk safely using json.loads
                        chunk_data = json.loads(chunk)
                        if "response" in chunk_data:
                            full_response += chunk_data["response"]
                            response_placeholder.write(full_response)  # Update the placeholder
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing JSON response: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

            # Append the full response to chat history
            st.session_state.chat_history.append({"role": "Model", "content": full_response})

if __name__ == "__main__":
    main()