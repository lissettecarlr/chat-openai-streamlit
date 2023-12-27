from openai import OpenAI
import streamlit as st
import time 
import base64
import re

@st.cache_resource
def get_openai_client(url, api_key):
    '''
    使用了缓存，当参数不变时，不会重复创建client
    '''
    client = OpenAI(base_url=url, api_key=api_key)
    return client


def assistant_page():
    st.title("assistant")
    #st.caption("https://platform.openai.com/docs/assistants/overview")
    option = st.radio("change language:", ("En", "Zh"),horizontal=True,index=1)
    if option == "Zh":
        st.markdown(
            """
            * 1 通过侧边栏创建assistant将获得的ID填入下方,或者直接到[openai后台](https://platform.openai.com/assistants)创建.
            * 2 填入ID后点击load assistant,等待提示assistant loaded successfully
            * 3 开始对话吧
            """
        )
    else:
        st.markdown(
            """
            * 1 Create an assistant through the sidebar and fill in the obtained ID below, or create one directly on the OpenAI platform.
            * 2 After entering the ID, click "Load Assistant" and wait for the prompt "Assistant loaded successfully."
            * 3 Start the conversation.
            """
        )



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


    if "run" not in st.session_state:
        st.session_state.run = {"status": None}
    if "assistants_messages" not in st.session_state:
        st.session_state.assistants_messages = []
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = ""
    if "assistant" not in st.session_state:
        st.session_state.assistant = None


    # 用于控制输入框是否允许输入
    if "input_message_flag" not in st.session_state:
        st.session_state.input_message_flag = False
    def input_message_button_cb():
        st.session_state.input_message_flag = True


    client = get_openai_client(base_url, api_key)

    # 创建assistant
    assistant_name = st.sidebar.text_input("assistant name", "Math Tutor")
    instructions = st.sidebar.text_input("instructions", "You are a personal math tutor. Write and run code to answer math questions.")
    tools = st.sidebar.selectbox("tools", ["code_interpreter","Retrieval"])
    model = st.sidebar.selectbox('model', ["gpt-4-1106-preview", "gpt-3.5-turbo-1106"])

    #按键用于创建assistant
    if st.sidebar.button("create assistant"):
        if tools == "code_interpreter":
            tools = [{"type": "code_interpreter"}]
        elif tools == "Retrieval":
            tools = [{"type": "retrieval"}]
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            tools=tools,
            model=model,
        )
        st.sidebar.success("assistant created successfully!")
        st.sidebar.write("-------------------")
        st.sidebar.write(assistant.id)
        st.sidebar.write("-------------------")
        
    # 实际支持文件 见：https://platform.openai.com/docs/assistants/tools/supported-files
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file",
        type=[
            "txt",
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "csv",
            "json",
            "geojson",
            "xlsx",
            "xls",
        ],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        file = client.files.create(file=uploaded_file, purpose="assistants")
        st.session_state.file_id = file.id
    
    def load_assistant(assistant_id):
        st.session_state.assistant = client.beta.assistants.retrieve(assistant_id)
        st.session_state.thread = client.beta.threads.create()
        st.success("assistant loaded successfully!")

    # 加载assistant
    st.session_state.assistant_id = st.text_input("assistant id", st.session_state.assistant_id)
    col1, col2 ,col3 =  st.columns(3)
    if col1.button("load assistant"):
        load_assistant(st.session_state.assistant_id)

    if col2.button("delete assistant"):
        if(st.session_state.assistant_id == "" or st.session_state.assistant is None):
            st.error("please load assistant first!")
        else:
            client.beta.assistants.delete(assistant_id=st.session_state.assistant.id)
            st.session_state.assistant_id = ""
            st.session_state.assistant = None
            st.session_state.thread = None
            st.session_state.assistants_messages = []
            st.success("assistant deleted successfully!")
    if st.session_state.assistant is not None:
        text_status_assistant =  r"assistant : {}".format(st.session_state.assistant.name)   
    else:
        text_status_assistant =  r"assistant : None"    
    col3.write(text_status_assistant)

    def create_file_link(file_name, file_id):
        content = client.files.content(file_id)
        content_type = content.response.headers["content-type"]
        b64 = base64.b64encode(content.text.encode(content.encoding)).decode()
        link_tag = f'<a href="data:{content_type};base64,{b64}" download="{file_name}">Download Link</a>'
        return link_tag

    def parse_message(messages):
        '''
        解析返回的消息
        '''
        messages_value_list = []
        for message in messages:
            message_content = ""
            from openai.types.beta.threads import MessageContentImageFile
            if not isinstance(message, MessageContentImageFile):
                message_content = message.content[0].text
                annotations = message_content.annotations
            else:
                image_file = client.files.retrieve(message.file_id)
                messages_value_list.append(
                    f"Click <here> to download {image_file.filename}"
                )
            citations = []
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(
                    annotation.text, f" [{index}]"
                )

                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(
                        f"[{index}] {file_citation.quote} from {cited_file.filename}"
                    )
                elif file_path := getattr(annotation, "file_path", None):
                    link_tag = create_file_link(
                        annotation.text.split("/")[-1], file_path.file_id
                    )
                    message_content.value = re.sub(
                        r"\[(.*?)\]\s*\(\s*(.*?)\s*\)", link_tag, message_content.value
                    )

            message_content.value += "\n" + "\n".join(citations)
            messages_value_list.append(message_content.value)
            return messages_value_list

    def refresh_chat_box():
        '''
        刷新聊天框
        '''
        #print(st.session_state.assistants_messages)
        for chat in st.session_state.assistants_messages:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"], True)

    if st.session_state.assistant is not None and st.session_state.thread is not None:
        # 删除当前thread, 重新创建一个新的thread
        if st.button("clear history"):
            client.beta.threads.delete(thread_id=st.session_state.thread.id)
            st.session_state.thread = client.beta.threads.create()
            st.session_state.assistants_messages = []

        refresh_chat_box()    
        if prompt := st.chat_input("mseeage",on_submit=input_message_button_cb,disabled=st.session_state.input_message_flag):
            with st.chat_message("user"):
                st.markdown(prompt, True)
            with st.chat_message('assistant'):
                with st.spinner('Thinking...'):
                    # 包装消息
                    message_data = {
                        "thread_id": st.session_state.thread.id,
                        "role": "user",
                        "content": prompt
                    }
                    if "file_id" in st.session_state:
                        message_data["file_ids"] = [st.session_state.file_id]
                    # 将消息扔进去
                    client.beta.threads.messages.create(**message_data)
                    # 创建run执行
                    st.session_state.run = client.beta.threads.runs.create(
                        thread_id=st.session_state.thread.id,
                        assistant_id=st.session_state.assistant.id,
                    )
                    if hasattr(st.session_state.run, 'status'):
                        while 1:
                            # 获取当前run的状态
                            st.session_state.run = client.beta.threads.runs.retrieve(
                                thread_id=st.session_state.thread.id,
                                run_id=st.session_state.run.id,
                            )
                            if st.session_state.run.status == "failed":
                                with st.chat_message('assistant'):
                                    st.write("Run failed")
                                break
                            if st.session_state.run.status == "completed":
                                thread_messages = client.beta.threads.messages.list(
                                    thread_id=st.session_state.thread.id
                                )
                                result = "\n".join(parse_message(thread_messages))
                                
                                st.session_state.assistants_messages.append({"role": "user", "content": prompt})
                                st.session_state.assistants_messages.append({"role": "assistant", "content": result})
                                st.session_state.input_message_flag = False
                                st.rerun()#重新运行脚本
                                
                            time.sleep(1)


if __name__ == "__main__":
    assistant_page()