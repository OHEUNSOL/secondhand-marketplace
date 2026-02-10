"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { User } from "@/lib/types";

type AdminProduct = {
  id: number;
  title: string;
  status: string;
  is_blinded: boolean;
  blind_reason: string | null;
  seller_nickname: string;
};

export default function AdminPage() {
  const router = useRouter();
  const [items, setItems] = useState<AdminProduct[]>([]);
  const [reasonById, setReasonById] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [isAccessChecking, setIsAccessChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);

  const load = async () => {
    setIsLoading(true);
    try {
      setError("");
      const data = await request<{ items: AdminProduct[] }>("/admin/products", { auth: true });
      setItems(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "관리자 조회 실패");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void (async () => {
      try {
        setError("");
        const me = await request<User>("/auth/me", { auth: true });
        if (me.role !== "admin") {
          router.replace("/");
          return;
        }
        setIsAdmin(true);
      } catch {
        router.replace("/login");
      } finally {
        setIsAccessChecking(false);
      }
    })();
  }, [router]);

  useEffect(() => {
    if (isAdmin) {
      void load();
    }
  }, [isAdmin]);

  if (isAccessChecking) {
    return <p className="text-sm text-slate-600">권한 확인 중...</p>;
  }

  if (!isAdmin) {
    return null;
  }

  const blind = async (id: number) => {
    setIsMutating(true);
    try {
      setError("");
      await request(`/admin/products/${id}/blind`, {
        method: "POST",
        auth: true,
        body: { reason: reasonById[id] || "관리자 판단으로 판매 중지" },
      });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "블라인드 처리 실패");
    } finally {
      setIsMutating(false);
    }
  };

  const unblind = async (id: number) => {
    setIsMutating(true);
    try {
      setError("");
      await request(`/admin/products/${id}/unblind`, { method: "POST", auth: true });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "블라인드 해제 실패");
    } finally {
      setIsMutating(false);
    }
  };

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-bold">관리자 상품 관리</h1>
      {isLoading && <p className="text-sm text-slate-600">관리자 목록 로딩 중...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {items.map((item) => (
        <div key={item.id} className="rounded border bg-white p-3">
          <p className="font-semibold">{item.title}</p>
          <p className="text-sm">판매자: {item.seller_nickname}</p>
          <p className="text-sm">상태: {item.status}</p>
          <p className="text-sm">블라인드: {item.is_blinded ? `Y (${item.blind_reason})` : "N"}</p>
          <div className="mt-2 flex gap-2">
            <input
              className="flex-1 rounded border px-2 py-1"
              placeholder="블라인드 사유"
              value={reasonById[item.id] || ""}
              disabled={isMutating}
              onChange={(e) =>
                setReasonById((prev) => ({
                  ...prev,
                  [item.id]: e.target.value,
                }))
              }
            />
            <button
              className="rounded border px-2 py-1 disabled:opacity-50"
              disabled={isMutating}
              onClick={() => blind(item.id)}
            >
              {isMutating ? "처리 중..." : "판매중지"}
            </button>
            <button
              className="rounded bg-slate-900 px-2 py-1 text-white disabled:opacity-50"
              disabled={isMutating}
              onClick={() => unblind(item.id)}
            >
              블라인드 해제
            </button>
          </div>
        </div>
      ))}
    </section>
  );
}
