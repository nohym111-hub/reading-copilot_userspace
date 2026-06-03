# Reading Copilot — Claude Skill Pack

**에이전틱 독서 파트너.** 책 표지 사진 한 장만 보내면 자동으로 책을 인식·등록하고, 하이라이트를 저장하고, 대화로 생각을 정리해주고, 누적된 데이터에서 당신의 관심사 지도를 그려주는 Claude Code 스킬셋입니다.

> 사용자는 입력만 한다. 나머지는 스킬이 판단하고 실행하고 저장한다.

---

## 무엇을 할 수 있나

- 📷 **책 표지 사진** → 책 자동 식별 + Obsidian Vault에 등록
- ✍️ **본문 페이지 사진 / 텍스트** → 하이라이트로 즉시 저장 (OCR 포함)
- 💬 **자연스러운 대화** → 책에 대한 질문, 추천, 정리 요약
- 🧠 **온톨로지 자동 분석** → 하이라이트가 쌓이면 관심사 그래프·테마 사전을 자동 갱신
- ☁️ **GitHub 백업 (선택)** → Vault 변경사항을 깃 스냅샷으로 푸시

## 포함된 스킬 7종

| 스킬 | 역할 |
|---|---|
| `rc` | 라우터 — 모든 입력의 첫 관문, 의도를 분류해 적절한 스킬로 전달 |
| `rc-setup` | 초기 설치 — 1회 실행으로 Vault·Configuration 자동 생성 |
| `rc-register` | 책 식별 + Vault에 1책 1파일로 등록 |
| `rc-save` | 하이라이트·메모 즉시 저장 (이미지 OCR 포함) |
| `rc-talk` | 대화·유도·요약·추천 |
| `rc-ontology` | 지식 온톨로지 (테마/관심사 그래프) 자동 갱신 |
| `rc-git-push` | Vault → GitHub 스냅샷 백업 (선택) |

## 사전 요구사항

- **필수**: [Claude Code](https://claude.ai/code) (CLI / Desktop / IDE 어느 것이든)
- **권장**: [Obsidian](https://obsidian.md) + "Local REST API" 커뮤니티 플러그인 + [`mcp-obsidian`](https://github.com/MarkusPfundstein/mcp-obsidian)
  - 없어도 동작합니다 — 파일 시스템으로 직접 읽고 쓰는 폴백 모드 지원

## 설치 (3단계)

### 1. 패키지 받기
이 폴더를 통째로 받습니다 (zip 또는 `git clone`).

### 2. Claude Code 플러그인으로 설치
```bash
/plugin install <RC_claude 폴더 경로>
```
설치 후 Claude를 재시작하면 7개 스킬이 자동 로드됩니다.

### 3. 첫 대화에서 초기화
```
rc 설치해줘
```
`rc-setup`이 자동 실행되어 다음을 묻습니다:
- Vault를 어디에 둘지 (iCloud Obsidian / 로컬 / 직접 입력)
- 파일 접근 방식 (`obsidian-mcp` 권장 / `filesystem` 폴백)
- GitHub 백업 사용 여부 (선택)

응답 후 Vault 폴더 구조와 `CLAUDE.md`(Configuration 블록 포함)가 자동 생성됩니다.

### 4. 사용 시작
책 표지 사진을 한 장 보내보세요. `rc`가 자동으로 `rc-register`를 호출해 첫 책을 등록합니다.

## 동작 원리 (한 줄)

스킬들은 **절대경로를 하드코딩하지 않습니다.** 모든 경로·옵션은 사용자 Vault의 `CLAUDE.md` 안 `## ⚙ Configuration` 블록 한 곳에서만 관리됩니다. Vault를 옮기고 싶으면 그 블록의 `vault_root` 값만 바꾸면 됩니다.

자세한 설계 의도와 패키지 구조는 [`INSTALL.md`](./INSTALL.md), 서비스 사양은 [`Docs/PRD_v1.0.md`](./Docs/PRD_v1.0.md) 참고.

## 라이선스

작성자 본인 사용 + 지인 공유 목적. 별도 라이선스 부여 전까지 외부 재배포 비권장.

---

_Made with 🤍 by Sojung Noh ([@nohym111](mailto:nohym111@gmail.com))_
