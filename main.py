import streamlit as st


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="OMFS Case Lab",
    page_icon="☠️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 디자인
# =========================================================
st.markdown(
    """
<style>
    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(40, 90, 130, 0.18),
                transparent 32%
            ),
            linear-gradient(
                180deg,
                #070A0E 0%,
                #0D1218 100%
            );
        color: #F3F4F6;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: #0B0F14;
        border-right: 1px solid #202833;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB;
    }

    [data-testid="stSidebarNav"] a {
        border-radius: 10px;
        margin: 0.15rem 0.4rem;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: #17202A;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.8rem;
        border: 1px solid #28313C;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(18, 25, 34, 0.98),
                rgba(9, 13, 18, 0.98)
            );
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
        margin-bottom: 2rem;
    }

    .hero-skull {
        position: absolute;
        right: 2.5rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 9rem;
        opacity: 0.10;
        filter: grayscale(1);
    }

    .hero-label {
        color: #62A8DF;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        color: #F5F1E8;
        font-size: clamp(2.2rem, 5vw, 3.6rem);
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.08;
        margin-bottom: 0.9rem;
    }

    .hero-text {
        position: relative;
        z-index: 2;
        max-width: 720px;
        color: #A9B2BD;
        font-size: 1rem;
        line-height: 1.75;
    }

    .section-title {
        color: #F5F1E8;
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .section-text {
        color: #8F99A6;
        margin-bottom: 1.2rem;
    }

    .menu-card {
        min-height: 230px;
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #27313C;
        background:
            linear-gradient(
                180deg,
                #131A22 0%,
                #0E141B 100%
            );
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
        transition: 0.2s ease;
    }

    .menu-card:hover {
        transform: translateY(-4px);
        border-color: #4F83AA;
        box-shadow: 0 14px 30px rgba(32, 96, 150, 0.16);
    }

    .menu-number {
        color: #62A8DF;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }

    .menu-icon {
        font-size: 2rem;
        margin-bottom: 0.7rem;
    }

    .menu-title {
        color: #F1EEE7;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }

    .menu-text {
        color: #99A3AF;
        font-size: 0.92rem;
        line-height: 1.65;
    }

    .status-box {
        padding: 1.25rem;
        border-radius: 16px;
        border: 1px solid #27313C;
        background: #10161D;
        color: #AAB3BE;
        line-height: 1.7;
    }

    .warning-box {
        padding: 1.25rem;
        border-radius: 16px;
        border: 1px solid #5A4530;
        background: rgba(80, 54, 30, 0.22);
        color: #D8C3A5;
        line-height: 1.7;
    }

    .footer {
        text-align: center;
        color: #59636E;
        font-size: 0.8rem;
        margin-top: 2.5rem;
    }

    .stButton > button,
    [data-testid="stPageLink-NavLink"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 2rem 1.4rem;
        }

        .hero-skull {
            font-size: 6rem;
            right: 1rem;
        }

        .menu-card {
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
    st.markdown("## ☠️ OMFS Case Lab")
    st.caption("Academic Case Workspace")

    st.divider()

    st.markdown(
        """
        **01 · 새 증례 등록**

        **02 · 타임라인 작성**

        **03 · 증례 조회 및 수정**
        """
    )

    st.divider()

    st.warning(
        "환자 이름, 병록번호, 생년월일, 전화번호 등 "
        "직접 식별정보는 입력하지 마세요."
    )


# =========================================================
# 메인 히어로
# =========================================================
st.markdown(
    """
<div class="hero">
    <div class="hero-skull">☠</div>
    <div class="hero-label">ORAL & MAXILLOFACIAL SURGERY</div>
    <div class="hero-title">
        OMFS CASE LAB
    </div>
    <div class="hero-text">
        구강악안면외과 증례의 기본 정보와 진료 과정을 정리하고,
        학술대회 및 증례 발표 준비에 활용하는 전공의용 기록 도구입니다.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 빠른 메뉴
# =========================================================
st.markdown(
    """
<div class="section-title">CASE WORKFLOW</div>
<div class="section-text">
    현재 필요한 작업을 선택하세요.
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        """
<div class="menu-card">
    <div class="menu-number">STEP 01</div>
    <div class="menu-icon">📝</div>
    <div class="menu-title">새 증례 등록</div>
    <div class="menu-text">
        증례 고유번호와 비식별 환자코드를 생성하고,
        진단명, 병변 위치, 임상 및 치료 정보를 저장합니다.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/01_새_증례_등록.py",
        label="증례 등록 시작",
        icon="➡️",
        use_container_width=True,
    )

with col2:
    st.markdown(
        """
<div class="menu-card">
    <div class="menu-number">STEP 02</div>
    <div class="menu-icon">🗓️</div>
    <div class="menu-title">타임라인 작성</div>
    <div class="menu-text">
        초진, 영상검사, 조직검사, 수술 및 추적관찰을
        날짜순으로 추가하고 시각적으로 확인합니다.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/02_타임라인_작성.py",
        label="타임라인 작성",
        icon="➡️",
        use_container_width=True,
    )

with col3:
    st.markdown(
        """
<div class="menu-card">
    <div class="menu-number">STEP 03</div>
    <div class="menu-icon">🔎</div>
    <div class="menu-title">증례 조회 및 수정</div>
    <div class="menu-text">
        저장된 증례를 검색하고 수정하거나,
        연결된 타임라인과 경과를 함께 확인합니다.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/03_증례_조회_및_수정.py",
        label="증례 데이터베이스",
        icon="➡️",
        use_container_width=True,
    )


# =========================================================
# 하단 안내
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        """
<div class="status-box">
    <strong>현재 제공 기능</strong><br><br>
    · 증례 정보 등록<br>
    · 비식별 환자코드 자동 생성<br>
    · 진료 타임라인 작성<br>
    · 증례 검색, 수정 및 삭제<br>
    · Google Spreadsheet 저장
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
<div class="warning-box">
    <strong>개인정보 보호 안내</strong><br><br>
    환자 이름, 병록번호, 주민등록번호, 정확한 생년월일,
    전화번호 등 직접 식별 가능한 정보는 입력하지 마세요.
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# 향후 기능
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("🚀 향후 추가 가능한 발표 제작 기능"):
    st.markdown(
        """
        - 발표 제목 및 목차 생성
        - 증례 요약문 생성
        - 토론 질문 생성
        - 발표용 핵심 문장 생성
        - PubMed 검색 키워드 생성
        - PowerPoint 초안 생성
        """
    )


# =========================================================
# 푸터
# =========================================================
st.markdown(
    """
<div class="footer">
    OMFS Case Lab · Academic Case Presentation System
</div>
""",
    unsafe_allow_html=True,
)
