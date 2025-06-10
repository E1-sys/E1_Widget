#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import copy
import os
import json

# ---- 전역 스타일 설정 ----
st.markdown("""
    <style>
        * {
            font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
        }
        .bottom-links {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 10px 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .bottom-links a {
            margin: 0 10px;
            white-space: nowrap;
        }
    </style>
""", unsafe_allow_html=True)

# ---- 사용자 ID 입력 ----
user_id = st.text_input("사번 또는 사용자 ID를 입력하세요", value="", placeholder="예: honggildong")
if not user_id:
    st.warning("사번 또는 사용자 ID를 입력해주세요.")
    st.stop()

# ---- 기본 사이트 데이터 ----
sites_original = {
    "안전시공팀": {
        "description": "안전시공팀",
        "links": [
            {"description": "KSG code", "url": "https://cyber.kgs.or.kr/kgscode.Index.do", "favorite": False},
            {"description": "국가법령정보센터", "url": "https://www.law.go.kr/LSW/main.html", "favorite": False}
        ]
    },
    "기술운영": {
        "description": "기술운영",
        "links": [
            {"description": "항만물류정보시스템(PORT-MIS)", "url": "https://new.portmis.go.kr/portmis/websquare/websquare.jsp?w2xPath=/portmis/w2/main/intro.xml", "favorite": False}
        ]
    },
    "기술지원": {
        "description": "기술지원",
        "links": []
    },
    "SHE 지원팀": {
        "description": "SHE지원팀",
        "links": [
            {"description": "가스안전공사", "url": "https://www.kgs.or.kr/", "favorite": False},
            {"description": "안전보건공단", "url": "https://www.kosha.or.kr/kosha/index.do", "favorite": False}
        ]
    }
}

SAVE_DIR = "sites_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---- 데이터 로딩 및 저장 ----
def save_sites(user_id):
    file_path = os.path.join(SAVE_DIR, f"{user_id}_sites.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(st.session_state[f"sites_{user_id}"], f, ensure_ascii=False, indent=2)

def load_sites(user_id):
    file_path = os.path.join(SAVE_DIR, f"{user_id}_sites.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for tab in data:
                for link in data[tab]["links"]:
                    if "favorite" not in link:
                        link["favorite"] = False
            return data
    else:
        return copy.deepcopy(sites_original)

LINKS_PER_PAGE = 8

# ---- 세션 상태 초기화 ----
if f"sites_{user_id}" not in st.session_state:
    st.session_state[f"sites_{user_id}"] = load_sites(user_id)
    st.session_state[f"pages_{user_id}"] = {tab: 0 for tab in st.session_state[f"sites_{user_id}"]}

current_sites = st.session_state[f"sites_{user_id}"]
current_pages = st.session_state[f"pages_{user_id}"]

# ---- 링크 관리 함수 ----
def delete_link(tab_name, index):
    del current_sites[tab_name]["links"][index]
    save_sites(user_id)

def add_link(tab_name, title, url):
    current_sites[tab_name]["links"].append({"description": title, "url": url, "favorite": False})
    save_sites(user_id)

def toggle_favorite(tab_name, index):
    current_sites[tab_name]["links"][index]["favorite"] = not current_sites[tab_name]["links"][index].get("favorite", False)
    save_sites(user_id)

def add_tab(tab_name):
    if tab_name and tab_name not in current_sites:
        current_sites[tab_name] = {"description": tab_name, "links": []}
        current_pages[tab_name] = 0
        save_sites(user_id)

# ---- 링크 표시 ----
def display_links(tab_name):
    links = current_sites[tab_name]["links"]
    page = current_pages[tab_name]

    show_only_fav = st.checkbox("즐겨찾기만 보기", key=f"fav_filter_{user_id}_{tab_name}")
    filtered_links = [link for link in links if link.get("favorite", False)] if show_only_fav else links

    total_pages = (len(filtered_links) + LINKS_PER_PAGE - 1) // LINKS_PER_PAGE
    start, end = page * LINKS_PER_PAGE, page * LINKS_PER_PAGE + LINKS_PER_PAGE
    paged_links = filtered_links[start:end]

    for i, link in enumerate(paged_links):
        idx = links.index(link) if show_only_fav else start + i

        col0, col1, col2 = st.columns([1, 8, 1])
        fav_icon = "★" if link.get("favorite", False) else "☆"
        if col0.button(fav_icon, key=f"fav_{user_id}_{tab_name}_{idx}"):
            toggle_favorite(tab_name, idx)
            st.rerun()

        col1.markdown(
            f'''<div style="display: flex; align-items: center; height: 80%;">
            <a href="{link['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            {link['description']}</a></div>''', unsafe_allow_html=True)

        if col2.button("X", key=f"del_{user_id}_{tab_name}_{idx}"):
            delete_link(tab_name, idx)
            st.rerun()

    # 페이지 네비게이션 버튼 (오른쪽 정렬, 줄 바꿈 안되도록 조정)
    nav_col1, nav_col2 = st.columns([10, 2])
    with nav_col1:
        if page > 0 and st.button("← 이전", key=f"prev_{user_id}_{tab_name}"):
            current_pages[tab_name] -= 1
            st.rerun()
    with nav_col2:
        if end < len(filtered_links):
            if st.button("다음 →", key=f"next_{user_id}_{tab_name}"):
                current_pages[tab_name] += 1
                st.rerun()

    with st.expander("➕ 링크 추가"):
        with st.form(f"form_{user_id}_{tab_name}"):
            title = st.text_input("제목", key=f"title_{user_id}_{tab_name}")
            url = st.text_input("URL", key=f"url_{user_id}_{tab_name}")
            submit = st.form_submit_button("추가")
            if submit and title and url:
                add_link(tab_name, title, url)
                st.rerun()

# ---- 사이드바 ----
with st.sidebar:
    st.header("검색")
    
    search_col1, search_col2 = st.columns([5, 1])
    
    with search_col1:
        search_query = st.text_input("검색어를 입력하세요", key=f"search_input_{user_id}", label_visibility="collapsed")

    with search_col2:
        if st.button("❌", key=f"clear_search_btn_{user_id}", help="검색어 지우기"):
            search_query = ""
            st.session_state[f"do_search_{user_id}"] = False
            st.rerun()

    if st.button("🔍 검색", key=f"search_btn_{user_id}"):
        st.session_state[f"do_search_{user_id}"] = True
    
    # 탭 추가
    new_tab_name = st.text_input("새 탭 이름", key=f"new_tab_{user_id}")
    if st.button("탭 추가", key=f"add_tab_btn_{user_id}"):
        if not new_tab_name.strip():
            st.warning("탭 이름을 입력하세요.")
        elif new_tab_name in current_sites:
            st.warning("이미 존재하는 탭 이름입니다.")
        else:
            add_tab(new_tab_name.strip())
            st.success(f"'{new_tab_name.strip()}' 탭이 추가되었습니다.")
            st.rerun()

    # 탭 삭제
    delete_tab_name = st.selectbox("삭제할 탭 선택", options=list(current_sites.keys()), key=f"delete_tab_{user_id}")
    if st.button("탭 삭제", key=f"delete_tab_btn_{user_id}"):
        if delete_tab_name in current_sites:
            del current_sites[delete_tab_name]
            del current_pages[delete_tab_name]
            save_sites(user_id)
            st.success(f"'{delete_tab_name}' 탭이 삭제되었습니다.")
            st.rerun()

# ---- 제목 ----
st.markdown("""<h1 style='color: #FF6F00;'>E1 Link</h1>""", unsafe_allow_html=True)

# ---- 검색 기능 ----
if search_query and search_query.strip():
    search_lower = search_query.lower()
    results = [(tab, link) for tab, data in current_sites.items() for link in data["links"] if search_lower in link["description"].lower()]
    st.subheader(f"검색 결과 ({len(results)}개) — '{search_query}'")
    if results:
        for tab_name, link in results:
            st.markdown(f'<a href="{link["url"]}" target="_blank">[{tab_name}] {link["description"]}</a>', unsafe_allow_html=True)
    else:
        st.write("검색 결과가 없습니다.")
else:
    tab_titles = list(current_sites.keys())
    tabs = st.tabs(tab_titles)
    for i, tab in enumerate(tabs):
        with tab:
            st.header(tab_titles[i])
            display_links(tab_titles[i])

# ---- 포털 링크 하단 고정 ----
st.markdown("""
    <div class="bottom-links">
        <div style="display: flex; flex-direction: row; justify-content: center; gap: 20px;">
            <a href="https://bi.e1.co.kr/#/signin?isDefaultIdentityPoolLogin=true&redirect=%2Fsite%2FE1%2Fviews%2FBI-IX_S1_5__new%2FECOverallDashboard%3F%253Aiid%3D1" target="_blank">BI Portal</a>
            <a href="https://she.e1.co.kr/index" target="_blank">SHE Portal</a>
            <a href="https://ariba.portal.url" target="_blank">Ariba</a>
            <a href="https://www.e1.co.kr/ko/main" target="_blank">E1 홈페이지</a>
        </div>
    </div>
""", unsafe_allow_html=True)

