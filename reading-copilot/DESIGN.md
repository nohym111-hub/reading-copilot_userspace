# Reading Copilot — 설계 문서

패키지가 왜 이렇게 구성되어 있는지, 내부 구조와 개발자 배포 워크플로우를 정의한다. 사용자 설치 안내는 [`README.md`](./README.md)의 "30초 시작하기"를 본다 — 이 문서는 그 뒤에 있는 설계 근거용이다.

---

## 1. 설계 원칙

1. **단일 설정 진입점 (Single Source of Truth)** — 모든 경로·옵션은 사용자 Vault의 `CLAUDE.md` ⚙ Configuration 블록 한 곳에서만 관리한다. 스킬 파일에는 절대경로가 없다.
2. **자율 설치 (rc-setup 1회 실행)** — 사용자는 Vault 경로만 지정한다. 폴더 구조·CLAUDE.md·Ontology 시드는 rc-setup이 자동 생성한다.
3. **유연한 파일 접근** — Obsidian MCP가 있으면 그것을, 없으면 filesystem(Read/Write/Edit)을 사용한다. 둘 다 Configuration의 `file_access` 한 줄로 전환.

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
│   └── rc-ontology/SKILL.md              # 온톨로지 분석
├── DESIGN.md                             # 이 문서
└── README.md                             # 패키지 개요·Quickstart·라이선스
```

스킬 소스의 **단일 원본**은 이 plugin repo(`RC_claude`)의 `skills/<name>/SKILL.md`다. 개발자는 이 경로에서 직접 편집한다 — 데이터 Vault(`Reading Copilot_claude`, Contents/Ontology)와 스킬 소스 repo(`RC_claude`)는 분리되어 있으며, 별도의 Vault `Skills/` 사본을 두지 않는다.

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
    "skills/rc-ontology"
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

## 4. 업그레이드/이전 시나리오

### Vault 경로를 옮기고 싶을 때
1. 새 위치로 폴더 통째 이동 (드래그 앤 드롭).
2. `CLAUDE.md`의 Configuration 블록에서 `vault_root` 값만 새 절대경로로 변경.
3. (Obsidian 사용 시) Obsidian에서 Vault 위치 재지정.

**스킬 파일은 건드릴 필요 없음.**

### 다른 컴퓨터로 동기화
- iCloud 경로를 `vault_root`로 쓰면 자동 동기화.

### 플러그인 업데이트
- `/plugin update reading-copilot` 한 줄.
- Configuration은 사용자 Vault의 `CLAUDE.md`에 있으므로 업데이트 영향 없음.

---

## 5. 개발자 배포 워크플로우

1. 스킬 소스는 이 repo(`RC_claude`)의 `skills/<name>/SKILL.md`에서 **직접 편집**한다 — 소스 = 패키지이므로 별도 복사 단계가 없다 (예전의 `Vault/Skills/*.md → skills/<name>/SKILL.md` 매핑은 폐지).
2. `.claude-plugin/plugin.json`과 `marketplace.json`을 §3 양식에 맞게 유지한다.
3. GitHub 저장소에 푸시하거나 `.plugin` 압축 파일로 배포.
4. 편집한 스킬을 로컬에 반영하려면 `/plugin update reading-copilot`(또는 재설치) 후 Claude 재시작.
5. 버전 태깅: SemVer (`0.2.0` → 기능 추가 시 `0.3.0`, breaking change 시 `1.0.0`).

---

## 6. 호환성 메모

- 이 패키지는 **Claude Code v1.x / Cowork mode**를 가정한다.
- Obsidian MCP는 Obsidian 1.4 이상 + "Local REST API" 플러그인 0.5 이상에서 검증됨.
- Vault 경로에 공백·한글이 포함되어도 동작하지만, 항상 큰따옴표(`"..."`)로 감싼다.
- iCloud Vault 사용 시 `.icloud` placeholder 파일이 git에 커밋되지 않도록 `.gitignore` 권장:
  ```
  .DS_Store
  *.icloud
  *conflict*
  ```
