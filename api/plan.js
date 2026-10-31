const L = require("../lib.js");
const { gemini, MODEL } = require("./_ai.js");
function kstYm() { const d = new Date(Date.now() + 9 * 3600e3); return d.toISOString().slice(0, 7); }

const SCHEMA = { type: "OBJECT", properties: { items: { type: "ARRAY", items: { type: "OBJECT", properties: {
  when: { type: "STRING" }, title: { type: "STRING" }, detail: { type: "STRING" }, cites: { type: "ARRAY", items: { type: "STRING" } } },
  required: ["when", "title", "detail", "cites"] } } }, required: ["items"] };

function buildFacts(region, endYm, nowYm, twoYears, returnedHome) {
  const sch = L.schedule(endYm, nowYm), st = L.settleFact(region), al = L.allowFact(region);
  const cards = L.cardsFor(region);
  return { sch, st, al, cards };
}
module.exports = async function handler(req, res) {
  res.setHeader("content-type", "application/json; charset=utf-8");
  try {
    const b = req.method === "POST" ? (typeof req.body === "string" ? JSON.parse(req.body) : req.body) : req.query;
    const { region, endYm, twoYears = "unknown", returnedHome = "no" } = b || {};
    if (!L.REGIONS.includes(region) || !/^\d{4}-\d{2}$/.test(endYm || "")) return res.status(400).end(JSON.stringify({ error: "소재지와 보호종료월(YYYY-MM)을 확인해 주세요." }));
    const nowYm = b.nowYm && /^\d{4}-\d{2}$/.test(b.nowYm) ? b.nowYm : kstYm();
    const { sch, st, al, cards } = buildFacts(region, endYm, nowYm);
    const out = { region, endYm, nowYm, model: null, schedule: sch, items: [], held: [], dropped: [], notes: [] };
    if (sch.expired) { out.held.push({ title: "자립수당 60회차를 모두 지난 시기입니다", reason: "최대 60회차(보호종료일이 속한 달부터)", cites: ["seoul-period"] }); }
    if (returnedHome === "yes") out.notes.push({ text: "보호 조기종료 뒤 원가정으로 복귀한 경우는 원칙적으로 지원 제외입니다(예외는 위원회 심의).", cites: ["incheon-return", "mohw-home"] });
    if (twoYears === "no") out.notes.push({ text: "‘과거 2년 이상 연속 보호’ 요건에 못 미치면 수당 대상이 아닐 수 있습니다.", cites: ["incheon-2yr"] });
    if (st.status === "hold") out.held.push({ title: "자립정착금 금액은 답하지 않습니다", reason: st.reason, cites: st.cites });
    if (st.status === "ok" && st.conflicts && st.conflicts.length) out.notes.push({ text: `다른 문서에는 정착금이 ${st.conflicts.map(c => c.value + "만원").join(", ")}로 적혀 있으나 더 최근인 지자체 공식 안내를 따랐습니다. 신청 전 구·군에 확인하세요.`, cites: st.conflicts.map(c => c.cite) });
    const allowedExtra = [sch.used, sch.remaining, 60, 5, 30];
    const prompt = `당신은 보호종료 청년(자립준비청년)에게 해야 할 일을 월별로 알려 주는 안내 도우미입니다.
규칙: (1) 아래 [카드]에 적힌 내용만 사용하세요. 카드에 없는 금액·기한·제도는 쓰지 마세요. (2) 모든 항목은 cites에 근거 카드 id를 1개 이상 넣으세요. (3) 숫자는 카드 인용 또는 [계산]에 있는 것만 쓰세요. (4) 쉬운 말, 한 항목 두 문장 이내. (5) 보호종료가 이미 지난 경우 정착금은 종료 시 지급되는 돈이므로 아직 못 받았다면 구·군에 확인하라고 쓰고, 카드에 없는 날짜를 지어내지 마세요. 시기(when)는 “지금”, [계산]의 연월, 또는 카드에 적힌 기한(예: 종료 30일 전, 수령 1개월 이전)만 쓰세요. (6) 5~7개 항목, when은 시간 순서("지금", "보호종료 1개월 전", "2026-11" 같은 형식).
[청년 상황] 소재지 ${region} · 보호종료월 ${endYm} · 이번 달 ${nowYm} · 2년 이상 연속 보호: ${twoYears} · 원가정 복귀: ${returnedHome}
[계산] 수당 ${sch.used}회차째, 남은 회차 ${sch.remaining}, 마지막 회차 ${sch.lastYm}, ${sch.future ? "보호종료 예정(미래)" : "이미 종료됨"}, 정착금 ${st.status === "ok" ? st.value + "만원(" + (st.tier === 1 ? "지자체 공식" : "중앙 문서 2건 일치, 지자체 공식 미확인") + ")" : "보류"}
[카드]
${cards.map(c => `- id=${c.id} | ${c.doc} (${c.date}) | “${c.quote}”`).join("\n")}`;
    try {
      const r = await gemini(prompt, SCHEMA);
      out.model = gemini.used || MODEL;
      for (const it of r.items || []) {
        const v = L.verifyItem(it, allowedExtra);
        if (v.ok) out.items.push({ ...it, cites: it.cites.filter(id => L.cardById[id]) });
        else out.dropped.push({ title: it.title, why: v.why });
      }
    } catch (e) {
      out.model = "fallback(" + e.message + ")";
      out.notes.push({ text: "AI 호출이 제한돼 인용 카드를 그대로 보여 드립니다.", cites: [] });
      const base = [];
      if (st.status === "ok") base.push({ when: "지금", title: `자립정착금 ${st.value.toLocaleString()}만원`, detail: "신청 시기와 서류는 아래 인용을 확인하세요.", cites: st.cites });
      base.push({ when: "지금", title: "자립수당 월 50만원", detail: `${sch.used}회차째입니다.`, cites: al.cites });
      out.items = base.filter(x => L.verifyItem(x, allowedExtra).ok);
    }
    out.cards = {};
    for (const x of [...out.items, ...out.notes, ...out.held]) for (const id of x.cites || []) if (L.cardById[id]) out.cards[id] = L.cardById[id];
    return res.status(200).end(JSON.stringify(out));
  } catch (e) { return res.status(500).end(JSON.stringify({ error: "서버 오류: " + e.message })); }
};
module.exports.buildFacts = buildFacts;
