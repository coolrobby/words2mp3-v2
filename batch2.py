import asyncio  # 确保导入 asyncio
import os
import pandas as pd
import edge_tts
import streamlit as st
import zipfile
from io import BytesIO
import pyperclip  # 用于复制内容到剪贴板

# 设置输出目录
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Streamlit 页面标题
st.sidebar.title("Words2mp3")

# 默认使用英文语音
voices = [
    "en-US-AriaNeural",  # 默认选择此音色
    "en-US-AvaMultilingualNeural",
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
        rate_str = f"{rate}%"  # 将 rate 转换为百分比格式
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
def process_excel_and_generate_audio(file_path, selected_group):
    df = read_excel(file_path)
    if df is not None:
        # 获取每个组及对应的单词和解释
        groups = df.groupby(df.columns[0])
        audio_files = []
        if selected_group in groups:
            group_data = groups.get_group(selected_group)
            # 检查是否有足够的列
            if group_data.shape[1] >= 4:  # 至少有 4 列（组名、其它、单词、解释）
                words = group_data.iloc[:, 1].tolist()  # 使用第二列数据生成语音
                output_file = asyncio.run(generate_audio_for_group(selected_group, words))
                if output_file and os.path.exists(output_file):
                    audio_files.append(output_file)
                    # 显示组名、单词和解释
                    st.subheader(f"组名: {selected_group}")
                    content_to_copy = ""
                    for _, row in group_data.iterrows():
                        word = row[2]  # 第三列显示单词
                        explanation = row[3]  # 第四列显示解释
                        st.markdown(f"<h2>{word}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p>{explanation}</p><hr>", unsafe_allow_html=True)
                        content_to_copy += f"单词: {word}\n解释: {explanation}\n\n"
                    
                    # “复制”按钮
                    if st.button("复制"):
                        pyperclip.copy(content_to_copy)  # 复制内容到剪贴板
                        st.success("内容已复制到剪贴板！")
                    
                    st.audio(output_file, format='audio/mp3')
                    st.download_button(f"下载 {selected_group} 语音文件", output_file, f"{selected_group}.mp3", "audio/mpeg")
        return audio_files
    return []

# 读取 Excel 文件并显示组列表
def display_group_list(file_path):
    df = read_excel(file_path)
    if df is not None:
        groups = df.groupby(df.columns[0]).groups.keys()
        return list(groups)
    return []

# 开始处理 Excel 文件
if __name__ == "__main__":
    file_path = "list.xlsx"
    
    # 显示组选择
    available_groups = display_group_list(file_path)
    selected_group = st.sidebar.selectbox("选择组", available_groups, index=0)  # 只能选择一个组
    
    if selected_group:
        # 自动显示内容和生成语音
        with st.spinner("加载中..."):
            audio_files = process_excel_and_generate_audio(file_path, selected_group)

    # 生成按钮
    if selected_group and st.button("生成语音文件"):
        with st.spinner("生成中，请稍候..."):
            if os.path.exists(file_path):
                audio_files = process_excel_and_generate_audio(file_path, selected_group)
                
                if audio_files:
                    st.success("语音文件生成完毕！")

                # 提供下载 ZIP 文件（如果有多个文件）
                zip_file = create_zip_file(audio_files)
                st.download_button("下载所有语音文件 (ZIP)", zip_file, "audio_files.zip", "application/zip")
            else:
                st.warning("找不到 list.xlsx 文件，请确保文件存在。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write("<h2> 使用说明</h2><p>按组生成单词读音，每个单词读3遍，每组一个mp3文件。选择音色，选择语速后，点击生成语音即可。可以单独下载每个音频，也可以打包下载。川哥专用。</p><p>Made by：川哥</p>", unsafe_allow_html=True)
