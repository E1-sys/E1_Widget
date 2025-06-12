import streamlit as st
import copy
import os
import json
import zipfile
import io

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

# ---- 관리자 ID 목록 정의 ----
ADMIN_IDS = ["admin"]

SAVE_DIR = "sites_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---- 팀 목록 ----
teams = ["기술운영팀", "기술지원팀", "SHE지원팀", "안전시공팀", "여수기지", "대산기지", "인천기지"]

# ---- 세션 초기화 또는 홈으로 돌아가기 버튼 ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if st.sidebar.button("🏠 홈으로 돌아가기"):
    st.session_state.authenticated = False
    st.session_state.pop("user_id", None)
    st.session_state.pop("team", None)
    st.rerun()

# ---- 로그인 화면 ----
if not st.session_state.authenticated:
    with st.form("login_form", clear_on_submit=False):
        team = st.selectbox("팀을 선택하세요", teams, key="team_selectbox")
        user_id = st.text_input("사번 또는 사용자 ID를 입력하세요", value="", placeholder="예: honggildong", key="user_input")
        submitted = st.form_submit_button("접속")
        if submitted:
            if not user_id.strip():
                st.warning("사번 또는 사용자 ID를 입력해주세요.")
                st.stop()
            st.session_state.authenticated = True
            st.session_state.team = team
            st.session_state.user_id = user_id.strip()
            st.rerun()
    st.stop()

# ---- 로그인 이후 변수 할당 ----
user_id = st.session_state.user_id
is_admin = user_id in ADMIN_IDS

# admin이거나 일반 사용자일 때 team 선택 다르게 처리
if is_admin:
    team = st.selectbox("조회할 팀 선택", teams, index=teams.index(st.session_state.team), key="admin_team_selectbox")
    all_files = os.listdir(SAVE_DIR)
    all_user_ids = sorted(set(
        f.split("_")[0] for f in all_files if f.endswith(f"_{team}_sites.json")
    ))
    selected_user = st.selectbox("조회할 사용자 선택", all_user_ids, key="admin_user_select")
    viewing_user_id = selected_user
else:
    team = st.session_state.team
    viewing_user_id = user_id


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

# ---- 데이터 로딩 및 저장 ----
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
        return copy.deepcopy(default_sites[team])

LINKS_PER_PAGE = 8

# ---- 세션 상태 초기화 ----
site_key = f"sites_{viewing_user_id}_{team}"
page_key = f"pages_{viewing_user_id}_{team}"

if site_key not in st.session_state:
    st.session_state[site_key] = load_sites(viewing_user_id, team)
    st.session_state[page_key] = {tab: 0 for tab in st.session_state[site_key]}

current_sites = st.session_state[site_key]
current_pages = st.session_state[page_key]

# ---- 링크 관리 함수 ----
def delete_link(tab_name, index):
    del current_sites[tab_name]["links"][index]
    save_sites(viewing_user_id, team)

def add_link(tab_name, title, url):
    current_sites[tab_name]["links"].append({"description": title, "url": url, "favorite": False})
    save_sites(viewing_user_id, team)

def toggle_favorite(tab_name, index):
    current_sites[tab_name]["links"][index]["favorite"] = not current_sites[tab_name]["links"][index].get("favorite", False)
    save_sites(viewing_user_id, team)

def add_tab(tab_name):
    if tab_name and tab_name not in current_sites:
        current_sites[tab_name] = {"description": tab_name, "links": []}
        current_pages[tab_name] = 0
        save_sites(viewing_user_id, team)

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

    if tab_name not in default_sites[team]:
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
    search_query = st.text_input("검색어를 입력하세요", key=f"search_input_{viewing_user_id}")
    if st.button("🔍 검색", key=f"search_btn_{viewing_user_id}"):
        st.session_state[f"do_search_{viewing_user_id}"] = True

    st.markdown("---")
    st.header("탭 관리")
    new_tab_name = st.text_input("새 탭 이름", key=f"new_tab_{viewing_user_id}")
    if st.button("탭 추가", key=f"add_tab_btn_{viewing_user_id}"):
        if not new_tab_name.strip():
            st.warning("탭 이름을 입력하세요.")
        elif new_tab_name in current_sites:
            st.warning("이미 존재하는 탭 이름입니다.")
        else:
            add_tab(new_tab_name.strip())
            st.success(f"'{new_tab_name.strip()}' 탭이 추가되었습니다.")
            st.rerun()

    delete_tab_name = st.selectbox("삭제할 탭 선택", options=[tab for tab in current_sites.keys() if tab not in default_sites[team]], key=f"delete_tab_{viewing_user_id}")
    if st.button("탭 삭제", key=f"delete_tab_btn_{viewing_user_id}"):
        if delete_tab_name in current_sites:
            del current_sites[delete_tab_name]
            del current_pages[delete_tab_name]
            save_sites(viewing_user_id, team)
            st.success(f"'{delete_tab_name}' 탭이 삭제되었습니다.")
            st.rerun()

    if is_admin:
        st.markdown("---")
        st.subheader("사용자 데이터 삭제")
        del_user = st.selectbox("삭제할 사용자", all_user_ids, key="admin_del_user")
        if st.button("❌ 사용자 데이터 삭제"):
            deleted_any = False
            for t in teams:
                file_path = os.path.join(SAVE_DIR, f"{del_user}_{t}_sites.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_any = True
            if deleted_any:
                st.success(f"{del_user}의 모든 팀 데이터가 삭제되었습니다.")
                st.rerun()
            else:
                st.warning("해당 사용자의 데이터가 없습니다.")

        st.markdown("---")
        st.subheader("📦 전체 사용자 데이터 백업/복원")
        
        # 백업 다운로드
        if st.button("💾 전체 사용자 데이터 백업"):
            backup_buffer = io.BytesIO()
            with zipfile.ZipFile(backup_buffer, 'w') as zipf:
                for filename in os.listdir(SAVE_DIR):
                    if filename.endswith("_sites.json"):
                        filepath = os.path.join(SAVE_DIR, filename)
                        zipf.write(filepath, arcname=filename)
            st.download_button("📥 백업 파일 다운로드", data=backup_buffer.getvalue(),
                               file_name="backup_sites.zip", mime="application/zip")
        
        # 복원 업로드
        uploaded_zip = st.file_uploader("📤 백업 파일 업로드 (zip)", type=["zip"])
        if uploaded_zip is not None:
            with zipfile.ZipFile(uploaded_zip) as zipf:
                for member in zipf.namelist():
                    if member.endswith("_sites.json"):
                        with zipf.open(member) as f:
                            file_data = f.read()
                            save_path = os.path.join(SAVE_DIR, os.path.basename(member))
                            with open(save_path, "wb") as out_file:
                                out_file.write(file_data)
                st.success("📁 사용자 데이터가 성공적으로 복원되었습니다. 페이지를 새로고침 해주세요.")

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

