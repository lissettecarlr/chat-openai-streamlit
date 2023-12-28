import streamlit as st
from openai import OpenAI

st.set_page_config(
        page_title="speech to text",
        layout="wide",
)

@st.cache_resource
def get_openai_client(url, api_key):
    client = OpenAI(base_url=url, api_key=api_key)
    return client

def generated_speech(client,model,voice,prompt,speed):
    # 创建临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        speech_file_path = temp_file.name
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=prompt,
        speed=speed,
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path

def tts_page():
    st.title("text to speech")
    st.caption("The page provides a speech endpoint based on TTS (text-to-speech) model. It comes with 6 built-in voices")

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

    client = get_openai_client(base_url, api_key)

    # 选项
    model  = st.selectbox('model ',["tts-1","tts-1-hd"])
    voice  = st.selectbox('voice ',["alloy","echo","fable","onyx","nova","shimmer"])
    speed  = st.slider('speed', 0.25, 4.0, 1.0)

    option = st.radio("Input methods:", ("Manual input", "import document"),horizontal=True,index=0)

    if option == "import document":
        uploaded_file = st.file_uploader("Choose a file", type=["txt"])
        content = None
        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            st.text(content)
        if st.button("generated") and content:
            with st.spinner('doing...'):
                speech_file_path = generated_speech(client,model,voice,content,speed)
                st.audio(speech_file_path)
             
    else:
        if prompt := st.chat_input("prompt"):
            st.chat_message("user").write(prompt)
            with st.chat_message('assistant'):
                with st.spinner('doing...'):
                    try:
                        speech_file_path = generated_speech(client,model,voice,prompt,speed)
                        st.audio(speech_file_path)
                    except Exception as e:
                        st.error(e)
                        st.stop()

if __name__ == "__main__":
    tts_page()