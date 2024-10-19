import os
import pandas as pd
import edge_tts
import streamlit as st
import zipfile
import io
from IPython.display import Audio

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
async def text_to_speech(text, output_file):
    try:
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(output_file)
    except edge_tts.exceptions.NoAudioReceived:
        st.warning(f"无法生成音频: {text}")

# 处理输入的内容，生成语音文件
async def generate_audio_files(words):
    audio_files = []
    for word in words:
        if word.strip():  # 确保不处理空行
            filename = word.strip().replace(" ", "_")  # 替换空格
            output_file = os.path.join(output_dir, f"{filename}.mp3")
            await text_to_speech(word.strip(), output_file)
            if os.path.exists(output_file):  # 确保文件成功生成
                audio_files.append((output_file, word.strip()))  # 保存文件和对应文本
    return audio_files

# 生成单个 MP3 文件并提供试听和下载
async def generate_single_mp3(input_text):
    output_file = os.path.join(output_dir, "combined.mp3")
    tts = edge_tts.Communicate(input_text, voice=voice)
    await tts.save(output_file)
    return output_file

# 开始生成音频文件
if st.button("生成语音文件"):
    if input_text:
        words = input_text.splitlines()
        with st.spinner("生成中，请稍候..."):
            import asyncio
            # 如果输入内容有多行，则生成多个音频文件并合并为一个 MP3
            if len(words) > 1:
                audio_files = asyncio.run(generate_audio_files(words))
                combined_text = '\n'.join([text for _, text in audio_files])
                output_file = await generate_single_mp3(combined_text)
            else:
                output_file = await generate_single_mp3(input_text)
        st.success("语音文件生成完毕！")

        # 设置字体大小
        font_size = "16px" if input_type == "正常" else "50px"

        # 提供试听功能
        st.audio(output_file)

        # 下载链接
        with open(output_file, 'rb') as f:
            st.download_button("下载音频文件", f, "combined.mp3", "audio/mpeg")
    else:
        st.warning("请输入内容。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write(" Made by：川哥 ")
