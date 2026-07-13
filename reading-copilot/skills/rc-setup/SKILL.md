---
name: rc-setup
description: Reading Copilot 신규 설치 스킬. 처음 사용하는 사용자가 자신의 Vault 경로를 지정하면 폴더 구조, Configuration이 채워진 CLAUDE.md, Ontology 시드 파일을 자동 생성한다. "rc 설치해줘", "Reading Copilot 시작하기", "독서 코파일럿 초기 설정", 또는 다른 rc 스킬이 Configuration 부재로 중단된 직후에 트리거된다.
---

# rc_setup — 신규 설치

## 역할
새 사용자가 Reading Copilot을 처음 사용할 때, **최소한의 질문**으로 모든 초기 셋업을 끝낸다.
사용자는 Vault 경로만 답한다. 파일 접근 방식은 묻지 않고 filesystem을 기본 적용한다 — 나머지는 이 스킬이 자율 실행한다.

**이 서비스의 정규 경로는 iCloud + Obsidian이다.** 로컬 마크다운을 Obsidian 그래프 뷰로 보고, iCloud로 모바일까지 동기화할 때 서비스의 진가가 나온다. 그래서 셋업은 "다시는 이사할 필요 없는 목적지"를 처음부터 고르도록 유도한다 — 애플(Mac/iPhone) 사용자에게는 iCloud 안 Obsidian 경로를 1일차부터 기본값으로 제시한다.

## 트리거
- "rc 설치해줘" / "Reading Copilot 시작하기" / "독서 코파일럿 초기 설정"
- 다른 rc 스킬이 CLAUDE.md Configuration 부재로 중단되며 안내한 직후
- 사용자가 명시적으로 rc 스킬셋을 처음 사용한다고 밝힐 때

## 권장 모델
Claude Sonnet 이상 — 디렉토리·파일 생성을 안정적으로 처리해야 한다.

## 동작 흐름

### 단계 1 — Vault 경로 결정

정규 경로는 iCloud + Obsidian이다. 아래 순서로 경로를 정한다 — 각 단계에서 결론이 나면 다음 질문은 생략한다.

**1-a. 기존 Obsidian 볼트 자동 감지**
아래 위치에서 `obsidian.json`을 읽어 사용자가 이미 쓰는 볼트가 있는지 확인한다.
- Mac: `~/Library/Application Support/obsidian/obsidian.json`
- Windows: `%APPDATA%\obsidian\obsidian.json`

기존 볼트가 있으면 → 그 목록을 보여주고 한 줄로 확인한다:
> "이미 쓰고 계신 Obsidian 볼트가 있네요. 여기 안에 독서 기록을 넣을까요, 아니면 새 폴더를 만들까요?"

볼트 안에 넣기로 하면 그 볼트 경로 하위의 `Reading Copilot` 폴더를 `vault_root`로 삼는다.

**⚠ iCloud 위치 가드 (Mac 한정).** 사용자가 실수로 메인 볼트를 로컬에 깔아둔 경우를 잡는다.
선택한 볼트 경로가 iCloud 컨테이너(`~/Library/Mobile Documents/iCloud~md~obsidian/`) 안이 **아니면**, 그대로 진행하지 말고 한 번 되묻는다:
> "찾은 볼트가 로컬에 있어서 아이폰에서는 안 보여요. 모바일까지 쓰시려면 iCloud에 독서 전용 볼트를 새로 만드는 걸 추천해요.
> (a) iCloud에 새로 만들기 [추천] / (b) 그냥 이 로컬 볼트에 넣기(데스크톱 전용)"
- (a) 선택 → 1-b의 Mac 기본 iCloud 경로로 새로 만든다.
- (b) 선택 → 로컬 볼트를 그대로 쓰되, `file_access`·경로는 그대로 두고 진행한다.
- Windows(win32)에서는 이 가드를 적용하지 않는다(로컬이 정상 경로).

→ 확정되면 **1-c로 이동**

**1-b. 기존 볼트가 없으면 — 플랫폼으로 기본 경로 결정**
환경의 platform 값을 확인한다 (질문하지 않는다).
- **Mac (darwin)** → 기본 추천 = iCloud 안 Obsidian 경로:
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Reading Copilot`
  이 경로에 두면 아이폰 Obsidian 앱과 **자동 동기화**된다 (임의 iCloud 폴더는 모바일 Obsidian이 못 연다 — 반드시 이 컨테이너 경로여야 한다).
- **Windows (win32)** → 기본 추천 = 로컬:
  `~/Documents/Reading Copilot`
  (모바일 동기화는 지금 범위 밖. 완료 안내에서 추후 방법을 한 줄 고지한다.)

**1-c. 확정 질문 (`AskUserQuestion` 한 번)**
- "[추천 경로] (Recommended)" → 위에서 정한 기본 경로
- "다른 경로 직접 입력" → 사용자가 절대경로 입력

경로에 `~`가 있으면 홈 디렉토리로 전개하고, `vault_root` 절대경로 1개를 확정한다.

**파일 접근**: `file_access: filesystem`을 기본 적용한다 (묻지 않는다). Obsidian은 이 폴더를 **열기만** 하면 되고, MCP 연결은 선택이다. Obsidian 미설치가 감지돼도 셋업을 멈추지 않는다 — 단계 5 완료 안내에서 설치를 **적극 안내**한다.

### 단계 2 — 폴더 구조 생성
bash 또는 파일 도구로 다음을 생성한다:
```
{vault_root}/
├ README.md                 # 이 위키의 철학 (vault 최상위)
├ Contents/                 # 빈 폴더
├ Ontology/                 # LLM Wiki 온톨로지 (Karpathy 위키 모델)
│  ├ index.md               # 엔티티 레지스트리
│  ├ profile.md             # 독자 레이어 시드
│  ├ people.md              # 인물 (빈 시드)
│  ├ claims.md              # 주장 (빈 시드)
│  └ Concepts/              # 개념 노드 폴더 (빈)
└ CLAUDE.md                 # Configuration 포함된 마스터 컨텍스트
```

> `Skills/` 폴더는 만들지 않는다. 실제 스킬은 Claude Code 플러그인이 제공하므로 Vault에 사본을 둘 필요가 없다.

이미 존재하는 폴더/파일은 **덮어쓰지 않는다**. 사용자에게 알리고 건너뛴다.

### 단계 3 — CLAUDE.md 자동 생성
아래 템플릿의 `{ ... }` 자리를 단계 1의 응답으로 채워 `{vault_root}/CLAUDE.md`로 저장한다.

```markdown
# Reading Copilot — CLAUDE.md
_모든 Claude 세션에서 자동으로 로드되는 마스터 컨텍스트_

---

## ⚙ Configuration (Single Source of Truth)

> 이 블록은 rc 스킬셋의 **중앙 설정**입니다. 모든 rc 스킬은 동작 전에 이 블록을 읽어 경로·옵션을 결정합니다.
> Vault 위치를 옮기거나 옵션을 바꿔야 하면 **이 블록만** 수정하세요. 스킬 파일들은 건드릴 필요가 없습니다.

```yaml
vault_root: "{vault_root}"
books_dir: "Contents"          # vault_root 기준 상대경로 (후행 슬래시 없음)
ontology_dir: "Ontology"       # vault_root 기준 상대경로 (후행 슬래시 없음)
file_access: "filesystem"      # 기본값. Obsidian을 이미 쓰고 있다면 "obsidian-mcp"로 직접 바꿔도 된다
obsidian_mcp_prefix: ""        # file_access를 obsidian-mcp로 바꿀 때만 사용. MCP root가 vault 상위 폴더면 폴더명 입력
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
- **`{vault_root}/{ontology_dir}/`**: LLM Wiki 온톨로지 (AI 자동 관리) — index(레지스트리)·profile(독자 레이어)·Concepts/(개념 노드). Content 노드는 Contents 노트 자체. 생성·갱신 규칙은 rc_ontology 스킬 보유.
- 실제 실행 스킬은 Claude Code 플러그인에서 로드된다 (Vault에 스킬 사본을 두지 않는다).
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

## 핵심 원칙

1. **Single Input** — 사용자는 입력만. 메뉴·모드 선택 없음
2. **Intent-First** — 내가 먼저 의도를 판단. 사용자는 확인만
3. **Ambient Persistence** — 세션이 끊겨도 Vault가 컨텍스트를 유지
4. **Seamless Capture** — 순간을 놓치지 않는다. 저장은 빠르게, 마찰 없이
5. **Human + AI 분리** — ai_ 접두사 필드는 스킬만 쓴다. 사용자 LAYER 1·2만 편집 가능

## 세션 시작 시 체크리스트

새 세션이 시작될 때:
1. Ontology/profile.md 로드 → 현재 관심사·읽는 책 파악
2. Contents/ 폴더에서 status: explored인 파일 확인
3. 마지막 수정일 확인 → 2일+ 경과 시 rc_talk Remind 모드 실행
4. 이후 사용자 입력을 rc로 처리

## 데이터 구분 원칙

| 구분 | 생성 주체 | 필드/섹션 | 편집 권한 |
|---|---|---|---|
| Human Data | 사용자 | LAYER 1·2 / 하이라이트·인상 섹션 | 사용자만 |
| AI Data | 스킬 | ai_* 필드 / AI 분석 섹션 | 스킬만 |
| Human+AI | 대화 | 대화 기록 섹션 | 사용자 발화만 |
```

### 단계 4 — Ontology 시드 파일 생성 (LLM Wiki 모델)

`{vault_root}/Ontology/Concepts/` 폴더를 만들고, 아래 시드 파일들을 생성한다. 개념 노드 생성·규칙 적용은 첫 책부터 rc_ontology가 담당한다. **온톨로지 규칙(명명·점수·갱신·고아)은 rc_ontology 스킬이 단일 보유하며, Vault엔 규칙 사본을 두지 않는다.**

`{vault_root}/Ontology/profile.md` (독자 레이어 시드):
```markdown
# 독자 프로파일 (Reader Layer)
_AI 자동 관리. rc_ontology가 갱신._
## 관심사 그래프
_(책과 하이라이트가 쌓이면 채워집니다.)_
## 탐색 공백
## 시간축 변화
```

`{vault_root}/README.md`(vault 최상위), `{vault_root}/Ontology/index.md`, `people.md`, `claims.md`는 헤더만 있는 빈 시드로 생성한다(rc_ontology가 채움).

### 단계 5 — 완료 보고 + Obsidian 적극 안내

생성된 파일 목록과 함께 완료 안내문을 출력한다. **Obsidian이 이 서비스의 정규 뷰어이므로, 미설치가 감지되면 설치를 적극 안내한다** (셋업을 막지는 않는다 — 사용자는 지금 바로 책 등록을 시작할 수 있다).

Obsidian 설치 여부는 단계 1-a의 `obsidian.json` 감지 결과로 판단한다.

```
✓ Reading Copilot 초기 설정 완료

생성된 파일:
- {vault_root}/CLAUDE.md
- {vault_root}/Contents/
- {vault_root}/Ontology/profile.md
- {vault_root}/Ontology/Concepts/

📌 첫 사용
다음 메시지부터 책 표지 사진이나 제목을 보내주시면 rc가 자동으로 책 등록을 시작합니다. 지금 바로 시작하셔도 됩니다.
```

이어서, **Obsidian 미설치가 감지된 경우** 아래 안내를 덧붙인다 (이미 설치돼 있으면 생략):

```
📖 Obsidian으로 보면 진가가 나옵니다
지금은 마크다운 파일이라 하나씩 열어야 보이지만, Obsidian으로 이 폴더를 열면
책·개념·하이라이트가 그래프로 연결돼 한눈에 보입니다. 3분이면 됩니다:

  1. https://obsidian.md 에서 Obsidian을 설치하세요 (무료)
  2. "Open folder as vault" → 이 폴더를 선택하세요:
     {vault_root}
  3. 끝. 앞으로 쌓이는 기록이 자동으로 이 볼트에 들어옵니다.
```

**Vault가 iCloud 경로(Mac)인 경우** 모바일 안내를 추가한다:

```
📱 아이폰에서도 보려면
  1. App Store에서 Obsidian 앱을 설치하세요
  2. "Open vault from iCloud" → 방금 만든 볼트를 선택하세요
  → Mac과 아이폰이 iCloud로 자동 동기화됩니다.
```

**Vault가 로컬 경로(Windows 등)인 경우** 모바일 대신 아래 한 줄만 고지한다:

```
📱 모바일 동기화는 지금은 지원 범위 밖입니다. 나중에 원하시면 Obsidian Sync 등으로 연결할 수 있어요.
```

마지막으로, 고급 사용자용 한 줄(항상 생략 가능):

```
⚙ (고급·선택) Obsidian에서 Claude가 직접 읽고 쓰게 하려면 CLAUDE.md의 file_access를 "obsidian-mcp"로 바꾸고 "Local REST API" 플러그인 + mcp-obsidian MCP를 연결하세요. 필요할 때 하시면 됩니다.
```

## 주의
- **기존 파일을 덮어쓰지 않는다.** `{vault_root}`에 이미 CLAUDE.md가 있으면, Configuration 블록만 갱신할지 사용자에게 묻는다.
- 생성 도중 실패하면 어디서 멈췄는지 사용자에게 정확히 보고하고, 재실행 가능하도록 한다.
- 이 스킬은 1회만 실행하면 충분하다. 재설정이 필요하면 사용자가 CLAUDE.md의 Configuration 블록을 직접 수정하면 된다.
