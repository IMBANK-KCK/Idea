# iM-AI ESG Connect 데모: 기업 금융 금리 산정 시스템
def calculate_corporate_loan_rate(company_name, esg_metrics):
    """
    company_name: 기업명
    esg_metrics: dict {'E': 0~100, 'S': 0~100, 'G': 0~100}
    """
    # 1. AI 가중치 적용 (리스크 관리를 위한 은행 내부 로직)
    weights = {'E': 0.4, 'S': 0.3, 'G': 0.3}
    esg_score = sum(esg_metrics[k] * weights[k] for k in weights)
    
    # 2. 금리 산정 (기본 금리 5.0%에서 ESG 점수별 차등 감면)
    # 금융감독원 가이드라인에 따른 리스크 기반 금리 산정
    base_rate = 5.0
    interest_rate = max(2.5, base_rate - (esg_score / 25))
    
    # 3. XAI (설명 가능한 AI) 근거 생성 - 금감원 규제 준수 로직
    reasons = []
    if esg_metrics['E'] < 60: reasons.append("환경(E) 지표 개선 필요")
    if esg_metrics['S'] < 60: reasons.append("사회(S) 부문 투자 확대 권고")
    if esg_metrics['G'] < 60: reasons.append("지배구조(G) 투명성 강화 필요")
    
    explanation = " 및 ".join(reasons) if reasons else "모든 ESG 지표 우수"
    
    return {
        "기업명": company_name,
        "ESG종합점수": round(esg_score, 1),
        "산정금리": f"{round(interest_rate, 2)}%",
        "AI_판단근거": explanation
    }

# 데모 실행 예시
data = {'E': 75, 'S': 55, 'G': 80}
result = calculate_corporate_loan_rate("대한테크", data)

print(f"--- iM-AI ESG Connect 분석 결과 ---")
for key, value in result.items():
    print(f"{key}: {value}")
