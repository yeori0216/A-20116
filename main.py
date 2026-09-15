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

st.divider()

# ----------------------------------------------------
# 3. 총 관객 수 분포 (히스토그램)
# ----------------------------------------------------
st.subheader("3. 총 관객 수 분포 히스토그램")

# Plotly 히스토그램 생성
fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포 구간",
    labels={"total_audi": "총 관객 수 (명)"},
)

fig_hist.update_layout(
    xaxis_title="총 관객 수 (명)",
    yaxis_title="영화 수 (편)",
    bargap=0.1,
)

fig_hist.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)

st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 정보 자동 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

# 그래프 해석 및 분석 문구 안내 영역
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 **0~200만 명 미만 구간**에 압도적으로 몰려 있으며, "
    f"오른쪽으로 갈수록 편수가 급격히 줄어드는 롱테일 분포를 보입니다. "
    f"이 중 가장 많은 관객을 모은 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)

st.divider()

# ----------------------------------------------------
# 4. 개봉일 스크린수 vs 총 관객수 (산점도)
# ----------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

# Plotly 산점도 생성
fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="primary_genre",
    hover_name="movieNm",
    title="개봉일 스크린 수(first_scrn) vs 총 관객 수(total_audi)",
    labels={
        "first_scrn": "개봉일 스크린 수 (개)",
        "total_audi": "총 관객 수 (명)",
        "primary_genre": "장르",
    },
)

fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>"
)

fig_scatter.update_layout(
    xaxis_title="개봉일 스크린 수 (개)",
    yaxis_title="총 관객 수 (명)",
)

st.plotly_chart(fig_scatter, use_container_width=True)

# 그래프 해석 안내 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많을수록 대체로 총 관객 수가 늘어나는 양의 상관관계를 보이나, 스크린 수가 적음에도 높은 관객 수를 기록한 흥행 이탈작이나 그 반대의 사례도 장르별로 확인할 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 5. 주요 장르별 총 관객 수 상자 그림 (박스플롯)
# ----------------------------------------------------
st.subheader("5. 주요 장르별 총 관객 수 박스플롯")

# 영화가 10편 이상 포함된 장르 필터링
genre_counts_series = df["primary_genre"].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df["primary_genre"].isin(major_genres)]

# Plotly 박스플롯 생성
fig_box = px.box(
    df_filtered,
    x="primary_genre",
    y="total_audi",
    color="primary_genre",
    hover_data=["movieNm"],
    points="outliers",  # 이상치 점 표기
    title="영화 수 10편 이상 주요 장르별 총 관객 수 분포",
    labels={
        "primary_genre": "장르",
        "total_audi": "총 관객 수 (명)",
        "movieNm": "영화명",
    },
)

fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수 (명)",
    showlegend=False,
)

st.plotly_chart(fig_box, use_container_width=True)

# 그래프 해석 안내 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 장르별 중간값(중앙선)을 통해 평균적인 흥행 규모를 비교할 수 있으며, 상자 밖으로 점으로 돌출된 대형 흥행 이탈작(Outlier)의 존재 유무와 흥행 편차를 확인할 수 있습니다."
)
