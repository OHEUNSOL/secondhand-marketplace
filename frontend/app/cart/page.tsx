"use client";

import { useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { CartResponse } from "@/lib/types";

function recalculateTotal(cart: CartResponse): CartResponse {
  const total = cart.items
    .filter((item) => item.selected)
    .reduce((sum, item) => sum + item.price * item.quantity, 0);
  return { ...cart, total_amount: total };
}

export default function CartPage() {
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);

  const load = async () => {
    setIsLoading(true);
    try {
      setError("");
      const data = await request<CartResponse>("/cart", { auth: true });
      setCart(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "장바구니 조회 실패");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const updateItem = async (itemId: number, payload: { quantity?: number; selected?: boolean }) => {
    if (!cart) return;
    const previous = cart;
    const next = recalculateTotal({
      ...cart,
      items: cart.items.map((item) => {
        if (item.id !== itemId) return item;
        return {
          ...item,
          quantity: payload.quantity ?? item.quantity,
          selected: payload.selected ?? item.selected,
        };
      }),
    });

    setCart(next);
    setIsMutating(true);
    try {
      setError("");
      await request(`/cart/${itemId}`, { method: "PATCH", auth: true, body: payload });
    } catch (e) {
      setCart(previous);
      setError(e instanceof Error ? e.message : "장바구니 수정 실패");
    } finally {
      setIsMutating(false);
    }
  };

  const deleteItem = async (itemId: number) => {
    if (!cart) return;
    const previous = cart;
    const next = recalculateTotal({
      ...cart,
      items: cart.items.filter((item) => item.id !== itemId),
    });

    setCart(next);
    setIsMutating(true);
    try {
      setError("");
      await request(`/cart/${itemId}`, { method: "DELETE", auth: true });
    } catch (e) {
      setCart(previous);
      setError(e instanceof Error ? e.message : "삭제 실패");
    } finally {
      setIsMutating(false);
    }
  };

  const checkout = async () => {
    if (!cart) return;
    const previous = cart;
    const next = recalculateTotal({
      ...cart,
      items: cart.items.filter((item) => !item.selected),
    });

    setCart(next);
    setIsMutating(true);
    try {
      setError("");
      await request("/purchases/checkout-selected", { method: "POST", auth: true });
      setMessage("선택 구매 완료");
    } catch (e) {
      setCart(previous);
      setError(e instanceof Error ? e.message : "구매 실패");
    } finally {
      setIsMutating(false);
    }
  };

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-bold">장바구니</h1>
      {isLoading && <p className="text-sm text-slate-600">장바구니 불러오는 중...</p>}
      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="space-y-2">
        {cart?.items.map((item) => (
          <div key={item.id} className="rounded border bg-white p-3">
            <div className="flex items-center justify-between">
              <p className="font-semibold">{item.title}</p>
              <button
                className="text-sm text-red-700 disabled:opacity-50"
                disabled={isMutating}
                onClick={() => deleteItem(item.id)}
              >
                삭제
              </button>
            </div>
            <p className="text-sm">가격: {item.price.toLocaleString()}원</p>
            <p className="text-sm">상태: {item.status}</p>
            <div className="mt-2 flex items-center gap-2">
              <label className="text-sm">
                <input
                  type="checkbox"
                  checked={item.selected}
                  disabled={isMutating}
                  onChange={(e) => updateItem(item.id, { selected: e.target.checked })}
                />{" "}
                선택 구매
              </label>
              <p className="text-sm text-slate-600">수량: 1 (중고 단일 상품)</p>
            </div>
          </div>
        ))}
      </div>
      <div className="rounded border bg-white p-3">
        <p className="font-semibold">선택 합계: {(cart?.total_amount ?? 0).toLocaleString()}원</p>
        <button
          className="mt-2 rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
          disabled={isMutating || isLoading || !cart?.items.some((item) => item.selected)}
          onClick={checkout}
        >
          선택 상품 구매
        </button>
      </div>
    </section>
  );
}
