// 로컬 핸들러 직접 호출(시험용). 사용: node scripts/call-local.js plan '{"region":"서울",...}'
const h = { plan: require("../api/plan.js"), ask: require("../api/ask.js") };
const [,, which, body] = process.argv;
const res = { setHeader() {}, status(c) { this.c = c; return this; }, end(s) { console.log(this.c, s); } };
h[which]({ method: "POST", body }, res);
