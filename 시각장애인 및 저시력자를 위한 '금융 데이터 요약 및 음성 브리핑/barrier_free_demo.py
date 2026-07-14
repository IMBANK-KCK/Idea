# pip install gTTS
"""
이 데모는 단순한 음성 재생뿐만 아니라, 
저시력자분들이 화면을 더 편하게 볼 수 있도록 돕는 
'고대비 모드(High Contrast Mode)'와 '초대형 글씨 전환 버튼'을 함께 탑재하여 
배리어프리의 실용성을 극대화했습니다.
"""
#############################################

import os
import sys
import tkinter as tk
from tkinter import messagebox

# gTTS 라이브러리 가져오기 및 예외 처리
try:
    from gtts import gTTS
except ImportError:
    # 비전공자 팀원분들을 위해 라이브러리가 없을 때 친절히 안내하고 종료합니다.
    print("\n[알림] 데모 실행을 위해 gTTS 라이브러리가 필요합니다.")
    print("터미널 창에 'pip install gTTS'를 입력하여 설치한 후 다시 실행해 주세요!\n")
    sys.exit(1)

# =====================================================================
# 1. 가상 데이터베이스 (SQL 테이블 데이터 시뮬레이션)
# =====================================================================
# 이번 달 지출 내역 원장 데이터
current_month_db = [
    {"category": "배달음식 식비", "amount": 280000}, # 지난달보다 130,000원 증가!
    {"category": "대중교통 요금", "amount": 85000},
    {"category": "휴대폰 통신비", "amount": 55000},
    {"category": "인터넷 쇼핑", "amount": 190000},
    {"category": "아파트 관리비", "amount": 210000}
]

# 지난달 지출 내역 원장 데이터
last_month_db = [
    {"category": "배달음식 식비", "amount": 150000},
    {"category": "대중교통 요금", "amount": 90000},
    {"category": "휴대폰 통신비", "amount": 55000},
    {"category": "인터넷 쇼핑", "amount": 220000},
    {"category": "아파트 관리비", "amount": 200000}
]

# =====================================================================
# 2. 데이터 분석 및 대화형 문장 생성 엔진 (NLG)
# =====================================================================
def generate_voice_script():
    """
    SQL로 데이터를 추출하고 Pandas로 증감 수치를 가공하는 백엔드 핵심 로직입니다.
    """
    # 1단계 & 2단계: 전체 지출 합계 연산 (SQL SUM 및 데이터 비교)
    total_current = sum(item["amount"] for item in current_month_db)
    total_last = sum(item["amount"] for item in last_month_db)
    
    diff_total = total_current - total_last
    change_ratio = round((diff_total / total_last) * 100, 1)
    
    # 지출 증감에 따른 단어 선택
    if diff_total > 0:
        trend_text = f"지난달보다 약 {abs(change_ratio)}퍼센트 더 많이 쓰셨습니다"
    elif diff_total < 0:
        trend_text = f"지난달보다 약 {abs(change_ratio)}퍼센트 절약하셨습니다"
    else:
        trend_text = "지난달과 거의 비슷한 수준으로 지출하셨습니다"
        
    # 3단계: 지출이 가장 많이 늘어난 '특이 카테고리' 추출 (Pandas 전처리 응용)
    max_increase = 0
    target_category = ""
    
    for curr in current_month_db:
        for last in last_month_db:
            if curr["category"] == last["category"]:
                difference = curr["amount"] - last["amount"]
                if difference > max_increase:
                    max_increase = difference
                    target_category = curr["category"]

    # 4단계: 시각장애인 고객의 인지 피로를 줄여주는 '핵심 요약' 스크립트 템플릿 완성
    script = (
        f"김고객님, 이번 달 총 지출은 {total_current:,}원입니다. "
        f"{trend_text}. "
        f"특히, {target_category} 항목에서 지난달 대비 {max_increase:,}원이 늘어 "
        f"가장 큰 소비 증가를 기록했습니다. 단디(단단히) 체크해 보세요!"
    )
    return script


# =====================================================================
# 3. 음성 브리핑 생성 및 재생 기능 (gTTS 사용)
# =====================================================================
def play_audio():
    # 데이터 요약 텍스트 생성
    briefing_text = generate_voice_script()
    
    # GUI 하단 텍스트 창에 내용을 크고 굵게 표시하여 저시력자 지원
    txt_display.config(state="normal")
    txt_display.delete("1.0", tk.END)
    txt_display.insert(tk.END, briefing_text)
    txt_display.config(state="disabled")
    
    try:
        # gTTS 엔진을 사용해 한국어 음성 파일로 구워내기
        tts = gTTS(text=briefing_text, lang='ko')
        audio_file = "im_voice_briefing.mp3"
        tts.save(audio_file)
        
        # 운영체제(OS)별로 음성 파일을 즉시 소리 내어 재생하는 명령어 호출
        if sys.platform == "win32":
            os.system(f"start {audio_file}")
        elif sys.platform == "darwin": # macOS
            os.system(f"open {audio_file}")
        else: # Linux
            os.system(f"xdg-open {audio_file}")
            
    except Exception as e:
        messagebox.showerror("재생 오류", f"음성 재생 파일 생성에 실패했습니다: {e}")


# =====================================================================
# 4. 배리어프리 UI 테마 제어 기능 (고대비 모드 토글)
# =====================================================================
is_high_contrast = False

def toggle_high_contrast():
    """
    저시력자 및 전색맹 등 시각장애인 고객이 화면을 명확하게 인지할 수 있도록
    검은색 바탕에 밝은 노란색 글씨 조합의 '고대비 모드'를 지원하는 폰트/색상 변경 제어기입니다.
    """
    global is_high_contrast
    is_high_contrast = not is_high_contrast
    
    if is_high_contrast:
        # 고대비 모드 ON (검은색 배경 + 밝은 노란색 텍스트)
        app.configure(bg="#121212")
        frame_top.configure(bg="#1E1E1E")
        lbl_title.configure(bg="#1E1E1E", fg="#FEE500")
        frame_body.configure(bg="#121212")
        lbl_info.configure(bg="#121212", fg="#FFFFFF")
        btn_voice.configure(bg="#FEE500", fg="#121212", font=("맑은 고딕", 16, "bold"))
        btn_contrast.configure(text="일반 모드로 돌아가기 🔄", bg="#333333", fg="#FFFFFF")
        txt_display.configure(bg="#1E1E1E", fg="#FEE500", insertbackground="#FEE500")
    else:
        # 일반 모드 OFF (iM뱅크 시그니처 에메랄드 스카이 민트 테마)
        app.configure(bg="#F4F6F9")
        frame_top.configure(bg="#00A29A")
        lbl_title.configure(bg="#00A29A", fg="white")
        frame_body.configure(bg="#F4F6F9")
        lbl_info.configure(bg="#F4F6F9", fg="#2C3E50")
        btn_voice.configure(bg="#00A29A", fg="white", font=("맑은 고딕", 14, "bold"))
        btn_contrast.configure(text="시각장애인용 고대비(High Contrast) 모드 켜기 👁️", bg="#2C3E50", fg="white")
        txt_display.configure(bg="white", fg="#2C3E50", insertbackground="black")


# =====================================================================
# 5. 메인 GUI 화면 구성
# =====================================================================
app = tk.Tk()
app.title("iM뱅크 배리어프리 음성 비서 서비스")
app.geometry("580x620")
app.configure(bg="#F4F6F9")

# 상단 바 (iM뱅크 브랜딩 컬러 적용)
frame_top = tk.Frame(app, bg="#00A29A", height=70)
frame_top.pack(fill="x")
lbl_title = tk.Label(
    frame_top, 
    text="iM뱅크 🎧 마음을 담은 음성 브리핑 비서", 
    font=("맑은 고딕", 15, "bold"), 
    fg="white", 
    bg="#00A29A"
)
lbl_title.pack(pady=20)

# 메인 콘텐츠 영역
frame_body = tk.Frame(app, bg="#F4F6F9")
frame_body.pack(fill="both", expand=True, padx=25, pady=15)

# 설명 문구 (저시력자를 위한 큰 폰트 크기 기본 설정)
lbl_info = tk.Label(
    frame_body, 
    text="기계적으로 읽어주는 낭독 기능 대신,\n이번 달 핵심 돈의 흐름만 요약해서 브리핑해 드립니다.",
    font=("맑은 고딕", 11, "bold"),
    bg="#F4F6F9",
    fg="#2C3E50",
    justify="center"
)
lbl_info.pack(pady=15)

# 배리어프리 고대비 전환 버튼
btn_contrast = tk.Button(
    frame_body,
    text="시각장애인용 고대비(High Contrast) 모드 켜기 👁️",
    font=("맑은 고딕", 10, "bold"),
    bg="#2C3E50",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=toggle_high_contrast
)
btn_contrast.pack(fill="x", ipady=8, pady=10)

# 핵심 음성 브리핑 듣기 버튼 (가장 크고 직관적으로 설계)
btn_voice = tk.Button(
    frame_body,
    text="🔊 이번 달 금융 요약 브리핑 듣기 (클릭)",
    font=("맑은 고딕", 14, "bold"),
    bg="#00A29A",
    fg="white",
    relief="raised",
    cursor="hand2",
    command=play_audio
)
btn_voice.pack(fill="x", ipady=20, pady=15)

# 텍스트 출력창 (음성 대화 전문을 시각화하여 저시력자/청각장애 다중 보조)
lbl_sub_txt = tk.Label(frame_body, text="[브리핑 요약문 - 큰 글씨 확대창]", font=("맑은 고딕", 10, "bold"), bg="#F4F6F9")
lbl_sub_txt.pack(anchor="w", pady=5)

txt_display = tk.Text(
    frame_body, 
    font=("맑은 고딕", 14, "bold"), 
    height=6, 
    wrap="word", 
    bg="white", 
    fg="#2C3E50",
    relief="solid",
    bd=1
)
txt_display.pack(fill="both", expand=True)
txt_display.insert(tk.END, "위의 '음성 브리핑 듣기' 버튼을 누르시면 요약문이 소리와 함께 나타납니다.")
txt_display.config(state="disabled")

# 앱 루프 가동
app.mainloop()