---
name: rc-ontology
description: Reading Copilot 지식 온톨로지 생성·갱신 스킬. 사용자의 독서 데이터를 분석해 LLM Wiki(엔티티 지식 그래프)와 책 간 연결을 만드는 두뇌 역할입니다. "온톨로지 업데이트해줘", "내 독서 패턴 분석해줘", "어떤 주제에 관심 있는지 정리해줘", 하이라이트 5개 누적, 완독 선언, 7일 이상 미입력 등의 상황에서 트리거합니다. Book-level / User-level / Cross-book 3개 레이어로 분석하고 로컬 Obsidian Vault의 Ontology/ 폴더를 갱신합니다.
---

# rc_ontology — 지식 온톨로지 생성·갱신 (LLM Wiki 모델)

> **이 SKILL이 온톨로지 규칙의 단일 원본이다.** 명명·점수·갱신·고아 규칙을 모두 여기서 정의한다.
> Vault에는 규칙 사본을 두지 않는다 (Ontology 폴더는 산출물만 담는다).

## 역할
Reading Copilot의 두뇌. 모든 Human + AI 데이터를 분석해 사용자의 지식 온톨로지를 지속 갱신한다.
다른 모든 스킬에 컨텍스트를 공급하는 상시 운용 엔진이다.

## 온톨로지 모델 — LLM Wiki (Karpathy)
Andrej Karpathy의 "LLM이 읽기 좋은 지식 = 촘촘히 링크된 위키/지식그래프" 관점을 채택한다.
책들이 기술하는 **세계 자체**를 엔티티 그래프로 모델링하고, **독자 관점**을 profile로 보강한다.

- 엔티티 타입:
  | 타입 | 저장 위치 | 노드 |
  |---|---|---|
  | **Content** (책·영화·다큐) | `{books_dir}/{제목}.md` (노트 자체) | ✅ |
  | **Concept** (개념) | `{ontology_dir}/Concepts/{개념명}.md` (개별 파일) | ✅ |
  | **Person** (인물) | `{ontology_dir}/people.md` (섹션) | 참조 |
  | **Claim** (근거 앵커 명제) | `{ontology_dir}/claims.md` (섹션) | 참조 |
- **Content 노드는 새로 만들지 않는다** — Contents 노트가 곧 Content 노드다(중복 금지).
- **Concept만 개별 파일** → `[[개념명]]` 이 실제 그래프 노드로 해석되고 Obsidian 백링크가 양방향성을 자동 생성한다.

## Ontology 폴더 구조 (산출물)
```
{vault_root}/
├ README.md          # 이 위키의 철학 (vault 최상위)
└ {ontology_dir}/
  ├ index.md    # 엔티티 레지스트리 + 컨텍스트 적재 가이드
  ├ profile.md  # 독자 레이어 — 관심사·공백·추천 힌트
  ├ people.md   # 인물 (2차 참조)
  ├ claims.md   # 주장 (2차 참조)
  └ Concepts/   # 개념 노드 (개별 파일 = 그래프 노드)
```

## 명명 규칙 (링크 해석의 핵심)
1. **위키링크 타깃 = 파일명과 정확히 일치**해야 한다. 불일치 시 링크가 죽는다.
2. **Content**: 파일명 = 사용자가 정한 제목 그대로 (`[[테니스 이너 게임]]`, `[[Devil Wears Prada 2]]`).
3. **Concept**: 한국어 명사구, 공백 허용, 특수문자 회피 (`몰입`, `정보 네트워크`). 파일명 = 링크명.
4. **별칭**: 한 작품이 여러 이름으로 불리면 그 노트 프론트매터에 `aliases: [...]`를 두어 링크가 해석되게 한다.
5. 프론트매터의 모든 엔티티 참조는 `"[[...]]"` **따옴표+위키링크** 형식.

## 책 노트 `ai_*` 스키마
```yaml
ai_entity_type: Content
ai_concepts:          ["[[몰입]]", ...]        # 이 작품이 인스턴스화하는 Concept
ai_connected_contents: ["[[씻다르타]]", ...]    # 개념을 공유하는 다른 Content
ai_cross_themes:      ["[[몰입]]"]              # 연결 근거 개념(ai_concepts 부분집합)
ai_interest_score:    0.00                      # 아래 공식
ai_summary:           "한 문장 요약"
ai_last_analyzed:     YYYY-MM-DD
```
- `ai_*`만 쓴다. **불변 대상 = Human 하이라이트·인상·대화 발화.** ai_ 프론트매터는 AI 파생 레인이므로 여기 쓰는 것은 불문율 위반이 아니다.

## interest_score 공식
```
score = min(1.0, 0.04·H + 0.06·E + 0.20·D)
  H=하이라이트 수 · E=감정 마킹 수(?!,!!,💭,메모) · D=서사 깊이(0/1/2)
```
데이터 없으면 0.10 고정(스텁).

## 노드 종류 × 분석 레이어
| 노드 | 레이어 | 생성 조건 |
|---|---|---|
| Concept(핵심) | Book-level | 같은 책에서 키워드 3회+ 또는 감정 마킹 동반 |
| 독자 가중치 | User-level | profile.md 관심사 그래프 갱신 |
| 연결(Concept 승격) | Cross-book | 2권+ 공통 개념 → Concept 파일로 승격 |

## 트리거 → 실행 레이어
| 조건 | 레이어 |
|---|---|
| 하이라이트 5개 누적(5,10,15…) | Book-level |
| 새 개념이 2번째 Content에 등장 | Cross-book (Concept 승격) |
| 완독 선언(status→explored) | Book + User |
| 7일 무입력 | Book + User |
| 사용자 명시 요청 | 3레이어 전체 |

## 분석 3레이어

### Book-level (개별 책 1권)
- 입력: `{books_dir}/{제목}.md`
- 출력: 해당 책의 `ai_concepts`·`ai_interest_score`·`ai_summary` 갱신 (위 스키마)
- 개념 후보 추출 → **고아 정책 통과분만** Concept로 승격(2 Content+ 또는 2 Concept 연결). 미달은 인라인 태그(비링크 문자열)로만 남긴다.

### User-level (전체 + profile.md)
- 입력: 전체 독서 이력, 대화 패턴
- 출력: `{ontology_dir}/profile.md` 관심사 그래프·시간축·**탐색 공백** 갱신
- Concept/Content의 reader_weight 조정

### Cross-book (전체 + Concepts/)
- 입력: 전체 책의 `ai_concepts`
- 출력:
  - 2권+ 공통 개념 → `Concepts/{개념}.md` 생성/갱신
  - 양쪽 책의 `ai_connected_contents` **양방향** 갱신 (한쪽만 적으면 불일치 — 금지)
  - `index.md` 레지스트리 갱신

## 하이라이트 갱신 원칙
1. **증분**: 기존 노드 삭제 금지, 병합·가중치 조정. 링크 무결성 우선.
2. **멱등**: 같은 하이라이트 재분석 시 결과 동일 (rc_save.py 지문 중복제거와 정합).
3. 매 갱신 `ai_last_analyzed` 갱신.
4. Human 데이터는 읽기만.

## 고아 노드 금지
- Concept 승격 조건: 2개+ Content 등장 **또는** 2개+ Concept 연결. 미달이면 파일 생성 금지(인라인 태그만).
- **스텁**(하이라이트·인상 전무): 개념 생성 금지, `ai_interest_score: 0.10`, `ai_summary`에 "데이터 부족" 명시. **환각 방지 최우선.**
- 링크 차수 0 파일은 사용자에게 보고(자동 삭제 금지).

## 저장소 (Configuration 참조)
- 경로·옵션은 **CLAUDE.md의 `## ⚙ Configuration` 블록**에서 읽는다.
- `obsidian-mcp` 도구 매핑: 다건 `obsidian_batch_get_file_contents` / 단건 `obsidian_get_file_contents` / 부분수정 `obsidian_patch_content` / 신규 `obsidian_append_content`.
- 경로 규칙: `{obsidian_mcp_prefix}/{상대경로}` (후행 슬래시 금지). 예) `reading-copilot-vault/Ontology/Concepts/몰입.md`
- Configuration 없으면 → "rc-setup을 먼저 실행해주세요" 후 중단.

## 동작 흐름
1. 트리거 감지 → 실행 레이어 결정
2. 범위 데이터 로드 (Book-level 단건 / User·Cross-book 일괄)
3. 키워드·빈도·감정 분석 → interest_score 공식 적용
4. `Concepts/` 대조 → 기존 개념 병합 또는 승격(고아 정책 통과 시)
5. 책 노트 `ai_*` 프론트매터를 위키링크 스키마로 갱신 (Human 섹션 불가침)
6. Cross-book: `ai_connected_contents` 양방향 + `index.md` 갱신
7. User-level: `profile.md` 갱신
8. `ai_last_analyzed` 타임스탬프 갱신

## 노드 기준 변경 시 확산 절차
사용자가 "A 개념을 B로 통합" 요청 시:
1. `Concepts/A.md`·`Concepts/B.md` 정의 병합 (파일 rename/merge)
2. `ai_concepts`에 `[[A]]`가 있는 모든 책 탐색 → `[[B]]`로 치환
3. `ai_connected_contents`·`ai_cross_themes` 재계산 (양방향)
4. `index.md` 갱신 + 영향받은 책 목록 사용자 보고

## 사용자 응답 예시
```
"분석 완료.

핵심 개념: [[정보 네트워크]] · [[알고리즘 통제]] · [[상호주관적 현실]]
관심도: 0.95 (하이라이트 25개)

[[기술공화국 선언]]과 '정보 네트워크·알고리즘 통제' 개념이 겹쳐 두 책을 양방향으로 연결했어요.
탐색 공백: 'AI 해법·거버넌스' 방향 책이 아직 없어요."
```

## 주의
- `ai_` 접두사 필드만 수정한다. LAYER 1·2, Human 섹션은 절대 건드리지 않는다.
- **이 SKILL이 규칙의 단일 원본이다.** Vault 산출물과 이 문서가 어긋나면 이 문서가 우선.
- Obsidian MCP로 Vault 파일을 직접 읽고 쓴다.
- 권장 모델: Claude Sonnet 이상.
