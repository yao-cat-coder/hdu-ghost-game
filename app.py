import streamlit as st
import os
import json
from openai import OpenAI
st.set_page_config(page_title="杭电奇妙夜", page_icon="🏰", layout="wide", initial_sidebar_state = "expanded" )
be_home = "https://imgs.699pic.com/images/500/441/402.jpg!list1x.v2"
be_food = "https://img95.699pic.com/photo/60018/1797.jpg_wh860.jpg"
be_ghost =  "https://img.cgmodel.com/image/2023/1214/cover/1361108-725795395.png"
st.sidebar.header("导航栏")
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
header {{
    background-color: rgba(20, 20, 30, 0.6) !important;
}}
[data-testid="collapsedControl"] {{
    display: block !important;
    color: white !important;
    background-color: #8b0000 !important; 
    border-radius: 8px;
    margin: 10px;
}}
[data-testid="stAppViewContainer"] {{
    background-image: url("{current_bg}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
[data-testid="stAppViewContainer"] > section {{
    background-color: rgba(15, 15, 26, 0.85) !important; 
}}
[data-testid="stSidebar"] {{
    background-color: rgba(20, 20, 30, 0.95) !important;
    border-right: 1px solid #555;
}}
p, span, div, label, h1, h2, h3 {{
    color: #ffffff !important;
}}
.stTextInput>div>div>input {{
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid #555 !important;
}}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)
if page == "🏠 首页大厅":
    st.title("🍜 杭电美食城 AI 推荐馆")
    st.info("👈 找不到功能入口？请点击左上角的 `>>` 箭头打开导航栏，选择【美食频道】或【怪谈游戏】！")
    st.write("不知道吃什么？告诉我你的口味，我让AI给你用最真实的评价给你推荐")
    st.divider()
    reviews_data = []
    if os.path.exists("reviews.json"):
        try:
            with open("reviews.json", "r", encoding = "utf-8")as f:
                reviews_data = json.load(f)
        except:
            pass
    if len(reviews_data) > 0:
        context = "以下是真实食客的评价：\n"
        for r in reviews_data:
            context += f"- 区域：{r.get('location', '未知')}，店名：{r.get('name', '未知')}，评分：{r.get('score', '未知')}，评价：{r.get('comment', '无')}\n"
    else:
        pass
    name = st.text_input("请输入你的昵称：")
    user_want = st.text_input("你想吃点什么😊，你的口味是什么❓（想吃点辣的吗、预算20以内想吃好评最多的）")
    submit = st.button("🤖让AI帮我选一家！")
    if submit:
        if name != "" and user_want != "":
            if len(reviews_data) == 0:
                st.warning("⚠️ 抱歉，目前大家的评价库还是空的，AI 拒绝提供不存在的推荐。快点击左侧【美食频道】写下第一条评价吧！")
            else:
                with st.spinner("🤖AI正在翻阅大家的评价，为你疯狂挑选中... "):
                    client = OpenAI(
                        api_key = st.secrets["ZHIPU_API_KEY"],
                        base_url = "https://open.bigmodel.cn/api/paas/v4/"
                    )
                    prompt = f"""
                    你是一个及其严格的杭电美食推荐官。同学 {name} 的需求是：{user_want}。
                    这是你手头的真实评价数据：{context}
                    【核心执行逻辑】（必须严格遵守）：
                    1.请你现在后台仔细核对：上述真实评价里的菜品和口味，是否真的符合同学的需求；
                    2.如过数据里写的和同学的需求不匹配，必须无情拒绝，直接回答：“抱歉，目前大家的真实评价里没有符合你口味的店铺哦”，绝不允许自己不顾需求和实际强行推荐！
                    3只有当真实评价确实符合同学需求时，你才能用热情、幽默的的方式以小红书的风格输出推荐，要求60字以内
                    """
                    response = client.chat.completions.create(
                        model = "glm-4-flash",
                        messages = [
                            {"role": "user", "content": prompt},
                        ]
                    )
                    ai_reply = response.choices[0].message.content
                    st.success("✨AI为你找到了绝佳选择：")
                    st.markdown(ai_reply)
                    st.balloons()
        else:
            st.warning("⚠️请先输入你的口味需求哦！")
elif page == "美食频道":
    st.header("🍜 美食推荐区")
    st.write("你可以在这里评价周围美食")
    try:
        with open("reviews.json", "r", encoding="utf-8")as f:
            reviews=json.load(f)
    except FileNotFoundError:
        reviews=[]
    except json.JSONDecodeError:
        reviews = []
    with st.form("my_view_form"):
        st.subheader("发布你的专属评价")
        location = st.selectbox("选择区域", ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"])
        food_name=st.text_input("美食/店名")
        score=st.slider("打分（1-10分）", 1, 10, 5)
        comment=st.text_area("写下你的真实感受")
        submitted=st.form_submit_button("提交评价")
    if submitted:
        if food_name!="" and comment!="":
            new_review={"location": location, "name": food_name, "score": score, "comment": comment}
            reviews.append(new_review)
            with open("reviews.json", "w",encoding="utf-8")as f:
                json.dump(reviews, f, ensure_ascii=False,indent=4)
            st.success("✅评价成功")
        else:
            st.warning("⚠️店名和评价不能为空哦！")
    st.divider()
    st.subheader("🔥大家怎么说")
    if len(reviews)==0:
        st.info("大家还没有评价快来抢沙发🛋️")
    else:
        regions = ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"]
        tabs = st.tabs(regions)
        for tab, region in zip(tabs, regions):
            with tab:
                region_reviews = [r for r in reversed(reviews) if r.get("location")==region]
                if len(region_reviews) == 0:
                    st.write("这个区域目前空空如也，快来抢首评论！")
                else:
                    for r in region_reviews:
                        with st.expander(f"📍{r['name']}——⭐{r['score']}/10"):
                            st.write(r['comment'])
                            if st.button("🗑️ 删除这条评价", key=f"del_{r['location']}_{r['name']}_{r['score']}"):
                                reviews.remove(r)
                                with open("reviews.json", "w", encoding="utf-8")as f:
                                    json.dump(reviews, f, ensure_ascii=False, indent=4)
                                st.rerun()        
elif page == "怪谈游戏":
    st.header("👻 怪谈游戏区")
    st.write("欢迎来到受诅咒的杭电美食城")
    map_location = ["绍味堂一层大众餐厅", "绍味堂二层美食城", "绍信公寓周边", "东门“芯潮集合街”与周边"]
    current_location = st.radio("选择探索地区", map_location, horizontal=True)
    recent_reviews=[]
    if os.path.exists("reviews.json"):
        try:
            with open("reviews.json", "r", encoding="utf-8")as f:
                all_reviews = json.load(f)
                for r in all_reviews:
                    if r.get("location") == current_location:
                        recent_reviews.append(f"店名：{r['name']},评价:{r['comment']}")
        except:
            pass
    if len(recent_reviews)>0:
        reviews_context = "以下是食客在这里留下的真是线索："+";".join(recent_reviews)
        st.info(f"已收集到{len(recent_reviews)}条关于【{current_location}】的真实线索！")
    else:
        reviews_context = "目前还没有人在这里留下评价，这里一片死寂"
        st.warning(f"⚠️【{current_location}】暂无真实评价AI只能瞎编了。")
    system_prompt = f"""
    你是一个克苏鲁风格的怪谈游戏主持人，每个人的初始理智值都为100，每次出错都会扣除5点理智值
    玩家现在处在【{current_location}】，根据食客的评价{reviews_context}来生成一个50子左右的恐怖诡异场景。并给出玩家十条规则，
    可以在这十条规则中设置一些矛盾的规则，让玩家自行判断在哪些情况下，矛盾条件的某一条件会成立，另一条件不成立，
    整个地图的大背景是诡异游戏降临杭电，学生们在这里艰难求生，街道上弥漫着诡气，他们打着能抵御诡气的灯笼在街上行走，寻找一家能填饱肚子的小店。
    一旦理智值低于30他们便会同化为诡异的一员，并失去意识，只有在这里生存4天4夜才能彻底离开。
    """
    st.divider()
    if "messages" not in st.session_state or st.session_state.get("current_loc")!= current_location:
        st.session_state.current_loc = current_location
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我决定在【{current_location}】碰碰运气"},
            {"role": "assistant", "content": f"你缓缓推开了【{current_location}】的门..."}
        ]
    for msg in st.session_state.messages:
        if msg["role"]!= "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    if play_action := st.chat_input(f"你在【{current_location}】打算怎么做？"):
        st.session_state.messages.append({"role": "user", "content": play_action})
        with st.chat_message("user"):
            st.markdown(play_action)
        with st.chat_message("assistant"):
            with st.spinner("周围的空气变粘稠了..."):
                client = OpenAI(
                    api_key =st.secrets["ZHIPU_API_KEY"],
                    base_url = "https://open.bigmodel.cn/api/paas/v4/"
                )
                response = client.chat.completions.create(
                    model = "glm-4-flash",
                    messages = st.session_state.messages
                )
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            
    

    






    
