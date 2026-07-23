import streamlit as st


# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="구강악안면외과 증례 발표 도우미",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# 화면 스타일
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.3rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }

        .sub-title {
            font-size: 1.1rem;
            color: #555555;
            margin-bottom: 1.8rem;
        }

        .guide-card {
            padding: 1.2rem;
            border-radius: 14px;
            background-color: #F7F9FC;
            border: 1px solid #E3E8EF;
            min-height: 180px;
        }

        .warning-box {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            background-color: #FFF7E6;
            border-left: 5px solid #F2A93B;
            margin-top: 1rem;
        }

        .small-text {
            color: #666666;
            font-size: 0.92rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.title("🦷 증례 발표 도우미")

    st.markdown(
        """
        왼쪽 메뉴에서 원하는 기능을 선택하세요.

        **권장 사용 순서**

        1. 새 증례 등록  
        2. 타임라인 작성  
        3. 증례 조회 및 수정
        """
    )

    st.divider()

    st.info(
        "이 앱에는 환자 이름, 병록번호, 생년월일, 전화번호 등 "
        "직접 식별정보를 입력하지 마세요."
    )


# ---------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🦷 구강악안면외과 증례 발표 제작 도우미</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        증례 정보를 체계적으로 정리하고, 발표용 타임라인과 핵심 내용을 준비하는 웹앱입니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 주요 기능 안내
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="guide-card">
            <h3>① 새 증례 등록</h3>
            <p>
                증례 고유번호와 비식별 환자코드를 자동으로 생성하고,
                환자의 기본 정보와 증례 내용을 Google Spreadsheet에 저장합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="guide-card">
            <h3>② 타임라인 작성</h3>
            <p>
                초진, 영상검사, 생검, 수술, 추적관찰 등
                환자의 주요 사건을 날짜순으로 입력하고 확인합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="guide-card">
            <h3>③ 증례 조회 및 수정</h3>
            <p>
                저장된 증례를 불러와 내용을 확인하고,
                수정하거나 연결된 타임라인을 조회합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("---")


# ---------------------------------------------------------
# 현재 앱 구성
# ---------------------------------------------------------
st.subheader("📂 앱 구성")

st.code(
    """
프로젝트폴더/
│
├── main.py
├── requirements.txt
│
└── pages/
    ├── 1_새_증례_등록.py
    ├── 2_타임라인_작성.py
    └── 3_증례_조회_및_수정.py
    """,
    language="text",
)


# ---------------------------------------------------------
# 비식별화 안내
# ---------------------------------------------------------
st.markdown(
    """
    <div class="warning-box">
        <strong>⚠️ 개인정보 보호 안내</strong><br><br>
        이 앱은 학술대회 및 증례 발표 준비를 위한 비식별 정보 관리 도구입니다.<br>
        환자 이름, 주민등록번호, 병록번호, 정확한 생년월일, 전화번호,
        주소와 같은 직접 식별정보는 입력하지 마세요.
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown("---")


# ---------------------------------------------------------
# 향후 기능 안내
# ---------------------------------------------------------
st.subheader("🚀 향후 추가 예정 기능")

st.markdown(
    """
    - 증례 발표 목차 자동 생성
    - 발표용 타임라인 문장 생성
    - 발표 핵심 문장 및 Take-home message 생성
    - 토론 질문 생성
    - PubMed 검색 키워드 생성
    """
)

st.caption(
    "현재 단계에서는 증례 등록, 타임라인 작성 및 증례 조회 기능을 먼저 구성합니다."
)
