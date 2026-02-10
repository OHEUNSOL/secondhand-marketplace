export type UserRole = "user" | "admin";

export type User = {
  id: number;
  email: string;
  nickname: string;
  role: UserRole;
};

export type ProductStatus = "on_sale" | "reserved" | "sold";
export type ProductCategory =
  | "electronics"
  | "clothes"
  | "home"
  | "books"
  | "etc";
export type ProductCondition = "new" | "used";

export type ProductSummary = {
  id: number;
  title: string;
  price: number;
  category: ProductCategory;
  condition: ProductCondition;
  status: ProductStatus;
  is_blinded: boolean;
  seller_nickname: string;
  thumbnail_url: string | null;
  created_at: string;
};

export type ProductListResponse = {
  total: number;
  page: number;
  page_size: number;
  items: ProductSummary[];
};

export type ProductDetail = {
  id: number;
  title: string;
  price: number;
  description: string;
  category: ProductCategory;
  condition: ProductCondition;
  status: ProductStatus;
  is_blinded: boolean;
  blind_reason: string | null;
  seller_id: number;
  seller_nickname: string;
  image_urls: string[];
  created_at: string;
  updated_at: string;
};

export type CartItem = {
  id: number;
  product_id: number;
  title: string;
  status: ProductStatus;
  price: number;
  quantity: number;
  selected: boolean;
  subtotal: number;
};

export type CartResponse = {
  items: CartItem[];
  total_amount: number;
};

export type PurchaseItem = {
  id: number;
  product_id: number;
  product_title: string;
  quantity: number;
  amount: number;
  purchased_at: string;
};

export type PurchaseResponse = {
  purchases: PurchaseItem[];
};
