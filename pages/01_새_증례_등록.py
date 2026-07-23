import random
import string
from datetime import datetime

import requests
import streamlit as st


# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="새 증례 등록",
    page_icon="📝",
    layout="wide",
)


# ---------------------------------------------------------
# Google Apps Script 주소 불러오기
# ---------------------------------------------------------
try:
    SHEET_URL = st.secrets["SHEET_URL"]
except KeyError:
    SHEET_URL = ""


# ---------------------------------------------------------
# ID 생성 함수
# ---------------------------------------------------------
def generate_random_code(length: int = 6) -> str:
    """
    영문 대문자와 숫자를 조합한 무작위 코드를 생성합니다.
    혼동하기 쉬운 I, O, 0, 1은 제외합니다.
    """
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(characters, k=length))


def generate_case_id() -> str:
    """
    증례 고유번호 예시:
    OMFS-20260723-A7K3
    """
    today = datetime.now().strftime("%Y%m%d")
    random_code = generate_random_code(4)
    return f"OMFS-{today}-{random_code}"


def generate_patient_code() -> str:
    """
    비식별 환자코드 예시:
    PT-X7K4M2
    """
    return f"PT-{generate_random_code(6)}"


# ---------------------------------------------------------
# Google Apps Script 요청 함수
# ---------------------------------------------------------
def save_case(case_data: dict) -> dict:
    """
    Google Apps Script 웹앱으로 증례 데이터를 전송합니다.
    """
    if not SHEET_URL:
        return {
            "success": False,
            "message": "SHEET_URL이 설정되지 않았습니다.",
        }

    try:
        response = requests.post(
            SHEET_URL,
            json=case_data,
            timeout=20,
        )

        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            return {
                "success": False,
                "message": "Google Apps Script가 올바른 JSON을 반환하지 않았습니다.",
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Google Spreadsheet 연결 시간이 초과되었습니다.",
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Google Spreadsheet에 연결하지 못했습니다.",
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "message": f"저장 요청 중 오류가 발생했습니다: {error}",
        }


# ---------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------
if "new_case_id" not in st.session_state:
    st.session_state.new_case_id = generate_case_id()

if "new_patient_code" not in st.session_state:
    st.session_state.new_patient_code = generate_patient_code()

if "case_saved" not in st.session_state:
    st.session_state.case_saved = False


# ---------------------------------------------------------
# 화면 스타일
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .page-title {
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .page-description {
            font-size: 1rem;
            color: #666666;
            margin-bottom: 1.4rem;
        }

        .info-card {
            padding: 1rem 1.2rem;
            border-radius: 14px;
            background-color: #F7F9FC;
            border: 1px solid #E3E8EF;
            margin-bottom: 1rem;
        }

        .privacy-box {
            padding: 0.9rem 1rem;
            border-radius: 12px;
            background-color: #FFF8E7;
            border-left: 5px solid #E6A23C;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 제목
# ---------------------------------------------------------
st.markdown(
    '<div class="page-title">📝 새 증례 등록</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        비식별화된 증례 정보를 입력하고 Google Spreadsheet에 저장합니다.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="privacy-box">
        <strong>개인정보 보호 안내</strong><br>
        환자 이름, 병록번호, 생년월일, 전화번호, 주소 등 직접 식별정보는 입력하지 마세요.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 연결 상태 표시
# ---------------------------------------------------------
if SHEET_URL:
    st.success("Google Spreadsheet 저장 주소가 연결되어 있습니다.")
else:
    st.error(
        "Streamlit Secrets에 SHEET_URL이 없습니다. "
        "저장 기능을 사용하려면 먼저 설정해 주세요."
    )


# ---------------------------------------------------------
# 자동 생성 코드 표시
# ---------------------------------------------------------
st.subheader("1. 증례 식별 정보")

id_col1, id_col2, id_col3 = st.columns([1, 1, 0.5])

with id_col1:
    st.text_input(
        "증례 고유번호",
        value=st.session_state.new_case_id,
        disabled=True,
        help="웹앱에서 자동으로 생성되는 증례 고유번호입니다.",
    )

with id_col2:
    st.text_input(
        "비식별 환자코드",
        value=st.session_state.new_patient_code,
        disabled=True,
        help="환자의 직접 식별정보와 관련 없는 무작위 코드입니다.",
    )

with id_col3:
    st.write("")
    st.write("")

    if st.button(
        "코드 새로 만들기",
        use_container_width=True,
    ):
        st.session_state.new_case_id = generate_case_id()
        st.session_state.new_patient_code = generate_patient_code()
        st.rerun()


st.divider()


# ---------------------------------------------------------
# 증례 입력 폼
# ---------------------------------------------------------
st.subheader("2. 기본 정보 및 증례 내용")

with st.form("new_case_form", clear_on_submit=False):

    basic_col1, basic_col2 = st.columns(2)

    with basic_col1:
        age = st.number_input(
            "내원 당시 나이",
            min_value=0,
            max_value=120,
            value=None,
            step=1,
            placeholder="예: 52",
        )

    with basic_col2:
        sex = st.selectbox(
            "성별",
            options=[
                "선택",
                "남성",
                "여성",
                "기타",
                "미상",
            ],
        )

    chief_complaint = st.text_input(
        "환자의 주소 (Chief Complaint)",
        placeholder="예: 좌측 하악부 종창",
    )

    diagnosis_col1, diagnosis_col2 = st.columns(2)

    with diagnosis_col1:
        clinical_diagnosis = st.text_input(
            "임상 진단명",
            placeholder="예: Ameloblastoma, suspected",
        )

    with diagnosis_col2:
        pathologic_diagnosis = st.text_input(
            "병리 진단명",
            placeholder="예: Conventional ameloblastoma",
        )

    lesion_site = st.text_input(
        "병변 위치",
        placeholder="예: 좌측 하악체부 및 하악지",
    )

    clinical_summary = st.text_area(
        "임상 요약",
        placeholder=(
            "현병력, 주요 구내·구외 소견, 증상 기간 등을 간단히 입력하세요.\n"
            "예: 약 3개월 전부터 좌측 하악부 종창이 발생하였고 점차 증가함."
        ),
        height=140,
    )

    imaging_summary = st.text_area(
        "영상 소견 요약",
        placeholder=(
            "파노라마, CT, MRI 등의 핵심 소견을 입력하세요.\n"
            "예: 좌측 하악체부에서 하악지까지 다방성 방사선투과성 병변이 관찰됨."
        ),
        height=140,
    )

    treatment_summary = st.text_area(
        "치료 요약",
        placeholder=(
            "수술명, 치료 방법, 재건 방법 등을 입력하세요.\n"
            "예: 하악골 분절절제술 및 비골 유리피판 재건술을 시행함."
        ),
        height=120,
    )

    outcome_followup = st.text_area(
        "경과 및 추적관찰",
        placeholder=(
            "합병증, 재발 여부, 추적관찰 기간 등을 입력하세요.\n"
            "예: 수술 후 12개월 추적관찰에서 재발 소견 없음."
        ),
        height=120,
    )

    presentation_point = st.text_area(
        "발표에서 강조하고 싶은 점",
        placeholder=(
            "이 증례가 특별한 이유나 발표에서 강조할 내용을 입력하세요.\n"
            "예: 광범위한 병변의 절제 범위 결정과 재건 방법을 강조하고 싶음."
        ),
        height=120,
    )

    submitted = st.form_submit_button(
        "증례 저장하기",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# 저장 처리
# ---------------------------------------------------------
if submitted:

    required_fields = []

    if age is None:
        required_fields.append("내원 당시 나이")

    if sex == "선택":
        required_fields.append("성별")

    if not chief_complaint.strip():
        required_fields.append("환자의 주소")

    if not lesion_site.strip():
        required_fields.append("병변 위치")

    if required_fields:
        st.error(
            "다음 필수 항목을 입력해 주세요: "
            + ", ".join(required_fields)
        )

    else:
        case_data = {
            "action": "case_save",
            "case_id": st.session_state.new_case_id,
            "patient_code": st.session_state.new_patient_code,
            "age": int(age),
            "sex": sex,
            "chief_complaint": chief_complaint.strip(),
            "clinical_diagnosis": clinical_diagnosis.strip(),
            "pathologic_diagnosis": pathologic_diagnosis.strip(),
            "lesion_site": lesion_site.strip(),
            "clinical_summary": clinical_summary.strip(),
            "imaging_summary": imaging_summary.strip(),
            "treatment_summary": treatment_summary.strip(),
            "outcome_followup": outcome_followup.strip(),
            "presentation_point": presentation_point.strip(),
        }

        with st.spinner("증례를 저장하고 있습니다."):
            result = save_case(case_data)

        if result.get("success"):
            saved_case_id = st.session_state.new_case_id
            saved_patient_code = st.session_state.new_patient_code

            st.session_state.case_saved = True
            st.session_state.last_saved_case_id = saved_case_id
            st.session_state.last_saved_patient_code = saved_patient_code

            st.success("증례가 Google Spreadsheet에 저장되었습니다.")

            st.markdown(
                f"""
                <div class="info-card">
                    <strong>저장된 증례 고유번호</strong><br>
                    {saved_case_id}<br><br>
                    <strong>비식별 환자코드</strong><br>
                    {saved_patient_code}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.info(
                "다음 단계에서 왼쪽 메뉴의 "
                "'타임라인 작성' 페이지로 이동해 주요 사건을 추가하세요."
            )

            st.session_state.new_case_id = generate_case_id()
            st.session_state.new_patient_code = generate_patient_code()

        else:
            st.error(
                result.get(
                    "message",
                    "증례 저장 중 알 수 없는 오류가 발생했습니다.",
                )
            )


# ---------------------------------------------------------
# 하단 안내
# ---------------------------------------------------------
st.divider()

with st.expander("입력 항목 작성 예시"):
    st.markdown(
        """
        **환자의 주소**

        좌측 하악부 종창

        **임상 진단명**

        Ameloblastoma, suspected

        **병리 진단명**

        Conventional ameloblastoma

        **병변 위치**

        좌측 하악체부에서 하악지

        **임상 요약**

        약 3개월 전부터 좌측 하악부 종창이 발생하였고 점차 증가하였다.
        구강 내에서 좌측 하악 구치부 협측 피질골 팽윤이 관찰되었다.

        **영상 소견 요약**

        파노라마에서 좌측 하악체부부터 하악지까지 다방성
        방사선투과성 병변이 관찰되었다. CT에서 협설측 피질골
        팽윤과 일부 천공이 확인되었다.

        **치료 요약**

        전신마취하 하악골 분절절제술과 비골 유리피판 재건술을 시행하였다.

        **경과 및 추적관찰**

        수술 후 특별한 합병증은 없었으며 12개월 추적관찰에서
        재발 소견은 확인되지 않았다.

        **발표에서 강조하고 싶은 점**

        광범위한 병변의 절제 범위 결정 과정과 즉시 재건 방법을 강조하고 싶다.
        """
    )
