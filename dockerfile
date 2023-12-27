FROM robd003/python3.10:latest

RUN pip install --no-cache-dir openai>=1.3.6 streamlit tiktoken audio_recorder_streamlit

WORKDIR /app
# 将src文件夹复制到app
COPY src/ /app

EXPOSE 10000

CMD ["streamlit", "run", "home.py", "--server.port", "10000"]