// Gemini 호출(인프라 계층). 키는 환경변수 GEMINI_API_KEY 로만 읽는다.
const MODEL = process.env.GEMINI_MODEL || "gemini-2.5-flash";
async function geminiOnce(MODEL, prompt, schema) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw new Error("no_key");
  const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), 45000);
  try {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`, {
      method: "POST", signal: ctl.signal,
      headers: { "content-type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json", responseSchema: schema, temperature: 0, thinkingConfig: { thinkingBudget: 0 } },
      }),
    });
    if (!r.ok) throw new Error("gemini_" + r.status);
    const j = await r.json();
    const t = j.candidates?.[0]?.content?.parts?.map(p => p.text).join("") || "";
    return JSON.parse(t);
  } finally { clearTimeout(to); }
}
// Upstage Solar(한국어 LLM) 우선, 한도 시 Gemini 로 넘어간다. 스키마(Gemini 형식)는 JSON 지시문으로 같이 전달한다.
async function solar(prompt, schema) {
  const key = process.env.UPSTAGE_API_KEY; if (!key) throw new Error("no_upstage_key");
  const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), 50000);
  try {
    const r = await fetch("https://api.upstage.ai/v1/chat/completions", { method: "POST", signal: ctl.signal,
      headers: { "content-type": "application/json", authorization: "Bearer " + key },
      body: JSON.stringify({ model: "solar-pro2", temperature: 0, response_format: { type: "json_object" },
        messages: [{ role: "system", content: "반드시 JSON 객체 하나만 출력한다. 스키마: " + JSON.stringify(schema) }, { role: "user", content: prompt }] }) });
    if (!r.ok) throw new Error("upstage_" + r.status);
    const j = await r.json(); const t = j.choices?.[0]?.message?.content || "";
    return JSON.parse(t.replace(/^```json\s*|```$/g, "").trim());
  } finally { clearTimeout(to); }
}
const MODELS = [MODEL, "gemini-2.5-flash-lite", "gemini-3-flash-preview"];
async function gemini(prompt, schema) {
  let last;
  try { const r = await solar(prompt, schema); gemini.used = "solar-pro2"; return r; } catch (e) { last = e; }
  for (const m of MODELS) {
    for (let k = 0; k < 2; k++) {
      try { const r = await geminiOnce(m, prompt, schema); gemini.used = m; return r; }
      catch (e) { last = e; if (!/gemini_(429|500|503)|abort/i.test(e.message + e.name)) throw e; await new Promise(r => setTimeout(r, 800)); }
    }
  }
  throw last;
}
module.exports = { gemini, MODEL };
