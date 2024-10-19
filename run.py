import os
import pandas as pd
import edge_tts
import streamlit as st
import zipfile
import io
from pydub import AudioSegment

# 设置输出目录
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Streamlit 页面标题
st.sidebar.title("文本转语音")

# 选择语言
language = st.sidebar.selectbox("选择语言", ["中文", "英文"])

# 根据选择的语言提供相应的音色
if language == "中文":
    voices = [
        "zh-CN-YunyangNeural",
        "zh-CN-XiaoyiNeural",
        "zh-CN-XiaoxiaoNeural",
    ]
else:
    voices = [
        "en-US-AriaNeural",
        "en-US-JennyNeural",
        "en-US-GuyNeural",
    ]
voice = st.sidebar.selectbox("选择音色", voices)

# 选择单词或句子
input_type = st.sidebar.selectbox("选择字号", ["大号", "正常"])

# 用户输入内容
input_text = st.text_area("请输入内容（每行一个）:")

# 初始化 edge-tts
async def text_to_speech(text):
    try:
        tts = edge_tts.Communicate(text, voice=voice)
        return tts.save_to_memory()
    except edge_tts.exceptions.NoAudioReceived:
        st.warning(f"无法生成音频: {text}")

# 处理输入的内容，生成单个的音频文件并合并
async def generate_and_combine_audio_files(words):
    combined_audio = AudioSegment.empty()
    for word in words:
        if word.strip():  # 确保不处理空行
            audio_bytes = await text_to_speech(word.strip())
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            combined_audio += audio_segment + AudioSegment.silent(duration=1000)  # 添加1秒间隔
    return combined_audio

# 开始生成音频文件
if st.button("生成语音文件"):
    if input_text:
        words = input_text.splitlines()
        with st.spinner("生成中，请稍候..."):
            import asyncio
            combined_audio = asyncio.run(generate_and_combine_audio_files(words))
        st.success("语音文件生成完毕！")

        # 提供试听功能和显示文本
        for word in words:
            if word.strip():
                st.markdown(f"<p style='font-size: 16px;'><strong>{word.strip()}</strong></p>", unsafe_allow_html=True)

        # 下载链接
        if combined_audio:
            combined_audio.export("combined_audio.mp3", format="mp3")
            with open("combined_audio.mp3", 'rb') as f:
                st.download_button("下载为单个音频", f, "combined_audio.mp3", "audio/mp3")
    else:
        st.warning("请输入内容。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write(" Made by：川哥 ")
