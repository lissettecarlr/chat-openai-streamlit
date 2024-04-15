import streamlit as st
from openai import OpenAI

def extra_page():
    st.title("extra playground")
    st.caption("该页面是对其他模型的测试页面，无需在home页面填写openai的密匙")
    option = st.radio("Select Function", ("moonshot", "test"),horizontal=True,index=0)
    st.markdown("-----------")
    if option == "moonshot":
        moonshot_option()

def moonshot_option():
    @st.cache_resource
    def get_monnshot_client(api_key,base_url="https://api.moonshot.cn/v1"):
        '''
        使用了缓存，当参数不变时，不会重复创建client
        '''
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        return client

    def upload_file(client,file):
        file_object = client.files.create(file=file, purpose="file-extract")
        return file_object

    def get_file_list(client):
        file_list = client.files.list()
        return file_list.data

    def del_file(client,file_id):
        return client.files.delete(file_id=file_id)

    def get_file_content(client,file_id):
        return client.files.content(file_id=file_id).text


    st.markdown("## 月之暗面")
    st.caption("由Moonshot AI开发的语言大模型，使用前需要取申请密钥：")
    st.caption("https://platform.moonshot.cn/docs/api-reference")

    if "moonshot_key" not in st.session_state:
        st.session_state.moonshot_key = ""
    st.session_state.moonshot_key =  st.text_input('API Key',st.session_state.moonshot_key, type='password')
    
    if st.session_state.moonshot_key == "":
        st.warning("请先输入密匙")
        st.stop()
    else:
        try:
            client =  get_monnshot_client(st.session_state.moonshot_key)
        except Exception as e:
            st.error(e)
            st.stop()     

    option_prarm = st.radio("使用默认参数:", ("是", "否"),horizontal=True,index=0)        
    if option_prarm == "是":
        stream = True
        temperature = 0.3
        model_name = "moonshot-v1-32k"
        system_prompt = "You are a hellpful assistant."
    else:
        #max_tokens = st.number_input('Max Tokens', 1, 200000, config_defalut["completions"]["max_tokens"], key='max_tokens')
        temperature = st.slider('Temperature', 0.0, 1.0,  0.3, key='temperature')
        #top_p = st.slider('Top P', 0.0, 1.0, config_defalut["completions"]["top_p"], key='top_p')
        stream = st.checkbox('Stream', True , key='stream')
        model_name = st.selectbox('Models', ["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k"], key='chat_model_name')
        system_prompt = st.text_input('System Prompt' ,"You are a hellpful assistant.")
    
    # print("------------------")    
    # print(stream)
    # print(temperature)
    # print(model_name)
    # print(system_prompt)
    # print("------------------")    

    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = [{"role": "system", "content": system_prompt}]
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'file_list' not in st.session_state:
        st.session_state.file_list = []

    option_show_list = st.radio("显示云文档:", ("是", "否"),horizontal=True,index=1)                
    if option_show_list == "是":
        file_list = get_file_list(client)
        for file in file_list:
            st.session_state.file_list.append(
                {
                    "id": file.id,
                    "filename": file.filename,
                }
            )
            st.write("文件ID：{}".format(file.id))
            st.write("文件名：{}".format(file.filename))
            st.write("大小：{} M".format(round(file.bytes/1024,2)))
            st.write("-----------------")
        if st.button("删除所有文件"):
            for file in file_list:
                del_file(client,file.id)
            st.success("文件已删除，请刷新页面以查看最新文件列表")

    option_delete = st.radio("删除云文档:", ("是", "否"),horizontal=True,index=1)        
    if option_delete == "是":
        file_id_to_delete = st.text_input("输入要删除的文件ID")
        if st.button("删除文件"):
            try:
                del_file(client,file_id_to_delete)
                st.success("文件已删除")
            except Exception as e:
                st.error(e)

    st.write("-----------------")
    if st.button("clear history"):
        st.session_state.chat_messages = [{"role": "system", "content": system_prompt}]
        st.session_state.file_uploaded = False

    if not st.session_state.file_uploaded:
        option = st.radio("文件选取方式:", ("文件ID", "上传"),horizontal=True,index=1)
        if option == "上传":
            #uploaded_file = st.file_uploader("选择文件", type=['xlsx'])
            uploaded_files = st.file_uploader("Upload", type=['xlsx'], accept_multiple_files=True)    
            if uploaded_files:
                for file in uploaded_files:
                    file_object = upload_file(client, file)
                    file_content = get_file_content(client, file_object.id)
                    st.session_state.chat_messages.append({"role": "system", "content": file_content})
                st.success("文件上传成功")
                # 标记文件已上传
                st.session_state.file_uploaded = True
        if option == "文件ID":
            file_id = st.text_input("文件ID")
            if st.button("确认文件"):
                file_content = get_file_content(client, file_id)
                st.session_state.chat_messages.append({"role": "system", "content": file_content})
                st.session_state.file_uploaded = True
                st.success("文件选择成功")
    else:
        st.write("文件已上传。重置对话则点击`clear history`按钮。")

    for msg in st.session_state.chat_messages:
        if msg['role'] == "system":
            continue
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                try: 
                    temp_chat_messages = st.session_state.chat_messages
                    temp_chat_messages.append({"role": "user", "content": prompt})
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=temp_chat_messages,
                        temperature=temperature,
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
                        st.markdown(model_msg)
                temp_chat_messages.append({"role": "assistant", "content": model_msg})
                st.session_state.chat_messages = temp_chat_messages        



if __name__ == "__main__":
    extra_page()