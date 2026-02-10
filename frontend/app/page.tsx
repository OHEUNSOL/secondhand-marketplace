"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { request } from "@/lib/api";
import type { ProductCategory, ProductListResponse } from "@/lib/types";

const CATEGORIES: ProductCategory[] = ["electronics", "clothes", "home", "books", "etc"];

export default function Home() {
  const [items, setItems] = useState<ProductListResponse | null>(null);
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState<string>("");
  const [sort, setSort] = useState("latest");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");
      const query = new URLSearchParams({
        page: String(page),
        page_size: "10",
        sort,
      });
      if (keyword.trim()) query.set("keyword", keyword.trim());
      if (category) query.set("category", category);
      const data = await request<ProductListResponse>(`/products?${query.toString()}`, {
        auth: true,
      });
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "목록 조회 실패");
    } finally {
      setIsLoading(false);
    }
  }, [page, sort, keyword, category]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">상품 목록</h1>

      <div className="grid gap-2 rounded border bg-white p-3 md:grid-cols-5">
        <input
          className="rounded border px-2 py-2 md:col-span-2"
          placeholder="키워드 검색"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
        <select
          className="rounded border px-2 py-2"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">전체 카테고리</option>
          {CATEGORIES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <select className="rounded border px-2 py-2" value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="latest">최신순</option>
          <option value="price_asc">가격 낮은순</option>
          <option value="price_desc">가격 높은순</option>
        </select>
        <button
          className="rounded bg-slate-900 px-3 py-2 text-white disabled:opacity-50"
          disabled={isLoading}
          onClick={() => load()}
        >
          검색
        </button>
      </div>

      {isLoading && <p className="rounded bg-slate-100 p-2 text-sm text-slate-700">목록 로딩 중...</p>}
      {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}

      <div className="space-y-2">
        {items?.items.map((product) => (
          <Link
            key={product.id}
            href={`/products/${product.id}`}
            className="block rounded border bg-white p-3 hover:border-slate-500"
          >
            <div className="flex items-center justify-between">
              <p className="font-semibold">{product.title}</p>
              <p className="text-sm text-slate-600">{product.status}</p>
            </div>
            <p className="mt-1 text-sm text-slate-700">판매자: {product.seller_nickname}</p>
            <p className="mt-1 text-sm text-slate-800">{product.price.toLocaleString()}원</p>
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <button
          className="rounded border px-3 py-1 disabled:opacity-40"
          disabled={page <= 1}
          onClick={() => setPage((prev) => prev - 1)}
        >
          이전
        </button>
        <p className="text-sm">페이지 {page}</p>
        <button
          className="rounded border px-3 py-1 disabled:opacity-40"
          disabled={!items || items.items.length < 10}
          onClick={() => setPage((prev) => prev + 1)}
        >
          다음
        </button>
      </div>
    </section>
  );
}
