import requests
import streamlit as st
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="학회 증례 발표 키워드 추천",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# Secrets 불러오기
# =========================================================
try:
    SHEET_URL = st.secrets["SHEET_URL"]
except KeyError:
    SHEET_URL = ""

try:
    SOLAR_API_KEY = st.secrets["SOLAR_API_KEY"]
except KeyError:
    SOLAR_API_KEY = ""


# =========================================================
# Solar 클라이언트 생성
# =========================================================
def get_solar_client():
    """Upstage Solar API에 연결할 클라이언트를 만듭니다."""
    if not SOLAR_API_KEY:
        return None

    return OpenAI(
        api_key=SOLAR_API_KEY,
        base_url="https://api.upstage.ai/v1",
    )


# =========================================================
# Google Apps Script 요청 함수
# =========================================================
def api_get(params: dict) -> dict:
    """Google Spreadsheet의 데이터를 조회합니다."""
    if not SHEET_URL:
        return {
            "success": False,
            "message": "SHEET_URL이 설정되지 않았습니다.",
        }

    try:
        response = requests.get(
            SHEET_URL,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

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

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "message": "증례 정보를 불러오는 중 문제가 발생했습니다.",
        }

    except ValueError:
        return {
            "success": False,
            "message": "Google Apps Script의 응답 형식을 확인해 주세요.",
        }


@st.cache_data(ttl=60)
def get_cases() -> list:
    """저장된 증례 목록을 불러옵니다."""
    result = api_get({"action": "case_list"})

    if result.get("success"):
        return result.get("cases", [])

    return []


@st.cache_data(ttl=60)
def get_timeline(case_id: str) -> list:
    """선택한 증례의 타임라인을 불러옵니다."""
    result = api_get(
        {
            "action": "timeline_list",
            "case_id": case_id,
        }
    )

    if result.get("success"):
        return result.get("timeline", [])

    return []


# =========================================================
# 화면 표시용 함수
# =========================================================
def clean_text(value) -> str:
    """빈 값은 하이픈으로 표시합니다."""
    if value is None:
        return "-"

    text = str(value).strip()
    return text if text else "-"


def make_case_label(case: dict) -> str:
    """증례 선택창에 표시할 이름을 만듭니다."""
    diagnosis = (
        case.get("pathologic_diagnosis")
        or case.get("clinical_diagnosis")
        or "진단명 미입력"
    )

    return (
        f"{clean_text(case.get('case_id'))} · "
        f"{clean_text(case.get('patient_code'))} · "
        f"{diagnosis}"
    )


def build_case_context(case: dict, timeline: list) -> str:
    """AI에게 전달할 증례 정보를 하나의 글로 정리합니다."""
    timeline_lines = []

    sorted_timeline = sorted(
        timeline,
        key=lambda item: str(item.get("event_date", "")),
    )

    for item in sorted_timeline:
        timeline_lines.append(
            "- "
            f"{clean_text(item.get('event_date'))} | "
            f"{clean_text(item.get('event_type'))} | "
            f"{clean_text(item.get('event_description'))}"
        )

    timeline_text = (
        "\n".join(timeline_lines)
        if timeline_lines
        else "등록된 타임라인 없음"
    )

    return f"""
다음은 사용자가 선택한 구강악안면외과 증례 정보이다.

[기본 정보]
증례 고유번호: {clean_text(case.get("case_id"))}
비식별 환자코드: {clean_text(case.get("patient_code"))}
내원 당시 나이: {clean_text(case.get("age"))}
성별: {clean_text(case.get("sex"))}
환자의 주소: {clean_text(case.get("chief_complaint"))}
병변 위치: {clean_text(case.get("lesion_site"))}

[진단]
임상 진단명: {clean_text(case.get("clinical_diagnosis"))}
병리 진단명: {clean_text(case.get("pathologic_diagnosis"))}

[증례 내용]
임상 요약: {clean_text(case.get("clinical_summary"))}
영상 소견 요약: {clean_text(case.get("imaging_summary"))}
치료 요약: {clean_text(case.get("treatment_summary"))}
경과 및 추적관찰: {clean_text(case.get("outcome_followup"))}
발표에서 강조하고 싶은 점: {clean_text(case.get("presentation_point"))}

[환자 타임라인]
{timeline_text}
""".strip()


# =========================================================
# AI 메시지 구성
# =========================================================
SYSTEM_PROMPT = """
너는 따뜻하고 친절한 데이터 분석 선생님이야.
반드시 순수 한국어로만 답해.

동시에 구강악안면외과 학술대회 증례 발표를 돕는 조언자 역할을 한다.

사용자가 제공한 증례 정보만을 근거로 분석한다.
입력되지 않은 사실을 임의로 만들어내지 않는다.
확실하지 않은 내용은 가능성 또는 확인할 점이라고 분명하게 표현한다.
실제로 확인하지 않은 논문 제목, 저자, 수치 또는 연구 결과를 만들어내지 않는다.

답변은 구강악안면외과 전공의가 학회 증례 발표를 준비하는 데
실제로 활용할 수 있도록 구체적이고 구조적으로 작성한다.

의학적 최종 판단은 발표자가 직접 검토해야 한다는 점을 고려한다.
""".strip()


INITIAL_ANALYSIS_PROMPT = """
이 증례를 학술대회 증례 발표 관점에서 분석해 줘.

다음 형식을 사용해 줘.

## 증례의 한 문장 요약

## 가장 흥미로운 발표 포인트
발표 가치가 높은 순서대로 3개에서 5개를 추천해 줘.
각 항목마다 다음 내용을 포함해 줘.

- 핵심 포인트
- 왜 흥미로운지
- 발표에서 다룰 내용
- 추가로 확인해야 할 정보

## 추천 핵심 키워드
증례 발표와 고찰 작성에 도움이 되는 핵심 키워드를 제안해 줘.

## 관련 논문 검색어
논문 검색에 사용할 수 있는 검색어 조합을 제안해 줘.
설명은 한국어로 작성하고, 검색에 필요한 의학 용어는 괄호 안에 함께 표시해 줘.

## 발표 제목 후보
학술대회에 사용할 수 있는 제목 후보를 3개 제안해 줘.

## 고찰 구성 방향
고찰을 어떤 순서로 작성하면 좋은지 간단한 목차를 만들어 줘.

## 예상 토론 질문
좌장이나 청중이 물어볼 가능성이 있는 질문을 3개에서 5개 제안해 줘.

## 발표 준비를 위해 추가로 필요한 정보
현재 입력 정보 중 부족하거나 확인이 필요한 항목을 정리해 줘.
""".strip()


def make_api_messages(
    case_context: str,
    chat_history: list,
) -> list:
    """증례 정보와 대화 기록을 Solar에 전달할 형식으로 만듭니다."""
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "system",
            "content": (
                "현재 선택된 증례 정보는 다음과 같다.\n\n"
                + case_context
            ),
        },
    ]

    messages.extend(chat_history)
    return messages


# =========================================================
# Solar 스트리밍 함수
# =========================================================
def stream_solar_answer(messages: list):
    """Solar의 답변을 실시간으로 조금씩 전달합니다."""
    client = get_solar_client()

    if client is None:
        raise RuntimeError("SOLAR_API_KEY가 설정되지 않았습니다.")

    stream = client.chat.completions.create(
        model="solar-open2",
        messages=messages,
        reasoning_effort="none",
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)

        if content:
            yield content


def show_friendly_ai_error(error: Exception) -> None:
    """API 오류를 사용자에게 이해하기 쉬운 문장으로 표시합니다."""
    if isinstance(error, AuthenticationError):
        st.error(
            "Solar API 인증에 실패했습니다. "
            "Streamlit Secrets의 SOLAR_API_KEY를 확인해 주세요."
        )

    elif isinstance(error, RateLimitError):
        st.warning(
            "현재 AI 요청이 많거나 사용 한도에 도달했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

    elif isinstance(error, APIConnectionError):
        st.error(
            "Solar API 서버에 연결하지 못했습니다. "
            "인터넷 연결 상태를 확인한 뒤 다시 시도해 주세요."
        )

    elif isinstance(error, APIStatusError):
        st.error(
            "Solar API가 요청을 처리하지 못했습니다. "
            "모델 이름, API 키 또는 계정 사용 상태를 확인해 주세요."
        )

    else:
        st.error(
            "AI 답변을 생성하는 중 문제가 발생했습니다. "
            "잠시 후 다시 시도해 주세요."
        )


# =========================================================
# 간단한 화면 디자인
# =========================================================
st.markdown(
    """
<style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .page-title {
        font-size: 2.15rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-bottom: 0.3rem;
    }

    .page-description {
        color: #667085;
        line-height: 1.65;
        margin-bottom: 1.4rem;
    }

    .keyword-header {
        padding: 1.3rem 1.5rem;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #101820,
                #1B2937
            );
        border: 1px solid #334155;
        color: #F8FAFC;
        margin-bottom: 1.4rem;
    }

    .keyword-header-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .keyword-header-text {
        color: #B8C4D1;
        line-height: 1.6;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.3rem;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 750;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 제목
# =========================================================
st.markdown(
    """
<div class="page-title">🧠 학회 증례 발표 키워드 추천</div>
<div class="page-description">
저장된 증례를 분석하여 흥미로운 발표 포인트와 고찰 방향을 추천합니다.
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 설정 확인
# =========================================================
missing_settings = []

if not SHEET_URL:
    missing_settings.append("SHEET_URL")

if not SOLAR_API_KEY:
    missing_settings.append("SOLAR_API_KEY")

if missing_settings:
    st.error(
        "Streamlit Secrets에 다음 항목이 필요합니다: "
        + ", ".join(missing_settings)
    )
    st.stop()


# =========================================================
# 증례 목록 불러오기
# =========================================================
refresh_col1, refresh_col2 = st.columns([5, 1])

with refresh_col2:
    if st.button(
        "새로고침",
        use_container_width=True,
    ):
        get_cases.clear()
        get_timeline.clear()
        st.rerun()


with st.spinner("저장된 증례를 불러오는 중입니다."):
    cases = get_cases()

if not cases:
    st.warning(
        "저장된 증례가 없습니다. "
        "먼저 새 증례 등록 페이지에서 증례를 저장해 주세요."
    )
    st.stop()


# =========================================================
# 증례 선택
# =========================================================
case_map = {
    make_case_label(case): case
    for case in cases
}

selected_label = st.selectbox(
    "분석할 증례",
    options=list(case_map.keys()),
)

selected_case = case_map[selected_label]
selected_case_id = clean_text(
    selected_case.get("case_id")
)

timeline = get_timeline(selected_case_id)
case_context = build_case_context(
    selected_case,
    timeline,
)


# =========================================================
# 증례 요약 표시
# =========================================================
diagnosis = (
    selected_case.get("pathologic_diagnosis")
    or selected_case.get("clinical_diagnosis")
    or "-"
)

with st.container(border=True):
    st.markdown("### 선택한 증례")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.caption("증례 고유번호")
        st.write(clean_text(selected_case.get("case_id")))

        st.caption("비식별 환자코드")
        st.write(clean_text(selected_case.get("patient_code")))

    with summary_col2:
        st.caption("나이 / 성별")
        st.write(
            f"{clean_text(selected_case.get('age'))}세 / "
            f"{clean_text(selected_case.get('sex'))}"
        )

        st.caption("병변 위치")
        st.write(clean_text(selected_case.get("lesion_site")))

    with summary_col3:
        st.caption("진단명")
        st.write(clean_text(diagnosis))

        st.caption("등록된 타임라인")
        st.write(f"{len(timeline)}개 사건")


with st.expander("AI에게 전달되는 증례 정보 확인"):
    st.text(case_context)


# =========================================================
# 증례별 대화 기록 초기화
# =========================================================
if "case_ai_chats" not in st.session_state:
    st.session_state.case_ai_chats = {}

if selected_case_id not in st.session_state.case_ai_chats:
    st.session_state.case_ai_chats[selected_case_id] = []

chat_history = st.session_state.case_ai_chats[selected_case_id]


# =========================================================
# 분석 시작 영역
# =========================================================
st.markdown(
    """
<div class="keyword-header">
    <div class="keyword-header-title">학술 발표 관점 분석</div>
    <div class="keyword-header-text">
        증례의 특이점, 핵심 키워드, 고찰 방향과 예상 질문을 분석합니다.
        AI가 생성한 내용은 발표 전에 반드시 의료진이 직접 검토해야 합니다.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

button_col1, button_col2 = st.columns([4, 1])

with button_col1:
    analyze_button = st.button(
        "🔍 이 증례의 발표 포인트 분석하기",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_button = st.button(
        "대화 지우기",
        use_container_width=True,
    )


if clear_button:
    st.session_state.case_ai_chats[selected_case_id] = []
    st.rerun()


# =========================================================
# 기존 대화 출력
# =========================================================
for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# 최초 분석 실행
# =========================================================
if analyze_button:
    user_message = {
        "role": "user",
        "content": INITIAL_ANALYSIS_PROMPT,
    }

    chat_history.append(user_message)

    with st.chat_message("user"):
        st.markdown(
            "이 증례에서 학회 발표에 적합한 "
            "흥미로운 포인트와 키워드를 분석해 줘."
        )

    api_messages = make_api_messages(
        case_context,
        chat_history,
    )

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                stream_solar_answer(api_messages)
            )

            if not answer:
                answer = (
                    "답변을 받지 못했습니다. "
                    "잠시 후 다시 시도해 주세요."
                )
                st.warning(answer)

            chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as error:
            # 실패한 사용자 메시지는 대화 기록에서 제거합니다.
            if chat_history and chat_history[-1] == user_message:
                chat_history.pop()

            show_friendly_ai_error(error)


# =========================================================
# 후속 채팅
# =========================================================
user_input = st.chat_input(
    "예: 이 증례의 고찰 목차를 더 자세히 만들어 줘."
)

if user_input:
    user_message = {
        "role": "user",
        "content": user_input,
    }

    chat_history.append(user_message)

    with st.chat_message("user"):
        st.markdown(user_input)

    api_messages = make_api_messages(
        case_context,
        chat_history,
    )

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                stream_solar_answer(api_messages)
            )

            if not answer:
                answer = (
                    "답변을 받지 못했습니다. "
                    "잠시 후 다시 질문해 주세요."
                )
                st.warning(answer)

            chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as error:
            if chat_history and chat_history[-1] == user_message:
                chat_history.pop()

            show_friendly_ai_error(error)
