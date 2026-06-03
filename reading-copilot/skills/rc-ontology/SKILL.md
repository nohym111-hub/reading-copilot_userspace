---
name: rc-ontology
description: Reading Copilot 지식 온톨로지 생성·갱신 스킬. 사용자의 독서 데이터를 분석해 관심사 그래프와 책 간 연결을 만드는 두뇌 역할입니다. "온톨로지 업데이트해줘", "내 독서 패턴 분석해줘", "어떤 주제에 관심 있는지 정리해줘", 하이라이트 5개 누적, 완독 선언, 7일 이상 미입력 등의 상황에서 트리거합니다. Book-level / User-level / Cross-book 3개 레이어로 분석하고 로컬 Obsidian Vault의 Ontology/ 폴더를 갱신합니다.
---

# rc_ontology — 지식 온톨로지 생성·갱신

## 역할
Reading Copilot의 두뇌. 모든 Human + AI 데이터를 분석해 사용자의 지식 온톨로지를 지속 갱신한다.
다른 모든 스킬에 컨텍스트를 공급하는 상시 운용 엔진이다.

## 권장 모델
Claude Sonnet 이상 — 전체 데이터 통합 분석과 온톨로지 추론이 필요하다.

## 노드 종류 × 분석 레이어

온톨로지는 3개 레이어로 분석하고, 각 레이어에서 특정 노드를 생성한다.

| 노드 종류 | 생성 레이어 | 생성 조건 |
|---|---|---|
| 핵심 노드 | Book-level | 같은 책 안에서 키워드 3회 이상 등장 |
| 고관심 노드 | Book-level | 하이라이트에 감정 표현 동반 ("!!", "중요", 반복 메모) |
| 탐색 노드 | User-level | 대화에서 반복적으로 나온 질문·주제 |
| 연결 노드 | Cross-book | 2권 이상에서 공통으로 등장한 개념 |

## 트리거 조건

| 조건 | 실행 레이어 |
|---|---|
| 하이라이트 5개 누적 (5, 10, 15... 마다) | Book-level |
| 하이라이트 추가 후 7일 이상 새 입력 없음 | Book-level + User-level |
| 완독 선언 (status: done) | Book-level + User-level |
| 2권 이상에서 공통 키워드 감지 | Cross-book 추가 실행 |
| 사용자 명시 요청 ("온톨로지 업데이트해줘") | 3레이어 전체 |

## 분석 3레이어 상세

### Book-level
- 범위: 개별 책 1권
- 입력: `{books_dir}/{제목}.md` 전체
- 출력:
  - ai_ontology_nodes: 핵심·고관심 노드 3~5개
  - ai_interest_score: 하이라이트 밀도 기반 0.0~1.0
  - 해당 책 노트 프론트매터 LAYER 3 갱신

### User-level
- 범위: `{books_dir}` 전체 + `{ontology_dir}/profile.md`
- 입력: 전체 독서 이력, 대화 패턴, 탐색 노드
- 출력:
  - `{ontology_dir}/profile.md` 관심사 그래프 갱신
  - 탐색 노드 추가
  - 공백 영역 감지 ("이 방향으로 이어지는 책이 아직 없어요")

### Cross-book
- 범위: `{books_dir}` 전체 + `{ontology_dir}/themes.md`
- 입력: 전체 책 노트의 하이라이트·ai_ontology_nodes
- 출력:
  - 각 책 노트 ai_connected_books, ai_cross_themes 갱신
  - `{ontology_dir}/themes.md` 연결 노드 추가
  - 연결 근거 코멘트 생성

## 저장소 (Configuration 참조)
- 경로·옵션은 **CLAUDE.md의 `## ⚙ Configuration` 블록**에서 읽는다.
  - Vault 루트: `vault_root` / Books: `{books_dir}` / Ontology: `{ontology_dir}`
  - 파일 접근: `file_access` (`obsidian-mcp` 1순위 / `filesystem` 폴백)
- `obsidian-mcp` 도구 매핑:
  - 다건 일괄 로드: `obsidian_batch_get_file_contents`
  - 단건 로드/검색: `obsidian_get_file_contents`, `obsidian_simple_search`, `obsidian_complex_search`
  - 프론트매터/섹션 부분 수정: `obsidian_patch_content`
  - 신규 추가: `obsidian_append_content`
- Configuration이 없으면 → "rc-setup을 먼저 실행해주세요" 한 줄 안내 후 중단.

## 동작 흐름
1. 트리거 감지 → 실행할 레이어 결정
2. 해당 범위 데이터 로드 — Book-level은 단건, User/Cross-book은 일괄 로드
3. 키워드·빈도·감정·반복 패턴 분석
4. `{ontology_dir}/themes.md` 대조 → 기존 노드 병합 또는 신규 추가
5. 책 노트 프론트매터 ai_* 필드 갱신
6. User-level 이상 실행 시 `{ontology_dir}/profile.md` 갱신
7. ai_last_analyzed 타임스탬프 업데이트

## 노드 기준 변경 시 확산 절차
사용자가 "A 노드를 B로 통합해줘" 요청 시:
1. `{ontology_dir}/themes.md` 노드 정의 변경
2. ai_ontology_nodes에 해당 노드가 있는 모든 책 노트 탐색 (`{books_dir}` 전체)
3. 일괄 치환 후 ai_connected_books, ai_cross_themes 재계산
4. 변경 영향받은 책 목록 사용자에게 보고

## 사용자 응답 예시
```
"분석 완료.

핵심 노드: 주의력, 전환비용, 디지털환경
관심도: 0.87 (이번 책에서 하이라이트 14개)

최근 읽으신 딥 워크와 '몰입'·'주의력 잔여물' 개념이 겹쳐요.
두 책을 연결했어요."
```

## 주의
- ai_ 접두사 필드만 수정한다. LAYER 1·2는 절대 건드리지 않는다.
- 태그·테마 초반 세팅 불필요. 첫 책부터 동적으로 생성한다.
- Obsidian MCP로 Vault 파일을 직접 읽고 쓴다.
