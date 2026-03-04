"""DevPulse Dashboard — Streamlit application."""

import streamlit as st

st.set_page_config(
    page_title="DevPulse - 개발자 채용시장 분석",
    page_icon="📊",
    layout="wide",
)

# Sidebar navigation
st.sidebar.title("DevPulse")
st.sidebar.markdown("개발자 채용시장 기술 트렌드 분석")
page = st.sidebar.radio(
    "메뉴",
    ["스킬 랭킹", "회사 프로필", "포지션 비교", "갭 분석", "공고 검색"],
)

# Demo mode: use sample data when API is not available
DEMO_MODE = st.sidebar.toggle("데모 모드", value=True)


def get_demo_skill_ranking(position_type: str) -> dict:
    """Sample data for demo mode."""
    data = {
        "BACKEND": {
            "snapshotDate": "2026-03-04",
            "totalPostings": 523,
            "positionType": "BACKEND",
            "rankings": [
                {"rank": 1, "skill": "Java", "count": 465, "percentage": 88.9, "requiredRatio": 0.76},
                {"rank": 2, "skill": "Spring Boot", "count": 429, "percentage": 82.0, "requiredRatio": 0.71},
                {"rank": 3, "skill": "AWS", "count": 351, "percentage": 67.1, "requiredRatio": 0.45},
                {"rank": 4, "skill": "Docker", "count": 319, "percentage": 61.0, "requiredRatio": 0.38},
                {"rank": 5, "skill": "Kubernetes", "count": 283, "percentage": 54.1, "requiredRatio": 0.22},
                {"rank": 6, "skill": "MySQL", "count": 267, "percentage": 51.1, "requiredRatio": 0.41},
                {"rank": 7, "skill": "Kafka", "count": 241, "percentage": 46.1, "requiredRatio": 0.18},
                {"rank": 8, "skill": "Redis", "count": 225, "percentage": 43.0, "requiredRatio": 0.15},
                {"rank": 9, "skill": "PostgreSQL", "count": 198, "percentage": 37.9, "requiredRatio": 0.20},
                {"rank": 10, "skill": "Kotlin", "count": 183, "percentage": 35.0, "requiredRatio": 0.25},
                {"rank": 11, "skill": "JPA", "count": 172, "percentage": 32.9, "requiredRatio": 0.30},
                {"rank": 12, "skill": "Git", "count": 156, "percentage": 29.8, "requiredRatio": 0.12},
                {"rank": 13, "skill": "Linux", "count": 141, "percentage": 27.0, "requiredRatio": 0.10},
                {"rank": 14, "skill": "Elasticsearch", "count": 120, "percentage": 22.9, "requiredRatio": 0.08},
                {"rank": 15, "skill": "MongoDB", "count": 104, "percentage": 19.9, "requiredRatio": 0.06},
            ],
        },
        "FDE": {
            "snapshotDate": "2026-03-04",
            "totalPostings": 189,
            "positionType": "FDE",
            "rankings": [
                {"rank": 1, "skill": "Python", "count": 162, "percentage": 85.7, "requiredRatio": 0.70},
                {"rank": 2, "skill": "SQL", "count": 145, "percentage": 76.7, "requiredRatio": 0.65},
                {"rank": 3, "skill": "AWS", "count": 132, "percentage": 69.8, "requiredRatio": 0.50},
                {"rank": 4, "skill": "Spark", "count": 118, "percentage": 62.4, "requiredRatio": 0.40},
                {"rank": 5, "skill": "Kafka", "count": 105, "percentage": 55.6, "requiredRatio": 0.35},
                {"rank": 6, "skill": "Airflow", "count": 95, "percentage": 50.3, "requiredRatio": 0.30},
                {"rank": 7, "skill": "Docker", "count": 89, "percentage": 47.1, "requiredRatio": 0.20},
                {"rank": 8, "skill": "Kubernetes", "count": 72, "percentage": 38.1, "requiredRatio": 0.15},
            ],
        },
    }
    return data.get(position_type, data["BACKEND"])


def get_demo_company_profile() -> dict:
    return {
        "companyId": 1,
        "companyName": "네이버",
        "category": "BIGTECH",
        "totalPostings": 87,
        "topSkills": [
            {"skill": "Java", "count": 72, "percentage": 82.8},
            {"skill": "Kotlin", "count": 58, "percentage": 66.7},
            {"skill": "Spring Boot", "count": 65, "percentage": 74.7},
            {"skill": "Kubernetes", "count": 45, "percentage": 51.7},
            {"skill": "Kafka", "count": 38, "percentage": 43.7},
            {"skill": "MySQL", "count": 35, "percentage": 40.2},
            {"skill": "Redis", "count": 32, "percentage": 36.8},
            {"skill": "Docker", "count": 52, "percentage": 59.8},
        ],
        "positionBreakdown": {"BACKEND": 65, "FDE": 15, "PRODUCT": 7},
    }


def get_demo_gap_analysis() -> dict:
    return {
        "positionType": "BACKEND",
        "matchPercentage": 40,
        "gaps": [
            {"skill": "Java", "marketRank": 1, "marketPercentage": 88.9, "userStatus": "OWNED", "priority": "MAINTAINED"},
            {"skill": "Spring Boot", "marketRank": 2, "marketPercentage": 82.0, "userStatus": "OWNED", "priority": "MAINTAINED"},
            {"skill": "AWS", "marketRank": 3, "marketPercentage": 67.1, "userStatus": "LEARNING", "priority": "CONTINUE"},
            {"skill": "Docker", "marketRank": 4, "marketPercentage": 61.0, "userStatus": "OWNED", "priority": "MAINTAINED"},
            {"skill": "Kubernetes", "marketRank": 5, "marketPercentage": 54.1, "userStatus": "LEARNING", "priority": "CONTINUE"},
            {"skill": "MySQL", "marketRank": 6, "marketPercentage": 51.1, "userStatus": "OWNED", "priority": "MAINTAINED"},
            {"skill": "Kafka", "marketRank": 7, "marketPercentage": 46.1, "userStatus": "LEARNING", "priority": "CONTINUE"},
            {"skill": "Redis", "marketRank": 8, "marketPercentage": 43.0, "userStatus": "NOT_OWNED", "priority": "HIGH"},
            {"skill": "PostgreSQL", "marketRank": 9, "marketPercentage": 37.9, "userStatus": "NOT_OWNED", "priority": "HIGH"},
            {"skill": "Kotlin", "marketRank": 10, "marketPercentage": 35.0, "userStatus": "NOT_OWNED", "priority": "HIGH"},
        ],
    }


# ------ Pages ------

if page == "스킬 랭킹":
    st.title("기술 스킬 랭킹")
    st.markdown("포지션별 채용공고에서 가장 많이 요구하는 기술 스택")

    col1, col2, col3 = st.columns(3)
    with col1:
        position = st.selectbox("포지션", ["BACKEND", "FDE", "PRODUCT"])
    with col2:
        top_n = st.slider("Top N", 5, 30, 15)
    with col3:
        include_closed = st.checkbox("마감 공고 포함")

    if DEMO_MODE:
        data = get_demo_skill_ranking(position)
    else:
        from api_client import DevPulseClient
        client = DevPulseClient()
        data = client.get_skill_ranking(position, include_closed=include_closed, top_n=top_n)

    rankings = data.get("rankings", [])[:top_n]

    if rankings:
        import plotly.graph_objects as go

        skills = [r["skill"] for r in rankings]
        percentages = [r["percentage"] for r in rankings]
        required_ratios = [r.get("requiredRatio", 0) * 100 for r in rankings]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=skills[::-1],
            x=percentages[::-1],
            orientation="h",
            name="출현율 (%)",
            marker_color="#4A90D9",
            text=[f"{p}%" for p in percentages[::-1]],
            textposition="auto",
        ))
        fig.update_layout(
            title=f"{position} 포지션 기술 랭킹 (총 {data.get('totalPostings', 0)}건)",
            xaxis_title="출현율 (%)",
            height=max(400, len(skills) * 35),
            margin=dict(l=120),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Detail table
        import pandas as pd
        df = pd.DataFrame(rankings)
        df["requiredRatio"] = df["requiredRatio"].apply(lambda x: f"{x:.0%}")
        df["percentage"] = df["percentage"].apply(lambda x: f"{x}%")
        df.columns = ["순위", "스킬", "공고 수", "출현율", "필수 비율"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("데이터가 없습니다.")

elif page == "회사 프로필":
    st.title("회사 기술 프로필")
    st.markdown("회사별 채용공고에서 사용하는 기술 스택 분석")

    if DEMO_MODE:
        company_name = st.selectbox("회사", ["네이버", "카카오", "쿠팡", "배달의민족"])
        data = get_demo_company_profile()
        data["companyName"] = company_name
    else:
        company_id = st.number_input("회사 ID", min_value=1, value=1)
        from api_client import DevPulseClient
        client = DevPulseClient()
        data = client.get_company_profile(company_id)

    st.subheader(f"{data['companyName']} ({data.get('category', '')})")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 공고 수", data.get("totalPostings", 0))
    with col2:
        breakdown = data.get("positionBreakdown", {})
        st.metric("포지션 수", len(breakdown))

    # Skill bar chart
    top_skills = data.get("topSkills", [])
    if top_skills:
        import plotly.express as px
        import pandas as pd

        df = pd.DataFrame(top_skills)
        fig = px.bar(
            df, x="percentage", y="skill", orientation="h",
            title=f"{data['companyName']} 기술 스택",
            labels={"percentage": "출현율 (%)", "skill": ""},
            text="percentage",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), height=max(300, len(top_skills) * 40))
        fig.update_traces(texttemplate="%{text}%", textposition="auto", marker_color="#2ECC71")
        st.plotly_chart(fig, use_container_width=True)

    # Position breakdown pie
    if breakdown:
        import plotly.express as px
        fig = px.pie(
            names=list(breakdown.keys()),
            values=list(breakdown.values()),
            title="포지션 분포",
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "포지션 비교":
    st.title("포지션별 기술 비교")
    st.markdown("서로 다른 포지션에서 요구하는 기술 스택 비교")

    positions = st.multiselect("비교할 포지션", ["BACKEND", "FDE", "PRODUCT"], default=["BACKEND", "FDE"])

    if len(positions) >= 2:
        if DEMO_MODE:
            profiles = []
            for pos in positions:
                ranking = get_demo_skill_ranking(pos)
                profiles.append({
                    "positionType": pos,
                    "totalPostings": ranking["totalPostings"],
                    "topSkills": ranking["rankings"][:10],
                })
            # Compute common/unique
            skill_sets = {}
            for p in profiles:
                skill_sets[p["positionType"]] = {r["skill"] for r in p["topSkills"]}
            all_skills = list(skill_sets.values())
            common = set.intersection(*all_skills) if all_skills else set()
            data = {
                "positions": profiles,
                "commonSkills": list(common),
                "uniqueSkills": {
                    k: list(v - set.union(*(s for key, s in skill_sets.items() if key != k)))
                    for k, v in skill_sets.items()
                },
            }
        else:
            from api_client import DevPulseClient
            client = DevPulseClient()
            data = client.get_position_comparison(positions)

        # Display side by side
        cols = st.columns(len(positions))
        for i, pos_data in enumerate(data.get("positions", [])):
            with cols[i]:
                st.subheader(f"{pos_data['positionType']}")
                st.caption(f"총 {pos_data.get('totalPostings', 0)}건")
                for skill in pos_data.get("topSkills", [])[:10]:
                    pct = skill.get("percentage", 0)
                    st.progress(pct / 100, text=f"{skill['skill']} ({pct}%)")

        # Common & unique skills
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("공통 스킬")
            for skill in data.get("commonSkills", []):
                st.markdown(f"- {skill}")
        with col2:
            st.subheader("고유 스킬")
            for pos, skills in data.get("uniqueSkills", {}).items():
                if skills:
                    st.markdown(f"**{pos}**: {', '.join(skills)}")
    else:
        st.warning("2개 이상의 포지션을 선택하세요.")

elif page == "갭 분석":
    st.title("스킬 갭 분석")
    st.markdown("내 기술 스택과 시장 수요를 비교하여 학습 우선순위를 분석합니다.")

    position = st.selectbox("목표 포지션", ["BACKEND", "FDE", "PRODUCT"])

    st.subheader("내 스킬 입력")
    st.caption("보유(OWNED), 학습 중(LEARNING), 미보유(NOT_OWNED)를 선택하세요")

    common_skills = ["Java", "Spring Boot", "Python", "AWS", "Docker", "Kubernetes",
                     "MySQL", "PostgreSQL", "Redis", "Kafka", "Kotlin", "React",
                     "Git", "Linux", "Elasticsearch", "MongoDB", "JPA", "Airflow"]

    user_skills = []
    cols = st.columns(3)
    for i, skill in enumerate(common_skills):
        with cols[i % 3]:
            status = st.selectbox(
                skill,
                ["NOT_OWNED", "LEARNING", "OWNED"],
                key=f"skill_{skill}",
                label_visibility="visible",
            )
            user_skills.append({"name": skill, "status": status})

    if st.button("분석 실행", type="primary"):
        owned = [s for s in user_skills if s["status"] != "NOT_OWNED"]

        if DEMO_MODE:
            data = get_demo_gap_analysis()
        else:
            from api_client import DevPulseClient
            client = DevPulseClient()
            data = client.analyze_gap(user_skills, position)

        # Match percentage
        match_pct = data.get("matchPercentage", 0)
        st.metric("시장 매칭률", f"{match_pct}%")

        # Priority breakdown
        gaps = data.get("gaps", [])

        priority_colors = {
            "CRITICAL": "#E74C3C",
            "HIGH": "#E67E22",
            "MEDIUM": "#F1C40F",
            "LOW": "#95A5A6",
            "CONTINUE": "#3498DB",
            "MAINTAINED": "#2ECC71",
        }

        for priority in ["CRITICAL", "HIGH", "CONTINUE", "MEDIUM", "MAINTAINED", "LOW"]:
            items = [g for g in gaps if g.get("priority") == priority]
            if items:
                color = priority_colors.get(priority, "#666")
                st.markdown(f"### :{priority.lower()}: {priority}")
                for item in items:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{item['skill']}**")
                    with col2:
                        st.caption(f"#{item['marketRank']}")
                    with col3:
                        st.caption(f"{item['marketPercentage']}%")

elif page == "공고 검색":
    st.title("채용공고 검색")
    st.markdown("필터를 적용하여 채용공고를 검색합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        position = st.selectbox("포지션", [None, "BACKEND", "FDE", "PRODUCT"])
    with col2:
        categories = st.multiselect("회사 카테고리", ["BIGTECH", "BIGTECH_SUB", "UNICORN", "STARTUP", "SI", "MID"])
    with col3:
        statuses = st.multiselect("상태", ["ACTIVE", "CLOSED", "EXPIRED"], default=["ACTIVE"])

    if DEMO_MODE:
        st.info("데모 모드에서는 공고 검색이 지원되지 않습니다. API 서버를 실행한 후 데모 모드를 해제하세요.")
        # Show sample data
        import pandas as pd
        sample = pd.DataFrame([
            {"제목": "백엔드 개발자", "회사": "네이버", "카테고리": "BIGTECH", "스킬": "Java, Spring Boot, Kafka", "상태": "ACTIVE"},
            {"제목": "서버 엔지니어", "회사": "쿠팡", "카테고리": "BIGTECH", "스킬": "Java, Kotlin, AWS", "상태": "ACTIVE"},
            {"제목": "백엔드 개발자", "회사": "토스", "카테고리": "UNICORN", "스킬": "Kotlin, Spring Boot, Kubernetes", "상태": "ACTIVE"},
            {"제목": "서버 개발자", "회사": "당근", "카테고리": "UNICORN", "스킬": "Go, Kubernetes, gRPC", "상태": "ACTIVE"},
            {"제목": "백엔드 엔지니어", "회사": "라인", "카테고리": "BIGTECH", "스킬": "Java, Spring, Kafka, Redis", "상태": "CLOSED"},
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)
    else:
        from api_client import DevPulseClient
        client = DevPulseClient()
        try:
            data = client.get_postings(
                position_type=position,
                company_category=categories or None,
                status=statuses or None,
            )
            postings = data.get("content", [])
            if postings:
                import pandas as pd
                df = pd.DataFrame([{
                    "제목": p["title"],
                    "회사": p["companyName"],
                    "카테고리": p["companyCategory"],
                    "포지션": p.get("positionType", ""),
                    "스킬": ", ".join(p.get("skills", [])),
                    "상태": p["status"],
                } for p in postings])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"총 {data.get('totalElements', 0)}건")
            else:
                st.info("검색 결과가 없습니다.")
        except Exception as e:
            st.error(f"API 연결 실패: {e}")
