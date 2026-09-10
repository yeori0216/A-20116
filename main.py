import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# 누적관객수가 높은 순서대로 전체 영화 목록 추출 (중복 제거)
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
# [세 번째 그래프: TOP10 20일 이상 등장 영화 중 TOP 5 누적 관객수 비교 (다중 선 그래프)]
# -------------------------------------------------------------------
st.subheader("🏆 3. 장기 흥행(TOP10 20일 이상) TOP 5 영화 누적 관객수 비교")

# 1) 영화별 TOP10 등장 일수 및 최고 누적관객수 계산
movie_stats = df.groupby("영화명").agg(
    top10_days=("기준일자", "count"),  # TOP10 등장 일수
    max_cum_audience=("누적관객수", "max"),  # 최대 누적관객수
)

# 2) TOP10 등장 일수가 20일 이상인 영화만 필터링 후, 누적관객수 기준 내림차순 정렬
filtered_movies = movie_stats[movie_stats["top10_days"] >= 20].sort_values(
    by="max_cum_audience", ascending=False
)

# 3) 상위 5개 영화명 추출
top5_long_run_movies = filtered_movies.head(5).index.tolist()

# 4) 해당 5개 영화 데이터만 전체 데이터셋에서 추출
top5_df = df[df["영화명"].isin(top5_long_run_movies)]

# Plotly 다중 선 그래프 생성 (color='영화명'으로 영화별 다른 색상 및 범례 자동 표시)
fig_top5 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP10 20일 이상 차트인 영화 중 누적관객수 TOP 5의 추이 비교",
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
    "💡 **이 그래프로 알 수 있는 것:** 단기 반짝 흥행이 아닌 최소 20일 이상 박스오피스 상위권(TOP10)을 지킨 롱런 흥행작들 간의 누적 관객수 증가 속도와 최종 성적을 정밀하게 비교할 수 있습니다."
)

st.divider()


# -------------------------------------------------------------------
# [네 번째 그래프: 전체 박스오피스 관객수 7일 이동평균선]
# -------------------------------------------------------------------
st.subheader("📉 4. 전체 극장가 관객수 흐름 (7일 이동평균)")

# 1) 기준일자별 TOP10 영화 전체의 해당일관객수 합계 계산
daily_total = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2) 7일 이동평균 계산 (rolling window=7)
daily_total["7일_이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
)

# 3) Plotly graph_objects를 활용해 연한 일일 합계선과 진한 이동평균선 시각화
fig_ma = go.Figure()

# 원본 일일 총 관객수 (연한 반투명 파란색 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일일 관객수 합계",
        line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5),  # 연하고 얇은 선
    )
)

# 7일 이동평균선 (진한 붉은색 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="crimson", width=3),  # 진하고 두꺼운 선
    )
)

# 레이아웃 설정
fig_ma.update_layout(
    title="전체 박스오피스 TOP10 일일 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객수(명)",
    hovermode="x unified",
)

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_ma, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 평일과 주말 간의 심한 관객수 편차(노이즈)를 7일 이동평균으로 완화하여, 전체 극장가의 성수기/비수기 시즌성 흐름과 전반적인 시장 규모 변화를 한눈에 파악할 수 있습니다."
)

st.divider()


# -------------------------------------------------------------------
# [다섯 번째 그래프: 월별 전체 관객수 합계 (막대그래프)]
# -------------------------------------------------------------------
st.subheader("📊 5. 월별 전체 관객수 합계")

# 1) 기준일자에서 '연-월(YYYY-MM)' 형태의 컬럼 생성
daily_total["연월"] = daily_total["기준일자"].dt.to_period("M").astype(str)

# 2) 월(연월) 단위로 다시 그룹화하여 전체 관객수 합계 계산
monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3) Plotly 막대그래프 생성
fig_monthly = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 극장가 총 관객수 합계 비교",
    labels={"연월": "월(Year-Month)", "해당일관객수": "월 총 관객수(명)"},
    text_auto=".2s",  # 막대 위에 축약 형태의 수치 표시 (예: 1.5M)
)

# 레이아웃 커스텀
fig_monthly.update_traces(
    marker_color="royalblue", textposition="outside"
)
fig_monthly.update_layout(xaxis_type="category")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_monthly, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월에 총 관객수가 가장 많았는지 비교하여, 극장가의 월별 성수기/비수기 매출 및 흥행 집계 규모를 직관적으로 파악할 수 있습니다."
)

st.divider()


# -------------------------------------------------------------------
# [여섯 번째 그래프: 캘린더 히트맵 (주차별 x 요일별 관객수)]
# -------------------------------------------------------------------
st.subheader("🗓️ 6. 캘린더 히트맵 (주차 x 요일별 관객수)")

# 1) 날짜 관련 파생 컬럼 생성
cal_df = daily_total.copy()
cal_df["날짜_str"] = cal_df["기준일자"].dt.strftime("%Y-%m-%d")

# 요일 한글 변환 및 순서 지정 (월요일 ~ 일요일)
day_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
cal_df["요일_num"] = cal_df["기준일자"].dt.weekday
cal_df["요일"] = cal_df["요일_num"].map(day_map)

# 연월 및 주차 컬럼 (X축 레이블용)
cal_df["주차"] = cal_df["기준일자"].dt.strftime("%Y-%m (%W주차)")

# 2) 요일 순서 보장을 위한 정렬 처리
days_order = ["월", "화", "수", "목", "금", "토", "일"]

# 3) Plotly Express density_heatmap 생성
fig_cal = px.density_heatmap(
    cal_df,
    x="주차",
    y="요일",
    z="해당일관객수",
    category_orders={"요일": days_order},  # 월요일부터 일요일 순서 고정
    color_continuous_scale="Reds",  # 관객수가 많을수록 진한 붉은색
    title="주차별/요일별 극장가 관객수 분포 히트맵",
    labels={
        "주차": "월 및 주차",
        "요일": "요일",
        "해당일관객수": "일일 관객수(명)",
    },
    hover_data={
        "주차": False,
        "요일": False,
        "날짜_str": True,  # 마우스 호버 시 yyyy-mm-dd 표시
        "해당일관객수": ":,명",  # 천 단위 쉼표 포맷팅
    },
)

# 툴팁(Hover) 레이블 커스텀
fig_cal.update_traces(
    hovertemplate="<b>날짜: %{customdata[0]}</b><br>관객수: %{z:,}명<extra></extra>"
)

fig_cal.update_layout(xaxis_type="category")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig_cal, use_container_width=True)

# 그래프 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 주말(토·일)과 평일 간의 요일별 관객 차이는 물론, 특정 연휴나 성수기 주차에 관객이 얼마나 집중되었는지 달력 형태의 진함 정도로 한눈에 파악할 수 있습니다."
)
