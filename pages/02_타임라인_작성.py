from datetime import date
import html

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="타임라인 작성",
    page_icon="🗓️",
    layout="wide",
)


# =========================================================
# Google Apps Script 주소
# =========================================================
try:
    SHEET_URL = st.secrets["SHEET_URL"]
except KeyError:
    SHEET_URL = ""


# =========================================================
# API 요청 함수
# =========================================================
def api_get(params: dict) -> dict:
    """Google Apps Script에 GET 요청을 보냅니다."""
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

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "message": f"데이터 조회 중 오류가 발생했습니다: {error}",
        }

    except ValueError:
        return {
            "success": False,
            "message": "Google Apps Script가 올바른 JSON을 반환하지 않았습니다.",
        }


def api_post(data: dict) -> dict:
    """Google Apps Script에 POST 요청을 보냅니다."""
    if not SHEET_URL:
        return {
            "success": False,
            "message": "SHEET_URL이 설정되지 않았습니다.",
        }

    try:
        response = requests.post(
            SHEET_URL,
            json=data,
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

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "message": f"요청 처리 중 오류가 발생했습니다: {error}",
        }

    except ValueError:
        return {
            "success": False,
            "message": "Google Apps Script가 올바른 JSON을 반환하지 않았습니다.",
        }


# =========================================================
# 데이터 조회 함수
# =========================================================
def get_cases() -> list:
    """저장된 전체 증례 목록을 불러옵니다."""
    result = api_get({"action": "case_list"})

    if result.get("success"):
        return result.get("cases", [])

    st.error(
        result.get(
            "message",
            "증례 목록을 불러오지 못했습니다.",
        )
    )
    return []


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

    st.error(
        result.get(
            "message",
            "타임라인을 불러오지 못했습니다.",
        )
    )
    return []


# =========================================================
# 보조 함수
# =========================================================
def make_case_label(case: dict) -> str:
    """증례 선택창에 표시할 문구를 만듭니다."""
    case_id = str(case.get("case_id", "") or "")
    patient_code = str(case.get("patient_code", "") or "")

    diagnosis = (
        case.get("pathologic_diagnosis")
        or case.get("clinical_diagnosis")
        or "진단명 미입력"
    )

    return f"{case_id} · {patient_code} · {diagnosis}"


def clean_display_text(value) -> str:
    """빈 값을 하이픈으로 바꾸고 문자열로 반환합니다."""
    if value is None:
        return "-"

    text = str(value).strip()
    return text if text else "-"


def safe_html(value) -> str:
    """HTML 카드에 안전하게 출력할 문자열로 변환합니다."""
    if value is None:
        return "-"

    text = str(value).strip()

    if not text:
        return "-"

    return html.escape(text).replace("\n", "<br>")


def build_timeline_figure(timeline_df: pd.DataFrame) -> go.Figure:
    """사건들이 하나의 선 위에 연결되는 타임라인을 만듭니다."""
    plot_df = timeline_df.copy()

    plot_df["same_day_order"] = plot_df.groupby(
        "event_date"
    ).cumcount()

    y_positions = []

    for index, row in plot_df.iterrows():
        base_position = 0.32 if index % 2 == 0 else -0.32
        additional_offset = row["same_day_order"] * 0.15

        if base_position > 0:
            y_positions.append(base_position + additional_offset)
        else:
            y_positions.append(base_position - additional_offset)

    plot_df["y_position"] = y_positions

    event_colors = {
        "초진": "#2563EB",
        "외래": "#60A5FA",
        "영상검사": "#0891B2",
        "조직검사": "#7C3AED",
        "병리결과": "#A855F7",
        "입원": "#D97706",
        "수술": "#DC2626",
        "약물치료": "#16A34A",
        "방사선치료": "#EA580C",
        "항암치료": "#DB2777",
        "합병증": "#B91C1C",
        "퇴원": "#0284C7",
        "추적관찰": "#0D9488",
        "재발": "#991B1B",
        "기타": "#64748B",
    }

    marker_colors = [
        event_colors.get(event_type, "#64748B")
        for event_type in plot_df["event_type"]
    ]

    figure = go.Figure()

    minimum_date = plot_df["event_date"].min()
    maximum_date = plot_df["event_date"].max()

    if minimum_date == maximum_date:
        line_start = minimum_date - pd.Timedelta(days=2)
        line_end = maximum_date + pd.Timedelta(days=2)
    else:
        total_days = max(
            int((maximum_date - minimum_date).days),
            1,
        )

        padding_days = max(
            int(total_days * 0.1),
            1,
        )

        line_start = minimum_date - pd.Timedelta(
            days=padding_days
        )

        line_end = maximum_date + pd.Timedelta(
            days=padding_days
        )

    # 중앙 가로선
    figure.add_trace(
        go.Scatter(
            x=[line_start, line_end],
            y=[0, 0],
            mode="lines",
            line={
                "color": "#94A3B8",
                "width": 4,
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # 사건과 중앙선을 연결하는 세로선
    for _, row in plot_df.iterrows():
        figure.add_trace(
            go.Scatter(
                x=[
                    row["event_date"],
                    row["event_date"],
                ],
                y=[
                    0,
                    row["y_position"],
                ],
                mode="lines",
                line={
                    "color": "#CBD5E1",
                    "width": 2,
                },
                hoverinfo="skip",
                showlegend=False,
            )
        )

    custom_data = plot_df[
        [
            "event_type",
            "event_description",
            "display_date",
        ]
    ].values

    # 사건 마커와 사건명
    figure.add_trace(
        go.Scatter(
            x=plot_df["event_date"],
            y=plot_df["y_position"],
            mode="markers+text",
            marker={
                "size": 21,
                "color": marker_colors,
                "line": {
                    "color": "#FFFFFF",
                    "width": 3,
                },
            },
            text=plot_df["event_type"],
            textposition=[
                "top center" if value > 0 else "bottom center"
                for value in plot_df["y_position"]
            ],
            textfont={
                "size": 14,
                "color": "#0F172A",
            },
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>%{customdata[2]}"
                "<br><br>%{customdata[1]}"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    maximum_y = max(
        abs(plot_df["y_position"]).max() + 0.3,
        0.75,
    )

    figure.update_layout(
        height=430,
        margin={
            "l": 30,
            "r": 30,
            "t": 45,
            "b": 45,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={
            "bgcolor": "#111827",
            "font_color": "#FFFFFF",
            "bordercolor": "#334155",
        },
        xaxis={
            "title": "",
            "range": [line_start, line_end],
            "showgrid": False,
            "showline": False,
            "tickformat": "%Y-%m-%d",
            "tickfont": {
                "size": 12,
                "color": "#64748B",
            },
        },
        yaxis={
            "visible": False,
            "range": [
                -maximum_y,
                maximum_y,
            ],
            "fixedrange": True,
        },
        dragmode=False,
    )

    return figure


# =========================================================
# 디자인
# =========================================================
st.markdown(
    """
<style>
    .block-container {
        max-width: 1250px;
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

    .timeline-panel {
        padding: 1rem 1.2rem 0.2rem 1.2rem;
        border-radius: 20px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 1.5rem;
    }

    .event-count {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        background: #EAF2FF;
        color: #1D4ED8;
        font-size: 0.85rem;
        font-weight: 750;
        margin-bottom: 0.8rem;
    }

    .event-card {
        padding: 1rem 1.2rem;
        border-radius: 15px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #2563EB;
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.05);
        margin-bottom: 0.8rem;
    }

    .event-date {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 650;
        margin-bottom: 0.25rem;
    }

    .event-type {
        color: #0F172A;
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .event-description {
        color: #475569;
        line-height: 1.65;
    }

    div[data-testid="stForm"] {
        padding: 1.3rem;
        border-radius: 18px;
        border: 1px solid #DDE4EB;
        background: #FFFFFF;
    }

    .stButton > button,
    .stFormSubmitButton > button {
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
<div class="page-title">🗓️ 환자 진료 타임라인</div>
<div class="page-description">
초진부터 검사, 수술 및 추적관찰까지 주요 사건을 시간순으로 기록합니다.
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 연결 확인
# =========================================================
if not SHEET_URL:
    st.error(
        "Streamlit Secrets에 SHEET_URL이 없습니다. "
        "Google Apps Script 웹앱 주소를 설정해 주세요."
    )
    st.stop()


# =========================================================
# 증례 목록 불러오기
# =========================================================
with st.spinner("저장된 증례 목록을 불러오는 중입니다."):
    cases = get_cases()

if not cases:
    st.warning(
        "저장된 증례가 없습니다. "
        "먼저 '새 증례 등록' 페이지에서 증례를 등록해 주세요."
    )
    st.stop()


# =========================================================
# 증례 선택
# =========================================================
case_map = {
    make_case_label(case): case
    for case in cases
}

selected_case_label = st.selectbox(
    "타임라인을 작성할 증례",
    options=list(case_map.keys()),
)

selected_case = case_map[selected_case_label]
selected_case_id = clean_display_text(
    selected_case.get("case_id")
)


# =========================================================
# 선택한 증례 요약
# HTML을 사용하지 않고 Streamlit 기본 구성요소로 표시
# =========================================================
diagnosis_text = clean_display_text(
    selected_case.get("pathologic_diagnosis")
    or selected_case.get("clinical_diagnosis")
)

case_id_text = clean_display_text(
    selected_case.get("case_id")
)

patient_code_text = clean_display_text(
    selected_case.get("patient_code")
)

age_text = clean_display_text(
    selected_case.get("age")
)

sex_text = clean_display_text(
    selected_case.get("sex")
)

chief_complaint_text = clean_display_text(
    selected_case.get("chief_complaint")
)

lesion_site_text = clean_display_text(
    selected_case.get("lesion_site")
)

with st.container(border=True):
    st.markdown("### 🦷 선택한 증례")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.markdown("**증례 고유번호**")
        st.code(case_id_text, language=None)

        st.markdown("**비식별 환자코드**")
        st.code(patient_code_text, language=None)

        st.markdown("**나이 / 성별**")
        st.write(f"{age_text}세 / {sex_text}")

    with summary_col2:
        st.markdown("**환자의 주소**")
        st.write(chief_complaint_text)

        st.markdown("**진단명**")
        st.write(diagnosis_text)

        st.markdown("**병변 위치**")
        st.write(lesion_site_text)


# =========================================================
# 사건 추가
# =========================================================
st.subheader("1. 새 사건 추가")

event_type_options = [
    "초진",
    "외래",
    "영상검사",
    "조직검사",
    "병리결과",
    "입원",
    "수술",
    "약물치료",
    "방사선치료",
    "항암치료",
    "합병증",
    "퇴원",
    "추적관찰",
    "재발",
    "기타",
]

with st.form(
    "timeline_form",
    clear_on_submit=True,
):
    input_col1, input_col2 = st.columns(2)

    with input_col1:
        event_date = st.date_input(
            "사건 날짜",
            value=date.today(),
        )

    with input_col2:
        event_type = st.selectbox(
            "사건 유형",
            options=event_type_options,
        )

    event_description = st.text_area(
        "당시 발생한 일",
        placeholder=(
            "예: 좌측 하악부 종창을 주소로 초진 내원하였다. "
            "파노라마에서 다방성 방사선투과성 병변이 확인되었다."
        ),
        height=130,
    )

    submitted = st.form_submit_button(
        "타임라인에 추가",
        type="primary",
        use_container_width=True,
    )


if submitted:
    if not event_description.strip():
        st.error("사건 내용을 입력해 주세요.")

    else:
        payload = {
            "action": "timeline_save",
            "case_id": selected_case_id,
            "event_date": event_date.strftime("%Y-%m-%d"),
            "event_type": event_type,
            "event_description": event_description.strip(),
        }

        with st.spinner("타임라인 항목을 저장하고 있습니다."):
            result = api_post(payload)

        if result.get("success"):
            st.success("타임라인 항목이 저장되었습니다.")
            st.rerun()

        else:
            st.error(
                result.get(
                    "message",
                    "타임라인 저장 중 오류가 발생했습니다.",
                )
            )


st.divider()


# =========================================================
# 기존 타임라인
# =========================================================
st.subheader("2. 환자 진료 흐름")

with st.spinner("타임라인을 불러오는 중입니다."):
    timeline = get_timeline(selected_case_id)

if not timeline:
    st.info("아직 등록된 타임라인 항목이 없습니다.")
    st.stop()


timeline_df = pd.DataFrame(timeline)

required_columns = [
    "timeline_id",
    "event_date",
    "event_type",
    "event_description",
]

for column in required_columns:
    if column not in timeline_df.columns:
        timeline_df[column] = ""

timeline_df["event_date"] = pd.to_datetime(
    timeline_df["event_date"],
    errors="coerce",
)

invalid_date_count = int(
    timeline_df["event_date"].isna().sum()
)

timeline_df = timeline_df.dropna(
    subset=["event_date"]
)

if timeline_df.empty:
    st.warning(
        "타임라인 항목은 존재하지만 날짜 형식이 올바르지 않습니다."
    )
    st.stop()

timeline_df = timeline_df.sort_values(
    by=[
        "event_date",
        "timeline_id",
    ],
    ascending=True,
).reset_index(drop=True)

timeline_df["display_date"] = timeline_df[
    "event_date"
].dt.strftime("%Y-%m-%d")


if invalid_date_count > 0:
    st.warning(
        f"날짜 형식이 올바르지 않은 항목 {invalid_date_count}개는 "
        "타임라인에서 제외했습니다."
    )


# =========================================================
# 시각적 타임라인
# =========================================================
st.markdown(
    f"""
<div class="event-count">총 {len(timeline_df)}개의 주요 사건</div>
""",
    unsafe_allow_html=True,
)

timeline_figure = build_timeline_figure(
    timeline_df
)

with st.container(border=True):
    st.plotly_chart(
        timeline_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )


# =========================================================
# 상세 기록
# =========================================================
st.markdown("### 📌 상세 기록")

for _, row in timeline_df.iterrows():
    timeline_id = clean_display_text(
        row.get("timeline_id")
    )

    display_date = clean_display_text(
        row.get("display_date")
    )

    row_event_type = safe_html(
        row.get("event_type")
    )

    row_description = safe_html(
        row.get("event_description")
    )

    event_col, delete_col = st.columns(
        [8.5, 1.2],
        gap="medium",
    )

    with event_col:
        st.markdown(
            f"""
<div class="event-card">
<div class="event-date">{display_date}</div>
<div class="event-type">{row_event_type}</div>
<div class="event-description">{row_description}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with delete_col:
        st.write("")

        if st.button(
            "삭제",
            key=f"delete_{timeline_id}",
            use_container_width=True,
        ):
            st.session_state.delete_timeline_id = timeline_id
            st.session_state.delete_timeline_text = (
                f"{display_date} · "
                f"{clean_display_text(row.get('event_type'))}"
            )


# =========================================================
# 삭제 확인
# =========================================================
if st.session_state.get("delete_timeline_id"):
    st.warning(
        f"'{st.session_state.get('delete_timeline_text', '')}' "
        "항목을 삭제하시겠습니까?"
    )

    confirm_col1, confirm_col2 = st.columns(2)

    with confirm_col1:
        if st.button(
            "예, 삭제합니다",
            type="primary",
            use_container_width=True,
        ):
            result = api_post(
                {
                    "action": "timeline_delete",
                    "timeline_id": (
                        st.session_state.delete_timeline_id
                    ),
                }
            )

            if result.get("success"):
                st.session_state.delete_timeline_id = None
                st.session_state.delete_timeline_text = None

                st.success(
                    "타임라인 항목이 삭제되었습니다."
                )

                st.rerun()

            else:
                st.error(
                    result.get(
                        "message",
                        "삭제 중 오류가 발생했습니다.",
                    )
                )

    with confirm_col2:
        if st.button(
            "취소",
            use_container_width=True,
        ):
            st.session_state.delete_timeline_id = None
            st.session_state.delete_timeline_text = None
            st.rerun()


# =========================================================
# 표 형태
# =========================================================
with st.expander("표 형태로 전체 기록 보기"):
    display_df = timeline_df[
        [
            "display_date",
            "event_type",
            "event_description",
        ]
    ].rename(
        columns={
            "display_date": "날짜",
            "event_type": "유형",
            "event_description": "내용",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )
