# 16주차 관통 PJT: 백엔드&프론트엔드 프로젝트 구축(Vue와 Django)

> **목적: 학생들이 뷰와 장고를 활용하여 카프카와 플링크가 내부적으로 돌아가는 프론트와 백앤드를 구축한다**
>
> 세부사항:
>
> - 뷰와 장고는 학생들이 앞 단에서 배운 내용들만 가능하면 사용해야 한다.
>   - 이 부분은 지난 번 만들었던 최종 결과물에서 커뮤니티와 기사 주제로 대화 기능 제거
> - 데이터가 처리되는 것을 시각화 해야한다
>   - 예를들어, 새로고침 버튼을 누르면 RSS를 활용하여 새로운 데이터가 적재되고, 카프카와 플링크가 동작하여 뉴스 기사가 새롭게 화면에 뷰잉되어야 한다.

## 목차

1. 프로젝트 설치
2. DB 마이그레이션 및 실행

## 1. 프로젝트 설치

### 1.1. 저장소 클론

```bash
git clone https://github.com/surfers-ai/ssafy-custom-news-backend.git
cd ssafy-custom-news-backend
```

### 1.2. Poetry 환경 설정

```bash
# Poetry 설치 (필요한 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 가상환경 활성화
poetry shell
```

### 1.3. Django 설정

1. 데이터베이스 설정

`myproject/settings.py` 파일에서 PostgreSQL 데이터베이스 설정을 추가:
user, password는 ssafy-custom-news-data [week-14](https://github.com/surfers-ai/ssafy-custom-news-data/blob/weekly-modules/week-14/README.md#12-postgresql-%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4-%EC%84%A4%EC%A0%95)에서 생성한 정보 입력

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "news",              # 데이터베이스 이름
        "USER": "your_user",          # PostgreSQL 사용자명
        "PASSWORD": "your_password",  # PostgreSQL 비밀번호
        "HOST": "localhost",         # 데이터베이스 호스트
        "PORT": 5432,               # PostgreSQL 포트
    }
}
```

2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 적절히 수정하세요
```

## 2. DB 마이그레이션 및 실행

### 2.1. DB 마이그레이션

```bash
poetry run python manage.py migrate
```

<img width="1062" alt="image" src="https://github.com/user-attachments/assets/53cb93ef-37fd-4e40-a0e1-22a307c32efc" />


### 2.2. 서비스 실행

아래 명령어 실행 후 http://localhost:8000 에 접속해 정상동작 하는지 확인합니다.

```bash
poetry run bash start.sh
```

<img width="1145" alt="image" src="https://github.com/user-attachments/assets/a4f3a605-8232-4581-860e-a350417454b2" />

### 2.3. 로그 확인
/log 폴더의 access.log, error.log 파일에서 백엔드 요청 로그를 확인합니다.

access.log

<img width="1382" alt="image" src="https://github.com/user-attachments/assets/723db3e2-69b6-49f5-9595-3f448948e105" />

error.log

<img width="860" alt="image" src="https://github.com/user-attachments/assets/2007404a-6b73-42be-b6bf-b4cdccf3bd72" />



