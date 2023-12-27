import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
from io import BytesIO
import os,sys,json

filter_text = {
  "en": [
    " www.mooji.org",
  ],
  "nl": [
    " Ondertitels ingediend door de Amara.org gemeenschap",
    " Ondertiteld door de Amara.org gemeenschap",
    " Ondertiteling door de Amara.org gemeenschap"
  ],
  "de": [
    " Untertitelung aufgrund der Amara.org-Community"
    " Untertitel im Auftrag des ZDF für funk, 2017",
    " Untertitel von Stephanie Geiges",
    " Untertitel der Amara.org-Community",
    " Untertitel im Auftrag des ZDF, 2017",
    " Untertitel im Auftrag des ZDF, 2020",
    " Untertitel im Auftrag des ZDF, 2018",
    " Untertitel im Auftrag des ZDF, 2021",
    " Untertitelung im Auftrag des ZDF, 2021",
    " Copyright WDR 2021",
    " Copyright WDR 2020",
    " Copyright WDR 2019",
    " SWR 2021",
    " SWR 2020",
  ],
  "fr": [
    " Sous-titres réalisés para la communauté d'Amara.org",
    " Sous-titres réalisés par la communauté d'Amara.org",
    " Sous-titres fait par Sous-titres par Amara.org",
    " Sous-titres réalisés par les SousTitres d'Amara.org",
    " Sous-titres par Amara.org",
    " Sous-titres par la communauté d'Amara.org",
    " Sous-titres réalisés pour la communauté d'Amara.org",
    " Sous-titres réalisés par la communauté de l'Amara.org",
    " Sous-Titres faits par la communauté d'Amara.org",
    " Sous-titres par l'Amara.org",
    " Sous-titres fait par la communauté d'Amara.org"
    " Sous-titrage ST' 501",
    " Sous-titrage ST'501",
    " Cliquez-vous sur les sous-titres et abonnez-vous à la chaîne d'Amara.org",
    " ❤️ par SousTitreur.com",
  ],
  "it": [
    " Sottotitoli creati dalla comunità Amara.org",
    " Sottotitoli di Sottotitoli di Amara.org",
    " Sottotitoli e revisione al canale di Amara.org",
    " Sottotitoli e revisione a cura di Amara.org",
    " Sottotitoli e revisione a cura di QTSS",
    " Sottotitoli e revisione a cura di QTSS.",
    " Sottotitoli a cura di QTSS",
  ],
  "es": [
    " Subtítulos realizados por la comunidad de Amara.org",
    " Subtitulado por la comunidad de Amara.org",
    " Subtítulos por la comunidad de Amara.org",
    " Subtítulos creados por la comunidad de Amara.org",
    " Subtítulos en español de Amara.org",
    " Subtítulos hechos por la comunidad de Amara.org",
    " Subtitulos por la comunidad de Amara.org"
    " Más información www.alimmenta.com",
    " www.mooji.org",
  ],
  "gl": [
    " Subtítulos realizados por la comunidad de Amara.org"
  ],
  "pt": [
    " Legendas pela comunidade Amara.org",
    " Legendas pela comunidade de Amara.org",
    " Legendas pela comunidade do Amara.org",
    " Legendas pela comunidade das Amara.org",
    " Transcrição e Legendas pela comunidade de Amara.org"
  ],
  "la": [
    " Sottotitoli creati dalla comunità Amara.org",
    " Sous-titres réalisés para la communauté d'Amara.org"
  ],
  "ln": [
    " Sous-titres réalisés para la communauté d'Amara.org"
  ],
  "pl": [
    " Napisy stworzone przez społeczność Amara.org",
    " Napisy wykonane przez społeczność Amara.org",
    " Zdjęcia i napisy stworzone przez społeczność Amara.org",
    " napisy stworzone przez społeczność Amara.org",
    " Tłumaczenie i napisy stworzone przez społeczność Amara.org",
    " Napisy stworzone przez społeczności Amara.org",
    " Tłumaczenie stworzone przez społeczność Amara.org",
    " Napisy robione przez społeczność Amara.org"
    " www.multi-moto.eu",
  ],
  "ru": [
    " Редактор субтитров А.Синецкая Корректор А.Егорова"
  ],
  "tr": [
    " Yorumlarınızıza abone olmayı unutmayın.",
  ],
  "su": [
    " Sottotitoli creati dalla comunità Amara.org"
  ],
  "zh": [
    "字幕由Amara.org社区提供",
    "小編字幕由Amara.org社區提供",
    "请不吝点赞 订阅 转发 打赏支持明镜与点点栏目"
  ]
}

# 如果text在filter_text中有相同的句子
def filter(text, language):
    if language in filter_text:
        for filter_text_item in filter_text[language]:
            if filter_text_item in text:
                return True
    return False


MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

st.set_page_config(
        page_title="speech to text",
        layout="wide",
)

@st.cache_resource
def get_openai_client(url, api_key):
    client = OpenAI(base_url=url, api_key=api_key)
    return client

def stt_page():
    st.title("speech to text")
    st.caption("based on our state-of-the-art open source large-v2 Whisper model")
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


    if "button_active" not in st.session_state:
        st.session_state.button_active = False

    src_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open(os.path.join(src_path, 'config/default.json'), 'r',encoding='utf-8') as f:
        config_defalut = json.load(f)
    language_list = config_defalut["stt"]["language"]

    client = get_openai_client(base_url, api_key)
    audio_file = None
    
    option = st.radio("Input methods:", ("Recording", "uploading"),horizontal=True,index=1)
    if option == "Recording":
        audio_bytes = audio_recorder()
        if audio_bytes:
            st.text("Recorded audio")
            st.audio(audio_bytes, format="audio/wav")
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "audio.wav"

    else:
        st.write("ttention! Currently, the OpenAI interface only supports up to 25MB.")
        audio_file= st.file_uploader("Upload audio file", type=["wav","mp3","webm","mpeg","mpga"])
        if audio_file:
            if audio_file.size > MAX_FILE_SIZE:
                st.error("The uploaded file is too large. Please upload an audio smaller than 25MB.")
    # 语言选择  
    language = st.selectbox('language(To add other languages through a configuration file.)', language_list, key='language')

    def whisper_online(audio_file,language):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text",
            language=language
        )
        return transcript
    
    # 开始转换按钮
    if st.button("transcribe"):
        if audio_file:
            with st.spinner('please wait...'):
                try:
                    transcript = whisper_online(audio_file,language)
                    if filter(transcript, "zh") == False:
                        st.write(transcript)
                    else:
                        st.write("null")
                except Exception as e:
                    st.error(e)
                    st.stop()
        else:
            st.warning("Please upload the audio file first.")

if __name__ == "__main__":
    stt_page()
