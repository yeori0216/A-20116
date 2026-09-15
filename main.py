import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 TOP 10에 진입한 주요 개봉 영화 216편의 데이터를 분석합니다."
)


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 전처리: 첫 번째 장르만 추출 (세로막대 기호 '|' 기준 구분)
    df["primary_genre"] = df["genre"].fillna("미상").apply(lambda x: x.split("|")[0])

    return df


df = load_data()

st.divider()

# ----------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# ----------------------------------------------------
st.subheader("1. 장르별 영화 편수 비율")

# 장르별 빈도수 계산
genre_counts = df["primary_genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

# Plotly 도넛 그래프 생성
fig_donut = px.pie(
    genre_counts,
    values="count",
    names="genre",
    hole=0.4,
    title="장르별 영화 편수 분포",
)

# 마우스오버(Hover) 시 편수와 비율 표기 설정
fig_donut.update_traces(
    hoverinfo="label+value+percent",
    textinfo="percent+label",
    hovertemplate="<b>장르: %{label}</b><br>영화 수: %{value}편<br>비율: %{percent}",
)

st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 해석 안내 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르에 영화 개봉 편수가 쏠려 있는지, 전체적인 장르 다양성의 분포가 어떻게 형성되어 있는지 파악할 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 2. 장르 및 영화별 총 관객 수 (트리맵)
# ----------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 트리맵")

# Plotly 트리맵 그래프 생성 (계층 구조: primary_genre -> movieNm)
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "primary_genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 (칸 크기 = 총 관객 수)",
)

# 마우스오버(Hover) 시 영화명과 총 관객 수 표기 설정
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 해석 안내 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 어떤 장르가 흥행 관객의 대부분을 점유하는지, 그리고 특정 장르 내에서 특정 흥행작 한 두 편이 관객 수를 독식하고 있는지 한눈에 비교할 수 있습니다."
)
