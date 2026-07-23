import html

import pandas as pd
import requests
import streamlit as st


# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="증례 조회 및 수정",
    page_icon="🔎",
    layout="wide",
)


# ---------------------------------------------------------
# Google Apps Script 주소
# ---------------------------------------------------------
try:
    SHEET_URL = st.secrets["SHEET_URL"]
except KeyError:
    SHEET_URL = ""


# ---------------------------------------------------------
# Google Apps Script 요청 함수
# ---------------------------------------------------------
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
            "message": f"데이터 조회 중 오류가 발생했습니다: {error}",
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
            "message": f"요청 처리 중 오류가 발생했습니다: {error}",
        }


# ---------------------------------------------------------
# 데이터 조회 함수
# ---------------------------------------------------------
def get_cases() -> list:
    """전체 증례 목록을 불러옵니다."""
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


def get_case(case_id: str) -> dict:
    """특정 증례의 상세 정보를 불러옵니다."""
    result = api_get(
        {
            "action": "case_get",
            "case_id": case_id,
        }
    )

    if result.get("success"):
        return result.get("case", {})

    st.error(
        result.get(
            "message",
            "증례 정보를 불러오지 못했습니다.",
        )
    )
    return {}


def get_timeline(case_id: str) -> list:
    """특정 증례의 타임라인을 불러옵니다."""
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


# ---------------------------------------------------------
# 값 표시용 함수
# ---------------------------------------------------------
def safe_text(value) -> str:
    """HTML 화면에 안전하게 표시할 문자열로 변환합니다."""
    if value is None or str(value).strip() == "":
        return "-"

    return html.escape(str(value).strip())


def normalize_age(value) -> int:
    """시트에서 가져온 나이를 정수로 변환합니다."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def make_case_label(case: dict) -> str:
    """증례 선택창에 표시할 문구를 만듭니다."""
    case_id = case.get("case_id", "")
    patient_code = case.get("patient_code", "")
    diagnosis = (
        case.get("pathologic_diagnosis")
        or case.get("clinical_diagnosis")
        or "진단명 미입력"
    )

    return f"{case_id} · {patient_code} · {diagnosis}"


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
            color: #666666;
            margin-bottom: 1.3rem;
        }

        .summary-card {
            padding: 1.1rem 1.3rem;
            border-radius: 14px;
            background-color: #F7F9FC;
            border: 1px solid #E3E8EF;
            margin-bottom: 1rem;
            line-height: 1.8;
        }

        .detail-card {
            padding: 1rem 1.2rem;
            border-radius: 14px;
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            margin-bottom: 0.9rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }

        .detail-label {
            font-size: 0.88rem;
            font-weight: 700;
            color: #6B7280;
            margin-bottom: 0.35rem;
        }

        .detail-value {
            color: #222222;
            line-height: 1.65;
            white-space: pre-wrap;
        }

        .timeline-item {
            padding: 1rem 1.2rem;
            border-radius: 14px;
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #6C8EBF;
            margin-bottom: 0.8rem;
        }

        .timeline-date {
            font-size: 0.9rem;
            color: #6B7280;
            margin-bottom: 0.2rem;
        }

        .timeline-type {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .timeline-description {
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .delete-warning {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            background-color: #FFF1F2;
            border: 1px solid #FECDD3;
            margin-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 페이지 제목
# ---------------------------------------------------------
st.markdown(
    '<div class="page-title">🔎 증례 조회 및 수정</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        저장된 증례를 검색하고, 상세 내용을 확인하거나 수정·삭제할 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 연결 확인
# ---------------------------------------------------------
if not SHEET_URL:
    st.error(
        "Streamlit Secrets에 SHEET_URL이 없습니다. "
        "Google Apps Script 웹앱 주소를 먼저 설정해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 전체 증례 목록 불러오기
# ---------------------------------------------------------
with st.spinner("저장된 증례 목록을 불러오는 중입니다."):
    cases = get_cases()

if not cases:
    st.warning(
        "저장된 증례가 없습니다. 먼저 '새 증례 등록' 페이지에서 "
        "증례를 등록해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 검색 및 증례 선택
# ---------------------------------------------------------
st.subheader("1. 증례 선택")

search_keyword = st.text_input(
    "증례 검색",
    placeholder=(
        "증례번호, 비식별 환자코드, 진단명, 병변 위치 또는 주소를 입력하세요."
    ),
)

filtered_cases = cases

if search_keyword.strip():
    keyword = search_keyword.strip().lower()

    filtered_cases = [
        case
        for case in cases
        if keyword
        in " ".join(
            [
                str(case.get("case_id", "")),
                str(case.get("patient_code", "")),
                str(case.get("chief_complaint", "")),
                str(case.get("clinical_diagnosis", "")),
                str(case.get("pathologic_diagnosis", "")),
                str(case.get("lesion_site", "")),
            ]
        ).lower()
    ]

if not filtered_cases:
    st.warning("검색 조건에 해당하는 증례가 없습니다.")
    st.stop()

case_map = {
    make_case_label(case): case
    for case in filtered_cases
}

selected_label = st.selectbox(
    "조회할 증례",
    options=list(case_map.keys()),
)

selected_case_summary = case_map[selected_label]
selected_case_id = selected_case_summary.get("case_id", "")


# ---------------------------------------------------------
# 선택한 증례 상세 불러오기
# ---------------------------------------------------------
with st.spinner("증례 상세 정보를 불러오는 중입니다."):
    selected_case = get_case(selected_case_id)

if not selected_case:
    st.stop()


# ---------------------------------------------------------
# 상단 요약
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="summary-card">
        <strong>증례 고유번호</strong> · {safe_text(selected_case.get("case_id"))}<br>
        <strong>비식별 환자코드</strong> · {safe_text(selected_case.get("patient_code"))}<br>
        <strong>나이 / 성별</strong> · {safe_text(selected_case.get("age"))}세 /
        {safe_text(selected_case.get("sex"))}<br>
        <strong>주소</strong> · {safe_text(selected_case.get("chief_complaint"))}<br>
        <strong>병변 위치</strong> · {safe_text(selected_case.get("lesion_site"))}
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 탭 구성
# ---------------------------------------------------------
detail_tab, edit_tab, timeline_tab, delete_tab = st.tabs(
    [
        "📄 상세 정보",
        "✏️ 증례 수정",
        "🗓️ 타임라인",
        "🗑️ 증례 삭제",
    ]
)


# =========================================================
# 상세 정보 탭
# =========================================================
with detail_tab:
    st.subheader("증례 상세 정보")

    first_col, second_col = st.columns(2)

    with first_col:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">증례 고유번호</div>
                <div class="detail-value">{safe_text(selected_case.get("case_id"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">내원 당시 나이</div>
                <div class="detail-value">{safe_text(selected_case.get("age"))}세</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">환자의 주소</div>
                <div class="detail-value">{safe_text(selected_case.get("chief_complaint"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">임상 진단명</div>
                <div class="detail-value">{safe_text(selected_case.get("clinical_diagnosis"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with second_col:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">비식별 환자코드</div>
                <div class="detail-value">{safe_text(selected_case.get("patient_code"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">성별</div>
                <div class="detail-value">{safe_text(selected_case.get("sex"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">병변 위치</div>
                <div class="detail-value">{safe_text(selected_case.get("lesion_site"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">병리 진단명</div>
                <div class="detail-value">{safe_text(selected_case.get("pathologic_diagnosis"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    long_text_fields = [
        ("임상 요약", "clinical_summary"),
        ("영상 소견 요약", "imaging_summary"),
        ("치료 요약", "treatment_summary"),
        ("경과 및 추적관찰", "outcome_followup"),
        ("발표에서 강조하고 싶은 점", "presentation_point"),
    ]

    for label, field_name in long_text_fields:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">{label}</div>
                <div class="detail-value">{safe_text(selected_case.get(field_name))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 수정 탭
# =========================================================
with edit_tab:
    st.subheader("증례 정보 수정")

    st.info(
        "증례 고유번호와 비식별 환자코드는 연결 기준이므로 수정할 수 없습니다."
    )

    with st.form(
        f"edit_case_form_{selected_case_id}",
        clear_on_submit=False,
    ):
        id_col1, id_col2 = st.columns(2)

        with id_col1:
            st.text_input(
                "증례 고유번호",
                value=str(selected_case.get("case_id", "")),
                disabled=True,
            )

        with id_col2:
            st.text_input(
                "비식별 환자코드",
                value=str(selected_case.get("patient_code", "")),
                disabled=True,
            )

        basic_col1, basic_col2 = st.columns(2)

        with basic_col1:
            edited_age = st.number_input(
                "내원 당시 나이",
                min_value=0,
                max_value=120,
                value=normalize_age(selected_case.get("age")),
                step=1,
            )

        with basic_col2:
            sex_options = [
                "남성",
                "여성",
                "기타",
                "미상",
            ]

            current_sex = str(
                selected_case.get("sex", "미상")
            )

            if current_sex not in sex_options:
                current_sex = "미상"

            edited_sex = st.selectbox(
                "성별",
                options=sex_options,
                index=sex_options.index(current_sex),
            )

        edited_chief_complaint = st.text_input(
            "환자의 주소 (Chief Complaint)",
            value=str(
                selected_case.get(
                    "chief_complaint",
                    "",
                )
            ),
        )

        diagnosis_col1, diagnosis_col2 = st.columns(2)

        with diagnosis_col1:
            edited_clinical_diagnosis = st.text_input(
                "임상 진단명",
                value=str(
                    selected_case.get(
                        "clinical_diagnosis",
                        "",
                    )
                ),
            )

        with diagnosis_col2:
            edited_pathologic_diagnosis = st.text_input(
                "병리 진단명",
                value=str(
                    selected_case.get(
                        "pathologic_diagnosis",
                        "",
                    )
                ),
            )

        edited_lesion_site = st.text_input(
            "병변 위치",
            value=str(
                selected_case.get(
                    "lesion_site",
                    "",
                )
            ),
        )

        edited_clinical_summary = st.text_area(
            "임상 요약",
            value=str(
                selected_case.get(
                    "clinical_summary",
                    "",
                )
            ),
            height=140,
        )

        edited_imaging_summary = st.text_area(
            "영상 소견 요약",
            value=str(
                selected_case.get(
                    "imaging_summary",
                    "",
                )
            ),
            height=140,
        )

        edited_treatment_summary = st.text_area(
            "치료 요약",
            value=str(
                selected_case.get(
                    "treatment_summary",
                    "",
                )
            ),
            height=120,
        )

        edited_outcome_followup = st.text_area(
            "경과 및 추적관찰",
            value=str(
                selected_case.get(
                    "outcome_followup",
                    "",
                )
            ),
            height=120,
        )

        edited_presentation_point = st.text_area(
            "발표에서 강조하고 싶은 점",
            value=str(
                selected_case.get(
                    "presentation_point",
                    "",
                )
            ),
            height=120,
        )

        update_submitted = st.form_submit_button(
            "수정 내용 저장",
            type="primary",
            use_container_width=True,
        )

    if update_submitted:
        required_fields = []

        if not edited_chief_complaint.strip():
            required_fields.append("환자의 주소")

        if not edited_lesion_site.strip():
            required_fields.append("병변 위치")

        if required_fields:
            st.error(
                "다음 필수 항목을 입력해 주세요: "
                + ", ".join(required_fields)
            )

        else:
            update_data = {
                "action": "case_update",
                "case_id": selected_case_id,
                "age": int(edited_age),
                "sex": edited_sex,
                "chief_complaint": edited_chief_complaint.strip(),
                "clinical_diagnosis": edited_clinical_diagnosis.strip(),
                "pathologic_diagnosis": edited_pathologic_diagnosis.strip(),
                "lesion_site": edited_lesion_site.strip(),
                "clinical_summary": edited_clinical_summary.strip(),
                "imaging_summary": edited_imaging_summary.strip(),
                "treatment_summary": edited_treatment_summary.strip(),
                "outcome_followup": edited_outcome_followup.strip(),
                "presentation_point": edited_presentation_point.strip(),
            }

            with st.spinner("수정된 내용을 저장하고 있습니다."):
                result = api_post(update_data)

            if result.get("success"):
                st.success("증례 정보가 수정되었습니다.")
                st.rerun()
            else:
                st.error(
                    result.get(
                        "message",
                        "증례 수정 중 오류가 발생했습니다.",
                    )
                )


# =========================================================
# 타임라인 탭
# =========================================================
with timeline_tab:
    st.subheader("연결된 타임라인")

    with st.spinner("타임라인을 불러오는 중입니다."):
        timeline = get_timeline(selected_case_id)

    if not timeline:
        st.info(
            "이 증례에 등록된 타임라인이 없습니다. "
            "'타임라인 작성' 페이지에서 사건을 추가해 주세요."
        )

    else:
        timeline_df = pd.DataFrame(timeline)

        timeline_df["event_date"] = pd.to_datetime(
            timeline_df["event_date"],
            errors="coerce",
        )

        timeline_df = timeline_df.sort_values(
            by=["event_date", "timeline_id"],
            ascending=True,
        ).reset_index(drop=True)

        for _, row in timeline_df.iterrows():
            if pd.isna(row.get("event_date")):
                event_date_text = "-"
            else:
                event_date_text = row["event_date"].strftime(
                    "%Y-%m-%d"
                )

            event_type_text = safe_text(
                row.get("event_type")
            )

            description_text = safe_text(
                row.get("event_description")
            )

            st.markdown(
                f"""
                <div class="timeline-item">
                    <div class="timeline-date">{event_date_text}</div>
                    <div class="timeline-type">{event_type_text}</div>
                    <div class="timeline-description">{description_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("표 형태로 보기"):
            display_df = timeline_df.copy()

            display_df["날짜"] = display_df[
                "event_date"
            ].dt.strftime("%Y-%m-%d")

            display_df = display_df[
                [
                    "날짜",
                    "event_type",
                    "event_description",
                ]
            ].rename(
                columns={
                    "event_type": "유형",
                    "event_description": "내용",
                }
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# 삭제 탭
# =========================================================
with delete_tab:
    st.subheader("증례 삭제")

    st.markdown(
        """
        <div class="delete-warning">
            <strong>주의</strong><br><br>
            증례를 삭제하면 해당 증례와 연결된 모든 타임라인 항목도 함께 삭제됩니다.
            삭제한 데이터는 웹앱에서 복구할 수 없습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    delete_check = st.checkbox(
        "위 내용을 확인했으며, 이 증례를 삭제하겠습니다.",
        key=f"delete_check_{selected_case_id}",
    )

    delete_confirm_text = st.text_input(
        "삭제 확인을 위해 증례 고유번호를 입력하세요.",
        placeholder=selected_case_id,
        key=f"delete_confirm_{selected_case_id}",
    )

    delete_button = st.button(
        "증례와 타임라인 전체 삭제",
        type="primary",
        use_container_width=True,
        disabled=not delete_check,
    )

    if delete_button:
        if delete_confirm_text.strip() != selected_case_id:
            st.error(
                "입력한 증례 고유번호가 일치하지 않습니다."
            )

        else:
            with st.spinner(
                "증례와 연결된 타임라인을 삭제하고 있습니다."
            ):
                result = api_post(
                    {
                        "action": "case_delete",
                        "case_id": selected_case_id,
                    }
                )

            if result.get("success"):
                deleted_count = result.get(
                    "deleted_timeline_count",
                    0,
                )

                st.success(
                    f"증례가 삭제되었습니다. "
                    f"함께 삭제된 타임라인 항목: {deleted_count}개"
                )

                st.session_state.pop(
                    f"delete_check_{selected_case_id}",
                    None,
                )

                st.session_state.pop(
                    f"delete_confirm_{selected_case_id}",
                    None,
                )

                st.rerun()

            else:
                st.error(
                    result.get(
                        "message",
                        "증례 삭제 중 오류가 발생했습니다.",
                    )
                )
