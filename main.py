import pandas as pd
import plotly.express as px
import streamlit as st

# [설정] 웹페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="영화 박스오피스 분석 앱", layout="wide")


# [1. 데이터 불러오기]
# @st.cache_data를 사용하면 데이터를 한 번만 불러오고 캐시에 저장하여 앱 속도를 크게 향상시킵니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 값)가 있는 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 날짜 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # '기준일자' 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드
df = load_data()

# 앱 메인 제목
st.title("🎬 박스오피스 데이터 분석 웹앱")
st.write("영화별 관객수 변화 추이를 확인해보세요.")
st.divider()

# [3. 영화 선택 기능]
# 누적관객수가 높은 순서대로 영화 목록 추출 (중복 제거)
# 영화별 maximum 누적관객수를 기준으로 정렬합니다.
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에 영화 선택 드롭다운 메뉴 생성
st.sidebar.header("🔍 검색 옵션")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요 (누적관객수순)", options=movie_order
)

# 선택한 영화 데이터만 필터링
filtered_df = df[df["영화명"] == selected_movie]


# -------------------------------------------------------------------
# [첫 번째 그래프: 개별 영화 일별 관객수 추이 (선 그래프)]
# -------------------------------------------------------------------
st.subheader(f"📊 1. [{selected_movie}] 일별 관객수 추이")

# Plotly 선 그래프 생성
fig_daily = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} - 기준일자별 일일 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
    markers=True,  # 데이터 포인트에 점 표시
)

# 그래프 레이아웃 커스텀
fig_daily.update_layout(hovermode="x unified")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_daily, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 초기 일일 관객수 집중도와 이후 관객수 감소/유지 추세를 한눈에 파악할 수 있습니다."
)

st.divider()


# -------------------------------------------------------------------
# [두 번째 그래프: 개별 영화 누적 관객수 추이 (영역 차트)]
# -------------------------------------------------------------------
st.subheader(f"📈 2. [{selected_movie}] 누적 관객수 추이")

# Plotly 영역 차트(area chart) 생성
fig_cum = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} - 기준일자별 누적 관객수 증가 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
)

# 그래프 레이아웃 커스텀
fig_cum.update_layout(hovermode="x unified")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_cum, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 영화 상영 기간 동안 전체 관객수가 누적되어 증가하는 곡선의 경사(성장 속도)와 최종 흥행 규모를 파악할 수 있습니다."
)

st.divider()


# -------------------------------------------------------------------
# [세 번째 그래프: TOP 5 영화 누적 관객수 비교 (다중 선 그래프)]
# -------------------------------------------------------------------
st.subheader("🏆 3. 누적관객수 TOP 5 영화 비교")

# 누적관객수 상위 5개 영화 목록 추출
top5_movies = movie_order[:5]

# 전체 데이터에서 TOP 5 영화에 해당하는 데이터만 필터링
top5_df = df[df["영화명"].isin(top5_movies)]

# Plotly 다중 선 그래프 생성 (color='영화명'으로 영화별 다른 색상 및 범례 자동 생성)
fig_top5 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="누적관객수 TOP 5 영화의 기준일자별 관객수 증가 비교",
    labels={
        "기준일자": "날짜",
        "누적관객수": "누적 관객수(명)",
        "영화명": "영화 제목",
    },
)

# 그래프 레이아웃 커스텀
fig_top5.update_layout(hovermode="x unified")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_top5, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 가장 흥행한 상위 5개 영화들의 누적 관객수 증가 추이를 비교하여, 개봉 시기별 경쟁 구도와 흥행 속도 차이를 한눈에 비교 분석할 수 있습니다."
)
