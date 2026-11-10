/**
 * Authentication service.
 *
 * The FastAPI backend does not expose auth endpoints yet, so accounts are
 * stored in this browser (localStorage) with salted SHA-256 password hashes.
 * Every function is async and returns plain data, so swapping this module for
 * real HTTP calls (POST /auth/signup, POST /auth/login) requires no UI changes.
 */

export type User = {
  id: string;
  name: string;
  email: string;
  storeName: string;
  createdAt: string;
};

type StoredUser = User & { salt: string; passwordHash: string };

export type Session = { user: User; token: string; expiresAt: number };

export type SignupInput = {
  name: string;
  email: string;
  storeName: string;
  password: string;
};

export type LoginInput = { email: string; password: string; remember: boolean };

export class AuthError extends Error {
  constructor(
    message: string,
    readonly field?: "email" | "password" | "name" | "storeName",
  ) {
    super(message);
    this.name = "AuthError";
  }
}

const USERS_KEY = "shelf.users.v1";
const SESSION_KEY = "shelf.session.v1";
const DAY = 24 * 60 * 60 * 1000;

function readUsers(): StoredUser[] {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) ?? "[]") as StoredUser[];
  } catch {
    return [];
  }
}

function writeUsers(users: StoredUser[]) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function toHex(buffer: ArrayBuffer | Uint8Array) {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function randomHex(bytes = 16) {
  return toHex(crypto.getRandomValues(new Uint8Array(bytes)));
}

async function hashPassword(password: string, salt: string) {
  const data = new TextEncoder().encode(`${salt}:${password}`);
  return toHex(await crypto.subtle.digest("SHA-256", data));
}

function publicUser({ salt: _salt, passwordHash: _hash, ...user }: StoredUser): User {
  return user;
}

function persistSession(user: User, remember: boolean): Session {
  const session: Session = {
    user,
    token: randomHex(24),
    expiresAt: Date.now() + (remember ? 30 * DAY : DAY),
  };
  const storage = remember ? localStorage : sessionStorage;
  storage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

/** Small artificial latency so loading states are perceivable and honest. */
const settle = (ms = 650) => new Promise((resolve) => setTimeout(resolve, ms));

export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function hasAccounts() {
  return readUsers().length > 0;
}

export function getSession(): Session | null {
  for (const storage of [sessionStorage, localStorage]) {
    const raw = storage.getItem(SESSION_KEY);
    if (!raw) continue;
    try {
      const session = JSON.parse(raw) as Session;
      if (session.expiresAt > Date.now()) return session;
      storage.removeItem(SESSION_KEY);
    } catch {
      storage.removeItem(SESSION_KEY);
    }
  }
  return null;
}

export async function signup(input: SignupInput): Promise<Session> {
  await settle();
  const email = input.email.trim().toLowerCase();
  if (!EMAIL_PATTERN.test(email)) {
    throw new AuthError("Digite um e-mail válido, como voce@loja.com.", "email");
  }
  if (input.password.length < 8) {
    throw new AuthError("A senha precisa ter pelo menos 8 caracteres.", "password");
  }

  const users = readUsers();
  if (users.some((user) => user.email === email)) {
    throw new AuthError("Já existe uma conta com este e-mail. Entre com ela.", "email");
  }

  const salt = randomHex();
  const stored: StoredUser = {
    id: crypto.randomUUID(),
    name: input.name.trim(),
    email,
    storeName: input.storeName.trim(),
    createdAt: new Date().toISOString(),
    salt,
    passwordHash: await hashPassword(input.password, salt),
  };
  writeUsers([...users, stored]);
  return persistSession(publicUser(stored), true);
}

export async function login(input: LoginInput): Promise<Session> {
  await settle();
  const email = input.email.trim().toLowerCase();
  const user = readUsers().find((candidate) => candidate.email === email);
  const hash = user ? await hashPassword(input.password, user.salt) : "";

  if (!user || hash !== user.passwordHash) {
    throw new AuthError("E-mail ou senha incorretos. Confira e tente de novo.", "password");
  }
  return persistSession(publicUser(user), input.remember);
}

export function logout() {
  localStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SESSION_KEY);
}

export type PasswordStrength = { score: 0 | 1 | 2 | 3 | 4; label: string };

export function measurePassword(password: string): PasswordStrength {
  if (!password) return { score: 0, label: "" };
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password) && /[^A-Za-z0-9]/.test(password)) score++;
  const clamped = Math.max(1, Math.min(4, score)) as 1 | 2 | 3 | 4;
  const labels = { 1: "Fraca", 2: "Razoável", 3: "Boa", 4: "Forte" } as const;
  return { score: clamped, label: labels[clamped] };
}
