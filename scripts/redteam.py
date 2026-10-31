# -*- coding: utf-8 -*-
"""레드팀 8문: 제작자가 아닌 독립 모델(Upstage Solar API)에게 계획·산출물만 주고 '이 계획이 지는 이유'를 찾게 한다."""
import json, os, sys, re, urllib.request
SUB=open(sys.argv[1],encoding="utf-8").read(); KEY=os.environ["UPSTAGE_API_KEY"]
Q=["경쟁자: 최강 상대가 미리 만들어 오고 도움을 받고 규칙을 느슨히 해석해도 이기나","고객 가치: 지표가 청년의 돈·위험 중 무엇을 줄이나, 더 단순한 대안이 낫지 않나","물리 실현: 입력·데이터는 현실 어디서 오나, 없는 것을 가정하나","규칙·자원: 공고가 주는 것·안 주는 것·허용하는 것(원문)에 어긋나나","데모 현실성: 시연 조건이 실제 사용과 다른 점","기존 해법: 이미 있는 서비스와 같은가","근거 폭: 결론마다 출처 유형 수, 1경로 결론은 없나","실행 환경: 실제로 돌 기계·장소·사람에서 확인했나(무료 API 한도·호스팅)"]
prompt="당신은 레드팀입니다. 아래 제출물이 지는 이유를 찾으세요. 8개 질문마다 가장 치명적인 공격 1개와 그 공격이 맞는지(우리 전제)를 JSON 배열로: [{\"q\":번호,\"premise\":\"우리 전제\",\"attack\":\"공격 질문\",\"fatal\":true|false}]. 질문 목록:\n"+"\n".join(f"{i+1}. {q}" for i,q in enumerate(Q))+"\n\n[제출물]\n"+SUB+"\n[참고] 공고 원문: 심사항목 문제정의·AI 구현 수준·사회문제 기여·AI 창의적 응용, 대국민 투표 50%+심사 50%, 제출 필수 성과보고서·참가신청서·테스트URL·데모영상."
body=json.dumps({"model":"solar-pro2","temperature":0,"response_format":{"type":"json_object"},"messages":[{"role":"user","content":prompt+"\n반드시 {\"items\":[...]} 형태의 JSON 객체로."}]}).encode()
req=urllib.request.Request("https://api.upstage.ai/v1/chat/completions",body,{"content-type":"application/json","authorization":"Bearer "+KEY})
t=json.load(urllib.request.urlopen(req,timeout=120))["choices"][0]["message"]["content"]
print(json.dumps(json.loads(re.sub(r"^```json\s*|```$","",t.strip())),ensure_ascii=False,indent=1))
