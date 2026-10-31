const t = require("node:test"), a = require("node:assert");
const L = require("../lib.js");
t.test("서울 정착금 2000 공식", () => { const f = L.settleFact("서울"); a.equal(f.value, 2000); a.equal(f.tier, 1); });
t.test("경남 공식 1500, 복지부 2024 1200은 충돌로 표시", () => { const f = L.settleFact("경남"); a.equal(f.value, 1500); a.ok(f.conflicts.some(c => c.value === 1200)); });
t.test("충북 공식 정착금 없음 -> 중앙 두 문서 일치 1000 (2차)", () => { const f = L.settleFact("충북"); a.equal(f.value, 1000); a.equal(f.tier, 2); });
t.test("경기 1500 (2차)", () => { const f = L.settleFact("경기"); a.equal(f.value, 1500); a.equal(f.tier, 2); });
t.test("부산 1200 공식", () => a.equal(L.settleFact("부산").value, 1200));
t.test("회차 계산", () => { const s = L.schedule("2024-03", "2026-10"); a.equal(s.used, 32); a.equal(s.remaining, 28); a.equal(s.lastYm, "2029-02"); });
t.test("6년 지나면 만료", () => a.ok(L.schedule("2020-01", "2026-10").expired));
t.test("인용에 없는 숫자는 거부", () => {
  a.equal(L.verifyItem({ title: "정착금 700만원", cites: ["busan-settle"] }).ok, false);
  a.equal(L.verifyItem({ title: "정착금 1,200만원", cites: ["busan-settle"] }).ok, true);
  a.equal(L.verifyItem({ title: "정착금", cites: [] }).ok, false);
});
