import streamlit as st
import json

def import_config_file(file):
    '''
    侧边栏配置导入
    '''
    if file is not None:
        content = file.read()
        try:
            # 解析JSON数据
            json_data = json.loads(content)
            st.success("load config success")
        except Exception as e:
            st.error("load config error:{}".format(e))
        st.session_state.base_url = json_data.get("base_url")
        st.session_state.api_key = json_data.get("api_key")

def home():
    st.title("openai playground")
    st.caption("Please fill in the parameters in the sidebar before using, or import the parameters by uploading a file.")

    st.session_state['base_url'] = "https://api.openai.com/v1"
    st.session_state['api_key'] = ""

    #通过上传配置的方式导入base_url和api_key
    uploaded_file = st.sidebar.file_uploader("uploaded config", type="json",label_visibility="collapsed")
    if uploaded_file is not None:
        import_config_file(uploaded_file)

    ## 输入方式
    st.session_state.base_url = st.sidebar.text_input('Base URL', st.session_state.base_url)
    st.session_state.api_key =  st.sidebar.text_input('API Key',st.session_state.api_key, type='password')

    st.markdown(
            """
            请在填写完侧边栏参数后，选择页面进行使用。本应用将调用openai接口的方式来演示各项功能\n
            After filling in the parameters in the sidebar, please select a page to use. This application will demonstrate various functions by calling the OpenAI API.\n
            
            ### chat page\n
            该页面用于文本对话，对应openai文档：[text-generation](https://platform.openai.com/docs/guides/text-generation)
            This page is used for text conversations, corresponding to the OpenAI documentation: [text-generation](https://platform.openai.com/docs/guides/text-generation)\n
            
            ### vision page\n
            该页面用于图像理解，对应openai文档：[vision](https://platform.openai.com/docs/guides/vision)
            This page is used for image understanding, corresponding to the OpenAI documentation: [vision](https://platform.openai.com/docs/guides/vision)\n
            """
        )
if __name__ == "__main__":
    home()