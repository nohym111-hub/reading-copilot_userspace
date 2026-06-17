---
name: rc-register
description: Reading Copilot 책 등록 스킬. 사용자가 새 책을 독서 목록에 추가하고 싶을 때 사용하세요. 책 표지 이미지를 촬영해서 올리거나, "이 책 등록해줘", "독서 목록에 추가해줘", 책 제목·저자를 언급하며 읽기 시작을 알릴 때 트리거합니다. 서지 정보 수집 및 로컬 Obsidian Vault의 Books/ 폴더에 노트 파일을 생성하고, 기존 온톨로지와의 첫 연결을 만듭니다.
---

# rc_register — 책 등록

## 역할
책의 존재를 Reading Copilot에 처음 등록한다.
서지 정보 수집 + 기존 온톨로지와의 첫 연결 생성이 핵심이다.

## 트리거
- rc 케이스 A: 이미지가 책 표지로 판단될 때
- rc 케이스 C: 텍스트에 책 제목·저자가 언급될 때
- rc 케이스 G: 표지+내지 복합 업로드의 **첫 단계** — 표지로 책을 식별/확정한 뒤 rc_save에 경로를 인계한다

## 저장소 (Configuration 참조)
- 경로·옵션은 **CLAUDE.md의 `## ⚙ Configuration` 블록**에서 읽는다.
  - Vault 루트: `vault_root` / Books 폴더: `{vault_root}/{books_dir}` / Ontology: `{vault_root}/{ontology_dir}`
  - 파일 접근: `file_access` (`obsidian-mcp` 1순위 / `filesystem` 폴백)
- Configuration이 없으면 → "rc-setup을 먼저 실행해주세요" 한 줄 안내 후 중단.

## 동작 흐름
1. 이미지(표지) 또는 텍스트에서 제목·저자 추출
2. 서지 정보 수집: 출판연도 / 원제 / 국가 / 장르 / 언어(번역본 여부)
3. `{books_dir}` 폴더의 파일 목록 조회 → 이미 등록된 책인지 확인
   - `file_access: obsidian-mcp`: `obsidian_list_files_in_dir` 호출
   - `file_access: filesystem`: `vault_root` 절대경로 + `{books_dir}` 기준으로 디렉토리 나열
   - **이미 등록된 책일 때 분기**:
     - **케이스 G (같은 업로드에 본문 페이지가 함께 있음)** → 중단하지 않는다. 기존 노트의 상대경로(`{books_dir}/{기존 제목}.md`)를 확정해 **6단계로 건너뛴다**. 새 파일을 만들지 않는다 (rc_save가 이 경로에 본문을 저장).
     - **단독 등록 요청 (표지/제목만)** → "이미 목록에 있어요" 한 줄 안내 후 중단.
4. `{ontology_dir}/profile.md` 로드 → 기존 관심사와 매핑 → 연결 코멘트 생성
5. `{books_dir}/{제목}.md` 신규 생성 (아래 템플릿 사용)
   - obsidian-mcp: `obsidian_append_content` 또는 `obsidian_patch_content`
   - filesystem: Write 도구로 `{vault_root}/{books_dir}/{제목}.md` 생성
6. **대상 파일의 Vault 내 상대경로(`{books_dir}/{제목}.md`)를 컨텍스트에 반드시 기억한다** (신규 생성한 파일이든, 3단계에서 확정한 기존 파일이든) → 같은 대화 내 rc_save가 이 경로를 직접 사용한다
7. 사용자에게 등록 완료 + 연결 코멘트 출력

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
creator: "{저자/감독/채널명}"
translator: "{번역자}"
media_type: "{book|film|series|youtube}"
media_subtype: "{non-fiction|fiction|essay|academic|documentary|drama|lecture|vlog|...}"
genre: ["{장르1}", "{장르2}"]
released: {연도}
country: "{국가}"
language: "{ko|en|...}"
status: "interested"
started:
finished:
user_rating:
ai_ontology_nodes: []
ai_interest_score:
ai_connected: []
ai_cross_themes: []
ai_summary:
ai_last_analyzed:
---

## 한줄 인상 (Human)


## 하이라이트 & 메모 (Human)


## 대화 기록 (Human + AI)


## AI 분석 요약 (AI)


## 연결된 콘텐츠 (AI)

```

## 주의
- LAYER 1·2 (ai_ 없는 필드)는 사실 기반이다. 임의로 채우지 않는다.
- LAYER 3 (ai_ 접두사)는 rc_ontology가 채운다. 이 스킬은 빈 상태로 남긴다.
- 권장 모델: Claude Sonnet (서지 정보 추론·온톨로지 매핑)
