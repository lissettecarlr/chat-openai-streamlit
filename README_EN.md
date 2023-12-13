# chat-openai-streamlit
An interactive web application based on streamlit that supports various language models with openai interface.

## 0. Objective

- [x] Support the Chat Completions API page for text conversations
- [x] Support the Vision page for image understanding

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
* models: The models displayed in the dropdown menu on the homepage
* num_tokens: Whether to display the number of tokens consumed after each conversation
* use_time: Whether to display the time taken after each conversation