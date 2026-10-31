const L = require("../lib.js");
const { gemini, MODEL } = require("./_ai.js");
const SCHEMA = { type: "OBJECT", properties: { answerable: { type: "BOOLEAN" }, answer: { type: "STRING" }, cites: { type: "ARRAY", items: { type: "STRING" } }, why_not: { type: "STRING" } }, required: ["answerable", "answer", "cites", "why_not"] };
module.exports = async function handler(req, res) {
  res.setHeader("content-type", "application/json; charset=utf-8");
  try {
    const b = req.method === "POST" ? (typeof req.body === "string" ? JSON.parse(req.body) : req.body) : req.query;
    const { region, question } = b || {};
    if (!L.REGIONS.includes(region) || !question || question.length > 300) return res.status(400).end(JSON.stringify({ error: "소재지와 300자 이내 질문이 필요합니다." }));
    // 시·군·구 단위 질문은 광역 안내문으로 답할 수 없다(결정적 가드, lib.unitGuard)
    const ug = L.unitGuard(question);
    if (ug) return res.status(200).end(JSON.stringify({ region, question, model: "guard", answered: false, refusal: ug }));
    const cards = L.cardsFor(region);
    const st = L.settleFact(region);
    const prompt = `당신은 자립준비청년 지원 안내 도우미입니다. 아래 [카드](공식 안내문 인용)만 근거로 질문에 답하세요.
규칙: (1) 카드에 근거가 없으면 answerable=false, answer는 빈 문자열, why_not에 이유 한 줄. 반대로 “대상이 아니다/아니오”도 카드의 요건(예: 보호종료 5년 이내, 2년 이상 연속 보호, 원가정 복귀 제외)으로 판단할 수 있으면 answerable=true로 그 결론을 쓰세요. 질문에 든 금액·기간이 카드와 다르면 카드의 값으로 정정해 answerable=true로 답하세요. 답에 쓴 숫자가 들어 있는 카드는 모두 cites에 넣으세요. (2) 질문이 시·군·구 단위 금액, 다른 제도(가정 밖 청소년 쉼터 퇴소 지원, 시군 전입장려금 등), 카드에 없는 지역이나 연도를 묻는 경우에도 카드가 직접 답하지 않으면 answerable=false. 질문에 든 숫자가 카드와 다르면 정정해 주세요(카드 숫자로). (3) answerable=true이면 cites에 근거 카드 id 1개 이상, 숫자는 카드 인용에 있는 것만. (4) 쉬운 말 3문장 이내. (5) 정착금 금액을 묻거나 답할 때는 반드시 [정착금 판정]의 금액을 쓰고, 더 오래된 다른 문서의 다른 금액은 “다른 문서에는 ○○로 적혀 있으나 더 최근 지자체 안내를 따랐다”로만 덧붙이세요.
[질문의 지역] ${region}
[정착금 판정] ${st.status === "ok" ? st.value + "만원 (" + (st.tier === 1 ? "지자체 공식" : "중앙 문서 2건, 지자체 공식 미확인 — 답에 이 점을 밝힐 것") + ")" : "보류 — " + st.reason}
[카드]
${cards.map(c => `- id=${c.id} | ${c.doc} (${c.date}) | “${c.quote}”`).join("\n")}
[질문] ${question}`;
    const out = { region, question, model: null, answered: false };
    let r;
    try { r = await gemini(prompt, SCHEMA); out.model = gemini.used; } catch (e) { out.model = "fallback(" + e.message + ")"; out.refusal = "AI 호출이 제한돼 답하지 않습니다. 잠시 뒤 다시 시도해 주세요."; return res.status(200).end(JSON.stringify(out)); }
    if (!r.answerable) { out.refusal = r.why_not || "안내문에 근거가 없어 답하지 않습니다."; return res.status(200).end(JSON.stringify(out)); }
    const v = L.verifyItem({ answer: r.answer, cites: r.cites }, L.nums(question));
    if (!v.ok) { out.refusal = "인용 검증을 통과하지 못해 답하지 않습니다 (" + v.why + ")"; out.rejected_answer = r.answer; return res.status(200).end(JSON.stringify(out)); }
    // 정착금 금액 질문: 결정적 판정값(지자체 공식 우선)이 답에 들어 있어야 한다 — 옛 문서 값으로 답하면 거부
    if (st.status === "ok" && /정착금/.test(question) && /얼마|금액|몇/.test(question)) {
      const v = st.value, forms = [String(v), v.toLocaleString("en-US"), v === 1000 ? "1천만" : "", String(v) + "만"].filter(Boolean);
      if (!forms.some(f => r.answer.includes(f))) { out.refusal = "답한 금액이 지자체 공식 안내문 기준값(" + v.toLocaleString("en-US") + "만원)과 달라 답하지 않습니다."; out.rejected_answer = r.answer; return res.status(200).end(JSON.stringify(out)); }
    }
    out.answered = true; out.answer = r.answer; out.cites = r.cites.filter(id => L.cardById[id]);
    out.cards = Object.fromEntries(out.cites.map(id => [id, L.cardById[id]]));
    return res.status(200).end(JSON.stringify(out));
  } catch (e) { return res.status(500).end(JSON.stringify({ error: "서버 오류: " + e.message })); }
};
