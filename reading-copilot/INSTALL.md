# Reading Copilot — 설치 패키지 설계

새 사용자가 Reading Copilot(rc 스킬셋)을 설치하고 첫 사용까지 도달하는 흐름과, 그것을 가능하게 하는 패키지 구조를 정의한다.

---

## 1. 설계 원칙

1. **단일 설정 진입점 (Single Source of Truth)** — 모든 경로·옵션은 사용자 Vault의 `CLAUDE.md` ⚙ Configuration 블록 한 곳에서만 관리한다. 스킬 파일에는 절대경로가 없다.
2. **자율 설치 (rc-setup 1회 실행)** — 사용자는 Vault 경로만 지정한다. 폴더 구조·CLAUDE.md·Ontology 시드는 rc-setup이 자동 생성한다.
3. **유연한 파일 접근** — Obsidian MCP가 있으면 그것을, 없으면 filesystem(Read/Write/Edit)을 사용한다. 둘 다 Configuration의 `file_access` 한 줄로 전환.
4. **선택적 백업** — GitHub 푸시는 사용 시에만 활성. `git_remote`가 비어 있으면 rc_git_push는 조용히 비활성.

---

## 2. 패키지 구성

```
reading-copilot/                          # 배포 패키지 루트
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 마니페스트
├── skills/
│   ├── rc/SKILL.md                       # 라우터
│   ├── rc-setup/SKILL.md                 # 신규 설치 (NEW)
│   ├── rc-register/SKILL.md              # 책 등록
│   ├── rc-save/SKILL.md                  # 하이라이트 저장
│   ├── rc-talk/SKILL.md                  # 대화·유도·요약
│   ├── rc-ontology/SKILL.md              # 온톨로지 분석
│   └── rc-git-push/SKILL.md              # GitHub 백업 (선택)
├── INSTALL.md                            # 이 문서
└── README.md                             # 패키지 개요·라이선스
```

스킬 소스의 **단일 원본**은 이 plugin repo(`RC_claude`)의 `skills/<name>/SKILL.md`다. 개발자는 이 경로에서 직접 편집한다 — 데이터 Vault(`Reading Copilot_claude`, Books/Ontology)와 스킬 소스 repo(`RC_claude`)는 분리되어 있으며, 별도의 Vault `Skills/` 사본을 두지 않는다.

---

## 3. 플러그인 마니페스트 (`.claude-plugin/plugin.json`)

```json
{
  "name": "reading-copilot",
  "version": "0.3.0",
  "description": "에이전틱 독서 파트너 — 책 등록, 하이라이트 저장, 대화, 온톨로지 분석을 자율 실행하는 스킬셋",
  "author": {
    "name": "Sojung Noh",
    "email": "nohym111@gmail.com"
  },
  "skills": [
    "skills/rc",
    "skills/rc-setup",
    "skills/rc-register",
    "skills/rc-save",
    "skills/rc-talk",
    "skills/rc-ontology",
    "skills/rc-git-push"
  ],
  "recommended_mcps": [
    {
      "name": "mcp-obsidian",
      "purpose": "Vault 파일에 직접 읽고 쓰기 위해 1순위로 사용. 미설치 시 filesystem 폴백."
    }
  ],
  "entry_skill": "rc-setup",
  "homepage": "https://github.com/<owner>/reading-copilot"
}
```

`entry_skill: rc-setup`은 사용자가 플러그인 설치 직후 자동으로 안내받을 첫 스킬이다.

---

## 4. 새 사용자 설치 흐름

### Step 1 — 플러그인 설치
사용자는 다음 중 하나의 방법으로 패키지를 받는다:

- **GitHub 저장소**: `https://github.com/<owner>/reading-copilot`
  Claude의 `/plugin install <repo-url>` 명령으로 설치.
- **로컬 폴더**: 패키지를 압축 해제한 디렉토리를 가리키며
  `/plugin install <local-path>` 실행.
- **마켓플레이스**(향후): Anthropic 또는 커뮤니티 마켓플레이스에 등록되면 클릭 한 번.

설치 후 Claude를 재시작하면 7개 스킬이 로드된다.

### Step 2 — 첫 대화에서 rc-setup 실행
사용자는 다음 중 하나로 시작한다:
- "rc 설치해줘"
- "Reading Copilot 시작하기"
- 책 표지 사진을 곧바로 보냄 → rc가 Configuration 부재를 감지하고 rc-setup으로 라우팅

rc-setup은 `AskUserQuestion`으로 다음을 묻는다:
1. Vault 경로 (3가지 추천 + 직접 입력)
2. 파일 접근 방식 (obsidian-mcp / filesystem)
3. GitHub 백업 사용 여부 + URL (선택)

### Step 3 — 자동 생성
rc-setup이 자율 실행한다:
- Vault 폴더 구조 생성: `Books/`, `Ontology/` (스킬 소스는 별도 plugin repo `RC_claude`에 있으므로 Vault에 `Skills/`를 만들지 않는다)
- `CLAUDE.md` 작성 — Configuration 블록에 사용자 응답 채움
- `Ontology/README.md`, `Ontology/profile.md`, `Ontology/Concepts/` 등 LLM Wiki 시드 작성

### Step 4 — Obsidian MCP 안내 (선택)
`obsidian-mcp`를 택한 경우, rc-setup이 1회용 설치 가이드를 출력:
- Obsidian Vault 추가
- "Local REST API" 커뮤니티 플러그인 설치/활성화
- MCP 설정 JSON 스니펫

사용자는 위 안내대로 1회 설정 후 Claude를 재시작한다.

### Step 5 — 첫 책 등록
재시작 후 사용자가 책 표지를 보내면 rc → rc_register가 자동 실행되어 첫 책이 Vault에 등록된다.

---

## 5. 업그레이드/이전 시나리오

### Vault 경로를 옮기고 싶을 때
1. 새 위치로 폴더 통째 이동 (드래그 앤 드롭).
2. `CLAUDE.md`의 Configuration 블록에서 `vault_root` 값만 새 절대경로로 변경.
3. (Obsidian 사용 시) Obsidian에서 Vault 위치 재지정.
4. (GitHub 백업 사용 시) `git remote set-url origin <URL>`이 필요할 수도 있음.

**스킬 파일은 건드릴 필요 없음.**

### 다른 컴퓨터로 동기화
- iCloud 경로를 `vault_root`로 쓰면 자동 동기화.
- 또는 GitHub에 Vault를 푸시(rc_git_push)하고, 새 기기에서 clone.

### 플러그인 업데이트
- `/plugin update reading-copilot` 한 줄.
- Configuration은 사용자 Vault의 `CLAUDE.md`에 있으므로 업데이트 영향 없음.

---

## 6. 개발자 배포 워크플로우

1. 스킬 소스는 이 repo(`RC_claude`)의 `skills/<name>/SKILL.md`에서 **직접 편집**한다 — 소스 = 패키지이므로 별도 복사 단계가 없다 (예전의 `Vault/Skills/*.md → skills/<name>/SKILL.md` 매핑은 폐지).
2. `.claude-plugin/plugin.json`과 `marketplace.json`을 §3 양식에 맞게 유지한다.
3. GitHub 저장소에 푸시하거나 `.plugin` 압축 파일로 배포.
4. 편집한 스킬을 로컬에 반영하려면 `/plugin update reading-copilot`(또는 재설치) 후 Claude 재시작.
5. 버전 태깅: SemVer (`0.2.0` → 기능 추가 시 `0.3.0`, breaking change 시 `1.0.0`).

---

## 7. 호환성 메모

- 이 패키지는 **Claude Code v1.x / Cowork mode**를 가정한다.
- Obsidian MCP는 Obsidian 1.4 이상 + "Local REST API" 플러그인 0.5 이상에서 검증됨.
- Vault 경로에 공백·한글이 포함되어도 동작하지만, 항상 큰따옴표(`"..."`)로 감싼다.
- iCloud Vault 사용 시 `.icloud` placeholder 파일이 git에 커밋되지 않도록 `.gitignore` 권장:
  ```
  .DS_Store
  *.icloud
  *conflict*
  ```
