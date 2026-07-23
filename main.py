import streamlit as st


# =========================================================
# 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="구강악안면외과 증례 발표 도우미",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 전체 디자인
# =========================================================
st.markdown(
    """
    <style>
        /* 기본 화면 여백 */
        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* 기본 배경 */
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(214, 234, 255, 0.55),
                    transparent 32%
                ),
                linear-gradient(
                    180deg,
                    #FBFCFE 0%,
                    #F7F9FC 100%
                );
        }

        /* 사이드바 */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #F8FAFD 0%,
                    #EEF3F8 100%
                );
            border-right: 1px solid #E3E8EF;
        }

        /* 사이드바 메뉴 링크 */
        [data-testid="stSidebarNav"] a {
            border-radius: 10px;
            margin: 0.15rem 0.45rem;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #E8F1FB;
        }

        /* 히어로 영역 */
        .hero-box {
            position: relative;
            overflow: hidden;
            padding: 2.7rem 2.9rem;
            border-radius: 26px;
            background:
                linear-gradient(
                    135deg,
                    #163B65 0%,
                    #24598B 55%,
                    #4B82AE 100%
                );
            box-shadow:
                0 18px 40px rgba(28, 63, 101, 0.17);
            margin-bottom: 1.8rem;
        }

        .hero-box::after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            border-radius: 50%;
            right: -70px;
            top: -100px;
            background: rgba(255, 255, 255, 0.08);
        }

        .hero-box::before {
            content: "";
            position: absolute;
            width: 170px;
            height: 170px;
            border-radius: 50%;
            right: 120px;
            bottom: -110px;
            background: rgba(255, 255, 255, 0.07);
        }

        .hero-badge {
            display: inline-block;
            padding: 0.38rem 0.78rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.24);
            color: #F1F7FD;
            font-size: 0.83rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .hero-title {
            position: relative;
            z-index: 2;
            color: #FFFFFF;
            font-size: clamp(2rem, 4vw, 3rem);
            line-height: 1.2;
            font-weight: 850;
            letter-spacing: -0.04em;
            margin-bottom: 0.8rem;
        }

        .hero-description {
            position: relative;
            z-index: 2;
            max-width: 760px;
            color: rgba(255, 255, 255, 0.84);
            font-size: 1.05rem;
            line-height: 1.75;
            margin-bottom: 0;
        }

        /* 섹션 제목 */
        .section-eyebrow {
            color: #3B6F9E;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }

        .section-title {
            color: #172333;
            font-size: 1.55rem;
            font-weight: 820;
            letter-spacing: -0.025em;
            margin-bottom: 0.35rem;
        }

        .section-description {
            color: #697586;
            font-size: 0.96rem;
            line-height: 1.6;
            margin-bottom: 1.2rem;
        }

        /* 기능 카드 */
        .feature-card {
            position: relative;
            min-height: 255px;
            padding: 1.55rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #E3EAF1;
            box-shadow:
                0 8px 24px rgba(35, 57, 80, 0.06);
            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease,
                border-color 0.2s ease;
            margin-bottom: 0.5rem;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            border-color: #B9CDE0;
            box-shadow:
                0 14px 30px rgba(35, 57, 80, 0.10);
        }

        .feature-step {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: #EAF3FB;
            color: #24598B;
            font-size: 0.85rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.7rem;
        }

        .feature-title {
            color: #172333;
            font-size: 1.15rem;
            font-weight: 800;
            margin-bottom: 0.55rem;
        }

        .feature-text {
            color: #667384;
            font-size: 0.93rem;
            line-height: 1.65;
        }

        /* 핵심 가치 카드 */
        .mini-card {
            padding: 1.1rem 1.2rem;
            border-radius: 16px;
            background: #FFFFFF;
            border: 1px solid #E4E9EF;
            box-shadow:
                0 5px 16px rgba(32, 50, 70, 0.04);
            min-height: 118px;
        }

        .mini-card-title {
            color: #223146;
            font-size: 0.98rem;
            font-weight: 780;
            margin-bottom: 0.35rem;
        }

        .mini-card-text {
            color: #718096;
            font-size: 0.86rem;
            line-height: 1.55;
        }

        /* 사용 흐름 */
        .workflow-box {
            padding: 1.5rem;
            border-radius: 20px;
            background: #FFFFFF;
            border: 1px solid #E3E9EF;
            box-shadow:
                0 8px 24px rgba(35, 57, 80, 0.05);
        }

        .workflow-row {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
            padding: 0.85rem 0;
            border-bottom: 1px solid #EEF1F4;
        }

        .workflow-row:last-child {
            border-bottom: none;
        }

        .workflow-number {
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #24598B;
            color: white;
            font-size: 0.82rem;
            font-weight: 800;
        }

        .workflow-title {
            color: #1D2A3A;
            font-weight: 760;
            font-size: 0.96rem;
            margin-bottom: 0.18rem;
        }

        .workflow-text {
            color: #748092;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        /* 개인정보 안내 */
        .privacy-card {
            padding: 1.35rem 1.45rem;
            border-radius: 18px;
            background:
                linear-gradient(
                    135deg,
                    #FFF9ED 0%,
                    #FFF4D9 100%
                );
            border: 1px solid #F3DCAC;
        }

        .privacy-title {
            color: #795214;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .privacy-text {
            color: #80642C;
            font-size: 0.9rem;
            line-height: 1.65;
        }

        /* 개발 상태 */
        .status-card {
            padding: 1.35rem 1.45rem;
            border-radius: 18px;
            background:
                linear-gradient(
                    135deg,
                    #EEF8F3 0%,
                    #E3F4EB 100%
                );
            border: 1px solid #C8E5D5;
        }

        .status-title {
            color: #276246;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .status-text {
            color: #48745E;
            font-size: 0.9rem;
            line-height: 1.65;
        }

        /* 하단 문구 */
        .footer-text {
            text-align: center;
            color: #8A94A3;
            font-size: 0.82rem;
            margin-top: 2.3rem;
        }

        /* Streamlit 기본 버튼 */
        .stButton > button,
        [data-testid="stPageLink-NavLink"] {
            border-radius: 12px !important;
            font-weight: 700 !important;
        }

        /* 모바일 */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
            }

            .hero-box {
                padding: 2rem 1.4rem;
                border-radius: 20px;
            }

            .hero-title {
                font-size: 2rem;
            }

            .feature-card {
                min-height: auto;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.markdown("## 🦷 OMFS Case Lab")
    st.caption("증례 발표 준비를 위한 기록 도구")

    st.divider()

    st.markdown("### 사용 순서")

    st.markdown(
        """
        **01. 새 증례 등록**  
        환자 기본 정보와 증례 요약 저장

        **02. 타임라인 작성**  
        주요 진료 사건을 날짜순으로 기록

        **03. 증례 조회 및 수정**  
        기존 증례 확인, 수정 및 삭제
        """
    )

    st.divider()

    st.warning(
        "환자 이름, 병록번호, 생년월일, 전화번호 등 "
        "직접 식별정보를 입력하지 마세요.",
        icon="🔐",
    )

    st.caption("Academic case management prototype")


# =========================================================
# 히어로 영역
# =========================================================
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-badge">OMFS ACADEMIC CASE WORKSPACE</div>
        <div class="hero-title">
            증례 기록부터 발표 준비까지,<br>
            하나의 흐름으로 정리하세요.
        </div>
        <div class="hero-description">
            구강악안면외과 증례의 핵심 정보와 진료 과정을 체계적으로 기록하고,
            학술대회 및 증례 발표에 활용할 수 있도록 정리하는 웹앱입니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 빠른 시작
# =========================================================
st.markdown(
    """
    <div class="section-eyebrow">Quick start</div>
    <div class="section-title">어디서 시작할까요?</div>
    <div class="section-description">
        현재 작업 단계에 맞는 메뉴를 선택하세요.
    </div>
    """,
    unsafe_allow_html=True,
)

card_col1, card_col2, card_col3 = st.columns(3, gap="large")

with card_col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-step">01</div>
            <div class="feature-icon">📝</div>
            <div class="feature-title">새 증례 등록</div>
            <div class="feature-text">
                증례 고유번호와 비식별 환자코드를 자동으로 생성하고,
                진단명, 병변 위치, 임상·영상·치료 정보를 저장합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/01_새_증례_등록.py",
        label="새 증례 등록 시작",
        icon="➡️",
        use_container_width=True,
    )

with card_col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-step">02</div>
            <div class="feature-icon">🗓️</div>
            <div class="feature-title">타임라인 작성</div>
            <div class="feature-text">
                초진, 영상검사, 조직검사, 수술 및 추적관찰을
                시간순으로 기록하고 시각적인 타임라인으로 확인합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/02_타임라인_작성.py",
        label="타임라인 작성하기",
        icon="➡️",
        use_container_width=True,
    )

with card_col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-step">03</div>
            <div class="feature-icon">🔎</div>
            <div class="feature-title">증례 조회 및 수정</div>
            <div class="feature-text">
                기존 증례를 검색하고 세부 내용을 검토하거나 수정합니다.
                연결된 타임라인과 진료 경과도 함께 확인할 수 있습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/03_증례_조회_및_수정.py",
        label="저장된 증례 조회",
        icon="➡️",
        use_container_width=True,
    )


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# 앱의 핵심 가치
# =========================================================
st.markdown(
    """
    <div class="section-eyebrow">Core features</div>
    <div class="section-title">증례 발표 준비에 필요한 핵심 기능</div>
    <div class="section-description">
        불필요한 입력 항목을 줄이고, 실제 발표 준비에 필요한 정보에 집중했습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

value_col1, value_col2, value_col3, value_col4 = st.columns(4)

with value_col1:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">🔐 자동 비식별 코드</div>
            <div class="mini-card-text">
                직접 식별정보 대신 무작위 환자코드와 증례번호를 사용합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with value_col2:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">☁️ 스프레드시트 저장</div>
            <div class="mini-card-text">
                입력한 증례와 타임라인을 Google Spreadsheet에 저장합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with value_col3:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">🗓️ 진료 과정 시각화</div>
            <div class="mini-card-text">
                주요 진료 사건을 날짜순으로 정렬해 한눈에 확인합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with value_col4:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-card-title">🎓 발표 중심 기록</div>
            <div class="mini-card-text">
                임상 요약, 치료 과정과 발표 강조점을 체계적으로 관리합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("<br><br>", unsafe_allow_html=True)


# =========================================================
# 사용 흐름 및 안내
# =========================================================
left_col, right_col = st.columns([1.25, 1], gap="large")

with left_col:
    st.markdown(
        """
        <div class="section-eyebrow">Workflow</div>
        <div class="section-title">추천 사용 흐름</div>
        <div class="section-description">
            하나의 증례를 아래 순서로 작성하면 효율적으로 정리할 수 있습니다.
        </div>

        <div class="workflow-box">
            <div class="workflow-row">
                <div class="workflow-number">1</div>
                <div>
                    <div class="workflow-title">기본 증례 정보 등록</div>
                    <div class="workflow-text">
                        나이, 성별, 주소, 진단명, 병변 위치와 핵심 요약을 입력합니다.
                    </div>
                </div>
            </div>

            <div class="workflow-row">
                <div class="workflow-number">2</div>
                <div>
                    <div class="workflow-title">진료 사건 추가</div>
                    <div class="workflow-text">
                        초진부터 수술 및 추적관찰까지 주요 사건을 순서대로 기록합니다.
                    </div>
                </div>
            </div>

            <div class="workflow-row">
                <div class="workflow-number">3</div>
                <div>
                    <div class="workflow-title">기록 검토 및 수정</div>
                    <div class="workflow-text">
                        저장된 정보와 타임라인을 확인하고 필요한 부분을 보완합니다.
                    </div>
                </div>
            </div>

            <div class="workflow-row">
                <div class="workflow-number">4</div>
                <div>
                    <div class="workflow-title">발표 자료 생성 준비</div>
                    <div class="workflow-text">
                        정리된 증례 정보를 기반으로 향후 AI 발표 생성 기능을 활용합니다.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        """
        <div class="section-eyebrow">Important</div>
        <div class="section-title">사용 전 확인사항</div>
        <div class="section-description">
            환자 정보를 입력하기 전에 아래 원칙을 확인하세요.
        </div>

        <div class="privacy-card">
            <div class="privacy-title">🔐 개인정보 보호 원칙</div>
            <div class="privacy-text">
                환자 이름, 주민등록번호, 병록번호, 정확한 생년월일,
                전화번호, 주소 등 직접 식별 가능한 정보는 입력하지 마세요.
                영상 및 문서에서도 환자 식별정보를 제거한 후 사용해야 합니다.
            </div>
        </div>

        <br>

        <div class="status-card">
            <div class="status-title">✅ 현재 제공되는 기능</div>
            <div class="status-text">
                증례 등록, 자동 식별코드 생성, 진료 타임라인 작성,
                증례 검색, 수정 및 삭제 기능이 제공됩니다.
                발표 목차와 핵심 문장 자동 생성 기능은 추후 추가할 수 있습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 향후 기능
# =========================================================
st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("🚀 향후 추가 가능한 발표 제작 기능"):
    st.markdown(
        """
        - 증례 발표 제목과 목차 자동 생성
        - 발표 시간에 맞춘 슬라이드 구성안 생성
        - 날짜순 발표용 타임라인 문장 생성
        - 증례의 핵심 학습 포인트 정리
        - 토론 질문 및 예상 질의응답 생성
        - PubMed 검색 키워드와 Boolean 검색식 생성
        - 발표용 PowerPoint 초안 생성
        """
    )


# =========================================================
# 하단
# =========================================================
st.markdown(
    """
    <div class="footer-text">
        OMFS Case Lab · 구강악안면외과 증례 발표 관리 도구
    </div>
    """,
    unsafe_allow_html=True,
)
