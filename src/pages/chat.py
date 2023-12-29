from openai import OpenAI
import streamlit as st
import json
import time
import tiktoken
import os,sys


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """
    Return the number of tokens used by a list of messages.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-1106"
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4",
            "gpt-3.5-turbo"
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        raise NotImplementedError(
            f"""model {model} not supported. Please add it to the num_tokens_from_messages function."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

@st.cache_resource
def get_openai_client(url, api_key):
    '''
    使用了缓存，当参数不变时，不会重复创建client
    '''
    client = OpenAI(base_url=url, api_key=api_key)
    return client

def chat_page():
    st.title("Chat Completions")
    # 初始化参数
    api_key = (
        st.session_state.api_key
        if "api_key" in st.session_state and st.session_state.api_key != ""
        else None
    )
    if api_key is None:
        st.error("Please enter your API key in the home.")
        st.stop()

    if "base_url" in st.session_state:
        base_url = st.session_state.base_url
    else:
        base_url = "https://api.openai.com/v1"

    src_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open(os.path.join(src_path, 'config/default.json'), 'r',encoding='utf-8') as f:
        config_defalut = json.load(f)

    # if "system_prompt" not in st.session_state:
    #     st.session_state.system_prompt = config_defalut["completions"]["system_prompt"]
 
    # 显示配置项
    st.session_state['model_list'] = config_defalut["completions"]["models"]
    model_name = st.selectbox('Models', st.session_state.model_list, key='chat_model_name')

    option = st.radio("system_prompt", ("Manual input", "prompts"),horizontal=True,index=0)
    if option == "Manual input":
        system_prompt = st.text_input('System Prompt (Please click the button "clear history" after modification.)' ,config_defalut["completions"]["system_prompt"])
    else:
        # 加载预设提示词
        with open(os.path.join(src_path, 'config/prompt.json'), 'r',encoding='utf-8') as f:
            masks = json.load(f)
        masks_zh = [item['name'] for item in masks['zh']]
        masks_zh_name = st.selectbox('prompts', masks_zh)
        for item in masks['zh']:
            if item['name'] == masks_zh_name:
                system_prompt = item['context']
                break
    

    if not st.checkbox('default param',True):
        max_tokens = st.number_input('Max Tokens', 1, 200000, config_defalut["completions"]["max_tokens"], key='max_tokens')
        temperature = st.slider('Temperature', 0.0, 1.0,  config_defalut["completions"]["temperature"], key='temperature')
        top_p = st.slider('Top P', 0.0, 1.0, config_defalut["completions"]["top_p"], key='top_p')
        stream = st.checkbox('Stream', config_defalut["completions"]["stream"], key='stream')
    else:
        max_tokens = config_defalut["completions"]["max_tokens"]
        temperature = config_defalut["completions"]["temperature"]
        top_p = config_defalut["completions"]["top_p"]
        stream = config_defalut["completions"]["stream"]


    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = [{"role": "system", "content": system_prompt}]

    if st.button("clear history"):
        st.session_state.chat_messages = [{"role": "system", "content": system_prompt}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    if prompt := st.chat_input():
        try:
            client =  get_openai_client(base_url, api_key)
        except Exception as e:
            st.error(e)
            st.stop()

        st.chat_message("user").write(prompt)
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                start_time = time.time()
                try: 
                    temp_chat_messages = st.session_state.chat_messages
                    temp_chat_messages.append({"role": "user", "content": prompt})
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=temp_chat_messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        stream=stream
                    )
                except Exception as e:
                    st.error(e)
                    st.stop()
                if response:
                    if stream:
                        placeholder = st.empty()
                        streaming_text = ''
                        for chunk in response:
                            if chunk.choices[0].finish_reason == 'stop':
                                break
                            chunk_text = chunk.choices[0].delta.content
                            if chunk_text:
                                streaming_text += chunk_text
                                placeholder.markdown(streaming_text)
                        model_msg = streaming_text
                    else:
                        model_msg = response.choices[0].message.content
                        with st.chat_message('assistant'):
                            st.markdown(model_msg)
                    end_time = time.time()
                    temp_chat_messages.append({"role": "assistant", "content": model_msg})
                    st.session_state.chat_messages = temp_chat_messages        
                
                
                    # 计算当前对话的消耗的token数
                    if config_defalut["completions"]["num_tokens"]:
                        try:
                            num_tokens = num_tokens_from_messages(st.session_state.chat_messages, model=model_name)
                            info_num_tokens = f"use tokens: {num_tokens}"
                            st.info(info_num_tokens)
                        except Exception as e:
                            print(e)
                    # 生成当前对话耗时
                    if config_defalut["completions"]["use_time"]:
                        st.info(f"Use time: {round(end_time - start_time,2)}s")
              
                
if __name__ == "__main__":
    chat_page()