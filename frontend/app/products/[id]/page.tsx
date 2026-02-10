"use client";

import Image from "next/image";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { ProductCategory, ProductCondition, ProductDetail, User } from "@/lib/types";

const CATEGORIES: ProductCategory[] = ["electronics", "clothes", "home", "books", "etc"];
const CONDITIONS: ProductCondition[] = ["new", "used"];

function ImagePreview({ src }: { src: string }) {
  const [isBroken, setIsBroken] = useState(false);

  if (isBroken) {
    return <div className="flex h-48 items-center justify-center rounded border bg-slate-100 text-sm text-slate-500">이미지를 불러올 수 없습니다.</div>;
  }

  return (
    <div className="overflow-hidden rounded border bg-white">
      <Image
        src={src}
        alt="상품 이미지"
        width={960}
        height={720}
        className="h-48 w-full object-cover"
        unoptimized
        onError={() => setIsBroken(true)}
      />
    </div>
  );
}

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<ProductCategory>("electronics");
  const [condition, setCondition] = useState<ProductCondition>("used");
  const [imageUrls, setImageUrls] = useState("");

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

  useEffect(() => {
    void (async () => {
      try {
        const me = await request<User>("/auth/me", { auth: true });
        setCurrentUser(me);
      } catch {
        setCurrentUser(null);
      }
    })();
  }, []);

  useEffect(() => {
    if (!product) return;
    setTitle(product.title);
    setPrice(String(product.price));
    setDescription(product.description);
    setCategory(product.category);
    setCondition(product.condition);
    setImageUrls(product.image_urls.join("\n"));
  }, [product]);

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

  const updateProduct = async () => {
    if (!product) return;
    setIsSubmitting(true);
    try {
      setError("");
      setMessage("");
      const urls = imageUrls
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean)
        .slice(0, 5);
      const updated = await request<ProductDetail>(`/products/${product.id}`, {
        method: "PATCH",
        auth: true,
        body: {
          title,
          price: Number(price),
          description,
          category,
          condition,
          image_urls: urls,
        },
      });
      setProduct(updated);
      setIsEditing(false);
      setMessage("상품 정보를 수정했습니다.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "수정 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  const deleteProduct = async () => {
    if (!product) return;
    const ok = window.confirm("이 상품을 삭제할까요?");
    if (!ok) return;
    setIsSubmitting(true);
    try {
      setError("");
      await request(`/products/${product.id}`, { method: "DELETE", auth: true });
      window.location.href = "/";
    } catch (e) {
      setError(e instanceof Error ? e.message : "삭제 실패");
      setIsSubmitting(false);
    }
  };

  if (isLoading && !product) {
    return <p>상세 정보 불러오는 중...</p>;
  }

  if (!product) {
    return <p>{error || "로딩 중..."}</p>;
  }

  const isSeller = currentUser?.id === product.seller_id;

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
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3">
          {product.image_urls.map((url) => (
            <ImagePreview key={url} src={url} />
          ))}
        </div>
      )}

      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {isSeller && (
        <div className="space-y-2 rounded border bg-slate-50 p-3">
          <div className="flex flex-wrap gap-2">
            <button
              className="rounded border px-3 py-2 disabled:opacity-50"
              disabled={isSubmitting}
              onClick={() => setIsEditing((prev) => !prev)}
            >
              {isEditing ? "수정 취소" : "상품 수정"}
            </button>
            <button
              className="rounded bg-red-600 px-3 py-2 text-white disabled:opacity-50"
              disabled={isSubmitting || product.status === "sold"}
              onClick={deleteProduct}
            >
              상품 삭제
            </button>
          </div>

          {isEditing && (
            <div className="space-y-2">
              <input
                className="w-full rounded border px-2 py-2"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <input
                className="w-full rounded border px-2 py-2"
                type="number"
                min={1}
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
              <textarea
                className="w-full rounded border px-2 py-2"
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              <div className="grid gap-2 md:grid-cols-2">
                <select
                  className="rounded border px-2 py-2"
                  value={category}
                  onChange={(e) => setCategory(e.target.value as ProductCategory)}
                >
                  {CATEGORIES.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
                <select
                  className="rounded border px-2 py-2"
                  value={condition}
                  onChange={(e) => setCondition(e.target.value as ProductCondition)}
                >
                  {CONDITIONS.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
              <textarea
                className="w-full rounded border px-2 py-2"
                rows={4}
                placeholder="이미지 URL (줄바꿈으로 최대 5개)"
                value={imageUrls}
                onChange={(e) => setImageUrls(e.target.value)}
              />
              <button
                className="rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
                disabled={isSubmitting}
                onClick={updateProduct}
              >
                수정 저장
              </button>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2">
        <button
          className="rounded border px-3 py-2 disabled:opacity-50"
          disabled={isSubmitting || product.status !== "on_sale" || isSeller}
          onClick={addCart}
        >
          장바구니 담기
        </button>
        <button
          className="rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
          disabled={isSubmitting || product.status !== "on_sale" || isSeller}
          onClick={buyNow}
        >
          바로 구매
        </button>
      </div>
    </section>
  );
}
