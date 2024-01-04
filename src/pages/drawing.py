from openai import OpenAI
import streamlit as st


@st.cache_resource
def get_openai_client(url, api_key):
    '''
    使用了缓存，当参数不变时，不会重复创建client
    '''
    client = OpenAI(base_url=url, api_key=api_key)
    return client


def drawing_page():
    st.title("Drawing")
    st.caption("use DALL·E 3 to draw images")

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


    image_size = st.selectbox('image size', ["1024x1024", "1024x1792","1792x1024"], key='image_size')
    quality = st.selectbox('quality', ["standard", "hd"], key='quality')
    num_images = st.selectbox('num_images （dall-e-3 only n=1）', [1], key='num_images')
    
    if prompt := st.chat_input("prompt"):
        st.chat_message("user").write(prompt)
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                try:
                    client = get_openai_client(base_url, api_key)
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=image_size,
                        quality=quality,
                        n=num_images,
                    )
                    
                    #print(response)
                    for image in response.data:
                        image_url = image.url
                        revised_prompt = image.revised_prompt
                        st.image(image_url, caption=prompt, width=200)

                        # 添加下载链接
                        download_link = f'<a href="{image_url}" download>Download</a>'
                        st.markdown(download_link, unsafe_allow_html=True)
                        # 显示提示词
                        st.write("revised_prompt : "+ revised_prompt)
                except Exception as e:
                    st.error(e)
                    st.stop()



if __name__ == "__main__":
    drawing_page()