"use client";

import Link from "next/link";
import { useState } from "react";

import { request } from "@/lib/api";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async () => {
    setIsSubmitting(true);
    try {
      setError("");
      setMessage("");
      await request("/auth/signup", {
        method: "POST",
        body: { email, nickname, password },
      });
      setMessage("회원가입 완료. 로그인 해주세요.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "회원가입 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="mx-auto max-w-md space-y-3 rounded border bg-white p-4">
      <h1 className="text-xl font-bold">회원가입</h1>
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="닉네임"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
      />
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="비밀번호 (8자 이상)"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        className="w-full rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
        disabled={isSubmitting}
        onClick={submit}
      >
        회원가입
      </button>
      <Link className="text-sm text-slate-700 underline" href="/login">
        로그인 하러가기
      </Link>
    </section>
  );
}
