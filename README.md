# Secondhand Marketplace

중고 물품 등록, 탐색, 장바구니, 구매, 관리자 블라인드 처리를 지원하는 풀스택 웹 애플리케이션입니다.

## 프로젝트 소개
- 사용자: 회원가입/로그인 후 상품 등록, 탐색, 구매 가능
- 관리자: 전체 상품 조회, 판매 중지(블라인드) 및 해제 가능
- 결제 연동 없이 구매 완료 시점에 거래 확정 처리

## 기술 스택
- Frontend: Next.js (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- Auth: JWT Access Token + bcrypt
- Infra(Local): Docker Compose (PostgreSQL)

## 기술 스택 선정 시 고려한 점
- Next.js App Router
  - 이유: 페이지/라우트 기반 UI 구성 및 클라이언트 상태 관리가 명확해 기능 단위 개발에 유리.
  - 고려: 초기에는 Server Component/Client Component 경계가 혼동될 수 있어, 상태와 이벤트가 있는 화면은 Client Component로 명확히 분리.
- FastAPI
  - 이유: 타입 힌트 기반 API 개발 속도가 빠르고, `Depends`를 활용한 인증/권한 분리가 간결함.
  - 고려: 예외 처리 로직이 라우터별로 흩어질 수 있어 전역 예외 핸들러로 표준화.
- SQLAlchemy
  - 이유: 레이어 분리(router/service/repository) 구조에서 ORM 모델과 비즈니스 로직 분리에 적합.
  - 고려: 동시성 이슈 방지를 위해 구매 로직을 원자적 업데이트(조건부 상태 전환)로 설계.
- PostgreSQL
  - 이유: 관계형 데이터(유저-상품-장바구니-구매내역) 관리에 적합.
  - 고려: 로컬 실행 편의성을 위해 Docker Compose로 실행 절차 단순화.

## 아키텍처 설명

### 통신 구조
- `Next.js Frontend` -> `FastAPI Backend` -> `PostgreSQL`

### 인증 흐름
1. 사용자가 `/auth/login`으로 이메일/비밀번호 전송
2. FastAPI가 bcrypt 검증 후 JWT Access Token 발급
3. 프론트가 토큰을 `localStorage`에 저장
4. 보호 API 호출 시 `Authorization: Bearer <token>` 헤더 전송
5. 백엔드 `Depends`가 토큰 검증 후 사용자/관리자 권한 확인

### 간단 다이어그램
```text
[Browser / Next.js]
   |  HTTP(JSON) + Authorization Bearer JWT
   v
[FastAPI Router]
   -> [Service Layer]
   -> [Repository Layer]
   -> [SQLAlchemy ORM]
   v
[PostgreSQL]
```

## 디렉토리 구조
- `frontend/`: Next.js UI
- `backend/app/routers`: API 엔드포인트
- `backend/app/services`: 비즈니스 로직
- `backend/app/repositories`: DB 접근 레이어
- `backend/app/models`: SQLAlchemy 모델
- `backend/app/schemas`: 요청/응답 스키마
- `backend/tests`: 백엔드 테스트 코드

## 로컬 실행 방법

### 0) 사전 준비
- Node.js 20+
- Python 3.11+
- Docker / Docker Compose

### 1) PostgreSQL 실행
```bash
docker compose up -d
```

### 2) 백엔드 실행
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3) 프론트엔드 실행
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

### 4) 접속 주소
- Frontend: `http://localhost:3000`
- Backend Swagger: `http://localhost:8000/docs`

### 환경 변수

#### backend/.env
- `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/secondhand_marketplace`
- `JWT_SECRET_KEY=replace-with-strong-secret`
- `JWT_EXPIRE_MINUTES=120`
- `CORS_ORIGINS=http://localhost:3000`
- `ADMIN_EMAIL=admin@example.com`
- `ADMIN_PASSWORD=Admin1234!`
- `ADMIN_NICKNAME=market-admin`

#### frontend/.env.local
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

### 테스트 실행 방법
```bash
cd backend
source .venv/bin/activate
python -m unittest -v tests/test_requirements_unittest.py tests/test_error_format_unittest.py
```

## 배포 정보
- 현재는 로컬 실행 기준 제출입니다. (배포 URL 없음)

## 테스트 계정 정보
- 관리자(시드)
  - email: `admin@example.com`
  - password: `Admin1234!`
- 일반 사용자는 회원가입 화면에서 생성 가능

## 구현한 기능 체크리스트
- [x] 회원가입/로그인 (이메일+비밀번호)
- [x] bcrypt 해싱 저장 + JWT 발급/검증
- [x] Refresh Token 재발급(`/auth/refresh`) 및 프론트 자동 재시도
- [x] 관리자 시드 계정
- [x] 상품 등록/수정/삭제
- [x] 상품 목록/검색/카테고리/정렬/페이지네이션
- [x] 상품 상세/장바구니 담기/바로 구매
- [x] 장바구니 수량 변경/삭제/선택 구매/총액
- [x] 구매 완료 처리(상품 판매완료 + 구매내역 저장)
- [x] 마이페이지 구매/판매 내역
- [x] 관리자 상품 조회/블라인드/해제
- [x] API 에러 응답 표준화
- [x] 로딩/에러 상태 UI
- [x] 장바구니 낙관적 업데이트
- [x] 상품 동시 구매 방지(원자적 상태 전환)
- [x] 테스트 코드 작성 및 실행 검증

## 시간 부족으로 구현하지 못한 부분 및 계획
- Refresh Token 미구현
  - 계획: `refresh_tokens` 저장소(토큰 회전/폐기) 도입 후 `/auth/refresh` 엔드포인트 추가
- 실제 파일 업로드(이미지 저장소) 미구현
  - 계획: S3 또는 로컬 스토리지 업로드 API 추가, URL 입력 방식과 병행 지원
- 프론트 E2E 테스트 미구현
  - 계획: Playwright로 로그인 -> 상품 등록 -> 장바구니 -> 구매 -> 관리자 블라인드 흐름 자동화

## AI 활용 보고서
- 별도 문서: `AI_REPORT.md`
