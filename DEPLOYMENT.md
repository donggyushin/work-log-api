# Deployment Guide - Railway

이 문서는 Railway 플랫폼에 dailylog-api를 배포하는 방법을 설명합니다.

## 목차
1. [사전 준비](#사전-준비)
2. [Railway 프로젝트 생성](#railway-프로젝트-생성)
3. [MongoDB 배포](#mongodb-배포)
4. [API 서버 배포](#api-서버-배포)
5. [환경 변수 설정](#환경-변수-설정)
6. [배포 확인](#배포-확인)
7. [트러블슈팅](#트러블슈팅)

## 사전 준비

### 1. Railway 계정 생성
- https://railway.app 접속
- GitHub 계정으로 로그인

### 2. MongoDB Atlas 계정 생성 (권장)
- https://www.mongodb.com/cloud/atlas/register 접속
- Google 또는 이메일로 가입
- **무료 M0 티어** 선택 (512MB 영구 무료)

### 3. 필요한 외부 서비스 API 키 준비
다음 서비스들의 API 키가 필요합니다:
- ✅ **Resend** (이메일 인증): https://resend.com
- ✅ **Anthropic** (Claude AI): https://console.anthropic.com
- ✅ **OpenAI** (DALL-E 3): https://platform.openai.com
- ✅ **Cloudflare R2** (이미지 저장소): https://dash.cloudflare.com

## Railway 프로젝트 생성

### 1. 새 프로젝트 생성
```bash
# Railway CLI 설치 (선택사항)
npm install -g @railway/cli

# 로그인
railway login

# 새 프로젝트 생성
railway init
```

또는 Railway 웹 대시보드에서:
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 본 repository 선택

## MongoDB Atlas 설정 (강력 권장) 🌟

### 왜 Atlas를 권장하는가?

| 항목 | MongoDB Atlas | Railway MongoDB |
|------|---------------|-----------------|
| **무료 티어** | ✅ 512MB 영구 무료 | ❌ Volume 비용 별도 |
| **자동 백업** | ✅ 7일 자동 백업 | ❌ 직접 관리 필요 |
| **고가용성** | ✅ 3개 리전 복제 | ❌ 단일 인스턴스 |
| **모니터링** | ✅ 실시간 성능 모니터링 | ❌ 제한적 |
| **확장성** | ✅ 클릭으로 업그레이드 | ❌ 복잡한 마이그레이션 |
| **데이터 용량** | 512MB = 약 1,500명 사용자 | Volume 비용 증가 |

### Atlas 설정 단계

#### 1. 클러스터 생성

1. https://www.mongodb.com/cloud/atlas/register 접속 후 로그인
2. **"Build a Database"** 클릭
3. 배포 옵션 선택:
   - **M0 (Free)** 선택 ✅
   - Provider: **AWS** (권장)
   - Region: **Seoul (ap-northeast-2)** 선택
   - Cluster Name: `dailylog-cluster` (자유롭게 변경 가능)
4. **"Create"** 클릭

⏱️ 클러스터 생성까지 약 3-5분 소요

#### 2. 보안 설정

**A. 데이터베이스 사용자 생성:**

1. 좌측 메뉴 **"Security"** → **"Database Access"** 클릭
2. **"Add New Database User"** 클릭
3. 설정:
   - Authentication Method: **Password**
   - Username: `dailylog-admin` (원하는 이름)
   - Password: **강력한 비밀번호 생성**
     ```bash
     # 안전한 비밀번호 생성 예시
     openssl rand -base64 32
     ```
     ⚠️ **이 비밀번호를 반드시 저장하세요!**
   - Database User Privileges: **Read and write to any database**
4. **"Add User"** 클릭

**B. 네트워크 접근 허용:**

1. 좌측 메뉴 **"Security"** → **"Network Access"** 클릭
2. **"Add IP Address"** 클릭
3. **"Allow Access from Anywhere"** 선택
   - IP Address: `0.0.0.0/0` (자동 입력됨)
   - ℹ️ Railway 서버 IP가 동적이므로 필요합니다
   - 🔒 사용자명/비밀번호로 보안이 유지됩니다
4. **"Confirm"** 클릭

#### 3. 연결 문자열 가져오기

1. 좌측 메뉴 **"Database"** 탭으로 이동
2. 클러스터에서 **"Connect"** 버튼 클릭
3. **"Drivers"** 선택
4. 설정:
   - Driver: **Python**
   - Version: **3.12 or later**
5. **연결 문자열 복사** (Step 3):
   ```
   mongodb+srv://<username>:<password>@dailylog-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **실제 값으로 변경**:
   ```
   # 예시 (실제 값으로 변경하세요)
   mongodb+srv://dailylog-admin:your_password_here@dailylog-cluster.abc123.mongodb.net/?retryWrites=true&w=majority
   ```

   ⚠️ `<username>`과 `<password>`를 2단계에서 생성한 실제 값으로 변경!

7. **데이터베이스 이름 추가** (중요!):
   ```
   # /dailylog 추가
   mongodb+srv://dailylog-admin:your_password_here@dailylog-cluster.abc123.mongodb.net/dailylog?retryWrites=true&w=majority
   ```

✅ **이 최종 연결 문자열을 Railway 환경 변수에 사용합니다!**

#### 4. 연결 테스트 (선택사항)

로컬에서 테스트:
```bash
# MongoDB Compass 설치 (GUI 도구)
# https://www.mongodb.com/products/compass

# 또는 Python으로 테스트
pip install pymongo
python -c "from pymongo import MongoClient; client = MongoClient('your_connection_string'); print(client.server_info())"
```

## API 서버 배포

### 1. GitHub Repository 연결
1. Railway 프로젝트에서 "+ New" 클릭
2. "GitHub Repo" 선택
3. 본 repository (`dailylog-api`) 선택

Railway가 자동으로 Dockerfile을 감지하고 빌드합니다.

### 2. 자동 배포 확인
- Railway는 `main` 브랜치에 push할 때마다 자동으로 재배포됩니다
- 빌드 로그는 "Deployments" 탭에서 확인 가능

### 3. 포트 설정 확인
- Railway는 자동으로 포트 8000을 감지합니다
- "Settings" → "Networking"에서 확인 가능

## 환경 변수 설정

Railway 대시보드의 API 서비스에서 "Variables" 탭으로 이동하여 다음 환경 변수를 설정합니다.

### 필수 환경 변수

#### 1. JWT 설정
```bash
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
```
**생성 방법:**
```bash
# 랜덤 시크릿 키 생성
openssl rand -hex 32
```

#### 2. MongoDB Atlas 연결
```bash
# MongoDB Atlas 연결 문자열 (3단계에서 복사한 값)
MONGO_URL=mongodb+srv://dailylog-admin:your_password@dailylog-cluster.xxxxx.mongodb.net/dailylog?retryWrites=true&w=majority
```

⚠️ **주의사항:**
- `your_password`를 실제 비밀번호로 변경
- `/dailylog` 데이터베이스 이름 포함 확인
- 연결 문자열에 특수문자가 있으면 URL 인코딩 필요

#### 3. 외부 API 키
```bash
# Resend (이메일 인증)
RESEND_API_KEY=re_xxxxxxxxxxxxx

# Anthropic Claude AI
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# OpenAI DALL-E 3
OPEN_AI_API_KEY=sk-xxxxxxxxxxxxx

# Cloudflare R2 Storage
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=dailylog-images
CLOUDFLARE_R2_PUBLIC_DOMAIN=  # 선택사항: 커스텀 도메인
```

### Railway 서비스 간 연결

MongoDB와 API 서비스를 연결하려면:
1. API 서비스의 "Variables" 탭에서
2. "Reference Variable" 클릭
3. MongoDB 서비스의 변수 참조:
   ```
   MONGO_URL=${{MongoDB.MONGO_URL}}
   ```

**또는** Private Networking 사용:
```bash
MONGO_HOST=mongodb.railway.internal
```

## 배포 확인

### 1. 배포 상태 확인
```bash
railway status
```

또는 Railway 대시보드에서 "Deployments" 탭 확인

### 2. API 엔드포인트 확인
Railway가 자동으로 생성한 URL로 접속:
```
https://dailylog-production.up.railway.app/api/v1
```

예상 응답:
```json
{"message": "hello world"}
```

### 3. 로그 확인
```bash
# CLI로 로그 확인
railway logs

# 또는 대시보드에서 "Deployments" → 특정 배포 클릭 → "View Logs"
```

### 4. 헬스체크 확인
Railway는 `/api/v1` 엔드포인트를 자동으로 헬스체크합니다 (`railway.toml` 설정 참조).

## 커스텀 도메인 설정 (선택사항)

### 1. 도메인 추가
1. Railway 대시보드의 API 서비스에서 "Settings" 탭
2. "Domains" 섹션에서 "Custom Domain" 추가
3. 도메인 입력 (예: `api.dailylog.com`)

### 2. DNS 설정
도메인 레지스트라(예: Cloudflare, GoDaddy)에서:
```
Type: CNAME
Name: api (또는 원하는 subdomain)
Value: [Railway가 제공한 CNAME 값]
```

### 3. SSL 인증서
Railway가 자동으로 Let's Encrypt SSL 인증서를 발급합니다.

## 비용 예상

### Railway 무료 티어
- **Trial 플랜**: $5 크레딧/월
- 소규모 프로젝트에 충분할 수 있음

### 유료 플랜
- **Hobby 플랜**: $5/월 + 사용량
- **Pro 플랜**: $20/월 + 사용량

**예상 비용 (Hobby 플랜):**
- API 서버 (512MB RAM): ~$3-5/월
- MongoDB (512MB RAM): ~$3-5/월
- 총 예상: ~$6-15/월

**비용 절감 팁:**
- MongoDB는 MongoDB Atlas 무료 티어 사용 (512MB)
- 트래픽이 적으면 무료 크레딧으로 충분할 수 있음

## 트러블슈팅

### 1. 빌드 실패
**문제:** Dockerfile 빌드 실패
```
Error: failed to solve: executor failed running...
```

**해결:**
- `railway.toml`의 `dockerfilePath` 확인
- Dockerfile이 repository root에 있는지 확인
- 로그에서 구체적인 에러 메시지 확인

### 2. MongoDB 연결 실패
**문제:** `MongoServerError: Authentication failed`

**해결:**
- 환경 변수 `MONGO_HOST`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` 확인
- Railway Private Networking이 활성화되었는지 확인
- MongoDB 서비스가 실행 중인지 확인

### 3. API가 시작하지 않음
**문제:** 컨테이너가 시작 후 바로 종료됨

**해결:**
- 로그 확인: `railway logs`
- 필수 환경 변수가 모두 설정되었는지 확인
- 특히 `JWT_SECRET_KEY`, API 키들 확인

### 4. 외부 API 연결 실패
**문제:** Anthropic, OpenAI, Cloudflare API 호출 실패

**해결:**
- API 키가 올바른지 확인
- API 키에 충분한 크레딧/권한이 있는지 확인
- Railway의 "Variables" 탭에서 환경 변수 값 재확인

### 5. 이미지 업로드 실패
**문제:** Cloudflare R2 업로드 실패

**해결:**
- R2 버킷이 생성되었는지 확인
- Access Key와 Secret Key 권한 확인
- 버킷 이름이 정확한지 확인
- R2 Public Access 설정 확인

## 모니터링

### Railway 대시보드
- CPU/Memory 사용량
- 요청 수
- 응답 시간

### 로그 스트리밍
```bash
railway logs --follow
```

### 알림 설정
Railway 대시보드에서:
- "Settings" → "Notifications"
- 배포 실패, 서비스 다운 시 알림 설정

## 롤백

문제가 발생하면 이전 버전으로 롤백:
1. "Deployments" 탭
2. 정상 작동하던 이전 배포 선택
3. "Redeploy" 클릭

또는 CLI:
```bash
railway rollback
```

## CI/CD (자동 배포)

Railway는 GitHub과 자동으로 연동됩니다:
- `main` 브랜치에 push → 자동 배포
- PR 생성 → Preview 환경 자동 생성 (Pro 플랜)

수동 배포 비활성화:
1. "Settings" → "Service"
2. "Auto Deploy" 토글 OFF

## 참고 자료

- Railway 공식 문서: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Dockerfile 최적화: https://docs.docker.com/develop/dev-best-practices/
- MongoDB on Railway: https://docs.railway.app/databases/mongodb

## 지원

문제가 발생하면:
1. Railway Discord 커뮤니티에 질문
2. GitHub Issues에 보고
3. Railway 대시보드의 "Help" 버튼 사용
