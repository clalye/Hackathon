import streamlit as st
import boto3
import os
import json
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever


st.image("images/Agilent_Logo_RGB.png", width=200)
st.write(
    """
    ## Welcome to the Virtual AI assistant Agilent Hackathon Team 5 portal


    ### Hi, I'm an Agile Virtual Assistant for Troubleshooting or Technical advice. How can I help you today ?
    """
)
bedrockClient = boto3.client('bedrock-agent-runtime', 'us-west-2')

def letschat():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['text'])
    message_placeholder = st.empty()
    questions = st.chat_input('Enter you questions here...')
    if questions:
        with st.chat_message('user'):
            st.markdown(questions)
        st.session_state.chat_history.append({"role":'user', "text":questions})
        with st.spinner("Thinking..."):
            query=json.dumps(questions)
            response = getAnswers(questions)
        answer = response['output']['text']
        with st.chat_message('assistant'):
            with st.spinner("Thinking..."):
                st.markdown(answer)
        st.session_state.chat_history.append({"role":'assistant', "text": answer})
        with st.container():
            st.write("&nbsp;")
        if len(response['citations'][0]['retrievedReferences']) != 0:
            context = response['citations'][0]['retrievedReferences'][0]['content']['text']
            doc_url = response['citations'][0]['retrievedReferences'][0]['location']['s3Location']['uri']
            # st.markdown(f"<span style='color:#FFDA33'>Context used: </span>{context}", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#00008B'>Source Document: </span>{doc_url}", unsafe_allow_html=True)
        else:
                st.markdown(f"<span style='color:red'>No Context</span>", unsafe_allow_html=True)

def getAnswers(questions):
    knowledge_base_id="XIMGDIIOJQ"
    knowledgeBaseResponse = bedrockClient.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id,
                'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0',
                'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 100,
                            'overrideSearchType': 'HYBRID'
                        }
                    }
            },
            'type': 'KNOWLEDGE_BASE'
        })
    return knowledgeBaseResponse
def getAgentAnswers(questions):
    bedrockClient = boto3.client('bedrock-agent-runtime', 'us-west-2')
    agent_id = "F86UAKQKTK"
    agent_alias_id  ="agent5"
    response = bedrockClient.invoke_agent(
    inputText=questions,
    endSession=False,
    enableTrace=False,
    agentId=agent_id,
    agentAliasId=agent_alias_id,
    sessionId="team50")
    
    st.markdown(response)

    # stream = response.get("completion")
    # if stream:
    #     for event in stream:
    #         chunk = event.get('chunk')
    #         st.markdown(chunk)
    #         if chunk:
    #             yield chunk.get('bytes').decode()

    return response
# def getreply(query):
#     bedrockClient = boto3.client('bedrock-agent-runtime', 'us-west-2')
#     knowledge_base_id="XIMGDIIOJQ"
#     response = bedrockClient.retrieve(
#     knowledgeBaseId=knowledge_base_id,
#     retrievalQuery={'query':query},
#     retrievalConfiguration={
#                 'vectorSearchConfiguration': {
#                     'numberOfResults': 2
#                 }
#             },
#             nextToken='loan'
#     )
#     return response
def open_sidebar():
    st.session_state.sidebar = True

letschat()
