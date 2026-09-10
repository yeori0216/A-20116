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

# [4 & 5. 구역 나누기 및 그래프 그리기]
# 메인 화면 구역 설정 (추후 다른 그래프 추가를 위한 구역 분리)
st.subheader(f"📊 [{selected_movie}] 일별 관객수 추이")

# Plotly 선 그래프 생성
fig = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} - 기준일자별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
    markers=True,  # 데이터 포인트에 점 표시
)

# 그래프 레이아웃 커스텀
fig.update_layout(hovermode="x unified")

# Streamlit에 Plotly 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# [5. 그래프 설명 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 초기 관객수 집중도와 이후 관객수 감소/유지 추세를 한눈에 파악할 수 있습니다."
)

st.divider()

# [추후 그래프 추가 구역 예시]
# st.subheader("📊 추가 그래프 영역")
# st.write("여기에 새로운 분석 그래프를 추가할 수 있습니다.")
