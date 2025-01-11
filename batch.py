import asyncio  # 确保导入 asyncio
import os
import pandas as pd
import edge_tts
import streamlit as st
import zipfile
from io import BytesIO

# 设置输出目录
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Streamlit 页面标题
st.sidebar.title("Words2mp3")

# 默认使用英文语音
voices = [
    "en-US-AvaMultilingualNeural",  # 默认选择此音色
    "en-US-AriaNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural",
]

# 语音选择
voice = st.sidebar.selectbox("选择音色", voices)

# 语速设置，默认值为 -20%
rate = st.sidebar.slider("语速调节", min_value=-100, max_value=100, value=-30, step=10)

# 读取 Excel 文件
def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()  # 去除列名空格
        return df
    except Exception as e:
        st.error(f"读取 Excel 文件时出错: {e}")
        return None

# 初始化 edge-tts
async def text_to_speech(text, output_file):
    try:
        # 将 rate 转换为百分比格式，并确保它符合 edge_tts 的要求（例如 +10%, -10% 等）
        rate_str = f"{rate}%"  # 直接将 rate 加上百分号
        tts = edge_tts.Communicate(text, voice=voice, rate=rate_str)
        await tts.save(output_file)
    except edge_tts.exceptions.NoAudioReceived:
        st.warning(f"无法生成音频: {text}")
    except ValueError as e:
        st.error(f"生成语音时出错: {e}")

# 为每组生成音频文件的函数
async def generate_audio_for_group(group_name, words):
    output_file = os.path.join(output_dir, f"{group_name}.mp3")
    text = " ".join(words)  # 将单词合并为一个字符串
    await text_to_speech(text, output_file)
    return output_file

# 生成 ZIP 文件的函数
def create_zip_file(files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            zip_file.write(file, os.path.basename(file))
    zip_buffer.seek(0)
    return zip_buffer

# 读取 list.xlsx 文件并生成音频
def process_excel_and_generate_audio(file_path):
    df = read_excel(file_path)
    if df is not None:
        # 获取每个组及对应的单词
        groups = df.groupby(df.columns[0])
        audio_files = []
        for group_name, group_data in groups:
            words = group_data.iloc[:, 1].tolist()  # 获取单词列
            output_file = asyncio.run(generate_audio_for_group(group_name, words))
            if output_file and os.path.exists(output_file):
                audio_files.append(output_file)
                # 显示组名和单词
                st.subheader(f"组名: {group_name}")
                st.write("单词: " + ", ".join(words))
                st.audio(output_file, format='audio/mp3')
                st.download_button(f"下载 {group_name} 语音文件", output_file, f"{group_name}.mp3", "audio/mpeg")
        return audio_files
    return []

# 开始处理 Excel 文件
if st.button("生成语音文件"):
    with st.spinner("生成中，请稍候..."):
        # 确保文件存在
        file_path = "list.xlsx"
        if os.path.exists(file_path):
            audio_files = process_excel_and_generate_audio(file_path)
            
            if audio_files:
                st.success("语音文件生成完毕！")

                # 提供批量下载 ZIP 文件
                zip_file = create_zip_file(audio_files)
                st.download_button("下载所有语音文件 (ZIP)", zip_file, "audio_files.zip", "application/zip")
            else:
                st.warning("未能生成音频文件，请检查 Excel 文件内容。")
        else:
            st.warning("找不到 list.xlsx 文件，请确保文件存在。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write("<h2> 使用说明</h2><p>按组生成单词读音，每个单词读3遍，每组一个mp3文件。选择音色，选择语速后，点击生成语音即可。可以单独下载每个音频，也可以打包下载。</p><p>Made by：川哥</p>", unsafe_allow_html=True)

