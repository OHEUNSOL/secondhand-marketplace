"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { clearToken, getToken } from "@/lib/auth";
import { request } from "@/lib/api";
import type { User } from "@/lib/types";

export default function Header() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }

    void (async () => {
      try {
        const me = await request<User>("/auth/me", { auth: true });
        setUser(me);
      } catch {
        clearToken();
      }
    })();
  }, []);

  const logout = () => {
    clearToken();
    window.location.href = "/";
  };

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4">
        <Link className="text-xl font-bold text-slate-900" href="/">
          Secondhand
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link className="hover:underline" href="/sell">
            판매등록
          </Link>
          <Link className="hover:underline" href="/cart">
            장바구니
          </Link>
          <Link className="hover:underline" href="/mypage">
            마이페이지
          </Link>
          {user?.role === "admin" && (
            <Link className="hover:underline" href="/admin">
              관리자
            </Link>
          )}
          {!user ? (
            <>
              <Link className="hover:underline" href="/login">
                로그인
              </Link>
              <Link className="hover:underline" href="/signup">
                회원가입
              </Link>
            </>
          ) : (
            <button className="cursor-pointer rounded bg-slate-900 px-2 py-1 text-white" onClick={logout}>
              로그아웃 ({user.nickname})
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}
