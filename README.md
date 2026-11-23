# KANT NEXT DevDesk RAG

현행 문서를 찾아 출처와 함께 답하는 기능을 구현합니다. 필수 2문제와 선택 심화 1문제이며 이전 과제의 완성 코드 없이 시작할 수 있습니다.

세 번째 과제 묶음은 RAG, Context Engineering, LLMOps입니다. 웹사이트의 04, 05, 06은 전체 과목 순서입니다.

## 환경 준비와 첫 실행

ZIP을 풀고 `main.py`와 `pyproject.toml`이 바로 보이는 폴더를 VS Code로 엽니다. Windows에서는 바탕화면처럼 경로가 짧은 위치를 사용하세요. 폴더가 깊게 중첩되면 패키지를 불러오지 못할 수 있습니다.

VS Code의 Python 확장을 설치하고 새 터미널을 엽니다. uv가 없다면 [공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)를 따른 뒤 터미널을 새로 여세요.

```text
uv --version
uv sync --frozen
uv run --frozen python --version
uv run --frozen python main.py demo
```

Python 3.12가 표시되어야 합니다. `.python-version`이 Python 버전을 선택하며 패키지는 `pyproject.toml`과 `uv.lock`에 맞춰 설치됩니다. 버전을 바꾸거나 가상환경을 따로 활성화할 필요는 없습니다.

`demo`는 자료를 읽는 준비 확인입니다. TODO 완료를 검사하지 않습니다. 첫 실행을 확인했으면 [과제 안내](ASSIGNMENT.md)의 필수 1부터 진행하세요.

CPU에서 실행하는 `intfloat/multilingual-e5-small`이 문서와 질문의 임베딩을 만듭니다. 첫 `run index`에서 공개 모델을 내려받으므로 인터넷과 저장 공간이 필요합니다. 이후에는 모델 캐시를 재사용합니다. Qdrant는 프로그램 안에서 실행하므로 별도 서버나 계정이 필요하지 않습니다.

`check`는 작은 고정 벡터로 검사하며 모델 다운로드와 API 키가 필요하지 않습니다. 실제 검색과 생성 품질은 문제의 `run` 명령으로 따로 확인합니다.

## 진행 순서

문단 정리와 검색 → 별칭 변환과 답변 비교 → 실제 결과와 주석 확인

1. [과제 안내](ASSIGNMENT.md)에서 지금 작성할 함수의 조건과 예시를 읽습니다.
2. `main.py`의 해당 TODO를 채우고 바로 아래에 안내된 명령으로 검사하고 실행합니다.
3. 결과 파일을 읽고 요구된 이유와 관측 주석을 작성한 뒤 다음 기능으로 넘어갑니다.

작성할 파일은 `main.py`와 `AI_USAGE.md`입니다. [AI 활용 기준](AI_USAGE.md)을 먼저 확인하고 사용 여부를 기록하세요. 입력 필드가 궁금할 때 [제공 자료 안내](data/DATA_CARD.md)를 찾아봅니다.

`support.py`, `checks.py`, `uv.lock`의 내부를 모두 읽거나 이해할 필요는 없습니다. `todo` 함수 자체, 지원 코드, 검사, 데이터와 환경 버전은 제공된 상태로 사용합니다.

## 실제 연결 준비

필수 2의 답변 생성과 평가 전에 `.env`를 준비합니다. 기존 파일이 있으면 유지하세요. 없을 때만 다음 중 운영체제에 맞는 명령으로 만듭니다.

| 운영체제 | 명령 |
|---|---|
| Windows | `Copy-Item .env.example .env` |
| macOS와 Linux | `cp .env.example .env` |

`.env`의 `OPENAI_API_KEY=` 뒤에 본인 키를 넣습니다. `OPENAI_MODEL`은 사용할 수 있는 모델로 바꿀 수 있습니다. 파일명이 `.env.txt`가 되지 않도록 확인하세요.

실제 답변과 평가는 `--live`로 실행하며 비용이 발생합니다. RAG의 `run index`와 `run challenge`는 `--live` 없이 실제 E5 임베딩과 Qdrant 검색을 사용합니다. 각 단계의 정확한 명령은 [과제 안내](ASSIGNMENT.md)에 있습니다.

## 실행이 막혔을 때

`미완료`는 남은 TODO, `실패`는 구현한 조건을 다시 확인해야 한다는 뜻입니다. 결과는 `artifacts/`에 저장됩니다. 기능 검사 파일 `checks-기능명.json`에서 항목 이름과 오류 내용을 확인하세요. 검사 항목 수는 문제 수나 점수가 아닙니다.

패키지를 불러오지 못하면 폴더 위치와 `uv sync --frozen` 실행부터 확인합니다. 뒤 문제의 빈칸을 모두 채우기 전에 앞 기능부터 검사할 수 있습니다.

모델 답변은 실행마다 달라질 수 있습니다. 오류를 해결한 뒤 해당 단계를 다시 실행하고, 실행하지 못한 결과를 만들지 마세요.

## 제출

필수 구현, 실제 실행과 지정된 주석 작성을 마쳤다면 마지막 검사를 실행합니다.

```text
uv run --frozen python main.py check all
```

`check all`에는 선택 심화가 포함되지 않습니다. 선택 심화는 해당 문제의 명령으로 별도 확인하며, 하지 않아도 필수 제출을 완료할 수 있습니다.

과목별로 `main.py`와 `AI_USAGE.md` 두 파일만 기존 과제 제출 시스템에 제출합니다. 구현 이유와 관측 내용은 `main.py`의 지정된 주석에 짧게 남기세요. 두 파일 외의 추가 자료나 화면 캡처는 제출하지 않습니다.

제공 코드, 검사, 데이터, 환경 파일, `artifacts/`, 캐시와 `.venv/`는 제출하지 않습니다. `.env`, API 키와 개인정보는 제출물, 화면, 코드 주석과 AI 대화에 넣지 마세요.
