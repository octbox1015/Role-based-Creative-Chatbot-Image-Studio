import streamlit as st
import base64

# ===========================
# OpenAI SDK 初始化（兼容新旧版本）
# ===========================
try:
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    use_new_sdk = True
except ImportError:
    import openai
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    use_new_sdk = False

# ===========================
# 页面配置
# ===========================
st.set_page_config(
    page_title="🎭 Role-based Creative Chatbot + Image Studio",
    page_icon="🎨",
    layout="wide"
)

st.title("🎭 Role-based Creative Chatbot + Image Studio")
st.markdown("Chat with AI in different creative roles and generate images! 🎨")

# ===========================
# 角色选择
# ===========================
roles = {
    "Film Critic": "You are a sharp and insightful film critic with expertise in film analysis and visual storytelling.",
    "Fashion Consultant": "You are an energetic fashion consultant giving trendy and personalized style advice.",
    "Dance Coach": "You are a professional dance coach, giving detailed guidance on rhythm, moves, and stage performance.",
    "Digital Artist": "You are a digital artist, providing vivid, imaginative prompts for visual art and image creation.",
    "Creative Writing Mentor": "You are a creative writing mentor helping craft emotional, vivid, and expressive writing."
}

st.sidebar.header("🧠 Choose a Role")
role = st.sidebar.selectbox("Select a role for the chatbot:", list(roles.keys()))
role_prompt = roles[role]

st.sidebar.markdown("---")
enable_image = st.sidebar.checkbox("Enable Image Generation")

# ===========================
# 聊天功能
# ===========================
st.subheader(f"💬 Chat with {role}")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_area("Enter your message here:", height=120)

if st.button("Send Message"):
    if user_input.strip() != "":
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            if use_new_sdk:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": role_prompt},
                        *st.session_state.chat_history
                    ]
                )
                ai_reply = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": role_prompt},
                        *st.session_state.chat_history
                    ]
                )
                ai_reply = response["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

# 显示聊天记录
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**🧍 You:** {chat['content']}")
    else:
        st.markdown(f"**🎭 {role}:** {chat['content']}")

# ===========================
# 图片生成功能
# ===========================
st.markdown("---")
st.subheader("🎨 Image Studio")

image_prompt = st.text_input("Describe your image idea (e.g., 'A dreamy sunset over a neon city skyline'):")

if st.button("Generate Image"):
    if image_prompt.strip() != "":
        if enable_image:
            with st.spinner("Generating image..."):
                if use_new_sdk:
                    result = client.images.generate(
                        model="gpt-image-1",
                        prompt=image_prompt,
                        size="1024x1024"
                    )
                    image_base64 = result.data[0].b64_json
                    image_bytes = base64.b64decode(image_base64)
                else:
                    result = openai.Image.create(
                        model="gpt-image-1",
                        prompt=image_prompt,
                        size="1024x1024"
                    )
                    image_url = result["data"][0]["url"]
                    st.image(image_url, caption="🎨 AI-generated image", use_container_width=True)
                    image_bytes = None

                if image_bytes:
                    st.image(image_bytes, caption="🎨 AI-generated image", use_container_width=True)

# ===========================
# Footer
# ===========================
st.markdown("---")
st.caption("Created with ❤️ · Powered by OpenAI & Streamlit")
