import streamlit as st
from llama_index.llms.ollama import Ollama
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
)

st.set_page_config(page_title="Chat with Streamlit docs using local LLM", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Chat with Streamlit docs using local LLM 💬🦙")
st.info("Check out the page at [GitHub](https://github.com/JunyiYe/rag-local)", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Streamlit's open-source Python library!"}
    ]

@st.cache_resource(show_spinner=False)
def load_model():
    # load local LLM
    Settings.llm = Ollama(model="mistral", request_timeout=60.0)
    # load local embed model
    Settings.embed_model = "local:BAAI/bge-small-en-v1.5" #"local:BAAI/bge-small-en-v1.5"

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        index = VectorStoreIndex.from_documents(docs)
        return index

load_model()
index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", similarity_top_k=2, verbose=True)
if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history