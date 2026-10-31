# -*- coding: utf-8 -*-
# 데모 영상 녹화: 배포된 URL을 헤드리스 크로미움으로 조작하며 화면만 녹화(얼굴·목소리 없음, 자막 오버레이).
import json, sys, time, os
from playwright.sync_api import sync_playwright
URL = "https://meonjisalgi.vercel.app/"
res = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
o, b = res["ours"], res["baseline"]
CAP_JS = """(t)=>{let c=document.getElementById('cap');if(!c){c=document.createElement('div');c.id='cap';
c.style.cssText='position:fixed;left:0;right:0;bottom:0;z-index:99999;background:rgba(25,31,40,.92);color:#fff;font:600 24px/1.5 -apple-system,"Apple SD Gothic Neo",sans-serif;padding:16px 40px;text-align:center';document.body.appendChild(c)}
c.textContent=t;c.style.display=t?'block':'none'}"""
SLIDE_JS = """(h)=>{let s=document.getElementById('sl');if(!s){s=document.createElement('div');s.id='sl';
s.style.cssText='position:fixed;inset:0;z-index:99998;background:#f4f5f7;color:#191f28;font:500 26px/1.6 -apple-system,"Apple SD Gothic Neo",sans-serif;padding:60px 90px 120px;overflow:hidden';document.body.appendChild(s)}
s.innerHTML=h;s.style.display=h?'block':'none'}"""
def n(d, k): return d.get(k, 0)
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1280, "height": 800}, record_video_dir=os.path.dirname(OUT), record_video_size={"width": 1280, "height": 800}, locale="ko-KR")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="networkidle")
    def cap(t, s): pg.evaluate(CAP_JS, t); time.sleep(s)
    def slide(h, s): pg.evaluate(SLIDE_JS, h); time.sleep(s)
    slide("<h1 style='font-size:46px'>먼저살기</h1><p style='font-size:30px'>보호종료 청년이 받을 돈과 기한을<br><b>공식 안내문 인용으로만</b> 알려 주는 AI</p><p>2026 AI 라이프 솔루션 챌린지 · 테스트 URL meonjisalgi.vercel.app</p><p style='color:#6b7684;font-size:22px'>※ 화면 녹화만 사용했고 얼굴·목소리는 없습니다. 모든 설명은 자막입니다.</p>", 7)
    slide("<h2>문제</h2><ul><li>자립정착금은 지역마다 다릅니다 — 서울 2,000만원, 부산 1,200만원, 대구·인천 1,000만원, 경남 1,500만원 (각 지자체 공식 안내문)</li><li>검색하면 옛 금액(부산 700만원·광주 수당 30만원)과 다른 제도(가정 밖 청소년 지원)가 섞여 나옵니다</li><li>그래서 AI에게 그냥 물으면 틀린 숫자를 그럴듯하게 답합니다</li></ul><h2>먼저살기의 답</h2><p>① 공식 안내문 원문 42건만 읽는다 ② AI가 쉬운 말로 풀어 쓴다 ③ 서버가 모든 문장의 인용·숫자를 원문과 다시 대조한다 ④ 근거가 없거나 문서끼리 다르면 <b>답하지 않는다</b></p>", 16)
    slide("", 0)
    cap("1단계 — 내 상황 넣기: 보호시설이 있던 지역, 보호종료 월, 2년 이상 보호 여부", 4)
    pg.select_option("#region", "경남"); time.sleep(1)
    pg.fill("#endYm", "2025-03"); time.sleep(1.5)
    cap("‘내 월별 할 일 보기’ — AI가 공식 안내문 카드를 읽고 할 일을 씁니다", 3)
    pg.click("#go")
    pg.wait_for_selector(".item", timeout=90000); time.sleep(1)
    pg.evaluate("window.scrollTo({top:300,behavior:'smooth'})")
    cap("자립수당은 지금 ○회차째, 남은 회차를 서버가 계산합니다 (보호종료일이 속한 달부터 최대 60회차)", 7)
    pg.evaluate("document.querySelector('.item details summary').click()")
    cap("항목마다 ‘근거 보기’ — 공식 안내문의 원문 문장, 기관, 기준일, 링크가 붙습니다", 8)
    pg.evaluate("window.scrollTo({top:900,behavior:'smooth'})")
    cap("문서끼리 금액이 다르면 숨기지 않습니다 — 복지부 2024 문서(경남 1,200만원)와 경남 공식 안내(1,500만원)가 다르다고 알립니다", 9)
    pg.evaluate("window.scrollTo({top:0})")
    cap("2단계 — 다른 지역: 충북은 정착금 공식 페이지가 없습니다", 3)
    pg.select_option("#region", "충북"); pg.click("#go"); time.sleep(1)
    pg.wait_for_function("document.querySelectorAll('.item').length>0 || document.querySelector('.hold')", timeout=90000); time.sleep(1)
    pg.evaluate("window.scrollTo({top:250,behavior:'smooth'})")
    cap("공식 근거가 약하면 ‘중앙 문서 2건 일치·지자체 공식 미확인’처럼 등급을 밝히고, 갈리면 답하지 않습니다", 9)
    pg.evaluate("window.scrollTo({top:2000,behavior:'smooth'})"); time.sleep(1)
    cap("3단계 — 직접 물어보기: 사용자가 틀린 숫자로 물어도 인용으로 바로잡습니다", 4)
    def ask(region, q, wait_s, caption):
        pg.evaluate("window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'})")
        pg.select_option("#region", region)
        pg.fill("#qs", ""); pg.type("#qs", q, delay=70)
        cap(caption, 2); pg.click("#ask")
        pg.wait_for_function("document.querySelector('#ans .item, #ans .hold, #ans .err')", timeout=90000)
        time.sleep(wait_s)
    ask("부산", "부산 정착금이 700만원 맞나요?", 6, "질문: 부산 정착금 700만원 맞나요?")
    cap("→ 부산시 공식 안내문(2025-11-27)의 1,200만원으로 바로잡고 근거를 붙입니다", 6)
    ask("서울", "서울 강남구는 정착금을 더 주나요?", 5, "질문: 서울 강남구는 정착금을 더 주나요?")
    cap("→ 구 단위 안내문이 없으면 ‘답하지 않습니다’ — 지어내지 않습니다", 6)
    ask("충북", "충북 진천군에서 주는 100만원이 자립정착금인가요?", 5, "질문: 진천군 100만원이 자립정착금인가요? (다른 제도)")
    cap("→ 다른 제도로 보이는 질문도 근거가 없으면 답하지 않습니다", 6)
    slide(f"<h2>제품 오답률 실측 — 36문항 · 10곳 · 함정 12</h2><p>같은 AI(Upstage Solar)로 <b>안내문 카드 없이</b> 물은 대조군과 비교, 정답 기준은 공식 안내문 원문(실행 전 고정)</p><table style='font-size:28px;border-collapse:collapse;margin-top:10px'><tr><th style='text-align:left;padding:8px 24px'></th><th style='padding:8px 24px'>먼저살기</th><th style='padding:8px 24px'>카드 없는 같은 AI</th></tr><tr><td style='padding:8px 24px'>정답</td><td style='text-align:center'>{n(o,'정답')+n(o,'정답(보류)')}</td><td style='text-align:center'>{n(b,'정답')+n(b,'정답(보류)')}</td></tr><tr><td style='padding:8px 24px'>답하지 않음(보류)</td><td style='text-align:center'>{n(o,'보류(미답)')}</td><td style='text-align:center'>-</td></tr><tr><td style='padding:8px 24px'>오답</td><td style='text-align:center'><b>{n(o,'오답')+n(o,'오답(답함)')}</b></td><td style='text-align:center'><b>{n(b,'오답')+n(b,'오답(답함)')}</b></td></tr><tr><td style='padding:8px 24px'>판정 제외(AI 호출 실패)</td><td style='text-align:center'>{n(o,'제외')}</td><td style='text-align:center'>-</td></tr></table><p style='font-size:22px;color:#6b7684'>한계: 문항은 제작자가 만들었고 실사용자 측정은 아직 없습니다. 상세 표는 성과보고서와 GitHub 저장소 test/eval36-result.json.</p>", 20)
    slide("<h2>한계와 다음 단계</h2><ul><li>지자체 안내문은 바뀝니다 — 카드만 교체하면 되도록 카드 빌드 스크립트가 원문 일치를 검사합니다</li><li>경기·대전·제주 등은 지자체 현행 공식 페이지를 못 찾아 중앙 문서 기준(2차)으로 표시합니다</li><li>시·군·구 단위와 다른 제도는 답하지 않습니다</li><li>보호종료 청년 실사용자 측정은 아직 없습니다</li></ul><p>테스트 URL <b>meonjisalgi.vercel.app</b> · 로그인 없이 입력칸에 직접 넣어 볼 수 있습니다</p>", 14)
    ctx.close(); br.close()
print("recorded")
