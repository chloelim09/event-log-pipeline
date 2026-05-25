# Event Log Pipeline

웹 서비스에서 발생할 수 있는 이벤트 로그를 랜덤으로 생성하고, SQLite에 저장한 뒤 SQL로 분석하고 차트 이미지로 시각화하는 프로젝트입니다.

전체 흐름은 아래와 같습니다.

```text
[이벤트 생성 -> SQLite 저장 -> SQL 분석 -> 차트 생성 -> Docker 실행]
```

## 프로젝트 구조

```text
app/
  generator.py      # 랜덤 이벤트 2000개 생성 및 SQLite 저장
  analyzer.py       # 저장된 데이터 분석 및 차트 생성
charts/
  event_type_counts.png : 이벤트 타입별 발생 횟수
  top_purchase_users.png : 전체 상품을 대상으로 구매 횟수가 가장 많은 유저 3명
  product_review_rating.png : 상품별 리뷰 평점
  refund_ratio.png : 전체 이벤트 중 환불 비율
  top_amount_user_by_product.png : 상품별 구매액이 가장 높은 유저 1명
data/
  events.db         # SQLite DB 파일
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

## 실행 방법

### Docker로 실행

필요한 도구는 Docker Desktop입니다. Docker Desktop을 설치한 뒤 터미널에서 아래 명령어로 Docker와 Docker Compose가 실행되는지 확인합니다.

```bash
docker --version
docker compose version
```

Docker Compose v2 환경에서는 아래 명령어 한 번으로 실행할 수 있습니다.

```bash
docker compose up --build
```

구버전 Compose v1 환경에서는 아래 명령어를 사용하면 됩니다.

```bash
docker-compose up --build
```

실행 시 컨테이너 안에서 아래 순서가 자동으로 진행됩니다.

```text
1. Python 환경 구성
2. requirements.txt 설치
3. app/generator.py 실행
4. data/events.db 생성
5. app/analyzer.py 실행
6. charts 폴더에 PNG 차트 저장
```

`data/`와 `charts/`는 Docker volume으로 연결되어 있어 컨테이너 실행이 끝난 뒤에도 로컬 폴더에 결과가 남습니다.

## 사용 라이브러리

```text
matplotlib
```

`matplotlib`은 SQL 분석 결과를 막대그래프와 원형 차트 이미지로 저장하기 위해 사용했습니다.

`random`, `sqlite3`, `uuid`, `datetime`, `pathlib`, `os`는 Python 기본 내장 라이브러리라서 `requirements.txt`에 따로 추가하지 않았습니다.

## 이벤트 데이터

`generator.py`는 총 2000개의 이벤트를 생성합니다.

사용한 이벤트 타입은 아래와 같습니다.

```text
VIEW : 보기 이벤트. 예) 상품이나 페이지를 본 기록
CLICK : 클릭 이벤트. 예) 버튼이나 영역을 클릭한 기록
PURCHASE : 구매 이벤트. 예) 상품을 구매한 기록
REFUND : 환불 이벤트. 예) 상품을 환불한 기록
EXCHANGE : 교환 이벤트. 예) 상품을 교환한 기록
LOGIN : 로그인 이벤트. 예) 사용자가 로그인한 기록
LOGOUT : 로그아웃 이벤트. 예) 사용자가 로그아웃한 기록
```

사용한 이벤트 필드는 아래와 같습니다.

```text
event_id : 이벤트 아이디. 예) uuid로 생성된 "550e8400-e29b-41d4-a716-446655440000"
user_id : 유저 아이디. 예) "user_1"부터 "user_100" 중 하나
event_type : 이벤트 타입. 예) VIEW, CLICK, PURCHASE, REFUND, EXCHANGE, LOGIN, LOGOUT 중 하나
amount : 금액. 예) 10000, 15000, 20000, 30000, 50000 중 하나의 가격에 수량을 곱한 값
quantity : 수량. 예) 1부터 5 사이의 정수
created_at : 생성시각. 예) "2026-05-26 14:30:10" 형식의 현재 시각
review_rating : 평점. 예) PURCHASE 이벤트에서만 생성되는 1부터 5 사이의 정수
product : 상품명. 예) p1, p2, p3, p4, p5 중 하나
```

이벤트 타입은 웹 서비스에서 자주 발생할 수 있는 행동을 기준으로 정했습니다. `VIEW`, `CLICK`, `LOGIN`, `LOGOUT`은 사용자의 기본 행동 흐름을 보기 위한 이벤트이고, `PURCHASE`, `REFUND`, `EXCHANGE`는 상품과 금액이 연결되는 거래 이벤트입니다.

거래 이벤트는 금액(`amount`), 수량(`quantity`), 상품명(`product`)이 필요하지만 일반 행동 이벤트에는 이런 값이 필요하지 않습니다. 그래서 기본 로그는 `events`, 거래 정보는 `transactions`, 리뷰 정보는 `reviews`로 나누었습니다. 리뷰 평점(`review_rating`)은 구매한 상품에 대한 리뷰라고 보고 `PURCHASE` 이벤트에서만 생성했습니다.

## DB 스키마

### 저장소 선택 이유
이 프로젝트는 SQLite를 사용합니다. SQLite는 Python 기본 라이브러리인 `sqlite3`로 바로 사용할 수 있고, 별도 DB 서버 없이 파일 하나로 실행할 수 있어 과제 규모에 적합하다고 판단했습니다.

JSON 전체를 한 컬럼에 저장하지 않고, 분석에 필요한 필드를 컬럼으로 나누어 저장했습니다. 또한 모든 컬럼을 한 테이블에 넣지 않고 속성에 따라 3개 테이블로 분리했습니다.

### events

전체 이벤트의 기본 로그를 저장합니다.

```sql
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### transactions

구매, 환불, 교환처럼 상품, 금액, 수량이 있는 거래성 이벤트 정보를 저장합니다.

```sql
CREATE TABLE transactions (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product TEXT NOT NULL,
    amount INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
```

`transactions`에는 `event_type`을 중복 저장하지 않았습니다. 거래 이벤트 타입이 필요할 때는 `event_id`를 기준으로 `events` 테이블과 JOIN해서 확인합니다.

### reviews

상품 리뷰 평점 정보를 저장합니다.

```sql
CREATE TABLE reviews (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product TEXT NOT NULL,
    review_rating INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
```

## 분석 내용

`analyzer.py`에서는 체크리스트의 구현할 분석 항목에 맞춰 아래 5개 분석을 수행합니다.

```text
1. 이벤트 타입별 발생 횟수
2. 전체 상품을 대상으로 구매 횟수가 가장 많은 유저 3명
3. 상품별 리뷰 평점
4. 전체 이벤트 중 환불 비율
5. 상품별 구매액이 가장 높은 유저 1명
```

분석에는 `GROUP BY`, `ORDER BY`, `COUNT`, `SUM`, `AVG`, `JOIN`을 사용했습니다.

상품별 구매액이 가장 높은 유저를 찾는 분석은 SQL에서 상품별/유저별 구매액을 먼저 집계하고, Python에서 각 상품의 첫 번째 결과만 선택하는 방식으로 구현했습니다. 현재 구현할 수 있는 정도의 SQL 집계와 Python 후처리를 함께 사용했습니다.

## 생성 차트

분석 결과는 `charts/` 폴더에 PNG 파일로 저장됩니다.

```text
charts/event_type_counts.png
charts/top_purchase_users.png
charts/product_review_rating.png
charts/refund_ratio.png
charts/top_amount_user_by_product.png
```

막대그래프에는 막대 위에 정확한 숫자 값을 표시했습니다.

리뷰 평점 차트는 5점 만점 기준을 보여주기 위해 y축을 0부터 5까지로 고정했습니다.

## 구현하면서 고민한 점

처음에는 모든 이벤트 필드를 하나의 테이블에 넣는 방법도 생각했지만, 로그인이나 클릭 이벤트에는 금액, 수량, 리뷰 평점이 필요하지 않아 `NULL` 값이 많아질 수 있다고 판단했습니다. 그래서 기본 이벤트 로그는 `events`, 거래 정보는 `transactions`, 리뷰 정보는 `reviews`로 나누었습니다.

`transactions` 테이블에는 `event_type`을 저장하지 않았습니다. 이미 `events` 테이블에 같은 정보가 있으므로 중복 저장을 줄이고, 필요한 경우 `event_id`로 JOIN해서 이벤트 타입을 가져오도록 설계했습니다.

Docker 구성은 Python 코드가 실행되면서 SQLite DB 파일을 만드는 방식으로 만들었습니다. SQLite는 `data/events.db`처럼 파일 하나로 저장되기 때문에 따로 DB 프로그램을 실행하지 않아도 되고, Docker만 설치되어 있으면 같은 명령어로 실행할 수 있습니다.

## Docker 검증 결과

아래 명령어로 Docker 실행을 검증했습니다.

```bash
docker compose up --build
```

검증 결과 컨테이너 안에서 이벤트 2000개 생성, SQLite 저장, 분석 실행, 차트 PNG 생성까지 정상 동작했습니다.
