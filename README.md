# 🗞️ SSAFY DS PJT - Custom News Backend

맞춤형 뉴스 추천 시스템을 위한 백엔드 서비스

## 🌟 프로젝트 소개

SSAFY DS PJT는 사용자 맞춤형 뉴스 추천 시스템의 백엔드를 구현한 프로젝트입니다.

## 🚀 시작하기

### PostgreSQL 설치 및 설정

#### Linux (Ubuntu)

1. PostgreSQL 설치

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

2. 서비스 상태 확인

```bash
sudo service postgresql status
```

#### PostgreSQL 데이터베이스 설정

1. PostgreSQL 접속

```bash
sudo -i -u postgres
psql
```

2. 데이터베이스 생성

```sql
CREATE DATABASE news;
```

3. 사용자 생성 및 권한 부여

```sql
CREATE USER ssafyuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE news TO ssafyuser;
```

### 프로젝트 설치

1. 저장소 클론

```bash
git clone https://github.com/surfers-ai/ssafy-custom-news-data.git
cd ssafy-custom-news-data
```

2. Poetry 환경 설정

```bash
# Poetry 설치 (필요한 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 가상환경 활성화
poetry shell
```

3. Django 설정

#### 데이터베이스 설정

`myproject/settings.py` 파일에서 PostgreSQL 데이터베이스 설정을 추가:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "news",              # 데이터베이스 이름
        "USER": "postgres",          # PostgreSQL 사용자명
        "PASSWORD": "new_password",  # PostgreSQL 비밀번호
        "HOST": "localhost",         # 데이터베이스 호스트
        "PORT": 5432,               # PostgreSQL 포트
    }
}
```

4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 적절히 수정하세요
```

5. 데이터베이스 마이그레이션

```bash
poetry run python manage.py migrate
```

6. 서비스 실행

```bash
bash start.sh
```

## 🛠️ 주요 기능

### 1. 🤖 AI 기반 맞춤 뉴스 추천

- 사용자별 관심사와 소비 패턴 분석을 통한 개인화된 뉴스 추천
- 머신러닝 기반의 뉴스 컨텐츠 분석 및 카테고리화
- 실시간 사용자 피드백 기반 추천 알고리즘 개선

### 2. 📊 개인화 대시보드

- 사용자별 뉴스 소비 패턴 시각화
- 관심 분야 분석 및 트렌드 리포트
- 맞춤형 취업 정보 로드맵 제공
- 직관적인 UI를 통한 데이터 인사이트 제공

### 3. 🔐 계정 관리

- 안전한 회원가입 및 로그인 시스템
- JWT 기반 사용자 인증
- 개인정보 보호 및 보안 강화
- 사용자 프로필 관리

---

⭐️ Thank you!
