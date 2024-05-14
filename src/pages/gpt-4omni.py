from openai import OpenAI
import streamlit as st
import json
import os,sys
import base64
import requests


@st.cache_resource
def get_openai_client(url, api_key):
    '''
    使用了缓存，当参数不变时，不会重复创建client
    '''
    client = OpenAI(base_url=url, api_key=api_key)
    return client

def vision_page():
    st.title("GPT-4o ")
    st.caption("it accepts as input any combination of text, audio, and image and generates any combination of text, audio, and image outputs")
    st.caption("它接受文本、音频和图像的任何组合作为输入，并生成文本、音频和图像的任何组合作为输出")
    st.caption("！目前gpt-4o 的api接口还不支持音频输入，只能传入图片，所有就和gpt 4v差不多了")
    st.caption("！直接问它居然自己都不知道自己是gpt-4o,然后去官网的playground试一下也是一样，就不是我请求的问题了")
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

    st.session_state['model_list'] = config_defalut["completions"]["models"]

    upload_images = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"],label_visibility="collapsed")
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    bytes_data = None
    if upload_images is not None:
        if upload_images.size > MAX_FILE_SIZE:
            st.error("The uploaded file is too large. Please upload an image smaller than 5MB.")
        else:
            #image = Image.open(upload_images)
            bytes_data = upload_images.getvalue()
            st.image(bytes_data, caption=upload_images.name, width=200)

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                try: 
                    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                    if bytes_data is not None:
                    #res = post_gpt4v(base_url,api_key,bytes_data,prompt)
                        base64_image = base64.b64encode(bytes_data).decode("utf-8")
                        payload = {
                            "model": "gpt-4o",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": prompt,
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                        },
                                    ],
                                },
                            ],
                            "max_tokens": 5000,
                        }
                    else:
                        payload = {
                            "model": "gpt-4o",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt,
                                },
                            ],
                            "max_tokens": 300,
                        }
                    if base_url.endswith('/'):
                        base_url = base_url[:-1]
                    response = requests.post(
                        base_url + "/chat/completions", headers=headers, json=payload
                    )

                    # 检查状态码是否正常，不正常会触发异常
                    response.raise_for_status()
                    print(response.json())
                    result = response.json()["choices"][0]["message"]["content"]
                    st.markdown(result)
                except Exception as e:
                    st.error(e)
                    st.stop()

                

if __name__ == "__main__":
    vision_page()