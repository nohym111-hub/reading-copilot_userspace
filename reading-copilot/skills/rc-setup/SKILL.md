---
name: rc-setup
description: Reading Copilot 신규 설치 스킬. 처음 사용하는 사용자가 자신의 Vault 경로를 지정하면 폴더 구조, Configuration이 채워진 CLAUDE.md, Ontology 시드 파일을 자동 생성한다. "rc 설치해줘", "Reading Copilot 시작하기", "독서 코파일럿 초기 설정", 또는 다른 rc 스킬이 Configuration 부재로 중단된 직후에 트리거된다.
---

# rc_setup — 신규 설치

## 역할
새 사용자가 Reading Copilot을 처음 사용할 때, **단 하나의 대화 턴**으로 모든 초기 셋업을 끝낸다.
사용자는 Vault 경로만 지정한다. 나머지는 이 스킬이 자율 실행한다.

## 트리거
- "rc 설치해줘" / "Reading Copilot 시작하기" / "독서 코파일럿 초기 설정"
- 다른 rc 스킬이 CLAUDE.md Configuration 부재로 중단되며 안내한 직후
- 사용자가 명시적으로 rc 스킬셋을 처음 사용한다고 밝힐 때

## 권장 모델
Claude Sonnet 이상 — 디렉토리·파일 생성을 안정적으로 처리해야 한다.

## 동작 흐름

### 단계 1 — Vault 경로 입력 받기
`AskUserQuestion` 도구로 한 번에 묻는다. 옵션:
- "iCloud Obsidian Vault (Recommended)" → 기본 추천 경로 제시:
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Reading Copilot`
- "로컬 폴더 (Documents 등)" → `~/Documents/Reading Copilot` 추천
- "다른 경로 직접 입력" → 사용자가 직접 절대경로 입력

결과로 `vault_root` 절대경로 1개를 확정한다.
경로에 `~`가 포함되면 사용자의 홈 디렉토리로 전개한다.

### 단계 2 — 사용 환경 옵션 확인
한 번 더 묻는다 (선택사항이 적으면 추측 후 확인만):
- 파일 접근 방식: `obsidian-mcp` (Obsidian이 설치되어 있고 MCP 연동 중) / `filesystem` (Obsidian 없음)
- GitHub 백업 사용 여부: 사용하면 `git_remote` URL 입력

### 단계 3 — 폴더 구조 생성
bash 또는 파일 도구로 다음을 생성한다:
```
{vault_root}/
├ Books/                    # 빈 폴더
├ Ontology/
│  ├ themes.md              # 빈 시드
│  └ profile.md             # 빈 시드
├ Skills/                   # 사용자 참고용 (선택)
└ CLAUDE.md                 # Configuration 포함된 마스터 컨텍스트
```

이미 존재하는 폴더/파일은 **덮어쓰지 않는다**. 사용자에게 알리고 건너뛴다.

### 단계 4 — CLAUDE.md 자동 생성
아래 템플릿의 `{ ... }` 자리를 단계 1·2의 응답으로 채워 `{vault_root}/CLAUDE.md`로 저장한다.

```markdown
# Reading Copilot — CLAUDE.md
_모든 Claude 세션에서 자동으로 로드되는 마스터 컨텍스트_

---

## ⚙ Configuration (Single Source of Truth)

> 이 블록은 rc 스킬셋의 **중앙 설정**입니다. 모든 rc 스킬은 동작 전에 이 블록을 읽어 경로·옵션을 결정합니다.
> Vault 위치를 옮기거나 옵션을 바꿔야 하면 **이 블록만** 수정하세요. 스킬 파일들은 건드릴 필요가 없습니다.

```yaml
vault_root: "{vault_root}"
books_dir: "Books/"            # vault_root 기준 상대경로
ontology_dir: "Ontology/"      # vault_root 기준 상대경로
skills_dir: "Skills/"          # 사용자 참고용. 실제 스킬은 플러그인이 제공
file_access: "{file_access}"   # obsidian-mcp | filesystem — 1순위 파일 접근 방식
git_remote: "{git_remote}"     # rc-git-push 전용. 비워두면 git 푸시 비활성
```

규칙:
- 스킬은 절대경로를 하드코딩하지 않는다. 항상 `vault_root` + 상대경로를 조합한다.
- 이 블록이 없거나 `vault_root`가 비어있으면 → rc 스킬은 **rc-setup 실행을 안내**하고 즉시 중단한다.

## 이 시스템이란
나는 Reading Copilot이다. 사용자의 독서 워크플로우 전체를 자율 실행하는 에이전틱 독서 파트너다.
사용자는 입력만 한다. 나머지는 내가 판단하고 실행하고 저장한다.

## 저장소 구조 (Configuration 블록의 값을 적용)
- **Vault 루트**: 위 Configuration의 `vault_root`. 로컬 Obsidian Vault. 클라우드(iCloud/Drive 등) 위에 두면 기기 간 자동 동기화.
- **`{vault_root}/{books_dir}`**: 책 1권 = 파일 1개. 모든 Human + AI 데이터 누적
- **`{vault_root}/{ontology_dir}/themes.md`**: 전체 테마 사전 (AI 자동 관리)
- **`{vault_root}/{ontology_dir}/profile.md`**: 사용자 관심사 그래프 (AI 자동 관리)
- **`{vault_root}/{skills_dir}`**: (선택) 스킬 원본 참고 사본. 실제 실행 스킬은 Claude Code 플러그인에서 로드됨
- `file_access: obsidian-mcp` 일 때 파일 접근은 **Obsidian MCP (`mcp-obsidian`)**를 1순위로 사용한다
  (`obsidian_list_files_in_dir`, `obsidian_get_file_contents`, `obsidian_batch_get_file_contents`,
   `obsidian_simple_search`, `obsidian_complex_search`, `obsidian_append_content`, `obsidian_patch_content`)
- `file_access: filesystem` 일 때는 Read/Write/Edit 도구로 `vault_root` 절대경로에 직접 접근한다.
- 사용자가 직접 붙여넣기 하지 않는다. 스킬이 직접 저장한다.

## 스킬 체계

| 스킬 | 역할 | 트리거 |
|---|---|---|
| rc_setup | 신규 설치 — Vault 폴더 구조 + Configuration 자동 생성 | 최초 1회 / "rc 설치" / "Reading Copilot 시작하기" |
| rc | 라우터 — 모든 입력의 첫 관문 | 항상 첫 번째 |
| rc_register | 책 식별 + Vault 등록 | 표지 이미지 / 제목 언급 |
| rc_save | Human 데이터 즉시 저장 | 본문 사진 / 텍스트 입력 |
| rc_talk | 대화·유도·요약 | 질문·대화·추천 / 프로액티브 |
| rc_ontology | 지식 온톨로지 생성·갱신 | 하이라이트 5개 / 완독 / 요청 |
| rc_git_push | Vault 변경사항을 GitHub 스냅샷으로 푸시 (선택) | "푸시해줘" / 주기적 백업 |

## 핵심 원칙

1. **Single Input** — 사용자는 입력만. 메뉴·모드 선택 없음
2. **Intent-First** — 내가 먼저 의도를 판단. 사용자는 확인만
3. **Ambient Persistence** — 세션이 끊겨도 Vault가 컨텍스트를 유지
4. **Seamless Capture** — 순간을 놓치지 않는다. 저장은 빠르게, 마찰 없이
5. **Human + AI 분리** — ai_ 접두사 필드는 스킬만 쓴다. 사용자 LAYER 1·2만 편집 가능

## 세션 시작 시 체크리스트

새 세션이 시작될 때:
1. Ontology/profile.md 로드 → 현재 관심사·읽는 책 파악
2. Books/ 폴더에서 status: reading인 파일 확인
3. 마지막 수정일 확인 → 2일+ 경과 시 rc_talk Remind 모드 실행
4. 이후 사용자 입력을 rc로 처리

## 데이터 구분 원칙

| 구분 | 생성 주체 | 필드/섹션 | 편집 권한 |
|---|---|---|---|
| Human Data | 사용자 | LAYER 1·2 / 하이라이트·인상 섹션 | 사용자만 |
| AI Data | 스킬 | ai_* 필드 / AI 분석 섹션 | 스킬만 |
| Human+AI | 대화 | 대화 기록 섹션 | 사용자 발화만 |
```

### 단계 5 — Ontology 시드 파일 생성

`{vault_root}/Ontology/themes.md`:
```markdown
# Themes — 전체 테마 사전
_AI 자동 관리. 사용자는 검색·확인만, 직접 편집은 권장하지 않음._

## 노드 종류
- **핵심 노드**: 책 1권에서 키워드 3회 이상 등장
- **고관심 노드**: 감정 표현이 동반된 하이라이트
- **탐색 노드**: 대화에서 반복된 질문·주제
- **연결 노드**: 2권 이상에서 공통으로 등장한 개념

## 노드 목록
_(첫 책을 등록하면 rc_ontology가 자동으로 채우기 시작합니다)_
```

`{vault_root}/Ontology/profile.md`:
```markdown
# Profile — 사용자 관심사 그래프
_AI 자동 관리. rc_ontology가 갱신함._

## 현재 관심사
_(아직 분석 가능한 데이터가 없습니다. 책 한 권을 등록하고 하이라이트 5개를 저장하면 첫 분석이 실행됩니다.)_

## 최근 읽기 패턴
- 읽는 중: 0권
- 완독: 0권
- 마지막 활동: -

## 관심 공백 영역
_(분석 결과가 누적되면 여기 표시됩니다.)_
```

### 단계 6 — 완료 보고 + Obsidian MCP 설정 안내문

생성된 파일 목록과 함께, 사용자의 `file_access` 선택에 맞춰 안내문을 출력한다.

#### `file_access: obsidian-mcp`를 선택한 경우 — Obsidian MCP 설치 안내
```
✓ Reading Copilot 초기 설정 완료

생성된 파일:
- {vault_root}/CLAUDE.md
- {vault_root}/Books/
- {vault_root}/Ontology/themes.md
- {vault_root}/Ontology/profile.md

📌 다음 단계 — Obsidian MCP 연결 (1회만)
1. Obsidian을 설치하고, {vault_root}를 Vault로 추가합니다.
2. Obsidian Community Plugins에서 "Local REST API"를 설치·활성화합니다.
   - Settings → Community plugins → Browse → "Local REST API" → Install → Enable
   - 활성화 후 표시되는 API Key를 복사해 둡니다.
3. Claude 데스크탑 또는 Cowork의 MCP 설정에서 mcp-obsidian을 추가:
   {
     "mcpServers": {
       "obsidian": {
         "command": "uvx",
         "args": ["mcp-obsidian"],
         "env": {
           "OBSIDIAN_API_KEY": "<API Key>",
           "OBSIDIAN_HOST": "127.0.0.1"
         }
       }
     }
   }
4. Claude를 재시작하면 obsidian_* 도구가 자동으로 로드됩니다.

📌 첫 사용
- 다음 메시지부터 책 표지 사진이나 제목을 보내주시면 rc가 자동으로 책 등록을 시작합니다.
```

#### `file_access: filesystem`을 선택한 경우 — 안내 단순화
```
✓ Reading Copilot 초기 설정 완료

생성된 파일:
- {vault_root}/CLAUDE.md
- {vault_root}/Books/
- {vault_root}/Ontology/themes.md
- {vault_root}/Ontology/profile.md

📌 파일 접근
Obsidian 없이 파일 시스템으로 직접 동작합니다. 추가 설정 불필요.

📌 첫 사용
다음 메시지부터 책 표지 사진이나 제목을 보내주시면 rc가 자동으로 책 등록을 시작합니다.
```

#### `git_remote`를 입력한 경우 — 추가 안내
```
📌 GitHub 백업 (선택)
다음 명령을 터미널에서 1회 실행해 Vault를 GitHub와 연결하세요:
  cd "{vault_root}"
  git init
  git remote add origin {git_remote}
  git branch -M main

이후 "rc 푸시해줘"로 rc_git_push가 동작합니다.
```

## 주의
- **기존 파일을 덮어쓰지 않는다.** `{vault_root}`에 이미 CLAUDE.md가 있으면, Configuration 블록만 갱신할지 사용자에게 묻는다.
- 생성 도중 실패하면 어디서 멈췄는지 사용자에게 정확히 보고하고, 재실행 가능하도록 한다.
- 이 스킬은 1회만 실행하면 충분하다. 재설정이 필요하면 사용자가 CLAUDE.md의 Configuration 블록을 직접 수정하면 된다.
