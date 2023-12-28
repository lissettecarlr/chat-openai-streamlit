[English](./README_EN.md) | [中文](./README.md) |

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![OpenAI](https://camo.githubusercontent.com/ea872adb9aba9cf6b4e976262f6d4b83b97972d0d5a7abccfde68eb2ae55325f/68747470733a2f2f696d672e736869656c64732e696f2f7374617469632f76313f7374796c653d666f722d7468652d6261646765266d6573736167653d4f70656e414926636f6c6f723d343132393931266c6f676f3d4f70656e4149266c6f676f436f6c6f723d464646464646266c6162656c3d)


[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chat-openai-app.streamlit.app/)


# chat-openai-streamlit
Web application for various models' dialogue based on the OpenAI API, written in Streamlit,assistants,speech to text

## 0. Objective

- [x] Support the Chat Completions API page for text conversations
- [x] Support the Vision page for image understanding
- [x] A page that supports Image generation for generating images
- [x] Assistants page
- [x] Support the page for language to text
- [x] Support the page for text to speech

Other added features

- [x] Display the time taken after each conversation on the chat page (controlled by the configuration file)
- [x] Display the number of tokens consumed after each conversation on the chat page (controlled by the configuration file)

## 1. Installation

```bash
pip install -r requirements.txt
```

## 2. Running

```bash
cd src
streamlit run chat.py --server.port 1234
```

## 3. Screenshots
The following screenshots may not be the latest. You can see the latest examples [here]().


![1](./file/1.gif)


## 4. Configuration File

The default parameter configuration file is located at `src/config/default.yaml`. Here are the custom parameters explained:
* models: The models displayed in the dropdown menu on the chat page
* num_tokens: Whether to display the number of tokens consumed after each conversation
* use_time: Whether to display the time taken after each conversation