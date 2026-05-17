---
name: rc_register
description: Reading Copilot 책 등록 스킬. 사용자가 새 책을 독서 목록에 추가하고 싶을 때 사용하세요. 책 표지 이미지를 촬영해서 올리거나, "이 책 등록해줘", "독서 목록에 추가해줘", 책 제목·저자를 언급하며 읽기 시작을 알릴 때 트리거합니다. 서지 정보 수집 및 Google Drive Books/ 폴더에 노트 파일을 생성하고, 기존 온톨로지와의 첫 연결을 만듭니다.
---

# rc_register — 책 등록

## 역할
책의 존재를 Reading Copilot에 처음 등록한다.
서지 정보 수집 + 기존 온톨로지와의 첫 연결 생성이 핵심이다.

## 트리거
- rc 케이스 A: 이미지가 책 표지로 판단될 때
- rc 케이스 C: 텍스트에 책 제목·저자가 언급될 때

## 동작 흐름
1. 이미지(표지) 또는 텍스트에서 제목·저자 추출
2. 서지 정보 수집: 출판연도 / 원제 / 국가 / 장르 / 언어(번역본 여부)
3. Google Drive Books/ 폴더 확인 → 이미 등록된 책이면 중복 안내
4. Ontology/profile.md 로드 → 기존 관심사와 매핑 → 연결 코멘트 생성
5. Books/{제목}.md 신규 생성 (아래 템플릿 사용)
6. 사용자에게 등록 완료 + 연결 코멘트 출력

## 출력 예시
```
"도둑맞은 집중력이네요 (요한 하리, 2022).
최근 읽으신 딥 워크와 같은 '주의력 관리' 주제예요.
독서 목록에 추가했어요."
```

## 생성되는 파일 템플릿: Books/{제목}.md

```markdown
---
title: "{제목}"
author: "{저자}"
author_orig: "{원저자명}"
published: {연도}
country: "{국가}"
language: "{ko|en|...}"
type: "{non-fiction|fiction|essay|academic}"
genre: ["{장르1}", "{장르2}"]
status: "to-read"
started:
finished:
highlights_count: 0
user_rating:
ai_ontology_nodes: []
ai_interest_score:
ai_connected_books: []
ai_cross_themes: []
ai_summary:
ai_last_analyzed:
---

## 한줄 인상 (Human)


## 하이라이트 & 메모 (Human)


## 대화 기록 (Human + AI)


## AI 분석 요약 (AI)


## 연결된 책 (AI)

```

## 주의
- LAYER 1·2 (ai_ 없는 필드)는 사실 기반이다. 임의로 채우지 않는다.
- LAYER 3 (ai_ 접두사)는 rc_ontology가 채운다. 이 스킬은 빈 상태로 남긴다.
- 권장 모델: Claude Sonnet (서지 정보 추론·온톨로지 매핑)
