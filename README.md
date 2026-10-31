# 먼저살기
보호종료 청년의 자립정착금·자립수당을 공식 안내문 인용과 함께 월별 할 일로 알려 주고, 근거가 없으면 답하지 않는 AI 안내.
- 테스트 URL: https://meonjisalgi.vercel.app
- 설계: SPEC.md · 카드 빌드: `python3 scripts/build_cards.py` · 단위 시험: `node --test test/core.test.js`
- 36문항 실측: `node test/eval36.js <URL>` (결과 `test/eval36-result.json`)
- 환경변수: `UPSTAGE_API_KEY`(1순위), `GEMINI_API_KEY`(폴백)
