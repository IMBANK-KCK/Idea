import math
import time
import tkinter as tk
from tkinter import messagebox

# =====================================================================
# [핵심 알고리즘] 코사인 유사도 계산기
# 두 목소리 데이터가 얼마나 닮았는지 수학적으로 계산 (0 ~ 1 사이 결과)
# =====================================================================
def calculate_cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)


# =====================================================================
# 가상의 데이터베이스(DB) 세팅
# =====================================================================
crime_db = {
    "피싱 조직원_A(검사 사칭)": [0.91, 0.12, 0.34],
    "피싱 조직원_B(금융감독원 사칭)": [0.15, 0.88, 0.45]
}
user_db = {
    "사용자_홍길동(정상 고객)": [0.21, 0.33, 0.85]
}


# =====================================================================
# 어플 핵심 비즈니스 로직 및 화면 제어 함수
# =====================================================================
def run_app_scenario(scenario_type):
    # 어플 화면의 상태 메시지 업데이트
    status_label.config(text="상태: 🎙️ 수화기 너머 음성 분석 중... (3초 소요)", fg="#D35400")
    window.update() # 화면을 즉시 새로고침하여 텍스트 변경을 보여줌
    time.sleep(1.5) # 분석하는 척하는 가상의 시간 지연
    
    # 시나리오에 따른 가상의 입력 음성 벡터 세팅
    if scenario_type == "phishing":
        live_voice_vector = [0.89, 0.15, 0.32] # 피싱 조직원_A와 흡사한 목소리
    else:
        live_voice_vector = [0.22, 0.31, 0.88] # 사용자 본인과 흡사한 목소리

    threshold = 0.85
    is_phishing_detected = False
    
    # 1. 국과수 범죄자 DB와 대조 작업
    for name, crime_vector in crime_db.items():
        similarity = calculate_cosine_similarity(live_voice_vector, crime_vector)
        
        if similarity >= threshold:
            # [위험 상황] 어플 배경을 강렬한 빨간색으로 변경하고 위험 메시지 출력
            window.configure(bg="#FADBD8")
            title_label.configure(bg="#FADBD8")
            status_label.configure(text=f"🚨 보이스피싱 의심 인물 감지! ({similarity*100:.1f}% 일치)", fg="red", bg="#FADBD8")
            
            # 화면 전면에 팝업 경고창 띄우기
            messagebox.showerror(
                "❌ 보이스피싱 확정 경고", 
                f"현재 통화 중인 상대방의 목소리가 국과수에 등록된 사기꾼 [{name}]과 {similarity*100:.1f}% 일치합니다.\n\n즉시 통화를 종료하십시오! iM뱅크 송금 기능이 임시 차단되었습니다."
            )
            is_phishing_detected = True
            break
            
    # 2. 범죄자가 아니라면 사용자 본인 인증 진행
    if not is_phishing_detected:
        for name, user_vector in user_db.items():
            user_similarity = calculate_cosine_similarity(live_voice_vector, user_vector)
            
            if user_similarity >= threshold:
                # [안전 상황] 어플 배경을 평온한 초록/회색으로 유지하고 안전 알림
                window.configure(bg="#EAFAF1")
                title_label.configure(bg="#EAFAF1")
                status_label.configure(text=f"✅ 안심 거래 안내 (본인 인증 {user_similarity*100:.1f}%)", fg="blue", bg="#EAFAF1")
                
                messagebox.showinfo(
                    "안전 확인 완료", 
                    "사용자 본인의 정상 목소리가 확인되었습니다. 안심하고 안전하게 이체 거래를 진행하십시오."
                )
            else:
                # 데이터가 아예 없는 3의 인물인 경우
                window.configure(bg="#F5EEF8")
                title_label.configure(bg="#F5EEF8")
                status_label.configure(text="❓ 출처 불분명 음성 감지", fg="purple", bg="#F5EEF8")
                messagebox.showwarning(
                    "추가 인증 필요", 
                    "등록되지 않은 제3자의 목소리가 수집되었습니다. 안전을 위해 추가 일회용 비밀번호(OTP) 인증을 수행해 주세요."
                )


# =====================================================================
# 어플리케이션 인터페이스(UI) 구성부
# =====================================================================
# 1. 메인 윈도우 창 생성
window = tk.Tk()
window.title("iM뱅크 안심 AI 스마트 방어 시스템")
window.geometry("450x400") # 창 크기 세로 450, 가로 400
window.configure(bg="#F4F6F7") # 기본 세련된 배경색

# 2. 어플 상단 제목 UI 레이블
title_label = tk.Label(
    window, 
    text="iM뱅크 🛡️ 안심 AX 시스템", 
    font=("맑은 고딕", 16, "bold"), 
    bg="#F4F6F7", 
    fg="#2C3E50"
)
title_label.pack(pady=25)

# 3. 중앙 실시간 모니터링 상태 메시지 UI 레이블
status_label = tk.Label(
    window, 
    text="상태: 실시간 스마트폰 통화 및 앱 구동 감시 중", 
    font=("맑은 고딕", 11), 
    bg="#F4F6F7", 
    fg="#7F8C8D"
)
status_label.pack(pady=15)

# 4. 시뮬레이션 버튼 1 (보이스피싱 범죄 상황 유도 버튼)
btn_phishing = tk.Button(
    window, 
    text="⚠️ 시나리오 1: 사기꾼 통화 중 송금 시도", 
    font=("맑은 고딕", 11, "bold"),
    bg="#E74C3C", 
    fg="white", 
    width=35, 
    height=2,
    command=lambda: run_app_scenario("phishing") # 버튼을 누르면 피싱 시나리오 함수 호출
)
btn_phishing.pack(pady=12)

# 5. 시뮬레이션 버튼 2 (정상 본인 이용 상황 유도 버튼)
btn_safe = tk.Button(
    window, 
    text="👍 시나리오 2: 일반 통화 중 본인 정상 송금", 
    font=("맑은 고딕", 11, "bold"),
    bg="#2ECC71", 
    fg="white", 
    width=35, 
    height=2,
    command=lambda: run_app_scenario("safe") # 버튼을 누르면 안전 시나리오 함수 호출
)
btn_safe.pack(pady=12)

# 6. 어플리케이션 무한 루프 가동 (창이 닫히기 전까지 계속 켜두는 명령)
window.mainloop()