"use client";

import { useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { PurchaseResponse } from "@/lib/types";

export default function MyPage() {
  const [purchases, setPurchases] = useState<PurchaseResponse | null>(null);
  const [sales, setSales] = useState<PurchaseResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const load = async () => {
    setIsLoading(true);
    try {
      setError("");
      const [purchaseData, salesData] = await Promise.all([
        request<PurchaseResponse>("/purchases/me", { auth: true }),
        request<PurchaseResponse>("/purchases/sales/me", { auth: true }),
      ]);
      setPurchases(purchaseData);
      setSales(salesData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "마이페이지 조회 실패");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-bold">마이페이지</h1>
      {isLoading && <p className="text-sm text-slate-600">내역 불러오는 중...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="rounded border bg-white p-3">
        <h2 className="mb-2 font-semibold">구매 내역</h2>
        <ul className="space-y-1 text-sm">
          {purchases?.purchases.map((item) => (
            <li key={item.id}>
              {item.product_title} / 수량 {item.quantity} / {item.amount.toLocaleString()}원
            </li>
          ))}
        </ul>
      </div>

      <div className="rounded border bg-white p-3">
        <h2 className="mb-2 font-semibold">판매 내역</h2>
        <ul className="space-y-1 text-sm">
          {sales?.purchases.map((item) => (
            <li key={item.id}>
              {item.product_title} / 수량 {item.quantity} / {item.amount.toLocaleString()}원
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
