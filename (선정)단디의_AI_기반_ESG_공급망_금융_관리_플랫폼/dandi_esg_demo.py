"""
별도의 복잡한 라이브러리를 설치하다가 오류가 나서 곤란해지지 않도록, 
파이썬에 기본 탑재된 Tkinter 라이브러리만을 사용하여 제작했습니다. 
파이참(PyCharm) 등 파이썬 환경에서 코드를 그대로 복사해 실행(Run)하시면, 
슬라이더를 조절하며 금리가 실시간으로 계산되고 
설명 가능한 AI(SHAP) 분석 그래프와 마스코트 '단디'의 칭찬 메시지까지 
역동적으로 작동하는 진짜 앱 창이 뜹니다.
"""

######################################

import tkinter as tk
from tkinter import messagebox, ttk

# =====================================================================
# [핵심 알고리즘] AI 가상 모델 및 SHAP 기여도 분석 엔진
# =====================================================================
def evaluate_esg_finance(energy_saving, employment, governance_yn):
    """
    [2단계 & 3단계 파이프라인 시뮬레이션]
    실제 AI 모델(예: Random Forest) 대신 작동하는 가상의 선형 모델입니다.
    기본 금리(Base Rate) 6.0%에서 출발하여 ESG 성과에 따라 금리를 인하합니다.
    """
    base_rate = 6.0
    
    # 1. 각 요인별 금리 인하 기여도 (SHAP Value 시뮬레이션) 계산
    # [E] 에너지 절감 1%당 0.04% 금리 인하 (최대 2.0% 인하)
    shap_e = round(min(energy_saving * 0.04, 2.0), 2)
    
    # [S] 취약계층 고용 1명당 0.2% 금리 인하 (최대 2.0% 인하)
    shap_s = round(min(employment * 0.2, 2.0), 2)
    
    # [G] 투명 회계 공시 여부에 따라 1.5% 금리 인하
    shap_g = 1.5 if governance_yn else 0.0
    
    # 2. 최종 우대 금리 및 산출 금리 계산
    total_discount = round(shap_e + shap_s + shap_g, 2)
    final_rate = round(max(0.5, base_rate - total_discount), 2) # 최저 금리 하한선 0.5%
    
    # ESG 종합 점수 산출 (100점 만점 기준 환산)
    esg_score = int(min(100, (shap_e / 2.0 * 35) + (shap_s / 2.0 * 35) + (shap_g / 1.5 * 30)))
    
    return final_rate, total_discount, esg_score, shap_e, shap_s, shap_g


# =====================================================================
# 버튼 클릭 시 실행되는 이벤트 핸들러 (UI 제어)
# =====================================================================
def on_calculate():
    # 1단계: 사용자 입력 데이터 수집
    try:
        energy_saving = float(scale_energy.get())
        employment = int(scale_employ.get())
        governance_yn = var_gov.get()
    except ValueError:
        messagebox.showerror("입력 오류", "올바른 값을 선택해 주세요.")
        return

    # 2&3단계: AI 연산 및 SHAP 기여도 도출
    final_rate, total_discount, esg_score, shap_e, shap_s, shap_g = evaluate_esg_finance(
        energy_saving, employment, governance_yn
    )
    
    # 4단계: 결과 화면 시각화 업데이트
    lbl_score.config(text=f"{esg_score}점", fg="#2ECC71" if esg_score >= 70 else "#F39C12")
    lbl_rate.config(text=f"{final_rate:.2f}% (총 -{total_discount:.2f}%p 우대)")
    
    # SHAP 분석 결과 그래프 업데이트 (막대 길이 조절)
    progress_e["value"] = (shap_e / 2.0) * 100
    progress_s["value"] = (shap_s / 2.0) * 100
    progress_g["value"] = (shap_g / 1.5) * 100
    
    lbl_shap_e.config(text=f"-{shap_e:.2f}%p")
    lbl_shap_s.config(text=f"-{shap_s:.2f}%p")
    lbl_shap_g.config(text=f"-{shap_g:.2f}%p")
    
    # 단디 비서의 설명 가능한 AI(XAI) 분석 및 맞춤 피드백 말풍선 생성
    contributions = {
        "에너지 절감 노력": shap_e,
        "사회적 취약계층 고용": shap_s,
        "투명한 회계 경영": shap_g
    }
    
    # 가장 큰 공헌을 한 요인(SHAP 기여도가 최고인 변수) 찾기
    best_factor = max(contributions, key=contributions.get)
    best_value = contributions[best_factor]
    
    if total_discount == 0:
        dandi_msg = "대표님! 아직 등록된 ESG 경영 내역이 없어요.\n간단한 항목부터 단디와 함께 채워나가 보아요! 🐦"
    else:
        dandi_msg = f"대표님, 축하드려요! 🎉\n이번 달은 [{best_factor}] 활동이 금리를 무려 {best_value:.2f}%p나 낮추는 데 일등 공신 역할을 했어요!\n\n앞으로도 단디가 이체 수수료와 금리를 단디(단단히) 지켜드릴게요! 🐦"
        
    lbl_bubble.config(text=dandi_msg)


# =====================================================================
# 메인 GUI 어플리케이션 레이아웃 구성
# =====================================================================
app = tk.Tk()
app.title("단디의 ESG 공급망 금융 비서 - iM뱅크 데모")
app.geometry("580x680")
app.configure(bg="#F4F6F9")

# 1. 메인 타이틀
title_frame = tk.Frame(app, bg="#2C3E50", height=60)
title_frame.pack(fill="x")
lbl_title = tk.Label(
    title_frame, 
    text="iM뱅크 🛡️ 단디의 ESG 공급망 금융 비서", 
    font=("맑은 고딕", 14, "bold"), 
    fg="white", 
    bg="#2C3E50"
)
lbl_title.pack(pady=15)

# 2. [1단계] 데이터 입력 구역
input_frame = tk.LabelFrame(app, text=" 1단계: 소상공인/기업 ESG 데이터 수집 ", font=("맑은 고딕", 11, "bold"), bg="white", fg="#2980B9")
input_frame.pack(fill="x", padx=20, pady=10, ipady=10)

# E 요인 입력 슬라이더
tk.Label(input_frame, text="[E] 전력/가스 에너지 사용량 감축률 (%)", font=("맑은 고딕", 10), bg="white").pack(anchor="w", padx=15, pady=(5,0))
scale_energy = tk.Scale(input_frame, from_=0, to=50, orient="horizontal", bg="white", bd=0, highlightthickness=0)
scale_energy.pack(fill="x", padx=15)

# S 요인 입력 슬라이더
tk.Label(input_frame, text="[S] 지역사회 취약계층 고용 인원 (명)", font=("맑은 고딕", 10), bg="white").pack(anchor="w", padx=15, pady=(10,0))
scale_employ = tk.Scale(input_frame, from_=0, to=10, orient="horizontal", bg="white", bd=0, highlightthickness=0)
scale_employ.pack(fill="x", padx=15)

# G 요인 선택 체크박스
tk.Label(input_frame, text="[G] 투명한 회계 정보 및 정기 경영 성과 공시 여부", font=("맑은 고딕", 10), bg="white").pack(anchor="w", padx=15, pady=(10,0))
var_gov = tk.BooleanVar()
chk_gov = tk.Checkbutton(input_frame, text="국가 공인 투명 회계 시스템 사용 중 (Y/N)", variable=var_gov, bg="white", font=("맑은 고딕", 10, "italic"))
chk_gov.pack(anchor="w", padx=15, pady=5)

# 3. 실행 버튼
btn_calc = tk.Button(
    app, 
    text="AI 복합 ESG 신용 평가 및 맞춤 금리 조회", 
    font=("맑은 고딕", 12, "bold"), 
    bg="#3498DB", 
    fg="white", 
    relief="flat", 
    command=on_calculate
)
btn_calc.pack(fill="x", padx=20, pady=10, ipady=5)

# 4. [2단계] AI 평가 및 금리 산정 결과 화면
result_frame = tk.LabelFrame(app, text=" 2단계: AI 평가 및 산정 결과 ", font=("맑은 고딕", 11, "bold"), bg="white", fg="#27AE60")
result_frame.pack(fill="x", padx=20, pady=5, ipady=5)

# 결과 수치 레이블들
frame_metrics = tk.Frame(result_frame, bg="white")
frame_metrics.pack(fill="x", padx=15, pady=5)

tk.Label(frame_metrics, text="ESG 종합 평가 점수:", font=("맑은 고딕", 11), bg="white").grid(row=0, column=0, sticky="w")
lbl_score = tk.Label(frame_metrics, text="- 점", font=("맑은 고딕", 13, "bold"), bg="white", fg="#7F8C8D")
lbl_score.grid(row=0, column=1, padx=10, sticky="w")

tk.Label(frame_metrics, text="AI 조정 최종 대출 금리:", font=("맑은 고딕", 11), bg="white").grid(row=1, column=0, sticky="w", pady=5)
lbl_rate = tk.Label(frame_metrics, text="기본 금리 (6.00%)", font=("맑은 고딕", 13, "bold"), bg="white", fg="#2C3E50")
lbl_rate.grid(row=1, column=1, padx=10, sticky="w", pady=5)

# 5. [3단계] 설명 가능한 AI (XAI) 시각화 분석창 (SHAP 기여 막대그래프)
xai_frame = tk.LabelFrame(app, text=" 3단계: 설명 가능한 AI (XAI) 원인 규명 ", font=("맑은 고딕", 11, "bold"), bg="white", fg="#8E44AD")
xai_frame.pack(fill="x", padx=20, pady=10, ipady=5)

# E 막대그래프
frame_e = tk.Frame(xai_frame, bg="white")
frame_e.pack(fill="x", padx=15, pady=3)
tk.Label(frame_e, text="E 요인 기여도 (탄소 절감):", width=22, anchor="w", bg="white").pack(side="left")
progress_e = ttk.Progressbar(frame_e, length=180, mode="determinate")
progress_e.pack(side="left", padx=5)
lbl_shap_e = tk.Label(frame_e, text="0.00%p", bg="white", font=("맑은 고딕", 9, "bold"))
lbl_shap_e.pack(side="left", padx=5)

# S 막대그래프
frame_s = tk.Frame(xai_frame, bg="white")
frame_s.pack(fill="x", padx=15, pady=3)
tk.Label(frame_s, text="S 요인 기여도 (사회 고용):", width=22, anchor="w", bg="white").pack(side="left")
progress_s = ttk.Progressbar(frame_s, length=180, mode="determinate")
progress_s.pack(side="left", padx=5)
lbl_shap_s = tk.Label(frame_s, text="0.00%p", bg="white", font=("맑은 고딕", 9, "bold"))
lbl_shap_s.pack(side="left", padx=5)

# G 막대그래프
frame_g = tk.Frame(xai_frame, bg="white")
frame_g.pack(fill="x", padx=15, pady=3)
tk.Label(frame_g, text="G 요인 기여도 (경영 투명):", width=22, anchor="w", bg="white").pack(side="left")
progress_g = ttk.Progressbar(frame_g, length=180, mode="determinate")
progress_g.pack(side="left", padx=5)
lbl_shap_g = tk.Label(frame_g, text="0.00%p", bg="white", font=("맑은 고딕", 9, "bold"))
lbl_shap_g.pack(side="left", padx=5)

# 6. [4단계] 단디 비서 캐릭터 말풍선 (User Interface)
dandi_frame = tk.Frame(app, bg="#EAFAF1")
dandi_frame.pack(fill="x", padx=20, pady=10, ipady=10)

lbl_char = tk.Label(dandi_frame, text="🐦\n[단디 비서]", font=("맑은 고딕", 11, "bold"), bg="#EAFAF1", fg="#27AE60")
lbl_char.pack(side="left", padx=15)

lbl_bubble = tk.Label(
    dandi_frame, 
    text="대표님 안녕하세요!\n위의 슬라이더를 조절하신 후 버튼을 누르시면,\n어려운 ESG 경영 기여도를 단디가 알기 쉽게 브리핑해 드려요!", 
    font=("맑은 고딕", 10), 
    bg="white", 
    relief="solid", 
    bd=1, 
    justify="left", 
    padx=10, 
    pady=10,
    wraplength=380
)
lbl_bubble.pack(side="left", fill="both", expand=True, padx=(0, 15))

# 메인 루프 가동
app.mainloop()