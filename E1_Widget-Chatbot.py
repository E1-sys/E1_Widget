import streamlit as st
import copy
import os
import json
import zipfile
import io
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import google.generativeai as genai
from streamlit_chat import message
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import ssl
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

render_floating_chatbot()

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

# ---- 전역 CSS 스타일 (기존 스타일에 추가) ----
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
            height: 40px;
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

        .floating-chatbot-container {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
        }
        
        /* 플로팅 챗봇 아이콘 */
        .floating-chatbot-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(217, 119, 6, 0.4);
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
        }
        
        .floating-chatbot-icon:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 25px rgba(217, 119, 6, 0.6);
            animation: none;
        }
        
        /* 펄스 애니메이션 */
        @keyframes pulse {
            0% {
                box-shadow: 0 4px 20px rgba(217, 119, 6, 0.4);
            }
            50% {
                box-shadow: 0 4px 30px rgba(217, 119, 6, 0.7);
            }
            100% {
                box-shadow: 0 4px 20px rgba(217, 119, 6, 0.4);
            }
        }
        
        /* 채팅 메시지 컨테이너 */
        .chatbot-messages-container {
            max-height: 300px;
            overflow-y: auto;
            padding: 0.5rem 0;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #f8fafc;
            margin-bottom: 1rem;
        }
        
        /* 채팅 메시지 스타일 */
        .chat-message {
            margin: 0.5rem 0;
            display: flex;
            animation: fadeInUp 0.3s ease;
        }
        
        .chat-message.user-message {
            justify-content: flex-end;
        }
        
        .chat-message.assistant-message {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 80%;
            padding: 0.5rem 0.75rem;
            border-radius: 12px;
            word-wrap: break-word;
            white-space: pre-line;
            font-size: 0.9rem;
        }
        
        .user-message .message-content {
            background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .assistant-message .message-content {
            background: white;
            color: #374151;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 4px;
        }
        
        /* 스크롤바 스타일 */
        .chatbot-messages-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chatbot-messages-container::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }
        
        .chatbot-messages-container::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        .chatbot-messages-container::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* 팝오버 내용 스타일링 */
        .stPopover > div {
            width: 350px !important;
            max-width: 90vw !important;
        }
        
        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .floating-chatbot-container {
                bottom: 20px;
                right: 20px;
            }
            
            .floating-chatbot-icon {
                width: 50px;
                height: 50px;
                font-size: 1.3rem;
            }
            
            .stPopover > div {
                width: 300px !important;
                max-width: 85vw !important;
            }
            
            .chatbot-messages-container {
                max-height: 200px;
            }
        }
        
        /* 페이드인 애니메이션 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
""", unsafe_allow_html=True)

# SSL 인증서 검증 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def render_floating_chatbot():
    """플로팅 챗봇 UI 렌더링"""
    
    # 챗봇 세션 상태 초기화
    if 'chatbot_messages' not in st.session_state:
        st.session_state.chatbot_messages = [
            {"role": "assistant", "content": "안녕하세요! E1 Link AI 어시스턴트입니다. 등록하신 링크들을 분석하여 관련 질문에 답변드립니다. 궁금한 것이 있으시면 언제든 질문해주세요!"}
        ]
    
    if 'chatbot_input' not in st.session_state:
        st.session_state.chatbot_input = ""
    
    # 플로팅 챗봇 버튼과 팝오버
    with st.container():
        # 플로팅 챗봇 아이콘 (CSS로 위치 고정)
        st.markdown("""
            <div class="floating-chatbot-container">
                <div class="floating-chatbot-icon" id="chatbot-trigger">
                    아이콘
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 팝오버를 사용한 챗봇 창
        with st.popover("💬 AI 어시스턴트", use_container_width=False):
            render_chatbot_content()

def render_chatbot_content():
    """챗봇 팝오버 내용 렌더링"""
    
    # 현재 사용자 통계 표시 (간단하게)
    current_user_sites = st.session_state.get(f'sites_{st.session_state.get("viewing_user_id", "default")}_{st.session_state.get("team", "default")}', {})
    total_links = sum(len(tab_data.get("links", [])) for tab_data in current_user_sites.values())
    
    st.markdown(f"**등록된 링크**: {total_links}개")
    st.markdown("---")
    
    # 채팅 메시지 표시 영역 (높이 제한)
    with st.container():
        st.markdown('<div class="chatbot-messages-container">', unsafe_allow_html=True)
        
        # 메시지 표시
        for idx, msg in enumerate(st.session_state.chatbot_messages):
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-content">
                            <strong>You:</strong> {msg["content"]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-content">
                            <strong>🤖:</strong> {msg["content"]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 입력 영역
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "메시지 입력...", 
            key="chatbot_input_field",
            placeholder="예: 인천 지역 설비 모아줘",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("전송", key="chatbot_send", use_container_width=True)
    
    # 전송 버튼 클릭 또는 엔터 시 처리
    if send_button and user_input.strip():
        handle_chatbot_message(user_input.strip())
        st.rerun()
    
    # 채팅 내역 삭제 버튼
    if st.button("🗑️ 채팅 내역 삭제", key="chatbot_clear"):
        st.session_state.chatbot_messages = [
            {"role": "assistant", "content": "안녕하세요! E1 Link AI 어시스턴트입니다. 등록하신 링크들을 분석하여 관련 질문에 답변드립니다. 궁금한 것이 있으시면 언제든 질문해주세요!"}
        ]
        st.rerun()
    
    # 사용 가능한 명령어 안내 (축약형)
    with st.expander("💡 질문 예시"):
        st.markdown("""
        **설비 관련:**
        - "AIH 설비 링크 모아줘"
        - "펌프 설비 보여줘"
        - "인천 지역 설비 모아줘"
        
        **링크 관리:**
        - "즐겨찾기 링크 보여줘"
        - "[탭명] 탭 링크 보여줘"
        
        **시스템 도움말:**
        - "링크 추가 방법은?"
        - "즐겨찾기 설정 방법은?"
        """)

def handle_chatbot_message(user_input):
    """챗봇 메시지 처리"""
    # 사용자 메시지 추가
    st.session_state.chatbot_messages.append({
        "role": "user", 
        "content": user_input
    })
    
    # 현재 사용자 정보 수집
    viewing_user_id = st.session_state.get("viewing_user_id", "default")
    current_team = st.session_state.get("team", "default")
    current_user_sites = st.session_state.get(f'sites_{viewing_user_id}_{current_team}', {})
    total_links = sum(len(tab_data.get("links", [])) for tab_data in current_user_sites.values())
    total_aih_links = sum(
        sum(1 for link in tab_data.get("links", []) if "aih.e1.co.kr" in link.get("url", ""))
        for tab_data in current_user_sites.values()
    )
    
    # 컨텍스트 정보 추가
    context = f"""
    현재 페이지: {st.session_state.get('current_page', '홈')}
    사용자 탭 수: {len(current_user_sites)}
    총 링크 수: {total_links}
    AIH 설비 링크 수: {total_aih_links}
    """
    
    # AI 응답 생성 (기존 함수 사용)
    try:
        bot_response = get_chatbot_response(user_input, context)
    except:
        bot_response = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
    
    # 봇 응답 추가
    st.session_state.chatbot_messages.append({
        "role": "assistant", 
        "content": bot_response
    })
    
    # 입력 필드 초기화
    st.session_state.chatbot_input = ""

# 기존 챗봇 함수들을 플로팅 챗봇에 맞게 수정
def get_chatbot_response(message, context=""):
    """챗봇 응답 생성 (플로팅 챗봇용으로 수정)"""
    model = init_chatbot()
    if not model:
        return "챗봇 서비스를 사용할 수 없습니다. 관리자에게 문의해주세요."
    
    try:
        # 현재 사용자 정보 가져오기
        viewing_user_id = st.session_state.get("viewing_user_id", "default")
        current_team = st.session_state.get("team", "default")
        current_user_sites = st.session_state.get(f'sites_{viewing_user_id}_{current_team}', {})
        
        # 설비 정보 요청인지 확인
        equipment_info_request = False
        equipment_name = None
        
        # 설비 정보 요청 패턴 확인
        info_patterns = [
            r'(.+?)\s*제원\s*알려줘',
            r'(.+?)\s*정보\s*알려줘',
            r'(.+?)\s*사양\s*알려줘',
            r'(.+?)\s*규격\s*알려줘',
            r'(.+?)\s*데이터\s*보여줘',
            r'(.+?)\s*에\s*대해\s*알려줘',
        ]
        
        for pattern in info_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                equipment_name = match.group(1).strip()
                equipment_info_request = True
                break
        
        # 웹 스크래핑을 통한 설비 정보 수집
        web_content_info = ""
        if equipment_info_request and equipment_name:
            # 관련 링크 찾기
            found_links = find_equipment_link(equipment_name, current_user_sites)
            
            if found_links:
                # 플로팅 챗봇에서는 스피너 대신 간단한 메시지
                web_content_info += f"\n🔍 {equipment_name} 관련 정보를 검색 중...\n"
                
                for i, link_info in enumerate(found_links[:2]):  # 최대 2개 링크만 확인 (속도 향상)
                    html_content = fetch_web_content(link_info['url'])
                    
                    if not html_content.startswith("⚠️"):  # 오류가 아닌 경우
                        extracted_info = extract_equipment_info(html_content, equipment_name)
                        if extracted_info:
                            web_content_info += f"\n📋 **{link_info['description']}에서 수집한 정보:**\n{extracted_info}\n"
                    else:
                        web_content_info += f"\n⚠️ {link_info['description']}: 정보 수집 실패\n"
                    
                    time.sleep(0.5)  # 서버 부하 방지 (단축)
            else:
                web_content_info = f"\n⚠️ '{equipment_name}'과 관련된 링크를 찾을 수 없습니다."
        
        # 링크 데이터를 텍스트 형태로 변환
        links_info = []
        for tab_name, tab_data in current_user_sites.items():
            links_info.append(f"탭명: {tab_name}")
            for i, link in enumerate(tab_data.get("links", [])):
                description = link.get("description", "")
                url = link.get("url", "")
                is_favorite = "⭐" if link.get("favorite", False) else ""
                
                # AIH 설비 링크인지 판단
                is_aih = "http://aih.e1.co.kr" in url
                base_location = ""
                if is_aih:
                    if "DS%7C" in url:
                        base_location = "대산"
                    elif "IC%7C" in url:
                        base_location = "인천"
                    elif "YS%7C" in url:
                        base_location = "여수"
                
                links_info.append(f"  - {description} ({url}) {is_favorite} {'[AIH설비-' + base_location + ']' if is_aih else ''}")
        
        links_text = "\n".join(links_info) if links_info else "등록된 링크가 없습니다."
        
        # 시스템 프롬프트 설정 (플로팅 챗봇용 - 더 간결하게)
        system_prompt = f"""
        당신은 E1 Link 시스템의 AI 어시스턴트입니다. 간결하고 친근한 답변을 제공하세요.
        
        현재 사용자 정보:
        - 팀: {st.session_state.get('team', '알 수 없음')}
        - 사용자: {st.session_state.get('user_id', '알 수 없음')}
        
        사용자가 등록한 링크 정보:
        {links_text}
        
        {web_content_info if web_content_info else ""}
        
        답변 규칙:
        1. 간결하고 핵심적인 답변 제공 (최대 3-4줄)
        2. 설비 정보 요청시 웹에서 수집한 정보 활용
        3. 링크 추천시 사용자의 등록된 링크 중에서 제안
        4. 친근하고 도움이 되는 톤 유지
        5. 이모지 적절히 활용
        """
        
        # 대화 히스토리 구성 (플로팅 챗봇용 - 최근 3개 대화만)
        conversation_history = []
        chat_history = st.session_state.get("floating_chat_history", [])
        
        # 최근 3개 대화만 컨텍스트로 사용 (성능 최적화)
        for chat in chat_history[-6:]:  # 최근 3개 질문-답변 쌍
            if chat["role"] == "user":
                conversation_history.append({"role": "user", "content": chat["content"]})
            else:
                conversation_history.append({"role": "assistant", "content": chat["content"]})
        
        # 현재 메시지 추가
        conversation_history.append({"role": "user", "content": message})
        
        # AI 응답 생성
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history
        
        response = model.chat.completions.create(
            model=CHATBOT_MODEL,
            messages=messages,
            max_tokens=500,  # 플로팅 챗봇은 짧은 답변이 적합
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"챗봇 응답 생성 중 오류: {str(e)}")
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 🤖"

class SSOWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self.setup_session()
    
    def setup_session(self):
        """세션 초기 설정"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def login_with_credentials(self, login_url, username, password, username_field='username', password_field='password'):
        """폼 기반 로그인 시도"""
        try:
            # 로그인 페이지 접근
            response = self.session.get(login_url, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CSRF 토큰 찾기
            csrf_token = None
            csrf_input = soup.find('input', {'name': re.compile(r'csrf|token|_token', re.I)})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # 로그인 폼 데이터 준비
            login_data = {
                username_field: username,
                password_field: password
            }
            
            if csrf_token:
                login_data[csrf_input.get('name')] = csrf_token
            
            # 로그인 시도
            login_response = self.session.post(login_url, data=login_data, verify=False)
            
            # 로그인 성공 여부 확인 (리다이렉션 또는 특정 텍스트 확인)
            if login_response.status_code == 200 and 'login' not in login_response.url.lower():
                return True, "로그인 성공"
            else:
                return False, "로그인 실패"
        
        except Exception as e:
            return False, f"로그인 오류: {str(e)}"
    
    def setup_selenium_driver(self, headless=True):
        """Selenium WebDriver 설정"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Selenium 드라이버 설정 오류: {str(e)}")
            return False
    
    def selenium_login(self, login_url, username, password, username_selector='input[name="username"]', password_selector='input[name="password"]', submit_selector='button[type="submit"]'):
        """Selenium을 사용한 로그인"""
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return False, "Selenium 드라이버 설정 실패"
            
            self.driver.get(login_url)
            
            # 로그인 폼 요소 대기
            wait = WebDriverWait(self.driver, 10)
            
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))
            password_input = self.driver.find_element(By.CSS_SELECTOR, password_selector)
            submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
            
            # 로그인 정보 입력
            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            
            # 로그인 버튼 클릭
            submit_button.click()
            
            # 로그인 완료 대기 (URL 변경 또는 특정 요소 나타남)
            time.sleep(3)
            
            # 세션 쿠키를 requests 세션으로 복사
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            return True, "Selenium 로그인 성공"
        
        except Exception as e:
            return False, f"Selenium 로그인 오류: {str(e)}"
    
    def fetch_authenticated_content(self, url, timeout=10):
        """인증된 세션으로 콘텐츠 가져오기"""
        try:
            response = self.session.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            
            # 로그인 리다이렉션 확인
            if 'login' in response.url.lower() or 'signin' in response.url.lower():
                return None, "인증이 필요합니다"
            
            if response.encoding is None:
                response.encoding = 'utf-8'
            
            return response.text, "성공"
        
        except requests.exceptions.Timeout:
            return None, f"타임아웃: {url}"
        except requests.exceptions.ConnectionError:
            return None, f"연결 오류: {url}"
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP 오류: {e}"
        except Exception as e:
            return None, f"오류: {str(e)}"
    
    def fetch_with_selenium(self, url, wait_for_element=None, timeout=10):
        """Selenium으로 JavaScript 렌더링된 콘텐츠 가져오기"""
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return None, "Selenium 드라이버 설정 실패"
            
            self.driver.get(url)
            
            # 특정 요소 대기 (선택사항)
            if wait_for_element:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            else:
                time.sleep(2)  # 기본 대기
            
            return self.driver.page_source, "성공"
        
        except Exception as e:
            return None, f"Selenium 페이지 로드 오류: {str(e)}"

    # 기존 함수 수정 버전
    def fetch_web_content_sso(url, timeout=10, login_config=None):
        """SSO 대응 웹 콘텐츠 가져오기"""
        scraper = SSOWebScraper()
        
        try:
            # 로그인 필요 시 처리
            if login_config:
                if login_config.get('method') == 'selenium':
                    success, message = scraper.selenium_login(
                        login_config['login_url'],
                        login_config['username'],
                        login_config['password']
                    )
                else:
                    success, message = scraper.login_with_credentials(
                        login_config['login_url'],
                        login_config['username'],
                        login_config['password']
                    )
                
                if not success:
                    return f"⚠️ 로그인 실패: {message}"
            
            # 콘텐츠 가져오기
            content, status = scraper.fetch_authenticated_content(url, timeout)
            
            if not content:
                # Selenium으로 재시도
                content, status = scraper.fetch_with_selenium(url)
            
            return content if content else f"⚠️ {status}"
        
        finally:
            scraper.close()

    def extract_equipment_info_enhanced(self, html_content, equipment_name):
        """향상된 설비 정보 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # JavaScript로 동적 생성된 콘텐츠도 포함
            text_content = soup.get_text()
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # 설비 정보 패턴 (더 다양한 패턴 추가)
            equipment_patterns = [
                rf'{equipment_name}.*?(?=\n|$)',
                r'제원.*?(?=\n|제원|사양|규격)',
                r'사양.*?(?=\n|제원|사양|규격)',
                r'규격.*?(?=\n|제원|사양|규격)',
                r'용량.*?(?=\n|용량|압력|온도)',
                r'압력.*?(?=\n|용량|압력|온도)',
                r'온도.*?(?=\n|용량|압력|온도)',
                r'유량.*?(?=\n|유량|토출|흡입)',
                r'모델.*?(?=\n|모델|제조사|년식)',
                r'제조사.*?(?=\n|모델|제조사|년식)',
            ]
            
            extracted_info = []
            for pattern in equipment_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE | re.MULTILINE)
                extracted_info.extend(matches)
            
            # 테이블 데이터 추출 (더 정교한 방식)
            tables = soup.find_all('table')
            table_data = []
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        row_text = ' | '.join([cell.get_text().strip() for cell in cells])
                        if (equipment_name.lower() in row_text.lower() or 
                            any(keyword in row_text.lower() for keyword in 
                                ['제원', '사양', '규격', '용량', '압력', '온도', '유량', '모델', '제조사'])):
                            table_data.append(row_text)
            
            # JSON 데이터 추출 시도 (AJAX 응답일 경우)
            json_pattern = r'\{[^{}]*"' + equipment_name + r'"[^{}]*\}'
            json_matches = re.findall(json_pattern, html_content, re.IGNORECASE)
            json_data = []
            for match in json_matches:
                try:
                    parsed_json = json.loads(match)
                    json_data.append(str(parsed_json))
                except:
                    continue
            
            # 결과 조합
            result = []
            if extracted_info:
                result.extend(extracted_info[:10])
            if table_data:
                result.extend(table_data[:5])
            if json_data:
                result.extend(json_data[:3])
            
            return '\n'.join(result) if result else None
        
        except Exception as e:
            return f"정보 추출 중 오류: {str(e)}"
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        self.session.close()


GEMINI_API_KEY = st.secrets["chatbot"]["gemini_api_key"]
genai.configure(api_key=GEMINI_API_KEY)
@st.cache_resource
def init_chatbot():
    """챗봇 모델 초기화"""
    try:
        model = genai.GenerativeModel('gemma-3n-e4b-it')
        return model
    except Exception as e:
        st.error(f"챗봇 초기화 실패: {str(e)}")
        return None

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
    nav_options = ["🏠 홈", "🔗 링크 바로가기", "📖 사용자 매뉴얼", "🔧 설비 상태진단"]
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

# ---- 하단 고정 포털 링크 ----
st.markdown("""
    <div class="bottom-links">
        <a href="http://aih.e1.co.kr/#/" target="_blank">AIH 바로가기</a>
        <a href="https://she.e1.co.kr/index" target="_blank">SHE포탈</a>
        <a href="https://wels.lsworkplace.com/Website/Portal/Main.aspx" target="_blank">Wels(그룹웨어)</a>
        <a href="https://motor.guardione.ai/dashboard" target="_blank">예지보전</a>
    </div>
""", unsafe_allow_html=True)
