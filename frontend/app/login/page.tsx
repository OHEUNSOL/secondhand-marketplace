"use client";

import Link from "next/link";
import { useState } from "react";

import { setTokens } from "@/lib/auth";
import { request } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async () => {
    setIsSubmitting(true);
    try {
      setError("");
      const data = await request<{ access_token: string; refresh_token: string }>(
        "/auth/login",
        {
          method: "POST",
          body: { email, password },
        },
      );
      setTokens(data.access_token, data.refresh_token);
      window.location.href = "/";
    } catch (e) {
      setError(e instanceof Error ? e.message : "로그인 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="mx-auto max-w-md space-y-3 rounded border bg-white p-4">
      <h1 className="text-xl font-bold">로그인</h1>
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="비밀번호"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        className="w-full rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
        disabled={isSubmitting}
        onClick={submit}
      >
        로그인
      </button>
      <Link className="text-sm text-slate-700 underline" href="/signup">
        회원가입 하러가기
      </Link>
    </section>
  );
}
