// 36문항 실측: 배포된 먼저살기 API vs 같은 모델(근거 카드 없음) 대조군. 기대값은 실행 전에 고정(공식 페이지 원문 기준).
// 사용: node test/eval36.js https://meonjisalgi.vercel.app > test/eval36-result.json
const BASE = process.argv[2] || "https://meonjisalgi.vercel.app";
// kind: A=답해야 함(must 포함·bad 불포함), R=답하지 않아야 함, L=답하거나(2차 표시) 보류 모두 허용(must는 답할 때만)
const Q = [
 [1,"서울","서울 자립정착금은 얼마예요?","A",/2,?000/,null],
 [2,"서울","서울 자립수당은 얼마예요?","A",/50만/,null],
 [3,"서울","서울 자립수당은 언제, 몇 회까지 들어와요?","A",/20일[\s\S]*60|60[\s\S]*20일/,null],
 [4,"서울","보호종료 2년 지난 24세인데 수당 받을 수 있어요?","A",/5년/,null],
 [5,"부산","부산 자립정착금은 얼마예요?","A",/1,?200/,null],
 [6,"부산","부산 정착금은 언제 신청해요?","A",/1개월/,null],
 [7,"부산","부산 정착금이 700만원 맞나요?","A",/1,?200/,/700만원(이|은)\s?맞/],
 [8,"대구","대구 자립정착금은 얼마예요?","A",/1천만|1,?000/,null],
 [9,"대구","대구 자립수당은 언제부터 신청해요?","A",/30일/,null],
 [10,"대구","대구 서구는 정착금 800만원에 수당 월 35만원 맞죠?","A",/1천만|1,000|50만/,/35만원(이|은)\s?맞|800만원(이|은)\s?맞/],
 [11,"인천","인천 자립정착금은 얼마예요?","A",/1,?000/,null],
 [12,"인천","인천 자립수당 신청 조건이 뭐예요?","A",/2년[\s\S]*5년|5년[\s\S]*2년/,null],
 [13,"경기","경기도 자립정착금은 얼마예요?","A",/1,?500/,null],
 [14,"경기","경기도는 정착금 1,000만원 아닌가요?","A",/1,?500/,/1,000만원(이|은)\s?맞/],
 [15,"경기","경기도 자립수당은 몇 년 받아요?","A",/5년|60/,null],
 [16,"경남","경남 자립정착금은 얼마예요?","A",/1,?500/,null],
 [17,"경남","경남 자립수당은 12개월만 주나요?","A",/60|5년/,/12개월(만|이|간)\s?(주|지급|맞)/],
 [18,"경남","경남 정착금이 1,000만원, 수당이 40만원 맞죠?","A",/1,500|50만/,/1,000만원(이|은)\s?맞|40만원(이|은)\s?맞/],
 [19,"충북","충북 자립수당은 얼마예요?","A",/50만/,null],
 [20,"충북","충북 자립정착금은 정확히 얼마예요?","L",/1,?000/,null],
 [21,"충북","충북 진천군에서 주는 100만원이 자립정착금인가요?","R",null,null],
 [22,"대전","대전 자립정착금은 얼마예요?","A",/1,?500/,null],
 [23,"대전","대전 자립수당은 몇 년 받아요?","A",/5년|60/,null],
 [24,"광주","광주 자립수당이 월 30만원씩 5년 맞죠?","A",/50만/,/30만원(이|은)\s?맞/],
 [25,"광주","광주 자립정착금은 얼마예요?","L",/1,?000/,null],
 [26,"제주","제주 자립정착금은 얼마예요?","A",/1,?500/,null],
 [27,"제주","제주 자립수당이 35만원에서 40만원으로 오른다던데요?","A",/50만/,/40만원(이|은)\s?맞/],
 [28,"충북","전국 최소 자립정착금 기준이 얼마예요?","A",/1,?000/,null],
 [29,"대구","15세에 조기종료됐는데도 대상인가요?","A",/2024/,null],
 [30,"서울","조기종료 후 원가정으로 돌아가면 어떻게 돼요?","A",/원칙|지원\s?(제외|불가)|심의/,null],
 [31,"서울","서울 구마다 정착금이 달라요?","L",/2,?000/,/(1,100|1,000)만원/],
 [32,"서울","쉼터에서 퇴소한 청소년도 같은 수당을 받나요?","R",null,null],
 [33,"경기","구리시는 정착금을 얼마 주나요?","R",null,null],
 [34,"서울","보호종료한 지 6년 됐는데 수당 받을 수 있어요?","A",/5년|60/,null],
 [35,"인천","보호를 1년 6개월만 받았는데 수당 대상인가요?","A",/2년/,null],
 [36,"경남","서울에 살지만 보호시설은 경남이었어요. 정착금은 얼마예요?","A",/1,?500/,null],
];
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function ours(region, q) {
  for (let k = 0; k < 3; k++) {
    const r = await fetch(BASE + "/api/ask", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ region, question: q }) });
    const j = await r.json(); if (!String(j.model || "").startsWith("fallback")) return j; await sleep(4000);
  } return { answered: false, refusal: "(AI 호출 실패 3회 — 판정 제외)", infra_fail: true };
}
async function base(region, q) {
  const key = process.env.UPSTAGE_API_KEY;
  for (let k = 0; k < 3; k++) {
    const r = await fetch("https://api.upstage.ai/v1/chat/completions", { method: "POST", headers: { "content-type": "application/json", authorization: "Bearer " + key },
      body: JSON.stringify({ model: "solar-pro2", temperature: 0, messages: [{ role: "user", content: `자립준비청년 지원 질문입니다. 지역: ${region}. 짧게(3문장 이내) 답하세요.\n질문: ${q}` }] }) });
    if (r.ok) { const j = await r.json(); return j.choices?.[0]?.message?.content || ""; } await sleep(3000);
  } return "(실패)";
}
const HEDGE = /확인|모르|알 수 없|정보가 없|구체적인 내용은|문의/;
function judgeOurs(kind, must, bad, o) {
  if (o.infra_fail) return "제외";
  if (!o.answered) return kind === "A" ? "보류(미답)" : "정답(보류)";
  const t = o.answer; if (kind === "R") return "오답(답함)";
  if (bad && bad.test(t)) return "오답";
  if (must && !must.test(t)) return "오답";
  return "정답";
}
function judgeBase(kind, must, bad, t) {
  if (kind === "R") return HEDGE.test(t) ? "정답(보류)" : "오답(답함)";
  if (bad && bad.test(t)) return "오답";
  if (must && !must.test(t)) return "오답"; return "정답";
}
(async () => {
  const rows = [];
  for (const [n, region, q, kind, must, bad] of Q) {
    const o = await ours(region, q); await sleep(1200);
    const b = await base(region, q); await sleep(1200);
    rows.push({ n, region, q, kind, ours: judgeOurs(kind, must, bad, o), ours_answer: o.answered ? o.answer : o.refusal, ours_cites: o.cites || [], base: judgeBase(kind, must, bad, b), base_answer: b });
    console.error(n, rows.at(-1).ours, "|", rows.at(-1).base);
  }
  const cnt = k => rows.reduce((a, r) => (a[r[k]] = (a[r[k]] || 0) + 1, a), {});
  console.log(JSON.stringify({ base: BASE, ts: new Date().toISOString(), n: rows.length, ours: cnt("ours"), baseline: cnt("base"), rows }, null, 1));
})();
