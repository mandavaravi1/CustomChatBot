import streamlit as st
from llama_index.core import VectorStoreIndex, ServiceContext   
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader,StorageContext,load_index_from_storage
from dotenv import load_dotenv
import os

#st.set_page_config(page_title="Chat with the Training docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
##status openai.api_key = st.secrets['API_KEY']
openai.api_key = os.getenv('API_KEY')
st.title("Chat with the Training docs 💬")

         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the data trained!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    # check if storage already exists    
    PERSIST_DIR = "./storage"
 
    with st.spinner(text="Loading and indexing the  docs – hang tight! This should take 1-2 minutes."):
            reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
            docs = reader.load_data()
            service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert in PeopleSoft technical issues and  your job is to answer technical questions. Assume that all questions are related to the PeopleSoft. Keep your answers technical and based on facts – do not hallucinate features."))
            index = VectorStoreIndex.from_documents(docs, service_context=service_context)
            # store it for later
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            
            # load the existing index
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

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
