import streamlit as st
import copy
import os
import json
import zipfile
import io
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import requests
import time
# ---- 챗봇 설정 ----
# 방법 1: Hugging Face (무료)
HUGGINGFACE_API_KEY = "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"  # 실제 토큰으로 교체
HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

def call_ai_chatbot(message):
    """AI 챗봇 호출 (Hugging Face API 사용)"""
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": message,
        "parameters": {
            "max_length": 100,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(HUGGINGFACE_MODEL_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "죄송합니다. 응답을 생성할 수 없습니다.")
            else:
                return "죄송합니다. 응답을 생성할 수 없습니다."
        elif response.status_code == 503:
            return "🔄 AI 모델이 준비 중입니다. 잠시 후 다시 시도해주세요."
        else:
            return "⚠️ 일시적인 오류가 발생했습니다."
    except Exception as e:
        return "❌ 연결 오류가 발생했습니다."

# ---- 페이지 설정 ----
st.set_page_config(
    page_title="E1 Link - AIH Portal Hub",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- 화면 너비 감지용 JS 삽입 ----
components.html("""
    <script>
        const sendWidth = () => {
            const width = window.innerWidth;
            const streamlitDoc = window.parent.document;
            const dataElem = streamlitDoc.querySelector('div[data-testid="stData"]');
            if (dataElem) {
                dataElem.setAttribute("data-width", width);
            }
        };
        sendWidth();
        window.addEventListener("resize", sendWidth);
    </script>
""", height=0)

# ---- 모바일 감지 함수 ----
def is_mobile():
    try:
        import streamlit.components.v1 as components
        width = st._get_delta_from_queue("data-width")
        return width and int(width) < 768
    except Exception:
        return False

chatbot_css = """
<style>
    .floating-chat-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        cursor: pointer;
        z-index: 1000;
        font-size: 24px;
        color: white;
        text-decoration: none;
        transition: transform 0.3s ease;
    }
    
    .floating-chat-btn:hover {
        transform: scale(1.1);
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        background: white;
        margin-bottom: 15px;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 8px 12px;
        border-radius: 15px 15px 5px 15px;
        margin: 5px 0;
        text-align: right;
        margin-left: 20%;
    }
    
    .bot-message {
        background: #f1f3f4;
        color: #333;
        padding: 8px 12px;
        border-radius: 15px 15px 15px 5px;
        margin: 5px 0;
        margin-right: 20%;
    }
</style>
"""

# 기존 CSS 부분에 chatbot_css 추가
st.markdown(chatbot_css, unsafe_allow_html=True)

# ---- 전역 CSS 스타일 ----
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Noto Sans KR', 'Segoe UI', sans-serif;
        }
        
        /* 메인 컨테이너 스타일링 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 사이드바 스타일링 */
        .css-1d391kg {
            background: linear-gradient(180deg, #d97706 0%, #ea580c 100%);
        }
        
        .css-1d391kg .css-17eq0hr {
            color: white;
        }
        
        /* 헤더 스타일 */
        .main-header {
            background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
            margin: -80px auto 0;
            color: white;
            padding: 0.15rem;
            border-radius: 15px;
            margin-bottom: 0.5rem;
            text-align: center;
            box-shadow: 0 10px 25px rgba(217, 119, 6, 0.3);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            color: white;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* 대시보드 카드 스타일 */
        .dashboard-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid #d97706;
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #d97706;
            margin-bottom: 0.5rem;
        }
        
        .card-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ea580c;
        }
        
        .card-description {
            color: #6b7280;
            font-size: 0.9rem;
        }
        
        /* 링크 카드 스타일 */
        .link-card {
            height: 40px;  /* 원하는 높이로 조정 */
            display: flex;
            align-items: center;
            justify-content: left;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
        }
        
        .link-content {
            text-align: center;
            width: 100%;
        }
        
        .link-content a {
            text-decoration: none;
            color: #333;
            font-weight: 500;
        }
        
        .link-content a:hover {
            color: #007bff;
        }
        
        .link-card:hover {
            border-color: #ea580c;
            box-shadow: 0 4px 12px rgba(234, 88, 12, 0.15);
            transform: translateY(-1px);
        }
        
        .link-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 3px;
            background: #ea580c;
            transform: scaleY(0);
            transition: transform 0.2s ease;
        }
        
        .link-card:hover::before {
            transform: scaleY(1);
        }
        
        .link-content {
            display: flex;
            align-items: center;
            flex: 1;
        }
        
        .link-actions {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .favorite-btn {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            transition: transform 0.2s ease;
            color: #fbbf24;
        }
        
        .favorite-btn:hover {
            transform: scale(1.2);
        }
        
        .delete-btn {
            background: none;
            border: none;
            font-size: 1rem;
            cursor: pointer;
            color: #ef4444;
            transition: transform 0.2s ease;
        }
        
        .delete-btn:hover {
            transform: scale(1.1);
        }
        
        .link-card a {
            text-decoration: none;
            color: #374151;
            font-weight: 500;
            margin-left: 0.5rem;
        }
        
        .link-card a:hover {
            color: #d97706;
        }
        
        /* 탭 스타일 개선 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            color: #64748b;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: #d97706;
            color: white;
            border-color: #d97706;
        }
        
        /* 버튼 스타일 개선 */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* 포털 링크 하단 고정 */
        .bottom-links {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-top: 3px solid #d97706;
            z-index: 1000;
        }
        
        .bottom-links a {
            margin: 0 0.75rem;
            text-decoration: none;
            color: #d97706;
            font-weight: 500;
            white-space: nowrap;
            transition: color 0.2s ease;
        }
        
        .bottom-links a:hover {
            color: #ea580c;
        }
        
        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }
            
            .bottom-links {
                width: 90%;
                bottom: 10px;
                right: 5%;
                padding: 0.75rem;
                font-size: 0.9rem;
            }
            
            .bottom-links a {
                display: block;
                margin: 0.25rem 0;
                text-align: center;
            }
            
            .dashboard-card {
                padding: 1rem;
            }
            
            .card-value {
                font-size: 1.5rem;
            }
            
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
            }
        }
        
        /* 검색 결과 하이라이트 */
        .search-highlight {
            background: #fef3c7;
            padding: 0.1rem 0.3rem;
            border-radius: 4px;
            font-weight: 600;
        }
        
        /* 알림 스타일 */
        .success-message {
            background: #dcfce7;
            color: #166534;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border-left: 4px solid #22c55e;
            margin: 1rem 0;
        }
        
        .warning-message {
            background: #fef3c7;
            color: #92400e;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin: 1rem 0;
        }
        
        /* 설정 카드 스타일 */
        .settings-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .settings-card h4 {
            color: #d97706;
            margin-bottom: 1rem;
        }
        
        /* 상태 표시 배지 */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .status-online {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-offline {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .status-maintenance {
            background: #fef3c7;
            color: #92400e;
        }
    </style>
""", unsafe_allow_html=True)

# ---- 관리자 ID 및 설정 ----
ADMIN_IDS = ["admin"]
SAVE_DIR = "sites_data"
DEFAULT_TABS_DIR = "default_tabs"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(DEFAULT_TABS_DIR, exist_ok=True)

# ---- 팀 목록 ----
teams = ["기술운영팀", "기술지원팀", "SHE지원팀", "안전시공팀", "여수기지", "대산기지", "인천기지"]

# ---- 기본 사이트 데이터 ----
default_sites = {
    "기술운영팀": {
        "기술운영": {
            "description": "기술운영",
            "links": [
                {"description": "항만물류정보시스템(PORT-MIS)", "url": "https://new.portmis.go.kr/portmis/websquare/websquare.jsp?w2xPath=/portmis/w2/main/intro.xml", "favorite": False}
            ]
        }
    },
    "기술지원팀": {
        "기술지원": {
            "description": "기술지원",
            "links": []
        }
    },
    "SHE지원팀": {
        "SHE 지원팀": {
            "description": "SHE 지원팀",
            "links": [
                {"description": "가스안전공사", "url": "https://www.kgs.or.kr/", "favorite": False},
                {"description": "안전보건공단", "url": "https://www.kosha.or.kr/kosha/index.do", "favorite": False}
            ]
        }
    },
    "안전시공팀": {
        "안전시공": {
            "description": "안전시공",
            "links": [
                {"description": "KSG code", "url": "https://cyber.kgs.or.kr/kgscode.Index.do", "favorite": False},
                {"description": "국가법령정보센터", "url": "https://www.law.go.kr/LSW/main.html", "favorite": False}
            ]
        }
    },
    "여수기지": {
        "여수기지": {
            "description": "여수기지",
            "links": []
        }
    },
    "대산기지": {
        "대산기지": {
            "description": "대산기지",
            "links": []
        }
    },
    "인천기지": {
        "인천기지": {
            "description": "인천기지",
            "links": []
        }
    }
}

# ---- 세션 초기화 ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "홈"

# ---- 챗봇 함수들 ----
def get_ai_response(user_message, context=""):
    """AI 챗봇 응답 생성"""
    try:
        # OpenAI GPT 사용 예시
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""
                당신은 E1 회사의 AI 어시스턴트입니다. 
                주요 역할:
                1. 설비 관련 질문 답변 및 링크 제공
                2. 안전 가이드라인 제공
                3. 시스템 사용법 안내
                4. 링크 검색 및 추천
                
                현재 사용자 컨텍스트: {context}
                
                답변은 친근하고 전문적으로 해주세요.
                """},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"죄송합니다. 현재 AI 서비스에 문제가 있습니다. 오류: {str(e)}"

def search_links_with_ai(query, current_sites):
    """AI를 활용한 스마트 링크 검색"""
    matching_links = []
    
    # 기본 키워드 검색
    for tab_name, tab_data in current_sites.items():
        for link in tab_data["links"]:
            if query.lower() in link['description'].lower() or query.lower() in link['url'].lower():
                matching_links.append({
                    'tab': tab_name,
                    'title': link['description'],
                    'url': link['url'],
                    'favorite': link.get('favorite', False)
                })
    
    return matching_links

def get_chatbot_suggestions(user_role, current_team):
    """사용자 역할과 팀에 따른 챗봇 제안"""
    suggestions = {
        "기술운영팀": [
            "설비 점검 일정은 어떻게 확인하나요?",
            "AIH 시스템 사용법을 알려주세요",
            "펌프 이상 시 대처 방법은?"
        ],
        "SHE지원팀": [
            "안전 규정 최신 업데이트는?",
            "사고 발생시 보고 절차는?",
            "가스 누출 시 대응 방법은?"
        ],
        "기본": [
            "링크를 어떻게 추가하나요?",
            "즐겨찾기 설정 방법은?",
            "시스템 사용법을 알려주세요"
        ]
    }
    
    return suggestions.get(current_team, suggestions["기본"])

# ---- 데이터 관리 함수들 ----
def save_sites(uid, team):
    file_path = os.path.join(SAVE_DIR, f"{uid}_{team}_sites.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(st.session_state[f"sites_{uid}_{team}"], f, ensure_ascii=False, indent=2)

def load_sites(uid, team):
    file_path = os.path.join(SAVE_DIR, f"{uid}_{team}_sites.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for tab in data:
                for link in data[tab]["links"]:
                    if "favorite" not in link:
                        link["favorite"] = False
            return data
    else:
        # 팀별 기본 탭 로드
        default_tab_file = os.path.join(DEFAULT_TABS_DIR, f"{team}_default.json")
        if os.path.exists(default_tab_file):
            with open(default_tab_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return copy.deepcopy(default_sites[team])

def save_default_tabs(team, data):
    file_path = os.path.join(DEFAULT_TABS_DIR, f"{team}_default.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_default_tabs(team):
    file_path = os.path.join(DEFAULT_TABS_DIR, f"{team}_default.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return copy.deepcopy(default_sites[team])

# ---- 링크 관리 함수들 ----
def add_link(tab_name, title, url):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    
    st.session_state[site_key][tab_name]["links"].append({
        "description": title, 
        "url": url, 
        "favorite": False
    })
    save_sites(viewing_user_id, team)

def delete_link(tab_name, index):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    
    del st.session_state[site_key][tab_name]["links"][index]
    save_sites(viewing_user_id, team)

def toggle_favorite(tab_name, index):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    
    current_fav = st.session_state[site_key][tab_name]["links"][index].get("favorite", False)
    st.session_state[site_key][tab_name]["links"][index]["favorite"] = not current_fav
    save_sites(viewing_user_id, team)

def add_tab(tab_name):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    page_key = f"pages_{viewing_user_id}_{team}"
    
    if tab_name and tab_name not in st.session_state[site_key]:
        st.session_state[site_key][tab_name] = {"description": tab_name, "links": []}
        if page_key not in st.session_state:
            st.session_state[page_key] = {}
        st.session_state[page_key][tab_name] = 0
        save_sites(viewing_user_id, team)
        return True
    return False

def delete_tab(tab_name):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    page_key = f"pages_{viewing_user_id}_{team}"
    
    if tab_name in st.session_state[site_key]:
        del st.session_state[site_key][tab_name]
        if page_key in st.session_state and tab_name in st.session_state[page_key]:
            del st.session_state[page_key][tab_name]
        save_sites(viewing_user_id, team)

def rename_tab(old_name, new_name):
    viewing_user_id = st.session_state.get("viewing_user_id", st.session_state.user_id)
    team = st.session_state.get("current_team", st.session_state.team)
    site_key = f"sites_{viewing_user_id}_{team}"
    
    if new_name and new_name not in st.session_state[site_key]:
        st.session_state[site_key][new_name] = st.session_state[site_key][old_name]
        st.session_state[site_key][new_name]["description"] = new_name
        del st.session_state[site_key][old_name]
        save_sites(viewing_user_id, team)
        return True
    return False

def create_backup_zip():
    """모든 사용자 데이터를 ZIP 파일로 백업"""
    backup_data = {}
    
    # sites_data 폴더의 모든 파일 백업
    if os.path.exists(SAVE_DIR):
        for file in os.listdir(SAVE_DIR):
            if file.endswith('.json'):
                file_path = os.path.join(SAVE_DIR, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data[f"sites_data/{file}"] = json.load(f)
    
    # default_tabs 폴더의 모든 파일 백업
    if os.path.exists(DEFAULT_TABS_DIR):
        for file in os.listdir(DEFAULT_TABS_DIR):
            if file.endswith('.json'):
                file_path = os.path.join(DEFAULT_TABS_DIR, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data[f"default_tabs/{file}"] = json.load(f)
    
    # ZIP 생성
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 백업 정보 파일 추가
        backup_info = {
            "backup_date": datetime.now().isoformat(),
            "total_files": len(backup_data),
            "version": "1.0"
        }
        zip_file.writestr("backup_info.json", json.dumps(backup_info, ensure_ascii=False, indent=2))
        
        # 각 데이터 파일 추가
        for file_path, data in backup_data.items():
            zip_file.writestr(file_path, json.dumps(data, ensure_ascii=False, indent=2))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def restore_from_backup(uploaded_file):
    """백업 파일로부터 데이터 복원"""
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
            # 백업 정보 확인
            if "backup_info.json" in zip_file.namelist():
                backup_info = json.loads(zip_file.read("backup_info.json").decode('utf-8'))
                
                restored_files = []
                # 각 파일 복원
                for file_path in zip_file.namelist():
                    if file_path.startswith("sites_data/") and file_path.endswith(".json"):
                        data = json.loads(zip_file.read(file_path).decode('utf-8'))
                        local_path = os.path.join(SAVE_DIR, file_path.replace("sites_data/", ""))
                        with open(local_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        restored_files.append(file_path)
                    
                    elif file_path.startswith("default_tabs/") and file_path.endswith(".json"):
                        data = json.loads(zip_file.read(file_path).decode('utf-8'))
                        local_path = os.path.join(DEFAULT_TABS_DIR, file_path.replace("default_tabs/", ""))
                        with open(local_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        restored_files.append(file_path)
                
                return True, len(restored_files), backup_info["backup_date"]
            else:
                return False, 0, "백업 정보 파일이 없습니다."
    except Exception as e:
        return False, 0, f"복원 중 오류 발생: {str(e)}"

def apply_default_tabs_to_existing_users(team):
    """기본 탭 변경사항을 기존 사용자들에게 적용"""
    default_data = load_default_tabs(team)
    
    # 해당 팀의 모든 사용자 파일 찾기
    all_files = os.listdir(SAVE_DIR)
    user_files = [f for f in all_files if f.endswith(f"_{team}_sites.json")]
    
    updated_users = []
    for file in user_files:
        user_id = file.split("_")[0]
        file_path = os.path.join(SAVE_DIR, file)
        
        # 사용자 데이터 로드
        with open(file_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        # 기본 탭과 병합 (기존 사용자 데이터 우선)
        for tab_name, tab_data in default_data.items():
            if tab_name not in user_data:
                # 새로운 기본 탭 추가
                user_data[tab_name] = copy.deepcopy(tab_data)
            else:
                # 기존 탭에 새로운 기본 링크 추가 (중복 체크)
                existing_urls = [link["url"] for link in user_data[tab_name]["links"]]
                for default_link in tab_data["links"]:
                    if default_link["url"] not in existing_urls:
                        user_data[tab_name]["links"].append(copy.deepcopy(default_link))
        
        # 업데이트된 데이터 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        updated_users.append(user_id)
    
    return updated_users

# ---- 로그인 화면 ----
if not st.session_state.authenticated:
    st.markdown("""
        <div class="main-header">
            <h1>🔗 E1 Link</h1>
            <p>AIH Portal Hub - 설비 정보 통합 관리 시스템</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🚪 시스템 접속")
            team = st.selectbox("🏢 팀을 선택하세요", teams, key="team_selectbox")
            user_id = st.text_input("👤 사번 또는 사용자 ID", value="", placeholder="예: honggildong", key="user_input")
            submitted = st.form_submit_button("🔑 접속하기", use_container_width=True)
            
            if submitted:
                if not user_id.strip():
                    st.error("사번 또는 사용자 ID를 입력해주세요.")
                    st.stop()
                st.session_state.authenticated = True
                st.session_state.team = team
                st.session_state.user_id = user_id.strip()
                st.rerun()
    st.stop()

# ---- 메인 화면 ----
user_id = st.session_state.user_id
is_admin = user_id in ADMIN_IDS

# 관리자 또는 일반 사용자 설정
if is_admin:
    with st.sidebar:
        st.markdown("### 👨‍💼 관리자 설정")
        current_team = st.selectbox("조회할 팀 선택", teams, 
                                  index=teams.index(st.session_state.team), 
                                  key="admin_team_selectbox")
        
        all_files = os.listdir(SAVE_DIR)
        all_user_ids = sorted(set(
            f.split("_")[0] for f in all_files if f.endswith(f"_{current_team}_sites.json")
        ))
        
        if all_user_ids:
            selected_user = st.selectbox("조회할 사용자 선택", all_user_ids, key="admin_user_select")
            viewing_user_id = selected_user
        else:
            viewing_user_id = user_id
            st.info("해당 팀에 등록된 사용자가 없습니다.")
    
    st.session_state.current_team = current_team
    st.session_state.viewing_user_id = viewing_user_id
else:
    current_team = st.session_state.team
    viewing_user_id = user_id
    st.session_state.current_team = current_team
    st.session_state.viewing_user_id = viewing_user_id

# ---- 사이드바 네비게이션 ----
with st.sidebar:
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #d97706 0%, #ea580c 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">🔗 E1 Link</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                {current_team} | {viewing_user_id}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 네비게이션 메뉴
    nav_options = ["🏠 홈", "🔗 링크 바로가기", "🤖 AI 도우미", "📖 사용자 매뉴얼", "🔧 설비 상태진단"]
    if is_admin:
        nav_options.extend(["⚙️ 팀별 기본 탭 관리", "💾 데이터 백업 관리"])
    
    selected_nav = st.radio("메뉴", nav_options, key="navigation")
    st.session_state.current_page = selected_nav.split(" ", 1)[1]  # 이모지 제거

    st.markdown("---")
    # 사이드바에 검색 기능 추가
    with st.sidebar:
        st.markdown("### 🔍 링크 검색")
        search_query = st.text_input("검색어 입력", placeholder="링크 제목 또는 URL로 검색...", key="global_search")
        show_favorites_only = st.checkbox("⭐ 즐겨찾기만 보기", key="global_favorites")
    
    # 탭 관리 기능을 사이드바에 추가
    if is_admin or viewing_user_id == user_id:
        st.markdown("---")
        st.markdown("### 📝 탭 관리")
        
        # 탭 추가
        with st.expander("➕ 탭 추가", expanded=False):
            new_tab_name = st.text_input("새 탭 이름", key="sidebar_new_tab_input")
            if st.button("탭 추가", key="sidebar_add_tab"):
                if new_tab_name:
                    site_key = f"sites_{viewing_user_id}_{current_team}"
                    if site_key not in st.session_state:
                        st.session_state[site_key] = load_sites(viewing_user_id, current_team)
                    
                    if add_tab(new_tab_name):
                        st.success(f"'{new_tab_name}' 탭이 추가되었습니다.")
                        st.rerun()
                    else:
                        st.error("탭 이름을 입력하거나 이미 존재하는 탭입니다.")
        
        # 탭 이름 변경
        site_key = f"sites_{viewing_user_id}_{current_team}"
        if site_key not in st.session_state:
            st.session_state[site_key] = load_sites(viewing_user_id, current_team)
        
        current_sites = st.session_state[site_key]
        
        if current_sites:
            with st.expander("🏷️ 탭 이름 변경", expanded=False):
                tab_to_rename = st.selectbox("변경할 탭 선택", list(current_sites.keys()), key="sidebar_rename_tab_select")
                new_name = st.text_input("새 탭 이름", value=tab_to_rename, key="sidebar_rename_input")
                if st.button("이름 변경", key="sidebar_rename_btn"):
                    if rename_tab(tab_to_rename, new_name):
                        st.success(f"탭 이름이 '{new_name}'으로 변경되었습니다.")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 탭 이름이거나 비어있습니다.")
            
            # 탭 삭제
            with st.expander("🗑️ 탭 삭제", expanded=False):
                tab_to_delete = st.selectbox("삭제할 탭 선택", list(current_sites.keys()), key="sidebar_delete_tab_select")
                if st.button("탭 삭제", key="sidebar_delete_tab"):
                    delete_tab(tab_to_delete)
                    st.success(f"'{tab_to_delete}' 탭이 삭제되었습니다.")
                    st.rerun()
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("user_id", None)
        st.session_state.pop("team", None)
        st.rerun()

# ---- 데이터 로딩 ----
site_key = f"sites_{viewing_user_id}_{current_team}"
page_key = f"pages_{viewing_user_id}_{current_team}"

if site_key not in st.session_state:
    st.session_state[site_key] = load_sites(viewing_user_id, current_team)
    st.session_state[page_key] = {tab: 0 for tab in st.session_state[site_key]}

current_sites = st.session_state[site_key]
current_pages = st.session_state.get(page_key, [])

def apply_default_tabs_to_existing_users(team):
    """기본 탭 변경사항을 기존 사용자들에게 적용"""
    default_data = load_default_tabs(team)
    
    # 해당 팀의 모든 사용자 파일 찾기
    all_files = os.listdir(SAVE_DIR)
    user_files = [f for f in all_files if f.endswith(f"_{team}_sites.json")]
    
    updated_users = []
    for file in user_files:
        user_id = file.split("_")[0]
        file_path = os.path.join(SAVE_DIR, file)
        
        # 사용자 데이터 로드
        with open(file_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        # 기본 탭과 병합 (기존 사용자 데이터 우선)
        for tab_name, tab_data in default_data.items():
            if tab_name not in user_data:
                # 새로운 기본 탭 추가
                user_data[tab_name] = copy.deepcopy(tab_data)
            else:
                # 기존 탭에 새로운 기본 링크 추가 (중복 체크)
                existing_urls = [link["url"] for link in user_data[tab_name]["links"]]
                for default_link in tab_data["links"]:
                    if default_link["url"] not in existing_urls:
                        user_data[tab_name]["links"].append(copy.deepcopy(default_link))
        
        # 업데이트된 데이터 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        updated_users.append(user_id)
    
    return updated_users

# ---- 페이지 라우팅 ----
if st.session_state.current_page == "홈":
    # ---- 대시보드 페이지 ----
    st.markdown("""
        <div class="main-header">
            <h1>🏠 대시보드</h1>
            <p>E1 Link AIH Portal Hub 현황</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 통계 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    total_links = sum(len(tab_data["links"]) for tab_data in current_sites.values())
    total_favorites = sum(
        sum(1 for link in tab_data["links"] if link.get("favorite", False))
        for tab_data in current_sites.values()
    )
    total_tabs = len(current_sites)
    
    with col1:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">총 링크 수</div>
                <div class="card-value">{total_links}</div>
                <div class="card-description">등록된 전체 링크</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">즐겨찾기</div>
                <div class="card-value">{total_favorites}</div>
                <div class="card-description">즐겨찾기 설정된 링크</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">총 탭 수</div>
                <div class="card-value">{total_tabs}</div>
                <div class="card-description">생성된 탭 개수</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_links = round(total_links / total_tabs, 1) if total_tabs > 0 else 0
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">총 사용자 수</div>
                <div class="card-value">168</div>
                <div class="card-description">위젯 사용자 수</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 최근 활동 및 즐겨찾기
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⭐ 즐겨찾기 링크")
        favorite_links = []
        for tab_name, tab_data in current_sites.items():
            for link in tab_data["links"]:
                if link.get("favorite", False):
                    favorite_links.append((tab_name, link))
        
        if favorite_links:
            for tab_name, link in favorite_links[:5]:  # 최대 5개만 표시
                st.markdown(f"""
                    <div class="link-card">
                        <div class="link-content">
                            <span>⭐</span>
                            <a href="{link['url']}" target="_blank">{link['description']}</a>
                        </div>
                        <small style="color: #6b7280;">({tab_name})</small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("즐겨찾기로 설정된 링크가 없습니다.")
    
    with col2:
        st.markdown("### 📊 탭별 링크 현황")
        for tab_name, tab_data in current_sites.items():
            link_count = len(tab_data["links"])
            favorite_count = sum(1 for link in tab_data["links"] if link.get("favorite", False))
            
            st.markdown(f"""
                <div class="dashboard-card" style="margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="card-title" style="margin-bottom: 0.2rem; font-size: 1rem;">{tab_name}</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">
                                링크 {link_count}개 | 즐겨찾기 {favorite_count}개
                            </div>
                        </div>
                        <div class="card-value" style="font-size: 1.5rem;">{link_count}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.current_page == "링크 바로가기":
    # ---- 링크 관리 페이지 ----
    st.markdown("""
        <div class="main-header">
            <h1>🔗 E1 링크</h1>
            <p>팀별 포털 및 시스템 링크 관리</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 탭이 있는 경우에만 탭 표시
    if current_sites:
        tab_names = list(current_sites.keys())
        tabs = st.tabs(tab_names)
        
        # 각 탭의 내용 표시
        for i, (tab_name, tab) in enumerate(zip(tab_names, tabs)):
            with tab:
                # 탭별 개별 링크 추가 버튼 (각 탭 내부에 배치)
                if is_admin or viewing_user_id == user_id:
                    col1, col2 = st.columns([9, 2])
                    with col2:
                        with st.popover("➕ 새 링크"):
                            st.markdown(f"**{tab_name}** 탭에 추가")
                            
                            # 링크 제목
                            new_title = st.text_input("링크 제목", key=f"popup_title_{tab_name}_{i}")
                            
                            # AIH 설비 여부 체크박스
                            is_aih_equipment = st.checkbox("AIH 설비 여부", key=f"popup_aih_equipment_{tab_name}_{i}")
                            
                            # 기지 선택 (AIH 설비인 경우에만 표시)
                            selected_base = None
                            if is_aih_equipment:
                                selected_base = st.selectbox(
                                    "기지 선택", 
                                    ["대산", "인천", "여수"], 
                                    key=f"popup_base_select_{tab_name}_{i}"
                                )
                            
                            # URL 입력
                            if is_aih_equipment and selected_base:
                                # 기지별 기본 URL 매핑
                                base_urls = {
                                    "대산": "http://aih.e1.co.kr/#/item/DS%7C",
                                    "인천": "http://aih.e1.co.kr/#/item/IC%7C", 
                                    "여수": "http://aih.e1.co.kr/#/item/YS%7C"
                                }
                                
                                st.caption(f"기본 URL: {base_urls[selected_base]}")
                                equipment_name = st.text_input(
                                    "설비명", 
                                    placeholder="예: P-501A",
                                    key=f"popup_equipment_name_{tab_name}_{i}"
                                )
                                # 전체 URL 조합
                                new_url = base_urls[selected_base] + (equipment_name if equipment_name else "")
                                if equipment_name:
                                    st.caption(f"완성된 URL: {new_url}")
                            else:
                                new_url = st.text_input(
                                    "URL", 
                                    placeholder="http:// 또는 https://",
                                    key=f"popup_url_{tab_name}_{i}"
                                )
                            
                            # 추가 버튼
                            if st.button("링크 추가", key=f"popup_submit_{tab_name}_{i}", use_container_width=True):
                                if new_title and new_url:
                                    if not new_url.startswith(('http://', 'https://')):
                                        st.error("URL은 http:// 또는 https://로 시작해야 합니다.")
                                    elif is_aih_equipment and selected_base and not equipment_name:
                                        st.error("설비명을 입력해주세요.")
                                    else:
                                        add_link(tab_name, new_title, new_url)
                                        st.success(f"'{new_title}' 링크가 추가되었습니다.")
                                        st.rerun()
                                else:
                                    st.error("제목과 URL을 모두 입력해주세요.")
                
                tab_data = current_sites[tab_name]
                links = tab_data["links"]
                
                # 링크 목록 필터링 (사이드바의 검색 조건 사용)
                if links:
                    # 검색어 및 즐겨찾기 필터 적용
                    filtered_links = []
                    for idx, link in enumerate(links):
                        # 검색어 필터
                        if search_query:
                            if search_query.lower() not in link["description"].lower() and search_query.lower() not in link["url"].lower():
                                continue
                        # 즐겨찾기 필터
                        if show_favorites_only and not link.get("favorite", False):
                            continue
                        filtered_links.append((idx, link))
                    
                    # 필터링된 링크 표시
                    if filtered_links:
                        for idx, link in filtered_links:
                            col2, col1, col3 = st.columns([1, 15, 1])
                            with col1:
                                st.markdown(f"""
                                    <div class="link-card">
                                        <div class="link-content">
                                            <a href="{link['url']}" target="_blank">{link['description']}</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            if is_admin or viewing_user_id == user_id:
                                with col2:
                                    # 즐겨찾기 버튼: True면 노란별(⭐), False면 빈별(☆)
                                    fav_icon = "⭐" if link.get('favorite', False) else "☆"
                                    if st.button(fav_icon, 
                                               key=f"fav_{tab_name}_{idx}",
                                               help="즐겨찾기 토글"):
                                        toggle_favorite(tab_name, idx)
                                        st.rerun()
                                
                                with col3:
                                    if st.button("🗑️", key=f"del_{tab_name}_{idx}", help="링크 삭제"):
                                        delete_link(tab_name, idx)
                                        st.success("링크가 삭제되었습니다.")
                                        st.rerun()
                    else:
                        if show_favorites_only:
                            st.info("즐겨찾기한 링크가 없습니다.")
                        elif search_query:
                            st.info("검색 조건에 맞는 링크가 없습니다.")
                        else:
                            st.info("이 탭에는 아직 링크가 없습니다. 새 링크를 추가해보세요.")
                else:
                    st.info("이 탭에는 아직 링크가 없습니다. 새 링크를 추가해보세요.")
    else:
        st.info("탭이 없습니다. 사이드바에서 새 탭을 추가해주세요.")

elif st.session_state.current_page == "AI 도우미":
    st.markdown("""
        <div class="main-header">
            <h1>🤖 AI 도우미</h1>
            <p>E1 Link 시스템에 대해 궁금한 것이 있으면 언제든 물어보세요!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 채팅 기록 초기화
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.ai_chat_history:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for chat in st.session_state.ai_chat_history:
                st.markdown(f'<div class="user-message">👤 {chat["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bot-message">🤖 {chat["bot"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👋 안녕하세요! E1 Link AI 도우미입니다. 무엇을 도와드릴까요?")
    
    # 채팅 입력 폼
    with st.form("ai_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_message = st.text_input("💬 메시지를 입력하세요...", key="ai_chat_input", placeholder="예: 링크 추가 방법을 알려주세요")
        with col2:
            send_btn = st.form_submit_button("📤 전송", use_container_width=True)
    
    # 빠른 질문 버튼들
    st.markdown("### 💡 빠른 질문")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔗 링크 추가 방법", use_container_width=True):
            user_message = "링크를 추가하는 방법을 알려주세요"
            send_btn = True
    
    with col2:
        if st.button("📁 탭 관리 방법", use_container_width=True):
            user_message = "탭을 관리하는 방법을 알려주세요"
            send_btn = True
    
    with col3:
        if st.button("⭐ 즐겨찾기 사용법", use_container_width=True):
            user_message = "즐겨찾기 기능을 사용하는 방법을 알려주세요"
            send_btn = True
    
    # 메시지 처리
    if send_btn and user_message:
        # 사용자 메시지를 기록에 추가
        with st.spinner("🤖 AI가 답변을 생성하고 있습니다..."):
            ai_response = call_ai_chatbot(user_message)
            
            # 시스템 관련 질문에 대한 특별 응답
            if any(keyword in user_message.lower() for keyword in ['링크 추가', '링크추가', '링크 만들기']):
                ai_response = """
🔗 **링크 추가 방법:**

1. 원하는 탭을 선택합니다
2. 탭 내의 '➕ 새 링크' 버튼을 클릭합니다
3. 링크 제목과 URL을 입력합니다
4. AIH 설비인 경우 '기지 선택' 후 설비명을 입력하세요
5. '링크 추가' 버튼을 클릭하면 완료됩니다!

💡 **팁:** AIH 설비의 경우 기지를 선택하면 기본 URL이 자동으로 설정됩니다.
                """
            elif any(keyword in user_message.lower() for keyword in ['탭 관리', '탭 추가', '탭 삭제']):
                ai_response = """
📁 **탭 관리 방법:**

**탭 추가:**
- 사이드바 '📝 탭 관리' → '➕ 탭 추가'에서 새 탭 이름 입력

**탭 이름 변경:**
- 사이드바 '📝 탭 관리' → '🏷️ 탭 이름 변경'에서 수정

**탭 삭제:**
- 사이드바 '📝 탭 관리' → '🗑️ 탭 삭제'에서 삭제

⚠️ **주의:** 탭을 삭제하면 해당 탭의 모든 링크가 함께 삭제됩니다.
                """
            elif any(keyword in user_message.lower() for keyword in ['즐겨찾기', '즐겨 찾기', '북마크']):
                ai_response = """
⭐ **즐겨찾기 사용법:**

1. 링크 목록에서 각 링크 왼쪽의 별(☆) 버튼을 클릭합니다
2. 즐겨찾기가 설정되면 노란 별(⭐)로 변경됩니다
3. 사이드바에서 '⭐ 즐겨찾기만 보기'를 체크하면 즐겨찾기한 링크만 표시됩니다
4. 홈 화면에서도 즐겨찾기 링크들을 빠르게 확인할 수 있습니다

💡 **활용 팁:** 자주 사용하는 링크들을 즐겨찾기로 설정하여 빠르게 접근하세요!
                """
            
            # 채팅 기록에 추가
            st.session_state.ai_chat_history.append({
                "user": user_message,
                "bot": ai_response
            })
            
            # 기록이 너무 길어지면 오래된 것 삭제
            if len(st.session_state.ai_chat_history) > 50:
                st.session_state.ai_chat_history = st.session_state.ai_chat_history[-50:]
        
        st.rerun()
    
    # 채팅 기록 관리
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 대화 기록 삭제", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📄 대화 기록 내보내기", use_container_width=True):
            if st.session_state.ai_chat_history:
                chat_export = ""
                for i, chat in enumerate(st.session_state.ai_chat_history, 1):
                    chat_export += f"[{i}] 사용자: {chat['user']}\n"
                    chat_export += f"[{i}] AI: {chat['bot']}\n\n"
                
                st.download_button(
                    label="💾 대화 기록 다운로드",
                    data=chat_export,
                    file_name=f"e1_link_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

elif st.session_state.current_page == "사용자 매뉴얼":
    # ---- 사용자 매뉴얼 페이지 ----
    st.markdown("""
        <div class="main-header">
            <h1>📖 사용자 매뉴얼</h1>
            <p>E1 Link 시스템 사용 방법 안내</p>
        </div>
    """, unsafe_allow_html=True)
    
    manual_tabs = st.tabs(["🚀 시작하기", "🔗 링크 관리", "⚙️ 고급 기능", "❓ FAQ"])
    
    with manual_tabs[0]:
        st.markdown("""
        ## 🚀 시작하기
        
        ### 로그인
        1. **팀 선택**: 소속 팀을 드롭다운에서 선택합니다
        2. **사번 입력**: 사번 또는 사용자 ID를 입력합니다
        3. **접속하기**: 버튼을 클릭하여 시스템에 접속합니다
        
        ### 기본 화면 구성
        - **사이드바**: 메뉴 탐색 및 탭 관리
        - **메인 화면**: 선택한 메뉴의 내용 표시
        - **하단 고정 링크**: 주요 포털 바로가기
        
        ### 주요 메뉴
        - **홈**: 대시보드 및 통계 정보
        - **링크 바로가기**: 링크 목록 및 관리
        - **사용자 매뉴얼**: 현재 보고 있는 페이지
        - **설비 상태진단**: 설비 관련 정보 (개발 예정)
        """)
    
    with manual_tabs[1]:
        st.markdown("""
        ## 🔗 링크 관리
        
        ### 링크 추가
        1. 원하는 탭에서 **"➕ 새 링크 추가"** 섹션을 확장합니다
        2. **링크 제목**과 **URL**을 입력합니다
        3. **"링크 추가"** 버튼을 클릭합니다
        
        ### 링크 관리 기능
        - **⭐ 즐겨찾기**: 자주 사용하는 링크를 즐겨찾기로 설정
        - **🗑️ 삭제**: 불필요한 링크 제거
        - **🔍 검색**: 링크 제목이나 URL로 검색
        - **⭐ 즐겨찾기만 보기**: 즐겨찾기 링크만 필터링
        
        ### 탭 관리
        - **탭 추가**: 사이드바에서 새로운 카테고리 탭 생성
        - **탭 이름 변경**: 기존 탭의 이름 수정
        - **탭 삭제**: 불필요한 탭 제거 (링크도 함께 삭제됨)
        """)
    
    with manual_tabs[2]:
        st.markdown("""
        ## ⚙️ 고급 기능
        
        ### 관리자 기능
        관리자 계정으로 로그인 시 추가 기능이 제공됩니다:
        - **팀별 조회**: 다른 팀의 링크 현황 조회
        - **사용자별 조회**: 특정 사용자의 링크 관리
        - **기본 탭 관리**: 신규 사용자를 위한 기본 탭 설정
        
        ### 데이터 백업
        - 모든 링크 데이터는 자동으로 저장됩니다
        - 팀별, 사용자별로 개별 파일로 관리됩니다
        
        ### 반응형 디자인
        - 데스크톱, 태블릿, 모바일에서 모두 사용 가능
        - 화면 크기에 따라 레이아웃이 자동 조정됩니다
        """)
    
    with manual_tabs[3]:
        st.markdown("""
        ## ❓ 자주 묻는 질문
        
        ### Q: 링크가 저장되지 않아요
        **A**: 브라우저 새로고침 후에도 문제가 지속되면 관리자에게 문의하세요.
        
        ### Q: 다른 팀의 링크를 볼 수 있나요?
        **A**: 관리자 권한이 있는 경우에만 다른 팀의 링크를 조회할 수 있습니다.
        
        ### Q: 즐겨찾기는 어떻게 설정하나요?
        **A**: 각 링크 옆의 ⭐ 버튼을 클릭하면 즐겨찾기로 설정/해제됩니다.
        
        ### Q: 탭 순서를 변경할 수 있나요?
        **A**: 현재 버전에서는 탭 순서 변경 기능을 지원하지 않습니다.
        
        ### Q: 링크를 대량으로 추가할 수 있나요?
        **A**: 현재는 개별 추가만 지원합니다. 대량 추가가 필요한 경우 관리자에게 문의하세요.
        
        ### 📞 문의사항
        기술적 문제나 개선 사항이 있으시면 기술운영팀으로 연락주세요.
        """)

elif st.session_state.current_page == "설비 상태진단":
    # ---- 설비 상태진단 페이지 ----
    st.markdown("""
        <div class="main-header">
            <h1>🔧 설비 상태진단</h1>
            <p>설비 운영 현황 및 상태 모니터링</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 임시 대시보드 (실제 데이터 연동 전)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="dashboard-card">
                <div class="card-title">정상 설비</div>
                <div class="card-value" style="color: #22c55e;">85</div>
                <div class="card-description">전체 설비 중 정상 가동</div>
                <span class="status-badge status-online">정상</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="dashboard-card">
                <div class="card-title">점검 필요</div>
                <div class="card-value" style="color: #f59e0b;">12</div>
                <div class="card-description">정기점검 또는 주의 필요</div>
                <span class="status-badge status-maintenance">점검</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="dashboard-card">
                <div class="card-title">이상 설비</div>
                <div class="card-value" style="color: #ef4444;">3</div>
                <div class="card-description">즉시 조치 필요</div>
                <span class="status-badge status-offline">이상</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 설비 상태 목록 (샘플 데이터)
    st.markdown("### 📋 설비 상태 현황")
    
    equipment_data = [
        {"설비명": "펌프 #001", "상태": "정상", "온도": "45°C", "압력": "2.3 bar", "최종점검": "2024-06-15"},
        {"설비명": "밸브 #023", "상태": "점검", "온도": "52°C", "압력": "2.1 bar", "최종점검": "2024-06-10"},
        {"설비명": "센서 #045", "상태": "이상", "온도": "78°C", "압력": "1.8 bar", "최종점검": "2024-06-12"},
        {"설비명": "펌프 #002", "상태": "정상", "온도": "43°C", "압력": "2.4 bar", "최종점검": "2024-06-16"},
        {"설비명": "압축기 #001", "상태": "점검", "온도": "65°C", "압력": "3.2 bar", "최종점검": "2024-06-08"},
    ]
    
    for equipment in equipment_data:
        status_class = "status-online" if equipment["상태"] == "정상" else "status-maintenance" if equipment["상태"] == "점검" else "status-offline"
        
        st.markdown(f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="card-title" style="margin-bottom: 0.5rem;">{equipment["설비명"]}</div>
                        <div style="font-size: 0.9rem; color: #6b7280;">
                            온도: {equipment["온도"]} | 압력: {equipment["압력"]} | 점검일: {equipment["최종점검"]}
                        </div>
                    </div>
                    <span class="status-badge {status_class}">{equipment["상태"]}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("🔧 이 기능은 현재 개발 중입니다.")
 

elif st.session_state.current_page == "팀별 기본 탭 관리" and is_admin:
    # ---- 관리자 전용: 팀별 기본 탭 관리 ----
    st.markdown("""
        <div class="main-header">
            <h1>⚙️ 팀별 기본 탭 관리</h1>
            <p>신규 사용자를 위한 기본 탭 및 링크 설정</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 팀 선택
    selected_team_for_default = st.selectbox("기본 탭을 설정할 팀 선택", teams, key="default_team_select")
    
    # 기본 탭 데이터 로드
    default_tabs_key = f"default_tabs_{selected_team_for_default}"
    if default_tabs_key not in st.session_state:
        st.session_state[default_tabs_key] = load_default_tabs(selected_team_for_default)
    
    default_tabs_data = st.session_state[default_tabs_key]
    
    # 기본 탭 관리
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 기본 탭 편집")
        
        if default_tabs_data:
            # 기존 탭들 표시
            for tab_name in list(default_tabs_data.keys()):
                with st.expander(f"📁 {tab_name}", expanded=False):
                    # 탭 이름 변경
                    new_tab_name = st.text_input("탭 이름", value=tab_name, key=f"default_tab_name_{tab_name}")
                    
                    # 링크 목록
                    st.markdown("**링크 목록:**")
                    links = default_tabs_data[tab_name]["links"]
                    
                    for i, link in enumerate(links):
                        col_link1, col_link2, col_link3 = st.columns([3, 3, 1])
                        with col_link1:
                            new_desc = st.text_input("제목", value=link["description"], key=f"default_link_desc_{tab_name}_{i}")
                        with col_link2:
                            new_url = st.text_input("URL", value=link["url"], key=f"default_link_url_{tab_name}_{i}")
                        with col_link3:
                            if st.button("🗑️", key=f"default_delete_link_{tab_name}_{i}"):
                                default_tabs_data[tab_name]["links"].pop(i)
                                save_default_tabs(selected_team_for_default, default_tabs_data)
                                st.rerun()
                        
                        # 링크 업데이트
                        if new_desc != link["description"] or new_url != link["url"]:
                            default_tabs_data[tab_name]["links"][i] = {
                                "description": new_desc,
                                "url": new_url,
                                "favorite": link.get("favorite", False)
                            }
                    
                    # 새 링크 추가
                    st.markdown("**새 링크 추가:**")
                    col_new1, col_new2, col_new3 = st.columns([3, 3, 1])
                    with col_new1:
                        new_link_desc = st.text_input("새 링크 제목", key=f"new_default_link_desc_{tab_name}")
                    with col_new2:
                        new_link_url = st.text_input("새 링크 URL", key=f"new_default_link_url_{tab_name}")
                    with col_new3:
                        if st.button("➕", key=f"add_default_link_{tab_name}"):
                            if new_link_desc and new_link_url:
                                default_tabs_data[tab_name]["links"].append({
                                    "description": new_link_desc,
                                    "url": new_link_url,
                                    "favorite": False
                                })
                                save_default_tabs(selected_team_for_default, default_tabs_data)
                                st.rerun()
                    
                    # 탭 삭제
                    if st.button(f"탭 '{tab_name}' 삭제", key=f"delete_default_tab_{tab_name}"):
                        del default_tabs_data[tab_name]
                        save_default_tabs(selected_team_for_default, default_tabs_data)
                        st.rerun()
                    
                    # 탭 이름 변경 적용
                    if new_tab_name != tab_name and new_tab_name:
                        default_tabs_data[new_tab_name] = default_tabs_data.pop(tab_name)
                        default_tabs_data[new_tab_name]["description"] = new_tab_name
                        save_default_tabs(selected_team_for_default, default_tabs_data)
                        st.rerun()
        
        # 새 탭 추가
        st.markdown("### ➕ 새 기본 탭 추가")
        new_default_tab_name = st.text_input("새 탭 이름", key="new_default_tab_name")
        if st.button("기본 탭 추가"):
            if new_default_tab_name and new_default_tab_name not in default_tabs_data:
                default_tabs_data[new_default_tab_name] = {
                    "description": new_default_tab_name,
                    "links": []
                }
                save_default_tabs(selected_team_for_default, default_tabs_data)
                st.success(f"'{new_default_tab_name}' 기본 탭이 추가되었습니다.")
                st.rerun()

        with col2:
            st.markdown("### 💾 저장 및 적용")
            
            if st.button("변경사항 저장", use_container_width=True):
                save_default_tabs(selected_team_for_default, default_tabs_data)
                st.success("기본 탭 설정이 저장되었습니다.")
            
            st.markdown("### 📊 현재 설정 요약")
            total_default_tabs = len(default_tabs_data)
            total_default_links = sum(len(tab["links"]) for tab in default_tabs_data.values())
            
            st.markdown(f"""
                <div class="settings-card">
                    <h4>📁 {selected_team_for_default}</h4>
                    <p>기본 탭: {total_default_tabs}개</p>
                    <p>기본 링크: {total_default_links}개</p>
                </div>
            """, unsafe_allow_html=True)
        
        
        st.markdown("### ℹ️ 안내사항")
        st.info("""
        - 여기서 설정한 기본 탭은 해당 팀의 신규 사용자가 처음 로그인할 때 자동으로 생성됩니다.
        - 기존 사용자에게는 영향을 주지 않습니다.
        - 변경 후 반드시 '변경사항 저장'을 클릭해주세요.
        """)

elif st.session_state.current_page == "데이터 백업 관리" and is_admin:
    # ---- 관리자 전용: 데이터 백업 관리 ----
    st.markdown("""
        <div class="main-header">
            <h1>💾 데이터 백업 관리</h1>
            <p>시스템 데이터 백업 및 복원</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 데이터 백업")
        st.info("모든 사용자 데이터와 기본 탭 설정을 ZIP 파일로 백업합니다.")
        
        if st.button("전체 데이터 백업 생성", use_container_width=True):
            try:
                backup_zip = create_backup_zip()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"e1_link_backup_{timestamp}.zip"
                
                st.download_button(
                    label="💾 백업 파일 다운로드",
                    data=backup_zip,
                    file_name=filename,
                    mime="application/zip",
                    use_container_width=True
                )
                st.success("백업 파일이 생성되었습니다!")
            except Exception as e:
                st.error(f"백업 생성 중 오류 발생: {str(e)}")
    
    with col2:
        st.markdown("### 📂 데이터 복원")
        st.warning("⚠️ 복원 시 기존 데이터가 덮어씌워질 수 있습니다.")
        
        uploaded_file = st.file_uploader(
            "백업 파일 선택",
            type=['zip'],
            help="이전에 생성한 백업 ZIP 파일을 선택하세요."
        )
        
        if uploaded_file is not None:
            if st.button("데이터 복원 실행", use_container_width=True):
                success, restored_count, backup_date = restore_from_backup(uploaded_file)
                
                if success:
                    st.success(f"복원 완료! {restored_count}개 파일이 복원되었습니다.")
                    st.info(f"백업 날짜: {backup_date}")
                    st.rerun()
                else:
                    st.error(f"복원 실패: {backup_date}")
    
    # 현재 데이터 현황
    st.markdown("---")
    st.markdown("### 📊 현재 데이터 현황")
    
    # 파일 통계
    sites_files = len([f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]) if os.path.exists(SAVE_DIR) else 0
    default_files = len([f for f in os.listdir(DEFAULT_TABS_DIR) if f.endswith('.json')]) if os.path.exists(DEFAULT_TABS_DIR) else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("사용자 데이터 파일", sites_files)
    with col2:
        st.metric("기본 탭 설정 파일", default_files)
    with col3:
        st.metric("총 파일 수", sites_files + default_files)

# 페이지 최하단에 추가:
if st.session_state.current_page != "AI 도우미":
    st.markdown("""
        <div class="floating-chat-btn" onclick="document.querySelector('input[value=\\"🤖 AI 도우미\\"]').click();">
            🤖
        </div>
    """, unsafe_allow_html=True)

# ---- 하단 고정 포털 링크 ----
st.markdown("""
    <div class="bottom-links">
        <a href="http://aih.e1.co.kr/#/" target="_blank">AIH 바로가기</a>
        <a href="https://she.e1.co.kr/index" target="_blank">SHE포탈</a>
        <a href="https://wels.lsworkplace.com/Website/Portal/Main.aspx" target="_blank">Wels(그룹웨어)</a>
        <a href="https://motor.guardione.ai/dashboard" target="_blank">예지보전</a>
    </div>
""", unsafe_allow_html=True)
