# 단디 AI ESG 공급망 금융 플랫폼 — 전체 개발 파이프라인

> **프로젝트**: iM금융그룹 공모전 — "단디의 AI 기반 ESG 공급망 금융 관리 플랫폼"  
> **작성일**: 2026-07-21  
> **목적**: Python 백엔드 → 웹/모바일 UI까지 실제 작동하는 프로그램을 완성하기 위한 단계별 구현 로드맵

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)  
2. [전체 아키텍처 다이어그램](#2-전체-아키텍처-다이어그램)  
3. [기술 스택 선정](#3-기술-스택-선정)  
4. [Python 백엔드 파이프라인 (4-Step)](#4-python-백엔드-파이프라인-4-step)  
5. [웹 UI 파이프라인](#5-웹-ui-파이프라인)  
6. [모바일 앱 파이프라인](#6-모바일-앱-파이프라인-react-native)  
7. [디렉터리 구조](#7-디렉터리-구조)  
8. [단계별 실행 순서 (Quick Start)](#8-단계별-실행-순서-quick-start)  
9. [배포 파이프라인](#9-배포-파이프라인-deployment)  
10. [개발 로드맵 및 마일스톤](#10-개발-로드맵-및-마일스톤)

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|:---|:---|
| **서비스명** | 단디 AI ESG 공급망 금융 플랫폼 |
| **타깃** | 지역 소상공인 및 중소기업 (B2B) |
| **핵심 기능** | ESG 점수 기반 실시간 대출 금리 산출 + XAI 근거 설명 + 단디 챗봇 |
| **수익 구조** | ESG 우수 기업 → 저금리 대출 → 연체율 하락 → 은행 장기 수익 |
| **규제 준수** | 금융감독원 AI 가이드라인 (설명 가능한 AI, XAI 의무) |

---

## 2. 전체 아키텍처 다이어그램

```
[데이터 소스]
  ├── 에너지 사용량 (전력/가스 고지서 API)
  ├── 재무제표 (DART, 세금계산서)
  ├── 탄소 배출 지표 (환경부 공공 API)
  └── 고용/사회 지표 (고용보험 DB)
         │
         ▼
[1단계] ESG 데이터 수집 & 정규화
  src/pipeline/step1_ingest.py
         │
         ▼
[2단계] AI 신용 평가 모델 (Scikit-learn RandomForest)
  src/pipeline/step2_model.py
         │
         ▼
[3단계] SHAP XAI 설명 생성
  src/pipeline/step3_xai.py
         │
         ▼
[4단계] 단디 챗봇 응답 생성 (LangChain + OpenAI)
  src/pipeline/step4_dandy.py
         │
    ┌────┴────┐
    ▼         ▼
[웹 UI]    [모바일 앱]
Streamlit  React Native
(데모/발표)  (실사용자 앱)
    │         │
    └────┬────┘
         ▼
[FastAPI REST API 서버]
  src/api/main.py
         │
         ▼
[배포]
  Streamlit Cloud / Render / Expo (모바일)
```

---

## 3. 기술 스택 선정

### Python 백엔드

| 역할 | 라이브러리 | 버전 | 이유 |
|:---|:---|:---|:---|
| 데이터 처리 | `pandas`, `numpy` | 최신 안정 | ESG 데이터 정규화 및 조작 |
| AI 모델 | `scikit-learn` | ≥1.4 | RandomForest 기반 금리 예측 |
| XAI 분석 | `shap` | ≥0.45 | 변수 기여도 산출 및 시각화 |
| 챗봇 엔진 | `langchain`, `openai` | 최신 | 단디 대화형 AI 비서 |
| API 서버 | `fastapi`, `uvicorn` | 최신 | 웹/모바일 공통 REST 엔드포인트 |
| 환경 설정 | `python-dotenv` | 최신 | API 키 등 민감 정보 분리 |

### 웹 UI

| 역할 | 도구 | 이유 |
|:---|:---|:---|
| 빠른 데모 | `Streamlit` | Python만으로 대시보드·챗봇 구현 (공모전 발표용) |
| 프로덕션 웹 | `Next.js` (React) | 확장성·SEO·반응형 지원 |
| 차트 시각화 | `Plotly`, `recharts` | SHAP 폭포수 차트, ESG 트렌드 그래프 |

### 모바일 앱

| 역할 | 도구 | 이유 |
|:---|:---|:---|
| 크로스플랫폼 | `React Native` + `Expo` | iOS·Android 동시 지원, 웹 코드 재활용 |
| 상태 관리 | `Zustand` | 가볍고 직관적 |
| 알림 | `Expo Notifications` | 단디 푸시 알림 |

---

## 4. Python 백엔드 파이프라인 (4-Step)

### 4-1. Step 1: ESG 데이터 수집 & 전처리

**파일**: `src/pipeline/step1_ingest.py`

```python
"""
Step 1: ESG 데이터 수집 및 전처리 (Data Ingestion & Normalization)

입력: 기업 ID, 기간 (기본: 최근 30일)
출력: 정규화된 ESG 피처 딕셔너리
"""
import numpy as np

ESG_WEIGHTS = {
    'environmental': 0.40,
    'social': 0.30,
    'governance': 0.30,
}


def load_raw_data(company_id: str, source: str = "mock") -> dict:
    """
    실제 서비스에서는 공공 API / 내부 DB에서 수집.
    현재는 목(Mock) 데이터를 반환한다.
    """
    if source == "mock":
        return {
            'company_id': company_id,
            'energy_kwh': 3200,        # 월 전력 사용량 (kWh)
            'carbon_kg': 450,           # 월 탄소 배출량 (kg)
            'paper_receipt_ratio': 72,  # 전자 영수증 전환율 (%)
            'waste_recycle_ratio': 58,  # 폐기물 재활용 비율 (%)
            'vulnerable_hire_ratio': 15, # 취약계층 고용 비율 (%)
            'local_purchase_ratio': 40,  # 지역 상품 구매 비율 (%)
            'accounting_transparency': 85, # 투명 회계 점수 (0~100)
            'overdue_count': 0,          # 최근 1년 연체 횟수
        }
    raise NotImplementedError(f"source={source} 미구현")


def normalize_features(raw: dict) -> dict:
    """
    각 피처를 0~100 스케일로 정규화.
    에너지·탄소는 낮을수록 좋으므로 반전 처리.
    """
    normalized = {}
    # 환경(E) 점수 계산 — 낮을수록 좋은 지표는 반전
    normalized['env_energy'] = max(0, 100 - (raw['energy_kwh'] / 50))
    normalized['env_carbon'] = max(0, 100 - (raw['carbon_kg'] / 10))
    normalized['env_paper']  = raw['paper_receipt_ratio']
    normalized['env_waste']  = raw['waste_recycle_ratio']
    # 사회(S) 점수
    normalized['soc_hire']  = min(100, raw['vulnerable_hire_ratio'] * 2)
    normalized['soc_local'] = raw['local_purchase_ratio']
    # 지배구조(G) 점수
    normalized['gov_account'] = raw['accounting_transparency']
    normalized['gov_overdue'] = max(0, 100 - raw['overdue_count'] * 20)

    # 영역별 평균 점수
    normalized['E_score'] = np.mean([
        normalized['env_energy'], normalized['env_carbon'],
        normalized['env_paper'],  normalized['env_waste']
    ])
    normalized['S_score'] = np.mean([normalized['soc_hire'], normalized['soc_local']])
    normalized['G_score'] = np.mean([normalized['gov_account'], normalized['gov_overdue']])

    # 가중 합산 ESG 종합 점수
    normalized['total_esg'] = (
        normalized['E_score'] * ESG_WEIGHTS['environmental'] +
        normalized['S_score'] * ESG_WEIGHTS['social'] +
        normalized['G_score'] * ESG_WEIGHTS['governance']
    )
    return normalized


def run_step1(company_id: str) -> dict:
    raw = load_raw_data(company_id)
    features = normalize_features(raw)
    features['company_id'] = company_id
    print(f"[Step 1 완료] ESG 총점: {features['total_esg']:.1f}")
    return features
```

---

### 4-2. Step 2: AI 신용 평가 모델

**파일**: `src/pipeline/step2_model.py`

```python
"""
Step 2: AI 기반 ESG-신용 복합 평가 → 대출 금리 산출
모델: RandomForestRegressor (Scikit-learn)
학습 후 models/esg_interest_model.pkl 로 저장
"""
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from pathlib import Path

MODEL_PATH = Path("models/esg_interest_model.pkl")


def generate_training_data(n: int = 1000) -> tuple:
    """
    실제 서비스에서는 iM뱅크 과거 대출 데이터로 대체.
    현재는 규칙 기반 시뮬레이션으로 학습 데이터를 생성한다.
    """
    np.random.seed(42)
    E = np.random.uniform(30, 100, n)
    S = np.random.uniform(20, 100, n)
    G = np.random.uniform(40, 100, n)
    esg_total = E * 0.4 + S * 0.3 + G * 0.3
    # 기준 금리 5.0% → ESG 점수에 따라 최저 2.5%까지 인하
    interest = np.clip(5.0 - (esg_total / 20), 2.5, 5.0)
    interest += np.random.normal(0, 0.05, n)
    X = np.column_stack([E, S, G, esg_total])
    y = np.clip(interest, 2.5, 5.0)
    return X, y


def train_model() -> RandomForestRegressor:
    X, y = generate_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"[Step 2] 모델 학습 완료 — R² Score: {score:.4f}")
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model() -> RandomForestRegressor:
    if not MODEL_PATH.exists():
        print("[Step 2] 저장된 모델 없음 → 신규 학습 시작")
        return train_model()
    return joblib.load(MODEL_PATH)


def predict_interest_rate(features: dict) -> tuple:
    """
    정규화된 ESG 피처를 받아 예측 금리와 모델 객체를 반환.
    SHAP 분석을 위해 모델도 함께 리턴한다.
    """
    model = load_model()
    X = np.array([[features['E_score'], features['S_score'],
                   features['G_score'], features['total_esg']]])
    rate = float(model.predict(X)[0])
    rate = round(max(2.5, min(5.0, rate)), 2)
    print(f"[Step 2 완료] 예측 금리: {rate}%")
    return rate, model


def run_step2(features: dict) -> tuple:
    return predict_interest_rate(features)
```

---

### 4-3. Step 3: SHAP XAI 설명 생성

**파일**: `src/pipeline/step3_xai.py`

```python
"""
Step 3: SHAP 기반 XAI — 금리 결정 원인 분석
규제 준수: 금융감독원 AI 가이드라인 '설명 가능성 확보' 요건 충족

SHAP 수학 공식:
  φᵢ(v) = Σ [|S|!(|N|-|S|-1)! / |N|!] × [v(S∪{i}) - v(S)]
"""
import numpy as np
import shap
import matplotlib
matplotlib.use('Agg')  # GUI 없이 파일 저장
import matplotlib.pyplot as plt
from pathlib import Path

FEATURE_NAMES = ['환경(E)점수', '사회(S)점수', '지배구조(G)점수', 'ESG총점']
OUTPUT_DIR = Path("outputs/shap")


def compute_shap_values(model, features: dict) -> dict:
    """
    SHAP TreeExplainer로 각 피처의 기여도를 산출한다.
    반환값: {feature_name: {shap, pct, direction}} 딕셔너리
    """
    X = np.array([[features['E_score'], features['S_score'],
                   features['G_score'], features['total_esg']]])
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)[0]
    total_abs = np.sum(np.abs(shap_values)) + 1e-9
    contributions = {
        name: {
            'shap': float(val),
            'pct': round(abs(val) / total_abs * 100, 1),
            'direction': '금리 인하 기여 ↓' if val < 0 else '금리 인상 요인 ↑'
        }
        for name, val in zip(FEATURE_NAMES, shap_values)
    }
    return contributions


def generate_natural_language_explanation(contributions: dict, rate: float) -> str:
    """
    SHAP 값을 바탕으로 단디 캐릭터의 자연어 설명문을 생성한다.
    """
    top_feature = max(contributions, key=lambda k: contributions[k]['pct'])
    top_pct = contributions[top_feature]['pct']
    lines = [
        f"✅ AI 분석 결과: 대표님의 대출 금리는 **{rate}%** 로 산정되었습니다.",
        "",
        "📊 금리 결정에 기여한 항목별 분석:",
    ]
    for name, info in sorted(contributions.items(), key=lambda x: -x[1]['pct']):
        lines.append(f"  • {name}: {info['pct']}% 기여 ({info['direction']})")
    lines += [
        "",
        f"💡 가장 큰 영향 요인은 **{top_feature}** ({top_pct}%)입니다.",
        "   꾸준히 관리하시면 다음 평가에서 금리가 더 내려갈 수 있습니다!"
    ]
    return "\n".join(lines)


def save_shap_waterfall_chart(model, features: dict, company_id: str) -> str:
    """
    SHAP 폭포수 차트를 PNG로 저장한다.
    Streamlit·웹 UI에서 임베드하여 사용한다.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    X = np.array([[features['E_score'], features['S_score'],
                   features['G_score'], features['total_esg']]])
    explainer = shap.TreeExplainer(model)
    shap_exp = explainer(X)
    shap.plots.waterfall(shap_exp[0], show=False)
    path = OUTPUT_DIR / f"{company_id}_shap.png"
    plt.savefig(path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"[Step 3 완료] SHAP 차트 저장: {path}")
    return str(path)


def run_step3(model, features: dict, rate: float) -> dict:
    contributions = compute_shap_values(model, features)
    explanation = generate_natural_language_explanation(contributions, rate)
    chart_path = save_shap_waterfall_chart(model, features, features['company_id'])
    return {
        'contributions': contributions,
        'explanation': explanation,
        'chart_path': chart_path,
    }
```

---

### 4-4. Step 4: 단디 챗봇 & 알림 엔진

**파일**: `src/pipeline/step4_dandy.py`

```python
"""
Step 4: 단디 AI 비서 챗봇 + 맞춤 알림 메시지 생성
엔진: LangChain + OpenAI GPT-4o-mini (비용 절감)
OpenAI API 키 없을 시 → 규칙 기반 폴백 응답으로 자동 전환
"""
import os

DANDY_SYSTEM_PROMPT = """
당신은 iM금융그룹의 마스코트 '단디'입니다.
소상공인과 중소기업 사장님들을 위한 친근한 ESG 경영 비서 역할을 합니다.

특징:
- 따뜻하고 친근한 경상도 사투리를 적절히 섞어 사용합니다.
- 어려운 금융·ESG 용어를 쉽게 풀어서 설명합니다.
- 구체적인 수치와 실천 방법을 항상 함께 제시합니다.
- 응원과 격려를 아끼지 않습니다.
- 답변은 3~5문장 이내로 간결하게 합니다.
"""


def get_dandy_response(user_message: str, xai_context: dict = None) -> str:
    """
    단디 챗봇 응답 생성.
    xai_context: Step 3에서 생성한 SHAP 분석 결과 (선택)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _rule_based_response(user_message, xai_context)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
        context_text = ""
        if xai_context:
            context_text = f"\n\n[AI 분석 결과]\n{xai_context.get('explanation', '')}"
        messages = [
            SystemMessage(content=DANDY_SYSTEM_PROMPT),
            HumanMessage(content=f"{user_message}{context_text}")
        ]
        return llm.invoke(messages).content
    except Exception:
        return _rule_based_response(user_message, xai_context)


def _rule_based_response(user_message: str, xai_context: dict = None) -> str:
    """OpenAI API 키가 없거나 오류 시 동작하는 규칙 기반 단디 응답."""
    if xai_context and 'explanation' in xai_context:
        return (
            "안녕하세예! 단디입니더! 🎉\n"
            + xai_context['explanation']
            + "\n\n궁금한 점 있으면 언제든지 물어보이소!"
        )
    keywords = {
        '금리': "대표님! ESG 점수가 오르면 금리가 내려갑니더. 에너지 절약부터 시작해보이소! 💪",
        'ESG': "ESG는 환경(E)·사회(S)·지배구조(G)의 약자입니더. 세 가지를 고루 잘하면 대출 금리가 팍 내려가요!",
        '탄소': "탄소 배출을 줄이면 환경 점수가 오릅니더. 전자 영수증 쓰는 것부터 단디(단단히) 시작해보이소!",
        '서류': "ESG 인증 서류는 제가 도와드릴게예! 동반성장위원회 사이트에서 자가진단표를 먼저 작성해보이소.",
    }
    for kw, reply in keywords.items():
        if kw in user_message:
            return reply
    return "단디가 항상 옆에 있을게예! 더 궁금한 거 있으면 편하게 물어보이소~ 😊"


def generate_push_notification(features: dict, rate: float) -> str:
    """모바일 앱 푸시 알림 메시지 생성."""
    esg = features.get('total_esg', 0)
    msg = f"📊 [단디 리포트] 이번 달 ESG 점수: {esg:.0f}점\n"
    msg += f"💰 현재 적용 금리: {rate}%\n"
    if esg >= 75:
        msg += "✅ 우수! 이대로 유지하면 다음 달 금리 추가 인하 가능!"
    else:
        msg += "💡 에너지 절약 실천 시 금리 0.1%p 추가 인하 기회!"
    return msg


def run_step4(features: dict, rate: float, xai_result: dict) -> dict:
    push_msg = generate_push_notification(features, rate)
    initial_greeting = get_dandy_response("이번 달 ESG 분석 결과를 알려줘", xai_context=xai_result)
    print(f"[Step 4 완료] 단디 메시지 생성 완료")
    return {
        'push_notification': push_msg,
        'dandy_greeting': initial_greeting,
    }
```

---

### 파이프라인 통합 실행 진입점

**파일**: `src/main.py`

```python
"""
전체 파이프라인 통합 실행 진입점
사용: python src/main.py --company_id COMPANY_001
"""
import argparse
from pipeline.step1_ingest import run_step1
from pipeline.step2_model  import run_step2
from pipeline.step3_xai    import run_step3
from pipeline.step4_dandy  import run_step4


def run_pipeline(company_id: str) -> dict:
    print(f"\n{'='*50}")
    print(f" 단디 ESG 금융 파이프라인 시작: {company_id}")
    print(f"{'='*50}\n")

    features          = run_step1(company_id)           # ESG 데이터 수집 & 정규화
    rate, model       = run_step2(features)              # AI 금리 예측
    xai_result        = run_step3(model, features, rate) # SHAP XAI 분석
    dandy_result      = run_step4(features, rate, xai_result)  # 단디 응답 생성

    result = {
        'company_id': company_id,
        'esg_scores': {
            'E': round(features['E_score'], 1),
            'S': round(features['S_score'], 1),
            'G': round(features['G_score'], 1),
            'total': round(features['total_esg'], 1),
        },
        'interest_rate': rate,
        'xai': xai_result,
        'dandy': dandy_result,
    }

    print(f"\n{'='*50}")
    print(f" 최종 결과: {rate}% (ESG 총점 {features['total_esg']:.1f})")
    print(dandy_result['dandy_greeting'])
    print(f"{'='*50}\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="단디 ESG 금융 파이프라인")
    parser.add_argument("--company_id", default="COMPANY_001")
    args = parser.parse_args()
    run_pipeline(args.company_id)
```

---

## 5. 웹 UI 파이프라인

### Phase A — Streamlit 데모 앱 (공모전 발표용)

**파일**: `app/streamlit_app.py`  
**실행**: `streamlit run app/streamlit_app.py` → `http://localhost:8501`

```python
"""
Streamlit 데모 대시보드 — 공모전 발표 및 시뮬레이션용
HTML/JS 없이 Python만으로 인터랙티브 대시보드 구현
"""
import streamlit as st
import sys, os
sys.path.insert(0, 'src')

from pipeline.step1_ingest import normalize_features
from pipeline.step2_model  import load_model, predict_interest_rate
from pipeline.step3_xai    import compute_shap_values, generate_natural_language_explanation
from pipeline.step4_dandy  import get_dandy_response
import plotly.graph_objects as go

st.set_page_config(
    page_title="단디 AI ESG 금융 플랫폼",
    page_icon="🏦", layout="wide"
)

# ── 사이드바: 기업 ESG 데이터 입력 ─────────────────────────
with st.sidebar:
    st.title("📋 ESG 데이터 입력")
    company_id   = st.text_input("기업 ID", "COMPANY_001")
    st.subheader("🌿 환경(E)")
    energy_kwh   = st.slider("월 전력 사용량 (kWh)", 500, 10000, 3200)
    carbon_kg    = st.slider("월 탄소 배출량 (kg)",  50,  2000,  450)
    paper_ratio  = st.slider("전자 영수증 전환율 (%)", 0, 100, 72)
    waste_ratio  = st.slider("폐기물 재활용 비율 (%)", 0, 100, 58)
    st.subheader("🤝 사회(S)")
    hire_ratio   = st.slider("취약계층 고용 비율 (%)", 0, 50, 15)
    local_ratio  = st.slider("지역 상품 구매 비율 (%)", 0, 100, 40)
    st.subheader("⚖️ 지배구조(G)")
    account_score = st.slider("투명 회계 점수 (0~100)", 0, 100, 85)
    overdue_count = st.number_input("연체 횟수 (최근 1년)", 0, 20, 0)
    run_btn = st.button("🔍 AI 분석 시작", type="primary", use_container_width=True)

st.title("🏦 단디의 AI 기반 ESG 공급망 금융 플랫폼")
st.caption("iM금융그룹 × ESG × 소상공인 상생 금융")

if run_btn:
    with st.spinner("🤖 단디가 분석 중입니더..."):
        raw = {
            'energy_kwh': energy_kwh, 'carbon_kg': carbon_kg,
            'paper_receipt_ratio': paper_ratio, 'waste_recycle_ratio': waste_ratio,
            'vulnerable_hire_ratio': hire_ratio, 'local_purchase_ratio': local_ratio,
            'accounting_transparency': account_score, 'overdue_count': overdue_count,
        }
        features = normalize_features(raw)
        features['company_id'] = company_id
        model    = load_model()
        rate, _  = predict_interest_rate(features)
        contributions = compute_shap_values(model, features)
        explanation   = generate_natural_language_explanation(contributions, rate)
        dandy_msg     = get_dandy_response("이번 달 결과 알려줘", {'explanation': explanation})

    # 결과 카드
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌿 환경(E)", f"{features['E_score']:.1f}점")
    c2.metric("🤝 사회(S)", f"{features['S_score']:.1f}점")
    c3.metric("⚖️ 지배구조(G)", f"{features['G_score']:.1f}점")
    c4.metric("💰 적용 금리", f"{rate}%",
              delta=f"{5.0 - rate:.2f}% 인하", delta_color="inverse")

    st.divider()
    col_chart, col_explain = st.columns(2)

    with col_chart:
        st.subheader("📊 ESG 영역별 점수")
        fig = go.Figure(go.Bar(
            x=['환경(E)', '사회(S)', '지배구조(G)'],
            y=[features['E_score'], features['S_score'], features['G_score']],
            marker_color=['#2ecc71', '#3498db', '#9b59b6'],
        ))
        fig.update_layout(yaxis_range=[0, 100], height=300)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔍 SHAP 기여도 분석")
        fig2 = go.Figure(go.Bar(
            x=list(contributions.keys()),
            y=[v['pct'] for v in contributions.values()],
            marker_color='#e74c3c',
        ))
        fig2.update_layout(height=280)
        st.plotly_chart(fig2, use_container_width=True)

    with col_explain:
        st.subheader("🤖 AI 설명 (XAI)")
        st.info(explanation)
        st.subheader("💬 단디가 말합니더!")
        st.success(dandy_msg)

    # 챗봇 섹션
    st.divider()
    st.subheader("💬 단디에게 질문하기")
    if "history" not in st.session_state:
        st.session_state.history = []
    for msg in st.session_state.history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])
    if prompt := st.chat_input("단디에게 뭐든지 물어보이소!"):
        st.session_state.history.append({'role': 'user', 'content': prompt})
        reply = get_dandy_response(prompt, {'explanation': explanation})
        st.session_state.history.append({'role': 'assistant', 'content': reply})
        st.rerun()
```

---

### Phase B — FastAPI REST API 서버 (웹/모바일 공통 백엔드)

**파일**: `src/api/main.py`  
**실행**: `uvicorn src.api.main:app --reload --port 8000` → `http://localhost:8000/docs`

```python
"""
FastAPI REST API 서버
Next.js 웹앱과 React Native 앱이 공통으로 사용하는 백엔드
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
sys.path.insert(0, 'src')
from pipeline.step1_ingest import normalize_features
from pipeline.step2_model  import load_model, predict_interest_rate
from pipeline.step3_xai    import compute_shap_values, generate_natural_language_explanation
from pipeline.step4_dandy  import get_dandy_response, generate_push_notification

app = FastAPI(title="단디 ESG API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class ESGInput(BaseModel):
    company_id: str
    energy_kwh: float
    carbon_kg: float
    paper_receipt_ratio: float
    waste_recycle_ratio: float
    vulnerable_hire_ratio: float
    local_purchase_ratio: float
    accounting_transparency: float
    overdue_count: int


class ChatInput(BaseModel):
    message: str
    context: dict = None


@app.post("/api/analyze")
async def analyze(data: ESGInput):
    """ESG 데이터 분석 → 금리 + XAI 결과 반환"""
    try:
        raw = data.model_dump()
        features = normalize_features(raw)
        features['company_id'] = data.company_id
        model = load_model()
        rate, _ = predict_interest_rate(features)
        contributions = compute_shap_values(model, features)
        explanation = generate_natural_language_explanation(contributions, rate)
        return {
            "company_id": data.company_id,
            "esg_scores": {
                "E": round(features['E_score'], 1),
                "S": round(features['S_score'], 1),
                "G": round(features['G_score'], 1),
                "total": round(features['total_esg'], 1),
            },
            "interest_rate": rate,
            "rate_reduction": round(5.0 - rate, 2),
            "contributions": contributions,
            "explanation": explanation,
            "push_notification": generate_push_notification(features, rate),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(data: ChatInput):
    """단디 챗봇 응답"""
    reply = get_dandy_response(data.message, data.context)
    return {"reply": reply}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "단디 ESG API v1.0"}
```

---

### Phase C — Next.js 웹 앱 구조 (프로덕션)

```
web/
├── app/
│   ├── page.tsx           # 메인 대시보드 (ESG 점수 + 금리 요약)
│   ├── analyze/page.tsx   # ESG 데이터 입력 & 분석 결과
│   ├── chat/page.tsx      # 단디 챗봇 전용 페이지
│   └── report/page.tsx    # ESG 리포트 히스토리
├── components/
│   ├── ESGScoreCard.tsx   # ESG 점수 카드 (E/S/G 개별 표시)
│   ├── ShapChart.tsx      # SHAP 기여도 차트 (Recharts 막대)
│   ├── DandyChat.tsx      # 단디 챗봇 UI (말풍선 + 캐릭터)
│   └── RateGauge.tsx      # 금리 게이지 (2.5% ~ 5.0% 범위)
└── lib/
    └── api.ts             # FastAPI 클라이언트 함수 모음
```

**핵심 API 클라이언트** (`web/lib/api.ts`):
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function analyzeESG(data: ESGInput): Promise<ESGResult> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("분석 요청 실패");
  return res.json();
}

export async function chatWithDandy(message: string, context?: object) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });
  return res.json();
}
```

**실행**: `cd web && npm install && npm run dev` → `http://localhost:3000`

---

## 6. 모바일 앱 파이프라인 (React Native)

### 앱 구조

```
mobile/
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx      # 홈: ESG 점수 요약 + 현재 금리 표시
│   │   ├── input.tsx      # ESG 데이터 입력 폼 (슬라이더/입력창)
│   │   ├── chat.tsx       # 단디 챗봇 채팅 화면
│   │   └── report.tsx     # 월별 ESG 리포트 히스토리
│   └── _layout.tsx        # 탭 네비게이션 설정
├── components/
│   ├── ScoreRing.tsx      # ESG 점수 원형 게이지
│   ├── DandyBubble.tsx    # 단디 말풍선 UI (캐릭터 이미지 포함)
│   └── ShapBar.tsx        # SHAP 기여도 수평 막대 차트
└── hooks/
    └── useESGStore.ts     # Zustand 전역 상태 관리
```

### 핵심 화면: 홈

```typescript
// mobile/app/(tabs)/index.tsx
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useESGStore } from '@/hooks/useESGStore';
import ScoreRing   from '@/components/ScoreRing';
import DandyBubble from '@/components/DandyBubble';

export default function HomeScreen() {
  const { esgScore, interestRate, dandyMessage } = useESGStore();

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🏦 단디 ESG 금융</Text>

      {/* ESG 종합 점수 원형 게이지 */}
      <ScoreRing score={esgScore.total} label="ESG 총점" />

      {/* E / S / G 개별 점수 행 */}
      <View style={styles.scoreRow}>
        {[['🌿 환경', esgScore.E], ['🤝 사회', esgScore.S], ['⚖️ 지배구조', esgScore.G]].map(([label, val]) => (
          <View key={label} style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>{label}</Text>
            <Text style={styles.scoreValue}>{val}점</Text>
          </View>
        ))}
      </View>

      {/* 현재 적용 금리 카드 */}
      <View style={styles.rateCard}>
        <Text style={styles.rateLabel}>현재 적용 금리</Text>
        <Text style={styles.rateValue}>{interestRate}%</Text>
        <Text style={styles.rateDelta}>
          기준 금리 대비 {(5.0 - interestRate).toFixed(2)}%p 인하 혜택 중 🎉
        </Text>
      </View>

      {/* 단디 말풍선 */}
      <DandyBubble message={dandyMessage} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: '#f0f4f8', padding: 16 },
  title:      { fontSize: 24, fontWeight: 'bold', color: '#1a365d', marginBottom: 16 },
  scoreRow:   { flexDirection: 'row', justifyContent: 'space-around', marginVertical: 12 },
  scoreItem:  { alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 12, flex: 1, marginHorizontal: 4 },
  scoreLabel: { fontSize: 12, color: '#718096' },
  scoreValue: { fontSize: 20, fontWeight: 'bold', color: '#2d3748' },
  rateCard:   { backgroundColor: '#1a365d', borderRadius: 16, padding: 20, marginVertical: 12, alignItems: 'center' },
  rateLabel:  { color: '#bee3f8', fontSize: 14 },
  rateValue:  { color: '#fff', fontSize: 40, fontWeight: 'bold' },
  rateDelta:  { color: '#90cdf4', fontSize: 13, marginTop: 4 },
});
```

### 모바일 앱 실행

```bash
cd mobile
npx create-expo-app@latest ./ --template blank-typescript
npx expo install expo-notifications zustand recharts

npx expo start
# iOS 시뮬레이터 → i 키
# Android 에뮬레이터 → a 키
# 실물 기기 → Expo Go 앱으로 QR 코드 스캔
```

---

## 7. 디렉터리 구조

```
imbank-esg-platform/
│
├── src/                            # Python 백엔드
│   ├── main.py                     # 파이프라인 통합 실행 진입점
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── step1_ingest.py         # Step 1: ESG 데이터 수집 & 정규화
│   │   ├── step2_model.py          # Step 2: AI 금리 예측 모델
│   │   ├── step3_xai.py            # Step 3: SHAP XAI 분석
│   │   └── step4_dandy.py          # Step 4: 단디 챗봇 & 알림
│   └── api/
│       └── main.py                 # FastAPI REST API 서버
│
├── app/
│   └── streamlit_app.py            # Streamlit 데모 앱 (공모전 발표용)
│
├── web/                            # Next.js 프로덕션 웹 앱
│   ├── app/
│   ├── components/
│   └── lib/
│
├── mobile/                         # React Native 모바일 앱
│   ├── app/
│   ├── components/
│   └── hooks/
│
├── models/
│   └── esg_interest_model.pkl      # 학습된 RandomForest 모델
│
├── outputs/
│   └── shap/                       # SHAP 시각화 차트 PNG 저장소
│
├── assets/
│   └── dandy_logo.png              # 단디 마스코트 이미지
│
├── tests/
│   ├── test_pipeline.py            # Python 파이프라인 단위 테스트
│   └── test_api.py                 # FastAPI 엔드포인트 테스트
│
├── .env.example                    # 환경 변수 템플릿 (API 키 등)
├── requirements.txt                # Python 의존성 목록
└── README.md
```

---

## 8. 단계별 실행 순서 (Quick Start)

### 1. Python 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS / Linux

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (OpenAI API 키는 선택 사항)
copy .env.example .env
# .env 파일에 OPENAI_API_KEY=sk-... 입력
```

### requirements.txt

```
pandas>=2.0
numpy>=1.26
scikit-learn>=1.4
shap>=0.45
joblib
matplotlib
plotly
streamlit>=1.35
fastapi>=0.111
uvicorn[standard]
langchain>=0.2
langchain-openai>=0.1
openai>=1.30
python-dotenv
pydantic>=2.0
httpx
```

### 2. 실행 순서

```bash
# ① CLI 단독 실행 (파이프라인 기능 검증)
python src/main.py --company_id TEST_001

# ② Streamlit 데모 앱 (공모전 발표용 웹 UI)
streamlit run app/streamlit_app.py
# → http://localhost:8501

# ③ FastAPI 서버 (웹·모바일 공통 백엔드)
uvicorn src.api.main:app --reload --port 8000
# → http://localhost:8000/docs  (자동 생성 API 문서)

# ④ Next.js 웹 앱 (새 터미널)
cd web && npm install && npm run dev
# → http://localhost:3000

# ⑤ React Native 모바일 앱 (새 터미널)
cd mobile && npx expo start
```

---

## 9. 배포 파이프라인 (Deployment)

### 발표/데모용 (무료, 즉시 배포 가능)

| 서비스 | 대상 | 방법 |
|:---|:---|:---|
| **Streamlit Cloud** | Streamlit 데모 앱 | GitHub 연결 후 `app/streamlit_app.py` 지정 → 무료 공개 URL 발급 |
| **Render (무료)** | FastAPI 서버 | `Dockerfile` 업로드 후 Web Service로 배포 |

### 프로덕션용

| 서비스 | 대상 | 방법 |
|:---|:---|:---|
| **Vercel** | Next.js 웹 앱 | `cd web && npx vercel deploy` |
| **Railway / Render** | FastAPI API | Docker 컨테이너 자동 배포 |
| **Expo EAS** | React Native 앱 | `eas build && eas submit` (앱스토어/플레이스토어 제출) |

### Dockerfile (FastAPI 서버)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. 개발 로드맵 및 마일스톤

| 단계 | 기간 | 목표 | 산출물 |
|:---|:---|:---|:---|
| **Phase 0** | 1일차 | 환경 설정 & 의존성 설치 | `requirements.txt`, `.env` 세팅 완료 |
| **Phase 1** | 2~3일차 | Python 4-Step 파이프라인 구현 & CLI 테스트 | `src/pipeline/*.py` 전부 작동 확인 |
| **Phase 2** | 4~5일차 | Streamlit 데모 앱 완성 (공모전 핵심 산출물) | `app/streamlit_app.py` + 로컬 실행 영상 |
| **Phase 3** | 6~7일차 | FastAPI 서버 구축 & API 문서 자동 생성 | `src/api/main.py` + `/docs` 확인 |
| **Phase 4** | 8~10일차 | Next.js 웹 UI 개발 | `web/` 전체 + `localhost:3000` 접속 확인 |
| **Phase 5** | 11~14일차 | React Native 모바일 앱 개발 | `mobile/` + Expo Go 실기기 테스트 |
| **Phase 6** | 15일차 | 통합 테스트 & Streamlit Cloud 배포 | 공개 데모 URL 확보 → 발표 자료에 QR 코드 삽입 |

---

## 관련 문서

- [단디의 AI 기반 ESG 공급망 금융 관리 플랫폼](./단디의%20AI%20기반%20ESG%20공급망%20금융%20관리%20플랫폼.md)
- [시장의 선례와 우리의 차별점 정리](./시장의_선례와_우리의_차별점_정리.md)
- [dandi_1 데모 코드 원본](./dandi_1.md)

---

*본 파이프라인 문서는 iM금융그룹 공모전 팀 프로젝트 용도로 작성되었습니다.*  
*최초 작성: 2026-07-21 | Antigravity AI*
