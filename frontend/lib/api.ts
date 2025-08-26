// 仮のAPI関数群 - 実際のAPIエンドポイントに置き換えてください

export type CreateSessionRequest = { topic: string; summary?: string | null; language?: 'ja'|'en' };
export type CreateSessionResponse = { sessionId: string };
export type TitleCandidate = { id: string; title: string; score?: number | null; intent?: string | null; why?: string | null };
export type OutlineResponse = { outline: any } | any;
export type ArticleResponse = { markdown: string; sections?: string[] };

const HEADERS = { 'Content-Type': 'application/json' };
async function j<T>(r: Response): Promise<T> {
  if (!r.ok) {
    const text = await r.text()
    throw new Error(text || `${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<T>;
}

export async function createSession(body: CreateSessionRequest): Promise<CreateSessionResponse> {
  // API契約: { topic, draft?, language? } なので summary→draft へ写す
  const payload = { topic: body.topic, draft: body.summary ?? null, language: body.language ?? 'ja' };
  return fetch('/api/session', { method:'POST', headers: HEADERS, body: JSON.stringify(payload) }).then(j<CreateSessionResponse>);
}

export async function generateTitles(sessionId: string, count: number = 10): Promise<{ candidates: TitleCandidate[] }> {
  return fetch('/api/generate-titles', {
    method:'POST', headers: HEADERS, body: JSON.stringify({ sessionId, maxCandidates: count })
  }).then(j<{ candidates: TitleCandidate[] }>);
}

export async function selectTitle(sessionId: string, candidateId: string): Promise<{ ok: true; articleId: string }> {
  return fetch('/api/select-title', {
    method:'POST', headers: HEADERS, body: JSON.stringify({ sessionId, candidateId })
  }).then(j<{ ok: true; articleId: string }>);
}

export async function generateOutline(sessionId: string): Promise<{ outline: any }> {
  const res = await fetch('/api/generate-outline', {
    method:'POST', headers: HEADERS, body: JSON.stringify({ sessionId })
  }).then(j<OutlineResponse>);
  return typeof (res as any).outline !== 'undefined' ? (res as { outline: any }) : { outline: res };
}

export async function generateArticle(sessionId: string, outline?: any): Promise<ArticleResponse> {
  const payload: any = { sessionId };
  if (outline) payload.outline = outline;
  return fetch('/api/generate-article', {
    method:'POST', headers: HEADERS, body: JSON.stringify(payload)
  }).then(j<ArticleResponse>);
}