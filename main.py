import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (환경에 맞게 선택/설정)
plt.rc("font", family="Malgun Gothic")  # Windows: Malgun Gothic / Mac: AppleGothic
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# 서브플롯 설정 또는 단독 그래프 생성
fig, ax = plt.subplots(figsize=(12, 6))

# 8번째 그래프: 장르별 Top 10 랭킹 유지 기간 박스플롯
sns.boxplot(data=df, x="genre", y="days_in_top10", ax=ax, palette="Set2")

# 제목 지정 ('박스플롯' 문구 제외)
ax.set_title("8. 장르별 Top 10 랭킹 유지 기간", fontsize=14, fontweight="bold")
ax.set_xlabel("장르", fontsize=12)
ax.set_ylabel("유지 기간 (일)", fontsize=12)

# 레이아웃 정돈 및 그래프 출력
plt.tight_layout()
plt.show()
