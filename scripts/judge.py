"""모의 심사: 서로 다른 관점 3명(Upstage Solar API, 제작 모델과 같은 계열이라는 한계 명시). 제출물 텍스트만 준다 — 작성자·내부 이력 없음.
사용: python3 scripts/judge.py <제출물.txt> <유사서비스.txt> > out.json"""
import json, os, sys, urllib.request, re
SUB=open(sys.argv[1],encoding="utf-8").read(); SIM=open(sys.argv[2],encoding="utf-8").read() if len(sys.argv)>2 else ""
KEY=os.environ["UPSTAGE_API_KEY"]
CTX="""You are an independent expert judge for a Korean government AI challenge: "AI 라이프 솔루션 챌린지 2026" (KEIT, Ministry of Trade, Industry and Energy). You know nothing about who wrote the submission. Official text: 「AI(생성형AI, 피지컬AI, AI에이전트 등) 기술을 필히 사용해 문제 해결」, 「중저위수준의 AI기술을 반짝이는 아이디어를 통해 우리 생활주변의 불편, 애로, 규제 등을 해결하는 방법 모색」. 심사항목: (1) 문제정의 및 해결능력 (2) AI 기술의 구현 수준 및 결과물의 완성도 (3) 사회문제 해결 기여도 (4) AI 기술의 창의적 응용. Be harsh and specific: penalize claims without evidence, unmeasured effects, and anything a solo student prototype cannot support.
Score each of the four criteria 0-25 (sum = total /100). Output strictly JSON: {"c1":n,"c2":n,"c3":n,"c4":n,"total":n,"top_prize_candidate":true|false,"weaknesses":["...","...","..."],"reason":"one sentence"}. Weaknesses must name concrete missing evidence."""
LENS={
 "organizer":"Your lens: a KEIT program officer who must justify each prize as 'AI technology that visibly improves citizens' daily life' in a ministry press release.",
 "engineer":"Your lens: an AI engineering professor who checks whether the AI part is real, appropriate and verifiably working, not a buzzword wrapper.",
 "practitioner":"Your lens: a social-welfare practitioner who asks whether care-leavers would actually use it next month and whether wrong answers could hurt them.",
}
out={}
for k,l in LENS.items():
    prompt=f"{CTX}\n{l}\n\n[Submission text (성과보고서 + 시연 결과 요약)]\n{SUB}\n\n[Existing similar services known to the judges]\n{SIM}\n"
    body=json.dumps({"model":"solar-pro2","temperature":0,"response_format":{"type":"json_object"},"messages":[{"role":"user","content":prompt}]}).encode()
    req=urllib.request.Request("https://api.upstage.ai/v1/chat/completions",body,{"content-type":"application/json","authorization":"Bearer "+KEY})
    r=json.load(urllib.request.urlopen(req,timeout=120)); t=r["choices"][0]["message"]["content"]
    out[k]=json.loads(re.sub(r"^```json\s*|```$","",t.strip()))
print(json.dumps(out,ensure_ascii=False,indent=1))
