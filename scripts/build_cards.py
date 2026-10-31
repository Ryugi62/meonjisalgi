"""공식 안내문 원문(scripts/src/*.txt, 2026-10-31 열람)에서 인용 카드를 만든다.
모든 quote는 원문 텍스트에 글자 그대로 들어 있어야 한다(아니면 빌드 실패)."""
import json, re, sys, os
H = os.path.dirname(os.path.abspath(__file__))
def norm(s): return re.sub(r'\s+', ' ', s).strip()
SRC = {}
def load(n):
    if n not in SRC: SRC[n] = norm(open(f"{H}/src/{n}.txt", encoding="utf-8").read())
    return SRC[n]
# (id, 지역, 등급, 기관/문서, URL, 기준일, 파일, 인용(원문 그대로), field, value_manwon)
# 등급 1 = 지자체 공식 페이지, 2 = 중앙부처 문서, 3 = 국회 보고서
C = [
 ("seoul-hub", "서울", 1, "서울시 보도자료(서울 미디어허브)", "https://mediahub.seoul.go.kr/archives/2010251", "2024-02-08", "seoulhub",
  "‘자립수당’은 40만원에서 50만원, ‘자립정착금’은 1,500만원에서 2,000만원으로 각각 인상", "settle", 2000),
 ("seoul-allow", "서울", 1, "서울시 자립수당 신청 안내", "https://news.seoul.go.kr/welfare/archives/511982", "2026-04-20", "seoul",
  "매월 20일마다 50만원씩 신청 청년 본인 명의 계좌 지급", "allow", 50),
 ("seoul-period", "서울", 1, "서울시 자립수당 신청 안내", "https://news.seoul.go.kr/welfare/archives/511982", "2026-04-20", "seoul",
  "보호종료일이 속한 달부터 최대 60회차 까지 가능", "period", None),
 ("seoul-target", "서울", 1, "서울시 자립수당 신청 안내", "https://news.seoul.go.kr/welfare/archives/511982", "2026-04-20", "seoul",
  "만 18세 이후 만기 및 보호연장종료 또는 재보호 종료된 자로서, 보호종료 5년이내인 자립준비청년", "target", None),
 ("seoul-how", "서울", 1, "서울시 자립수당 신청 안내", "https://news.seoul.go.kr/welfare/archives/511982", "2026-04-20", "seoul",
  "'복지로' 홈페이지 온라인 신청 또는 관할 주소지 동주민센터 방문 신청", "how", None),
 ("busan-settle", "부산", 1, "부산시 자립정착금 지원", "https://www.busan.go.kr/depart/settlementgrant", "2025-11-27", "busan",
  "자립정착금 1인당 1,200만원(2회 분할 지급)", "settle", 1200),
 ("busan-when", "부산", 1, "부산시 자립정착금 지원", "https://www.busan.go.kr/depart/settlementgrant", "2025-11-27", "busan",
  "신청기간 : 자립정착금 수령 1개월 이전", "settle_when", None),
 ("busan-edu", "부산", 1, "부산시 자립정착금 지원", "https://www.busan.go.kr/depart/settlementgrant", "2025-11-27", "busan",
  "자립준비청년 금융교육(자립지원전담기관 실시) 의무 이수", "rule", None),
 ("busan-plan", "부산", 1, "부산시 자립정착금 지원", "https://www.busan.go.kr/depart/settlementgrant", "2025-11-27", "busan",
  "‘자립정착금 사용계획서’ 구‧군 제출", "how", None),
 ("daegu-allow", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "매월 50만원 현금지급(본인명의 계좌 이체 원칙)", "allow", 50),
 ("daegu-settle", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "보호종료 시 1인당 1천만원 지급", "settle", 1000),
 ("daegu-return", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "지원불가 : ①보호 조기종료 후 원가정으로 복귀한 경우", "rule", None),
 ("daegu-2yr", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "보호종료일을 기준으로 과거 2년 이상 연속하여 보호를 받은 자", "rule", None),
 ("daegu-pre", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "보호종료 30일 전부터 구군 아동보호팀으로 사전신청 가능(보호종료 이후 지급)", "allow_when", None),
 ("daegu-5yr", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "만18세 이후 만기 또는 연장 보호종료된 자로서 보호종료 5년 이내인 자", "target", None),
 ("daegu-early", "대구", 1, "대구시 자립준비청년 지원", "https://www.daegu.go.kr/woman/index.do?menu_id=00939670", "2026-03-23", "daegu",
  "만 15세 이후 보호조치가 조기 종료된 자로서 만18세가 된 때로부터 5년 이내인 자(단, 아동복지법 시행(‛24.2.9.)이후 만18세가 된 자부터 적용)", "target", None),
 ("incheon-allow", "인천", 1, "인천시 자립수당", "https://www.incheon.go.kr/welfare/WE020441", "2026-10-24", "inc41",
  "매월 50만원 현금 지급(본인 명의 계좌 이체) 원칙", "allow", 50),
 ("incheon-2yr", "인천", 1, "인천시 자립수당", "https://www.incheon.go.kr/welfare/WE020441", "2026-10-24", "inc41",
  "보호종료일을 기준으로 과거 2년 이상 연속하여 보호를 받은 아동", "rule", None),
 ("incheon-5yr", "인천", 1, "인천시 자립수당", "https://www.incheon.go.kr/welfare/WE020441", "2026-10-24", "inc41",
  "만18세 이후 만기 또는 연장 보호종료된 사람으로 보호종료 5년 이내인 사람", "target", None),
 ("incheon-docs", "인천", 1, "인천시 자립수당", "https://www.incheon.go.kr/welfare/WE020441", "2026-10-24", "inc41",
  "사이버강의 이수증 (서민금융진흥원 금융교육포털 http://edu.kinfa.or.kr 이수) 또는 국민연금공단 재무상담 확인서 중 택 1부", "rule", None),
 ("incheon-pre", "인천", 1, "인천시 자립수당", "https://www.incheon.go.kr/welfare/WE020441", "2026-10-24", "inc41",
  "신청기간 보호종료 전 30일 이내 사전신청 가능 상시신청가능", "allow_when", None),
 ("incheon-settle", "인천", 1, "인천시 자립정착금", "https://www.incheon.go.kr/welfare/WE020442", "2026-10-24", "inc42",
  "보호종료 시 1인당 자립정착금 1,000만원 지급", "settle", 1000),
 ("incheon-settle-when", "인천", 1, "인천시 자립정착금", "https://www.incheon.go.kr/welfare/WE020442", "2026-10-24", "inc42",
  "신청기간 : 자립정착금 수령 1개월 이전", "settle_when", None),
 ("incheon-return", "인천", 1, "인천시 자립정착금", "https://www.incheon.go.kr/welfare/WE020442", "2026-10-24", "inc42",
  "지원제외 : 보호 조기종료 이후 원가정으로 복귀한 경우", "rule", None),
 ("gn-settle", "경남", 1, "경상남도 청년포털 자립준비청년 지원", "https://youth.gyeongnam.go.kr/youth/menu.es?mid=a11303000000", "미표기", "gyeongnam",
  "자립준비청년 보호종료 시 15,000천원 일시금 지급", "settle", 1500),
 ("gn-allow", "경남", 1, "경상남도 청년포털 자립준비청년 지원", "https://youth.gyeongnam.go.kr/youth/menu.es?mid=a11303000000", "미표기", "gyeongnam",
  "자립수당 : 매월 50만원 현금 지급", "allow", 50),
 ("gn-period", "경남", 1, "경상남도 청년포털 자립준비청년 지원", "https://youth.gyeongnam.go.kr/youth/menu.es?mid=a11303000000", "미표기", "gyeongnam",
  "지급기한 : 보호종료일이 속한 달부터 최대 60회차까지 가능", "period", None),
 ("gn-pre", "경남", 1, "경상남도 청년포털 자립준비청년 지원", "https://youth.gyeongnam.go.kr/youth/menu.es?mid=a11303000000", "미표기", "gyeongnam",
  "보호종료 30일 이내 시설, 공동생활가정, 가정위탁지원센터 사전 신청이 우선이나, 퇴소 후 주소지 읍면동에서 아동 직접 신청 가능", "allow_when", None),
 ("gn-plan", "경남", 1, "경상남도 청년포털 자립준비청년 지원", "https://youth.gyeongnam.go.kr/youth/menu.es?mid=a11303000000", "미표기", "gyeongnam",
  "자립정착금 사용계획서 작성 후 행정복지센터 → 대상자 선정 → 계좌로 지급", "how", None),
 ("cb-allow", "충북", 1, "충청북도 자립준비청년 자립수당", "https://www.chungbuk.go.kr/young/contents.do?key=5040", "2026년 사업(1~12월)", "chungbuk",
  "자립준비청년에게 매월 50만원의 자립수당 지급", "allow", 50),
 ("cb-target", "충북", 1, "충청북도 자립준비청년 자립수당", "https://www.chungbuk.go.kr/young/contents.do?key=5040", "2026년 사업(1~12월)", "chungbuk",
  "아동복지시설․가정위탁 보호종료 5년 이내인 자", "target", None),
 ("cb-2yr", "충북", 1, "충청북도 자립준비청년 자립수당", "https://www.chungbuk.go.kr/young/contents.do?key=5040", "2026년 사업(1~12월)", "chungbuk",
  "보호종료일 기준 과거 2년 이상 연속보호를 받은자", "rule", None),
 ("cb-size", "충북", 1, "충청북도 자립준비청년 자립수당", "https://www.chungbuk.go.kr/young/contents.do?key=5040", "2026년 사업(1~12월)", "chungbuk",
  "사업규모 315명", "rule", None),
 ("gj-allow", "광주", 1, "광주시 자립준비청년 자립수당 지원", "https://www.gwangju.go.kr/mogef/contentsView.do?pageId=mogef62", "미표기", "gwangju",
  "5년간 자립수당 지원으로 자립 강화 (500천원*12월*5년)", "allow", 50),
 ("mohw-allow", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "올해 1월 10만 원을 추가 인상하여 월 50만 원씩 지급받고 있다", "allow", 50),
 ("mohw-settle", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "(24년 기준) 서울 2000만 원, 대전·경기·제주 1500만 원, 경남 1200만 원 외 1000만 원", "settle_table", None),
 ("mohw-min", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "전국 17개 시·도 모두 보건복지부 권고 기준인 1000만 원 이상을 지급", "rule", None),
 ("mohw-5yr", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "보호종료 후 5년간 지급되는 자립수당", "period", None),
 ("mohw-early", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "법 시행일 전에 15세 이후 보호종료된 아동의 경우에는 2024년 2월 9일 이후 18세가 되는 아동부터 지원받을 수 있다", "rule", None),
 ("mohw-home", "전국", 2, "보건복지부 보도자료(18세 이전 보호종료도 자립지원)", "https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1480211", "2024-02-07", "mohw",
  "원가정복귀 사유는 원칙적 지원 대상은 아니나, 아동복지심의위원회의 심의를 거쳐 필요하다고 판단되는 경우 예외적으로 지원받을 수 있다", "rule", None),
 ("nabo-settle", "전국", 3, "국회예산정책처 「자립지원 대상 아동·청년 지원사업 평가」 보도자료", "https://www.nabo.go.kr/ko/notice/releasesView.do?idx=8846", "2025-08-05", "nabo",
  "서울 2,000만원, 대전·경기·경남·제주 1,500만원, 부산 1,200만원, 기타 1,000만원", "settle_table", None),
 ("nabo-site", "전국", 3, "국회예산정책처 「자립지원 대상 아동·청년 지원사업 평가」 보도자료", "https://www.nabo.go.kr/ko/notice/releasesView.do?idx=8846", "2025-08-05", "nabo",
  "보호대상아동의 보호시설 소재지를 기준으로 지급되는 자립정착금", "rule", None),
]
KEYS = "id region tier doc url date file quote field value".split()
out = []
bad = 0
for row in C:
    d = dict(zip(KEYS, row))
    if norm(d["quote"]) not in load(d.pop("file")):
        print("원문에 없음:", d["id"], d["quote"]); bad += 1
    out.append(d)
# 전국 표(settle_table) -> 지역별 값(2차) : 두 문서가 일치하는 지역만 값을 둔다
TABLE = {  # 지역: (복지부 2024 값, 예산정책처 2025 값)
 "서울": (2000, 2000), "대전": (1500, 1500), "경기": (1500, 1500), "제주": (1500, 1500),
 "경남": (1200, 1500), "부산": (None, 1200),
}
OTHER = (1000, 1000)
json.dump({"cards": out, "table": TABLE, "other": OTHER}, open(f"{H}/../data/cards.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "cards", "bad", bad)
sys.exit(1 if bad else 0)
