import os
import pandas as pd
import edge_tts
import streamlit as st
import zipfile
import io
from pydub import AudioSegment
from pydub.playback import play

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
                audio_files.append(output_file)  # 保存文件
    return audio_files

# 合并音频文件
def merge_audio_files(audio_files):
    combined = AudioSegment.empty()
    for audio_file in audio_files:
        sound = AudioSegment.from_mp3(audio_file)
        combined += sound + AudioSegment.silent(duration=1000)  # 每个音频之间1秒的间隔
    combined_file = os.path.join(output_dir, "combined_audio.mp3")
    combined.export(combined_file, format="mp3")
    return combined_file

# 开始生成音频文件
if st.button("生成语音文件"):
    if input_text:
        words = input_text.splitlines()
        with st.spinner("生成中，请稍候..."):
            import asyncio
            audio_files = asyncio.run(generate_audio_files(words))
            st.success("语音文件生成完毕！")

        # 设置字体大小
        font_size = "16px" if input_type == "正常" else "50px"

        # 提供试听功能和显示文本
        for file in audio_files:
            st.audio(file)
            st.markdown(f"<p style='font-size: {font_size};'><strong>{os.path.basename(file).replace('_', ' ')}</strong></p>", unsafe_allow_html=True)

        # 下载所有音频文件的压缩包
        if audio_files:  # 确保有音频文件
            zip_file_path = "audio_files.zip"
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for file in audio_files:
                    zipf.write(file, os.path.basename(file))
            with open(zip_file_path, 'rb') as f:
                st.download_button("下载所有音频文件", f, "audio_files.zip", "application/zip")

        # 合并音频文件并提供下载
        combined_audio_file = merge_audio_files(audio_files)
        with open(combined_audio_file, 'rb') as f:
            st.download_button("下载为单个音频", f, "combined_audio.mp3", "audio/mpeg")

    else:
        st.warning("请输入内容。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write(" Made by：川哥 ")
