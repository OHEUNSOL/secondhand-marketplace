"use client";

import { useState } from "react";

import { request } from "@/lib/api";
import type { ProductCategory, ProductCondition } from "@/lib/types";

const CATEGORIES: ProductCategory[] = ["electronics", "clothes", "home", "books", "etc"];
const CONDITIONS: ProductCondition[] = ["new", "used"];

export default function SellPage() {
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<ProductCategory>("electronics");
  const [condition, setCondition] = useState<ProductCondition>("used");
  const [imageUrls, setImageUrls] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async () => {
    setIsSubmitting(true);
    try {
      setError("");
      setMessage("");
      const urls = imageUrls
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean)
        .slice(0, 5);

      await request("/products", {
        method: "POST",
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
      setMessage("상품 등록 완료");
      setTitle("");
      setPrice("");
      setDescription("");
      setImageUrls("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "등록 실패");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="space-y-3 rounded border bg-white p-4">
      <h1 className="text-xl font-bold">판매 물품 등록</h1>
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="상품명"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        className="w-full rounded border px-2 py-2"
        placeholder="가격"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
      />
      <textarea
        className="w-full rounded border px-2 py-2"
        placeholder="상품 설명"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={5}
      />
      <div className="grid gap-2 md:grid-cols-2">
        <select className="rounded border px-2 py-2" value={category} onChange={(e) => setCategory(e.target.value as ProductCategory)}>
          {CATEGORIES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <select className="rounded border px-2 py-2" value={condition} onChange={(e) => setCondition(e.target.value as ProductCondition)}>
          {CONDITIONS.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      <textarea
        className="w-full rounded border px-2 py-2"
        placeholder="이미지 URL (줄바꿈으로 최대 5개)"
        value={imageUrls}
        onChange={(e) => setImageUrls(e.target.value)}
        rows={5}
      />
      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        className="rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
        disabled={isSubmitting}
        onClick={submit}
      >
        등록하기
      </button>
    </section>
  );
}
