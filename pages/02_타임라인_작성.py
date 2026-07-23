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


def get_cases() -> list:
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
    case_id = case.get("case_id", "")
    patient_code = case.get("patient_code", "")

    diagnosis = (
        case.get("pathologic_diagnosis")
        or case.get("clinical_diagnosis")
        or "진단명 미입력"
    )

    return f"{case_id} · {patient_code} · {diagnosis}"


def safe_text(value) -> str:
    if value is None or str(value).strip() == "":
        return "-"

    return html.escape(str(value).strip()).replace("\n", "<br>")


def make_timeline_figure(timeline_df: pd.DataFrame) -> go.Figure:
    """
    막대그래프가 아닌 의료 증례용 사건 타임라인을 생성합니다.
    """

    plot_df = timeline_df.copy()

    # 같은 날짜의 사건이 겹치지 않도록 순서를 계산합니다.
    plot_df["same_day_order"] = plot_df.groupby(
        "event_date"
    ).cumcount()

    # 사건 라벨을 위아래로 번갈아 배치합니다.
    y_positions = []

    for index, row in plot_df.iterrows():
        base_y = 0.26 if index % 2 == 0 else -0.26

        # 같은 날짜에 여러 사건이 있으면 조금씩 더 벌립니다.
        extra_offset = row["same_day_order"] * 0.13

        if base_y > 0:
            y_positions.append(base_y + extra_offset)
        else:
            y_positions.append(base_y - extra_offset)

    plot_df["y_position"] = y_positions

    event_colors = {
        "초진": "#4EA1FF",
        "외래": "#7FB3FF",
        "영상검사": "#22C7A9",
        "조직검사": "#B58CFF",
        "병리결과": "#D079FF",
        "입원": "#F4B860",
        "수술": "#FF6B6B",
        "약물치료": "#62C370",
        "방사선치료": "#FF9F43",
        "항암치료": "#F368E0",
        "합병증": "#E74C3C",
        "퇴원": "#54A0FF",
        "추적관찰": "#48C9B0",
        "재발": "#C0392B",
        "기타": "#95A5A6",
    }

    marker_colors = [
        event_colors.get(event_type, "#95A5A6")
        for event_type in plot_df["event_type"]
    ]

    figure = go.Figure()

    # 중앙 기준선
    figure.add_trace(
        go.Scatter(
            x=[
                plot_df["event_date"].min(),
                plot_df["event_date"].max(),
            ],
            y=[0, 0],
            mode="lines",
            line={
                "color": "#718096",
                "width": 3,
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # 기준선과 사건 마커를 연결하는 세로선
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
                    "color": "#A0AEC0",
                    "width": 1.5,
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

    # 사건 마커
    figure.add_trace(
        go.Scatter(
            x=plot_df["event_date"],
            y=plot_df["y_position"],
            mode="markers+text",
            marker={
                "size": 19,
                "color": marker_colors,
                "line": {
                    "color": "#FFFFFF",
                    "width": 2,
                },
            },
            text=plot_df["event_type"],
            textposition=[
                "top center" if y > 0 else "bottom center"
                for y in plot_df["y_position"]
            ],
            textfont={
                "size": 14,
                "color": "#1F2937",
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

    minimum_date = plot_df["event_date"].min()
    maximum_date = plot_df["event_date"].max()

    if minimum_date == maximum_date:
        range_start = minimum_date - pd.Timedelta(days=3)
        range_end = maximum_date + pd.Timedelta(days=3)
    else:
        total_days = max(
            (maximum_date - minimum_date).days,
            1,
        )

        padding_days = max(
            int(total_days * 0.12),
            2,
        )

        range_start = minimum_date - pd.Timedelta(
            days=padding_days
        )
        range_end = maximum_date + pd.Timedelta(
            days=padding_days
        )

    maximum_y = max(
        abs(plot_df["y_position"]).max() + 0.25,
        0.65,
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
            "bgcolor": "#17202A",
            "font_color": "#FFFFFF",
            "bordercolor": "#3A4A5B",
        },
        xaxis={
            "title": "",
            "range": [
                range_start,
                range_end,
            ],
            "showgrid": False,
            "showline": False,
            "tickformat": "%Y-%m-%d",
            "tickfont": {
                "size": 12,
                "color": "#667085",
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
# 화면 디자인
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

    .case-card {
        padding: 1.15rem 1.3rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #F7F9FC,
            #EFF4F8
        );
        border: 1px solid #DDE5EC;
        line-height: 1.8;
        margin-bottom: 1.2rem;
    }

    .timeline-panel {
        padding: 1.3rem 1.4rem 0.5rem 1.4rem;
        border-radius: 20px;
        background-color: #FFFFFF;
        border: 1px solid #E1E7ED;
        box-shadow: 0 10px 30px rgba(31, 41, 55, 0.06);
        margin-bottom: 1.5rem;
    }

    .timeline-list {
        position: relative;
        margin-left: 1rem;
        padding-left: 2rem;
    }

    .timeline-list::before {
        content: "";
        position: absolute;
        left: 0.45rem;
        top: 0.7rem;
        bottom: 0.7rem;
        width: 3px;
        border-radius: 999px;
        background: linear-gradient(
            180deg,
            #3B82F6,
            #8B5CF6,
            #14B8A6
        );
    }

    .event-card {
        position: relative;
        padding: 1.05rem 1.2rem;
        border-radius: 15px;
        background: #FFFFFF;
        border: 1px solid #E1E7ED;
        box-shadow: 0 5px 16px rgba(31, 41, 55, 0.05);
        margin-bottom: 1rem;
    }

    .event-card::before {
        content: "";
        position: absolute;
        left: -2.02rem;
        top: 1.35rem;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        background: #3B82F6;
        border: 3px solid #FFFFFF;
        box-shadow: 0 0 0 2px #3B82F6;
    }

    .event-date {
        color: #667085;
        font-size: 0.84rem;
        font-weight: 650;
        margin-bottom: 0.25rem;
    }

    .event-type {
        color: #172333;
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .event-description {
        color: #475467;
        line-height: 1.65;
    }

    .event-count {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background-color: #EAF2FF;
        color: #2764B0;
        font-size: 0.85rem;
        font-weight: 750;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stForm"] {
        padding: 1.3rem;
        border-radius: 18px;
        border: 1px solid #DDE4EB;
        background-color: #FFFFFF;
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
        "저장된 증례가 없습니다. 먼저 새 증례를 등록해 주세요."
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
selected_case_id = selected_case.get("case_id", "")


st.markdown(
    f"""
<div class="case-card">
    <strong>증례 고유번호</strong> ·
    {safe_text(selected_case.get("case_id"))}<br>

    <strong>비식별 환자코드</strong> ·
    {safe_text(selected_case.get("patient_code"))}<br>

    <strong>나이 / 성별</strong> ·
    {safe_text(selected_case.get("age"))}세 /
    {safe_text(selected_case.get("sex"))}<br>

    <strong>주소</strong> ·
    {safe_text(selected_case.get("chief_complaint"))}<br>

    <strong>진단</strong> ·
    {safe_text(
        selected_case.get("pathologic_diagnosis")
        or selected_case.get("clinical_diagnosis")
    )}
</div>
""",
    unsafe_allow_html=True,
)


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

timeline_df["event_date"] = pd.to_datetime(
    timeline_df["event_date"],
    errors="coerce",
)

timeline_df = timeline_df.dropna(
    subset=["event_date"]
)

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


# =========================================================
# 진짜 타임라인 그래프
# =========================================================
st.markdown(
    f"""
<div class="event-count">
    총 {len(timeline_df)}개의 주요 사건
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="timeline-panel">',
    unsafe_allow_html=True,
)

timeline_figure = make_timeline_figure(
    timeline_df
)

st.plotly_chart(
    timeline_figure,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False,
    },
)

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# =========================================================
# 상세 세로 타임라인
# =========================================================
st.markdown("### 📌 상세 기록")

st.markdown(
    '<div class="timeline-list">',
    unsafe_allow_html=True,
)

for _, row in timeline_df.iterrows():
    timeline_id = str(
        row.get(
            "timeline_id",
            "",
        )
    )

    display_date = row.get(
        "display_date",
        "",
    )

    row_event_type = safe_text(
        row.get(
            "event_type",
            "",
        )
    )

    row_description = safe_text(
        row.get(
            "event_description",
            "",
        )
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
    <div class="event-description">
        {row_description}
    </div>
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
                f"{row.get('event_type', '')}"
            )

st.markdown(
    "</div>",
    unsafe_allow_html=True,
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
