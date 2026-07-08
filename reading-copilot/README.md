# Reading Copilot — Claude Skill Pack

**에이전틱 독서 파트너.** 책 표지 사진 한 장만 보내면 자동으로 책을 인식·등록하고, 하이라이트를 저장하고, 대화로 생각을 정리해주고, 누적된 데이터에서 당신의 관심사 지도를 그려주는 Claude Code 스킬셋입니다.

> 사용자는 입력만 한다. 나머지는 스킬이 판단하고 실행하고 저장한다.

---

## 30초 시작하기

```bash
/plugin install <RC_claude 폴더 경로>
```
1. 위 명령으로 설치 후 Claude 재시작
2. `rc 설치해줘` 전송 → Vault 저장 위치만 답하면 끝 (추가 설정 없음)
3. 책 표지 사진 한 장 전송 → 첫 책이 자동 등록됩니다

---

## 무엇을 할 수 있나

- 📷 **책 표지 사진** → 책 자동 식별 + Obsidian Vault에 등록
- ✍️ **본문 페이지 사진 / 텍스트** → 하이라이트로 즉시 저장 (OCR 포함)
- 💬 **자연스러운 대화** → 책에 대한 질문, 추천, 정리 요약
- 🧠 **온톨로지 자동 분석** → 하이라이트가 쌓이면 관심사 그래프·테마 사전을 자동 갱신

## 포함된 스킬 6종

| 스킬 | 역할 |
|---|---|
| `rc` | 라우터 — 모든 입력의 첫 관문, 의도를 분류해 적절한 스킬로 전달 |
| `rc-setup` | 초기 설치 — 1회 실행으로 Vault·Configuration 자동 생성 |
| `rc-register` | 책 식별 + Vault에 1책 1파일로 등록 |
| `rc-save` | 하이라이트·메모 즉시 저장 (이미지 OCR 포함) |
| `rc-talk` | 대화·유도·요약·추천 |
| `rc-ontology` | 지식 온톨로지 (테마/관심사 그래프) 자동 갱신 |

## 사전 요구사항

- **필수**: [Claude Code](https://claude.ai/code) (CLI / Desktop / IDE 어느 것이든) — 이것만 있으면 바로 시작할 수 있습니다
- **선택**: [Obsidian](https://obsidian.md) + "Local REST API" 커뮤니티 플러그인 + [`mcp-obsidian`](https://github.com/MarkusPfundstein/mcp-obsidian)
  - 설치 시점에 필요하지 않습니다. 나중에 Obsidian에서 Vault를 직접 보고 싶어지면 그때 연결하면 됩니다.

## 동작 원리 (한 줄)

스킬들은 **절대경로를 하드코딩하지 않습니다.** 모든 경로·옵션은 사용자 Vault의 `CLAUDE.md` 안 `## ⚙ Configuration` 블록 한 곳에서만 관리됩니다. Vault를 옮기고 싶으면 그 블록의 `vault_root` 값만 바꾸면 됩니다.

패키지 내부 구조·설계 원칙·업그레이드 시나리오·개발자 배포 워크플로우는 [`DESIGN.md`](./DESIGN.md) 참고.

## 라이선스

작성자 본인 사용 + 지인 공유 목적. 별도 라이선스 부여 전까지 외부 재배포 비권장.

---

_Made with 🤍 by Sojung Noh ([@nohym111](mailto:nohym111@gmail.com))_
