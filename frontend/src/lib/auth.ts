// src/lib/auth.ts

// ---- PKCE helpers ----
const PKCE_VERIFIER_KEY = "kc_pkce_verifier";

function base64UrlEncode(buf: ArrayBuffer) {
  let str = btoa(String.fromCharCode(...new Uint8Array(buf)));
  return str.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sha256(input: string) {
  const enc = new TextEncoder().encode(input);
  const hashBuf = await crypto.subtle.digest("SHA-256", enc);
  return base64UrlEncode(hashBuf);
}

function randomVerifier(length = 64) {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~";
  let out = "";
  const rnd = crypto.getRandomValues(new Uint8Array(length));
  for (let i = 0; i < length; i++) out += chars[rnd[i] % chars.length];
  return out;
}

async function ensurePkce() {
  let verifier = sessionStorage.getItem(PKCE_VERIFIER_KEY);
  if (!verifier) {
    verifier = randomVerifier(64);
    sessionStorage.setItem(PKCE_VERIFIER_KEY, verifier);
  }
  const challenge = await sha256(verifier);
  return { verifier, challenge };
}

// ---- URL builders ----
export async function kcAuthUrl(params: Record<string, string>) {
  const base = import.meta.env.VITE_KC_BASE_URL;
  const realm = import.meta.env.VITE_KC_REALM;
  const clientId = import.meta.env.VITE_KC_CLIENT_ID;
  const redirect = import.meta.env.VITE_KC_REDIRECT;

  const { challenge } = await ensurePkce();

  const u = new URL(`${base}/realms/${realm}/protocol/openid-connect/auth`);
  u.searchParams.set("client_id", clientId);
  u.searchParams.set("response_type", "code");
  u.searchParams.set("scope", "openid profile email");
  u.searchParams.set("redirect_uri", redirect);

  // PKCE
  u.searchParams.set("code_challenge", challenge);
  u.searchParams.set("code_challenge_method", "S256");

  Object.entries(params).forEach(([k, v]) => u.searchParams.set(k, v));
  return u.toString();
}

export const kcRegisterUrl = async () => kcAuthUrl({ kc_action: "register" });
export const kcLoginUrl    = async () => kcAuthUrl({});

export function kcLogoutUrl() {
  const base = import.meta.env.VITE_KC_BASE_URL;
  const realm = import.meta.env.VITE_KC_REALM;
  const redirect = import.meta.env.VITE_KC_REDIRECT;
  const u = new URL(`${base}/realms/${realm}/protocol/openid-connect/logout`);
  u.searchParams.set("post_logout_redirect_uri", redirect);
  return u.toString();
}
