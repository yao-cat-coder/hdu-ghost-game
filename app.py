import streamlit as st
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": st.secrets["NEON_HOST"],
    "port": st.secrets["NEON_PORT"],
    "user": st.secrets["NEON_USER"],
    "password": st.secrets["NEON_PASSWORD"],
    "dbname": st.secrets["NEON_DB"],
    "sslmode": "require",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_name TEXT NOT NULL,
            password TEXT NOT NULL,
            location TEXT NOT NULL,
            name TEXT NOT NULL,
            score INT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def add_review(user_name, password, location, name, score, comment):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO reviews (user_name, password, location, name, score, comment)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_name, password, location, name, int(score), comment))
    conn.commit()
    cur.close()
    conn.close()

def get_reviews(location=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if location:
        cur.execute("SELECT * FROM reviews WHERE location = %s ORDER BY id DESC", (location,))
    else:
        cur.execute("SELECT * FROM reviews ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def delete_review(review_id, user_name, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id = %s AND user_name = %s AND password = %s",
                (review_id, user_name, password))
    rows_deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return rows_deleted > 0
def admin_delete_review(review_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    cur.close()
    conn.close()
    return deleted

st.set_page_config(page_title="杭电奇妙夜", page_icon="🏰", layout="wide", initial_sidebar_state="expanded")
all_reviews = get_reviews()
with st.sidebar:
    st.subheader("开发者验证")
    dev_pwd = st.text_input("开发者密码", type="password")
    if st.button("确认验证"):
        if dev_pwd == st.secrets["PWD"]:
            st.session_state.dev_auth = True
            st.success("✅ 验证成功")
        else:
            st.session_state.dev_auth = False
            st.error("❌ 密码错误")

if st.session_state.get("dev_auth", False):
    if st.sidebar.checkbox("开发者查看全部评价"):
        st.subheader("📋数据库里所有评价")
        st.dataframe(all_reviews, use_container_width=True)
        st.markdown("### 🗑️ 管理员删除评论")
        del_id = st.number_input("输入要删除的评论ID", min_value=1, step=1)
        if st.button("确认删除这条", type="primary"):
            success = admin_delete_review(del_id)
            if success:
                st.success(f"✅ ID={del_id} 的评论删除成功！刷新页面看效果")
            else:
                st.error(f"❌ 找不到ID={del_id}这条评论")

#init_db()

if "user_name" not in st.session_state:
    st.session_state.user_name = "神秘食客"
    
be_home = "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1920&auto=format&fit=crop"
be_food = "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?q=80&w=1920&auto=format&fit=crop"
be_ghost = "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=1920&auto=format&fit=crop"

st.sidebar.header("导航栏")
user_name = st.sidebar.text_input("你的昵称:", value=st.session_state.user_name)
password = st.sidebar.text_input("密码", type="password")

if not user_name or not password:
    st.sidebar.warning("⚠️ 请填写昵称和密码，否则无法发布/删除评价")

st.session_state.user_name = user_name
st.session_state.password = password

page = st.sidebar.radio("选择频道", ["🏠 首页大厅", "美食频道", "怪谈游戏"])

if page == "🏠 首页大厅":
    current_bg = be_home
elif page == "美食频道":
    current_bg = be_food
else:
    current_bg = be_ghost

page_bg_css = f"""
<style>
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
.stDeployButton {{display: none !important;}}
[data-testid="stStatusWidget"] {{display: none !important;}}
[data-testid="manage-app-button"] {{display: none !important;}}
header {{ background-color: rgba(20, 20, 30, 0.6) !important; }}
[data-testid="stAppViewContainer"] {{
    background-image: url("{current_bg}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
[data-testid="stAppViewContainer"] > section {{
    background-color: rgba(15, 15, 26, 0.85) !important;
}}
p, span, label, h1, h2, h3, div:not([data-baseweb="select"]) {{
    color: #ffffff !important;
}}
[data-testid="stSidebar"] {{
    background-color: rgba(20, 20, 30, 0.95) !important;
    border-right: 1px solid #555;
}}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {{
    color: #000000 !important;
    background-color: #ffffff !important;
}}
.stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder {{
    color: #666666 !important;
}}
.stButton>button, .stFormSubmitButton>button {{
    color: #ffffff !important;
}}
div[data-baseweb="select"] > div {{
    color: #000000 !important;
    background-color: #ffffff !important;
}}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

if page == "🏠 首页大厅":
    st.title("🍜 杭电美食城 AI 推荐馆")
    st.info("👈 找不到功能入口？请点击左上角的 `>>` 箭头打开导航栏，选择【美食频道】或【怪谈游戏】！")
    st.write("不知道吃什么？告诉我你的口味，我让AI给你用最真实的评价给你推荐")
    st.divider()
    if len(all_reviews) > 0:
        context = "以下是真实食客的评价：\n"
        for r in all_reviews:
            context += f"- 区域：{r.get('location', '未知')}，店名：{r.get('name', '未知')}，评分：{r.get('score', '未知')}，评价：{r.get('comment', '无')}\n"
    else:
        context = ""
    
    col1, col2 = st.columns(2)
    with col1:
        user_want = st.text_input("你想吃点什么😊，你的口味是什么❓（辣的、清淡、预算20）")
    with col2:
        st.write("💡 不知道填什么？试试这些：")
        st.info("👉 想要吃辣，预算20以内\n\n👉 想吃清淡的面食，要好評最多的")
    
    submit = st.button("🤖让AI帮我选一家！", use_container_width=True)
    if submit:
        if user_want != "":
            if len(all_reviews) == 0:
                st.warning("⚠️ 抱歉，目前大家的评价库还是空的，AI 拒绝提供不存在的推荐。快点击左侧【美食频道】写下第一条评价吧！")
            else:
                with st.spinner("🤖AI正在翻阅大家的评价，为你疯狂挑选中... "):
                    client = OpenAI(api_key=st.secrets["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")
                    prompt = f"""
                    你是一个极其严格的杭电美食推荐官。同学的需求是：{user_want}。
                    这是你手头的真实评价数据：{context}
                    【核心执行逻辑】（必须严格遵守）：
                    1.请你现在后台仔细核对：上述真实评价里的菜品和口味，是否真的符合同学的需求；
                    2.如果数据里写的和同学的需求不匹配，必须无情拒绝，直接回答：“抱歉，目前大家的真实评价里没有符合你口味的店铺哦”，绝不允许自己不顾需求和实际强行推荐！
                    3.只有当真实评价确实符合同学需求时，你才能用热情、幽默的的方式以小红书的风格输出推荐，要求60字以内
                    """
                    response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
                    ai_reply = response.choices[0].message.content
                    st.success("✨AI为你找到了绝佳选择：")
                    st.markdown(ai_reply)
                    st.balloons()
        else:
            st.warning("⚠️请先输入你的口味需求哦！")

elif page == "美食频道":
    st.header("🍜 美食推荐区")
    st.write("你可以在这里评价周围美食")

    with st.form("my_view_form"):
        st.subheader("发布你的专属评价")
        location = st.selectbox("选择区域", ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍味堂三层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"])
        food_name = st.text_input("美食/店名")
        score = st.slider("打分（1-10分）", 1, 10, 5)
        comment = st.text_area("写下你的真实感受")
        submitted = st.form_submit_button("提交评价")
    
    if submitted:
        if user_name != "" and password != "":
            if food_name != "" and comment != "":
                add_review(user_name, password, location, food_name, score, comment)
                st.success("✅评价成功")
                st.caption("💡 发布评价时使用的昵称和密码，是后续删除本条评论的凭证，请妥善保存。")
                st.rerun()
            else:
                st.warning("⚠️店名和评价不能为空哦！")
        else:
            st.warning("⚠️ 昵称和密码不能为空哦！否则以后无法删除！")
        
    st.divider()
    st.subheader("🔥大家怎么说")

    if len(all_reviews) == 0:
        st.info("大家还没有评价快来抢沙发🛋️")
    else:
        regions = ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍味堂三层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"]
        tabs = st.tabs(regions)
        for tab, region in zip(tabs, regions):
            with tab:
                region_reviews = [r for r in all_reviews if r.get("location") == region]
                if len(region_reviews) == 0:
                    st.write("这个区域目前空空如也，快来抢首评论！")
                else:
                    for index, r in enumerate(region_reviews):
                        with st.expander(f"📍{r['name']}——⭐{r['score']}/10"):
                            st.write(f"发布者:{r.get('user_name', '匿名')}")
                            st.write(r['comment'])
                        
                            if st.button("🗑️ 删除这条评价", key=f"del_{region}_{index}"):
                                if delete_review(r['id'], user_name, password):
                                    st.success("✅ 删除成功！")
                                    st.rerun()        
                                else:
                                    st.error("❌ 删除失败！请检查侧边栏的【昵称】和【密码】是否与你发评论时一致。")
elif page == "怪谈游戏":
    st.header("👻 怪谈游戏区")
    st.write("欢迎来到受诅咒的杭电美食城")
    map_location = ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍味堂三层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"]
    current_location = st.radio("选择探索地区", map_location, horizontal=True)
    if "sanity" not in st.session_state:
        st.session_state.sanity = 100
    sanity = st.session_state.sanity
    if sanity > 60:
        st.success(f"🧠 当前理智值：{sanity}，精神稳定")
    elif sanity > 30:
        st.warning(f"🧠 当前理智值：{sanity}，你开始感到不安……")
    else:
        st.error(f"🧠 当前理智值：{sanity}，同化！你已经被诡异吞噬！")
    recent_reviews = []
    for r in all_reviews:
        if r.get("location") == current_location:
            recent_reviews.append(f"店名：{r['name']},评价:{r['comment']}")
        
    if len(recent_reviews) > 0:
        reviews_context = "以下是食客在这里留下的真实线索：" + ";".join(recent_reviews)
        st.info(f"已收集到{len(recent_reviews)}条关于【{current_location}】的真实线索！")
    else:
        reviews_context = "目前还没有人在这里留下评价，这里一片死寂"
        st.warning(f"⚠️【{current_location}】暂无真实评价AI只能瞎编了。")
    
    system_prompt = f"""
    你是一个克苏鲁风格的怪谈游戏主持人。
    玩家当前理智值：{st.session_state.sanity}。
    规则：
    1.玩家处在【{current_location}】，参考线索：{reviews_context}
    2.判断玩家行为：如果行为违反规则、危险、作死，回复时第一行写【-5】，然后写剧情；安全行为不扣理智，不要写【-5】
    3.理智低于等于30，玩家同化，游戏结束，不能继续交互
    4.生成50字左右诡异场景，附带十条矛盾怪谈规则
    5.背景：诡异降临杭电，学生持灯笼求生，需要存活4天4夜才能逃离
    """
    st.divider()

    if st.button("🔄 重新开始当前区域"):
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我决定在【{current_location}】碰碰运气"},
            {"role": "assistant", "content": f"你缓缓推开了【{current_location}】的门..."}
        ]
        st.rerun()
    
    if "messages" not in st.session_state or st.session_state.get("current_loc") != current_location:
        st.session_state.current_loc = current_location
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我决定在【{current_location}】碰碰运气"},
            {"role": "assistant", "content": f"你缓缓推开了【{current_location}】的门..."}
        ]
        st.session_state.sanity = 100
    
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    if st.session_state.sanity > 30:
        play_action = st.chat_input(f"你在【{current_location}】打算怎么做？")
    else:
        play_action = None
        st.info("你已经失去理智，无法行动了，请点击重新开始") 
    if play_action :
        st.session_state.messages.append({"role": "user", "content": play_action})
        with st.chat_message("user"):
            st.markdown(play_action)
        with st.chat_message("assistant"):
            with st.spinner("周围的空气变粘稠了..."):
                try:
                    client = OpenAI(api_key=st.secrets["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")
                    response = client.chat.completions.create(model="glm-4-flash", messages=st.session_state.messages)
                    ai_reply = response.choices[0].message.content

                    lose_sanity = False
                    if ai_reply.startswith("【-5】"):
                        lose_sanity = True
                        ai_reply = ai_reply.replace("【-5】", "")
                        st.session_state.sanity -= 5

                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    if lose_sanity:
                        st.warning("⚠️ 危险行为！理智 -5")

                except Exception as e:
                    err_text = "迷雾消散，暂时无法收到来自这片空间的回应，请稍后再试..."
                    st.markdown(err_text)
                    st.session_state.messages.append({"role": "assistant", "content": err_text})


