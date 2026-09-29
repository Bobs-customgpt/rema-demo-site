/* ============================================================
   CustomGPT.ai agent connections for the ReMA demo site
   ------------------------------------------------------------
   Two agents power the demo:
     1. Floating chat (bottom-right bubble) -> chat.js (p_id / p_key)
     2. AI search in the header search bar  -> sge.js  (sge_p_id / sge_p_key)
   Values come from CustomGPT -> agent -> Deploy -> Embed. They are public,
   client-side embed values (the same ones that sit in any website embed).

   Override the chat agent without editing this file by adding query params
   to the URL: index.html?p_id=12345&p_key=your-embed-key
   Deep-link a search result with ?q=your+question
   ============================================================ */
window.DEMO_CONFIG = {
  // "REMA Demo" chat agent (CustomGPT project 101035)
  p_id:  "101035",
  p_key: "3ca8d86c97dc65f4407c841d5e9e62de",

  // Search Generative Experience agent wired to the header search bar (project 101060)
  sge_p_id:  "101060",
  sge_p_key: "3870085f3052a3f32827cab81868bd16",
  sge_div_id: "customgpt_chat"
};
