import streamlit as st
import requests

st.set_page_config(layout="wide")
PROCESS_FILES_URL = "http://localhost:8000/process_files/"
PROCESS_DIR_URL = "http://localhost:8000/process_directory/"
PROCESS_QUERY_URL = "http://localhost:8000/query"

def main():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Multimodal RAG")
        
        input_method = st.radio("Choose input method:", ("Upload Files", "Enter Directory Path"))
        
        if input_method == "Upload Files":
            uploaded_files = st.file_uploader("Drag and drop files here", accept_multiple_files=True)
            if uploaded_files and st.button("Process Files"):
                with st.spinner("Processing files..."):
                    files = [("files", file) for file in uploaded_files]
                    response = requests.post(PROCESS_FILES_URL, files=files)
                    if response.status_code == 200:
                        st.success("Files processed and index created!")
                    else:
                        st.error("Error processing files.")
        else:
            directory_path = st.text_input("Enter directory path:")
            if directory_path and st.button("Process Directory"):
                with st.spinner("Processing directory..."):
                    response = requests.post(PROCESS_DIR_URL, json={"directory_path": directory_path})
                    if response.status_code == 200:
                        st.success("Directory processed and index created!")
                    else:
                        st.error("Error processing directory.")
    
    with col2:
        st.title("Chat")
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        
        user_input = st.chat_input("Enter your query:")

        chat_container = st.container()
        with chat_container:
            for message in st.session_state['history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state['history'].append({"role": "user", "content": user_input})
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                response = requests.post(PROCESS_QUERY_URL, json={"query": user_input})
                if response.status_code == 200:
                    full_response = response.json()["response"]
                    message_placeholder.markdown(full_response)
                else:
                    message_placeholder.markdown("Error querying the index.")
            st.session_state['history'].append({"role": "assistant", "content": full_response})

        if st.button("Clear Chat"):
            st.session_state['history'] = []
            st.rerun()

if __name__ == "__main__":
    main()