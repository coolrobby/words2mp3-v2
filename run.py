import os
import edge_tts
import streamlit as st
import zipfile
import io

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

# 用户输入内容
input_text = st.text_area("请输入内容：")

# 初始化 edge-tts
async def text_to_speech(text, output_file):
    try:
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(output_file)
    except edge_tts.exceptions.NoAudioReceived:
        st.warning(f"无法生成音频: {text}")

# 生成语音文件
if st.button("生成语音文件"):
    if input_text:
        output_file = os.path.join(output_dir, "output.mp3")
        with st.spinner("生成中，请稍候..."):
            import asyncio
            await text_to_speech(input_text, output_file)

        st.success("语音文件生成完毕！")

        # 提供试听功能
        if os.path.exists(output_file):
            st.audio(output_file)
            st.markdown(f"<p style='font-size: 16px;'><strong>文本:</strong> {input_text}</p>", unsafe_allow_html=True)

            # 下载链接
            with open(output_file, 'rb') as f:
                st.download_button("下载语音文件", f, "output.mp3", "audio/mpeg")
    else:
        st.warning("请输入内容。")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write(" Made by：川哥 ")
