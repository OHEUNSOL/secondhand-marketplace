"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { ProductDetail } from "@/lib/types";

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const load = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");
      const data = await request<ProductDetail>(`/products/${params.id}`, { auth: true });
      setProduct(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "조회 실패");
    } finally {
      setIsLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void load();
  }, [load]);

  const addCart = async () => {
    if (!product) return;
    setIsSubmitting(true);
    try {
      setError("");
      await request("/cart", {
        method: "POST",
        auth: true,
        body: { product_id: product.id, quantity: 1 },
      });
      setMessage("장바구니에 추가했습니다.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "장바구니 추가 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  const buyNow = async () => {
    if (!product) return;
    setIsSubmitting(true);
    try {
      setError("");
      await request(`/purchases/buy-now/${product.id}`, { method: "POST", auth: true });
      setMessage("구매 완료되었습니다.");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "구매 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading && !product) {
    return <p>상세 정보 불러오는 중...</p>;
  }

  if (!product) {
    return <p>{error || "로딩 중..."}</p>;
  }

  return (
    <section className="space-y-3 rounded border bg-white p-4">
      <h1 className="text-2xl font-bold">{product.title}</h1>
      <p>가격: {product.price.toLocaleString()}원</p>
      <p>카테고리: {product.category}</p>
      <p>상품상태: {product.condition}</p>
      <p>판매상태: {product.status}</p>
      <p>판매자: {product.seller_nickname}</p>
      <p className="whitespace-pre-wrap">{product.description}</p>

      {product.image_urls.length > 0 && (
        <div className="space-y-1">
          {product.image_urls.map((url) => (
            <a className="block text-sm text-blue-700 underline" key={url} href={url} target="_blank">
              {url}
            </a>
          ))}
        </div>
      )}

      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <button
          className="rounded border px-3 py-2 disabled:opacity-50"
          disabled={isSubmitting || product.status !== "on_sale"}
          onClick={addCart}
        >
          장바구니 담기
        </button>
        <button
          className="rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
          disabled={isSubmitting || product.status !== "on_sale"}
          onClick={buyNow}
        >
          바로 구매
        </button>
      </div>
    </section>
  );
}
