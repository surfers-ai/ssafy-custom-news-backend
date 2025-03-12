# 18주차 관통 PJT: 맞춤형 큐레이션을 위한 추천시스템 구현(OpenAI + Vector Search)

> **목적: 생성형 AI를 사용하기 위한 큐레이션 시스템 구현한다**
>
> 세부사항:
> - Postgresql을 사용해서 진행
> - 사전에 Postgresql을 배울 때 여기서 사용할 것이라고 명확한 안내 필요

## 목차
1. UserInteraction 데이터 생성
2. /news-list에서 latest, recommend 파라미터가 다르게 처리되는지 확인
   
## 1. UserInteraction 데이터 생성
프론트엔드 화면에서 기사 읽기 및 좋아요 클릭을 통해 UserInteraction 데이터를 생성합니다.

<img width="1366" alt="image" src="https://github.com/user-attachments/assets/cda9d175-bb4f-4eb8-b1b1-dfb500be3f63" />

SQL 쿼리를 통해 직접 생성하는 것도 가능합니다.
```sql
INSERT INTO mynews_userarticleinteraction ("interaction_type", interaction_date, "article_id", "user_id") VALUES ('read', NOW(), 22, 1)
```

<img width="751" alt="image" src="https://github.com/user-attachments/assets/8319497f-c930-480b-a7c5-19c7f4e391fb" />


## 2. /news-list에서 latest, recommend 파라미터가 다르게 처리되는지 확인
아래 url로 접속해 파라미터 별로 데이터 응답이 달라지는 것을 확인합니다.

latest

http://localhost:8000/news-list/?sort_by=latest&page=1

<img width="1728" alt="image" src="https://github.com/user-attachments/assets/ce5e9a57-0544-4d2d-974c-b2dbbecdea81" />


recommend

http://localhost:8000/news-list/?sort_by=recommend&page=1

<img width="1728" alt="image" src="https://github.com/user-attachments/assets/5ebe2c9a-dcef-4957-a822-99fd37e8884b" />


