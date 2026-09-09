import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="어제 박스오피스 대시보드", page_icon="🎬", layout="wide"
)


# API 데이터를 1시간(3600초) 동안 메모리에 캐싱(기억)하는 함수
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date, api_key):
    """KOBIS API를 호출하여 해당 날짜의 일별 박스오피스 데이터를 가져옵니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        # API 요청 보내기 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)

        # HTTP 응답 상태 코드가 200이 아닌 경우 예외 발생
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"

        data = response.json()

        # 1. API 자체 에러 처리 (인증키 오류 등: faultInfo 응답 확인)
        if "faultInfo" in data:
            error_msg = data["faultInfo"].get(
                "message", "알 수 없는 오류가 발생했습니다."
            )
            return None, f"API 오류 발생: {error_msg}"

        # 2. 박스오피스 결과 확인
        box_office_result = data.get("boxOfficeResult", {})
        movie_list = box_office_result.get("dailyBoxOfficeList", [])

        # 3. 데이터가 비어 있는 경우 처리
        if not movie_list:
            return None, "해당 날짜의 박스오피스 데이터가 비어 있습니다."

        return movie_list, None

    except requests.exceptions.RequestException as e:
        # 네트워크 오류 등 예외 발생 시 처리
        return None, f"네트워크 요청 중 오류가 발생했습니다: {str(e)}"


def main():
    st.title("🎬 어제 일별 박스오피스 TOP 10")

    # Streamlit Secrets에서 KOBIS_KEY 불러오기
    if "KOBIS_KEY" not in st.secrets:
        st.error("🔑 인증키(KOBIS_KEY)가 설정되지 않았습니다.")
        st.info(
            """
        **확인해 주세요:**
        1. Local 실행 시: `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = "발급받은 키"`를 입력했는지 확인하세요.
        2. Streamlit Cloud 배포 시: 앱 설정의 **App settings > Secrets** 메뉴에 `KOBIS_KEY`를 등록했는지 확인하세요.
        """
        )
        return

    api_key = st.secrets["KOBIS_KEY"]

    # 배포 서버 시계 기준이 아닌 '한국 시간(Asia/Seoul)' 기준으로 어제 날짜 계산
    korea_tz = pytz.timezone("Asia/Seoul")
    now_korea = datetime.datetime.now(korea_tz)
    yesterday = now_korea - datetime.timedelta(days=1)
    target_date = yesterday.strftime("%Y%m%d")
    formatted_date = yesterday.strftime("%Y년 %m월 %d일")

    st.caption(f"📅 기준 날짜: {formatted_date} (한국 시간 기준 어제)")

    # API 데이터 불러오기
    movie_data, error_message = fetch_box_office_data(target_date, api_key)

    # 데이터 호출 실패 시 안내 문구 출력
    if error_message:
        st.error("⚠️ 데이터를 불러오지 못했습니다.")
        st.warning(f"**원인:** {error_message}")
        st.info(
            """
        **확인 및 해결 방법:**
        - 입력된 KOBIS API 인증키가 유효한지 확인해 주세요.
        - [KOBIS 영화관입장권통합전산망 Open API](https://www.kobis.or.kr/kobisopenapi) 사이트의 서비스 상태를 확인해 주세요.
        - 일일 호출 수량이 초과되지 않았는지 확인해 주세요.
        """
        )
        return

    # 데이터프레임(Dataframe)으로 변환
    df = pd.DataFrame(movie_data)

    # 문자열로 들어오는 수치형 데이터를 숫자형(int) 데이터로 변환
    numeric_columns = [
        "rank",
        "rankInten",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "showCnt",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 순위 기준으로 오름차순 정렬
    df = df.sort_values(by="rank", ascending=True)

    # --------------------------------------------------
    # 1. 상단 1위 영화 지표 카드 3개 표시
    # --------------------------------------------------
    top_1_movie = df.iloc[0]

    st.markdown("---")
    st.subheader(f"🥇 1위 영화: {top_1_movie['movieNm']}")

    col1, col2, col3 = st.columns(3)

    # 관객수 증감 표시용 텍스트 만들기
    rank_inten = top_1_movie["rankInten"]
    delta_str = (
        f"{rank_inten} 계단 상승"
        if rank_inten > 0
        else (f"{abs(rank_inten)} 계단 하락" if rank_inten < 0 else "순위 변동 없음")
    )

    with col1:
        st.metric(
            label="어제 관객수",
            value=f"{top_1_movie['audiCnt']:,} 명",
            delta=delta_str,
        )
    with col2:
        st.metric(label="누적 관객수", value=f"{top_1_movie['audiAcc']:,} 명")
    with col3:
        st.metric(label="스크린수", value=f"{top_1_movie['scrnCnt']:,} 개")

    st.markdown("---")

    # --------------------------------------------------
    # 2. 관객수 상위 5편 막대그래프
    # --------------------------------------------------
    st.subheader("📊 관객수 상위 5개 영화")
    top_5_df = df.head(5)

    # Streamlit 기본 막대그래프 사용 (x축: 영화명, y축: 어제 관객수)
    chart_data = top_5_df.set_index("movieNm")[["audiCnt"]]
    chart_data.columns = ["어제 관객수"]
    st.bar_chart(chart_data)

    st.markdown("---")

    # --------------------------------------------------
    # 3. 전체 TOP 10 데이터 표(Table) 표시
    # --------------------------------------------------
    st.subheader("📋 박스오피스 순위표")

    # 화면에 보여줄 컬럼 선택 및 이름 변경
    display_df = df[
        ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
    ].copy()
    display_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "관객수(명)",
        "누적관객수(명)",
        "스크린수(개)",
    ]

    # 표 출력 (숫자 세 자릿수 콤마 서식 적용)
    st.dataframe(
        display_df.style.format(
            {"관객수(명)": "{:,}", "누적관객수(명)": "{:,}", "스크린수(개)": "{:,}"}
        ),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
