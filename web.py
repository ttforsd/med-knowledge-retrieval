import streamlit as st
from query import * 

# specify model 
llama_key = os.environ["LLAMA_API_KEY"]
google_key = os.environ["GOOGLE_API_KEY"]
llama = LlamaAPI(llama_key)
# llm = ChatLlamaAPI(client=llama, temperature=0.1, model="llama-70b-chat")
llm = GoogleGenerativeAI(model="gemini-1.0-pro", api_key=google_key)

st.title('Nice CKS Question Answering')

st.write("This is a question answering system for the National Institute for Health and Care Excellence (NICE) Clinical Knowledge Summaries (CKS).")

with st.form(key='my_form'): 
    question = st.text_input(label='Enter your question here')
    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        urls, ans = send_query("nice_cks", question)
        st.write("Links used to answer question: ")
        for url in urls:
            st.write(url)
        st.write("Answer: ")
        st.write(ans)

