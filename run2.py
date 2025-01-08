import os
import edge_tts
import streamlit as st

# 设置输出目录
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Streamlit 页面标题
st.sidebar.title("《Hello,广西》文本转语音")

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
        "en-US-AnaNeural",
        "en-US-ChristopherNeural",
        "en-US-EricNeural",
        "en-US-MichelleNeural",
        "en-US-RogerNeural",
        "en-US-SteffanNeural",
        "en-US-AvaMultilingualNeural",
    ]
voice = st.sidebar.selectbox("选择音色", voices)

# 语速设置
rate = st.sidebar.slider("语速调节", min_value=-100, max_value=100, value=0, step=10)

# 用户输入内容
input_text = st.text_area("请输入内容：")

# 初始化 edge-tts
async def text_to_speech(text, output_file):
    try:
        # 使用 rate 参数来控制语速
        tts = edge_tts.Communicate(text, voice=voice, rate=str(rate))
        await tts.save(output_file)
    except edge_tts.exceptions.NoAudioReceived:
        st.warning(f"无法生成音频: {text}")

# 生成语音文件的函数
async def generate_audio():
    if input_text:
        output_file = os.path.join(output_dir, "output.mp3")
        await text_to_speech(input_text, output_file)
        return output_file
    else:
        st.warning("请输入内容。")
        return None

# 开始生成音频文件
if st.button("生成语音文件"):
    with st.spinner("生成中，请稍候..."):
        import asyncio
        output_file = asyncio.run(generate_audio())

        if output_file and os.path.exists(output_file):
            st.success("语音文件生成完毕！")
            st.audio(output_file)
            st.markdown(f"<p style='font-size: 16px;'><strong>文本:</strong> {input_text}</p>", unsafe_allow_html=True)

            # 下载链接
            with open(output_file, 'rb') as f:
                st.download_button("下载语音文件", f, "output.mp3", "audio/mpeg")

# 侧边栏底部反馈信息
st.sidebar.markdown("---")
st.sidebar.write("www.helloguangxi.online")
