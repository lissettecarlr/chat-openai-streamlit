from openai import OpenAI
import streamlit as st
import yaml
import time
import tiktoken
import os,sys

st.title("Chat Completions")
st.caption("Please fill in the parameters in the sidebar before using, or import the parameters by uploading a file.")

# 初始化session_state
if 'base_url' not in st.session_state:
    st.session_state['base_url'] = "https://api.openai.com/v1"
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""


# 加载默认配置文件
src_path = os.path.dirname(os.path.realpath(sys.argv[0]))
with open(os.path.join(src_path, 'config/default.yaml'), 'r') as f:
    config_defalut = yaml.safe_load(f)


@st.cache_resource
def get_openai_client(url, api_key):
    '''
    使用了缓存，当参数不变时，不会重复创建client
    '''
    client = OpenAI(base_url=url, api_key=api_key)
    return client


def import_config_file(file):
    '''
    侧边栏配置导入
    '''
    if file is not None:
        content = file.read()
        config = yaml.safe_load(content)
        if 'base_url' in config:
            st.session_state.base_url= config['base_url']
        if 'api_key' in config:
            st.session_state.api_key = config['api_key']

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


# 在侧边栏添加一个文件上传器
uploaded_file = st.sidebar.file_uploader("uploaded config", type="yaml")
# 如果文件上传成功，则调用import_config_file函数
if uploaded_file is not None:
    import_config_file(uploaded_file)
    #print(st.session_state)

## 侧边栏
base_url = st.sidebar.text_input('Base URL', st.session_state.base_url, key='base_url')
api_key = st.sidebar.text_input('API Key',"", type='password', key='api_key')

# 模型列表
st.session_state['model_list'] = config_defalut["completions"]["models"]
model_name = st.selectbox('Models', st.session_state.model_list, key='chat_model_name')
system_prompt = st.text_input('System Prompt (Please click the button "clear history" after modification.)' ,config_defalut["completions"]["system_prompt"], key='system_prompt')

if not st.checkbox('default param',True):
    max_tokens = st.number_input('Max Tokens', 1, 200000, 512, key='max_tokens')
    temperature = st.slider('Temperature', 0.0, 1.0,  0.7, key='temperature')
    top_p = st.slider('Top P', 0.0, 1.0, 1.0, key='top_p')
    stream = st.checkbox('Stream', True, key='stream')
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
    if not api_key:
        st.info("Please enter the API key in the sidebar first.")
        st.stop()
    try:
        if st.session_state.get('base_url') is not None:
            param_url = st.session_state.base_url
        else:
            st.error("base_url is None")
            st.stop()
        if st.session_state.get('api_key') is not None:
            param_api_key = st.session_state.api_key
        else:
            st.error("api_key is None")
            st.stop()
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
                # st.session_state.use_time = round(end_time - start_time,2)
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
              
                

