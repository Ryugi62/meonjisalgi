// 먼저살기 핵심 로직 — 도메인(카드·규칙·검증)은 SDK·I/O를 모른다. AI 호출은 api/ 쪽에서 주입한다.
const data = require("./data/cards.json");
const REGIONS = ["서울","부산","대구","인천","광주","대전","울산","세종","경기","강원","충북","충남","전북","전남","경북","경남","제주"];
const cardById = Object.fromEntries(data.cards.map(c => [c.id, c]));

function cardsFor(region) {
  return data.cards.filter(c => c.region === region || c.region === "전국");
}
// 정착금: 지자체 공식(등급 1) 우선. 공식끼리 다르면 보류. 공식이 없으면 중앙 문서 두 건이 일치할 때만 2차 자료로 답.
function settleFact(region) {
  const t1 = data.cards.filter(c => c.region === region && c.field === "settle" && c.value != null);
  const vals = [...new Set(t1.map(c => c.value))];
  const mohw = cardById["mohw-settle"], nabo = cardById["nabo-settle"];
  const tb = data.table[region] || data.other;
  const other2 = [];
  if (vals.length > 1) return { status: "hold", reason: "지자체 공식 문서끼리 금액이 다릅니다", cites: t1.map(c => c.id) };
  if (vals.length === 1) {
    const diff = [];
    if (tb[0] != null && tb[0] !== vals[0]) diff.push({ cite: "mohw-settle", value: tb[0] });
    if (tb[1] != null && tb[1] !== vals[0]) diff.push({ cite: "nabo-settle", value: tb[1] });
    return { status: "ok", value: vals[0], tier: 1, cites: t1.map(c => c.id), conflicts: diff };
  }
  if (tb[0] === tb[1]) return { status: "ok", value: tb[0], tier: 2, cites: ["mohw-settle", "nabo-settle"], conflicts: [] };
  return { status: "hold", reason: "지자체 공식 페이지가 없고 중앙 문서끼리 금액이 다릅니다", cites: ["mohw-settle", "nabo-settle"] };
}
function allowFact(region) {
  const t1 = data.cards.filter(c => c.region === region && c.field === "allow");
  if (t1.length) return { value: 50, tier: 1, cites: t1.map(c => c.id) };
  return { value: 50, tier: 2, cites: ["mohw-allow"] };
}
function monthsBetween(endYm, nowYm) {
  const [a, b] = endYm.split("-").map(Number), [c, d] = nowYm.split("-").map(Number);
  return (c - a) * 12 + (d - b);
}
// 결정적 계산: 수당 회차(보호종료일이 속한 달부터 최대 60회차)
function schedule(endYm, nowYm) {
  const elapsed = monthsBetween(endYm, nowYm); // 종료월이 미래면 음수
  const used = elapsed < 0 ? 0 : elapsed + 1;
  const remaining = Math.max(0, 60 - used);
  const [y, m] = endYm.split("-").map(Number);
  const last = new Date(Date.UTC(y, m - 1 + 59, 1));
  const lastYm = `${last.getUTCFullYear()}-${String(last.getUTCMonth() + 1).padStart(2, "0")}`;
  return { elapsed, used, remaining, lastYm, expired: used > 60, future: elapsed < 0 };
}
// 숫자 토큰 검증: 문장 속 숫자가 인용·계산값에 있어야 한다
function nums(s) { return (String(s).match(/\d[\d,]*/g) || []).map(x => x.replace(/,/g, "")); }
function verifyItem(item, allowedExtra) {
  const cites = (item.cites || []).filter(id => cardById[id]);
  if (!cites.length) return { ok: false, why: "인용 카드 없음" };
  const pool = new Set();
  cites.forEach(id => nums(cardById[id].quote).forEach(n => pool.add(n)));
  cites.forEach(id => { if (/1천만/.test(cardById[id].quote)) pool.add("1000"); });
  (allowedExtra || []).forEach(n => pool.add(String(n)));
  const text = [item.title, item.detail, item.answer].filter(Boolean).join(" ").replace(/\d{4}-\d{2}/g, " ").replace(/\d{4}년/g, " ").replace(/\d{1,2}월/g, " ");
  // 천 단위(15,000천원 ↔ 1,500만원) 표기 차이를 흡수하기 위해 파생값도 허용
  [...pool].forEach(n => { const v = Number(n); if (!isNaN(v)) { pool.add(String(v / 10)); pool.add(String(v * 10)); pool.add(String(v / 10000)); } });
  const bad = nums(text).filter(n => !pool.has(n));
  if (bad.length) return { ok: false, why: "인용에 없는 숫자: " + [...new Set(bad)].join(", ") };
  return { ok: true };
}
module.exports = { REGIONS, data, cardById, cardsFor, settleFact, allowFact, schedule, verifyItem, nums };
