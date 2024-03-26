import streamlit as st
from query import * 

# set custom title
st.set_page_config(page_title="Medibot", page_icon="🤖")

# specify model 
llama_key = os.environ["LLAMA_API_KEY"]
google_key = os.environ["GOOGLE_API_KEY"]
llama = LlamaAPI(llama_key)
# llm = ChatLlamaAPI(client=llama, temperature=0.1, model="llama-70b-chat")
llm = GoogleGenerativeAI(model="gemini-1.0-pro", api_key=google_key)



st.title('Nice CKS AI powered knowledge retrieval system')
cks_url = "https://cks.nice.org.uk/"
bnf_url = "https://bnf.nice.org.uk/treatment-summary/"


# write a description of the system with embedded links for NICE CKS and NICE BNF

st.markdown("This is an AI powered knowledge retrieval system based on the information from the [National Institute for Health and Care Excellence Clinical Knowledge Summaries (NICE CKS)](https://cks.nice.org.uk/) and [British National Formulary Treatment summaries (NICE BNF)](https://bnf.nice.org.uk/treatment-summary/)")


st.write("Please do not use this system for medical advice. The answers generated may not be accurate. I am not responsible for any harm caused by the use of this system. Always consult a healthcare professional for medical advice.")

with st.form(key='my_form'): 
    question = st.text_input(label='Question:')
    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        urls, ans = send_query("nice_cks", question)
        st.write("Links used to answer question: ")
        for url in urls:
            st.write(url)
        st.write("Answer: ")
        st.write(ans)

