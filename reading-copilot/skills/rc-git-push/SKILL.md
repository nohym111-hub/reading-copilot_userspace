---
name: rc-git-push
description: Reading Copilot 파일의 변경사항을 GitHub에 스냅샷으로 푸시한다
---

# rc-git-push

Reading Copilot Vault의 변경사항을 GitHub에 버전 기록으로 푸시하는 스킬.

## 저장소 (Configuration 참조)
- 경로·옵션은 **CLAUDE.md의 `## ⚙ Configuration` 블록**에서 읽는다.
  - 작업 디렉토리: `vault_root`
  - 원격 저장소: `git_remote` (비어있으면 이 스킬은 비활성. 사용자에게 "git_remote가 비어 있어요"라고 안내하고 종료)
- Configuration이 없으면 → "rc-setup을 먼저 실행해주세요" 한 줄 안내 후 중단.

## 실행 순서

아래 단계를 순서대로 실행한다. 각 단계는 이전 단계가 성공해야 진행한다. 모든 명령은 `vault_root`를 `$VAULT` 환경변수로 치환해 실행한다고 가정한다.

### 1. 변경사항 확인

```bash
git -C "$VAULT" status --short
```

변경사항이 없으면 "변경된 파일이 없습니다. 푸시를 건너뜁니다." 메시지를 출력하고 종료한다.

### 2. 변경된 파일 목록 출력

변경된 파일 목록을 사용자에게 보여준다.

### 3. 스테이징

```bash
git -C "$VAULT" add -A
```

### 4. 커밋

커밋 메시지는 `[snapshot] YYYY-MM-DD HH:MM` 형식으로 오늘 날짜와 현재 시각을 사용한다.

```bash
git -C "$VAULT" commit -m "[snapshot] $(date '+%Y-%m-%d %H:%M')"
```

### 5. 푸시

```bash
git -C "$VAULT" push origin main
```

### 6. 완료 메시지

성공 시: "✓ GitHub 푸시 완료 — [snapshot] YYYY-MM-DD HH:MM"
실패 시: 오류 내용을 출력하고 원인을 분석해 사용자에게 알린다.

## 사전 조건 체크리스트 (최초 1회)
- `$VAULT` 디렉토리에서 `git init`이 끝나 있어야 한다.
- `git remote add origin <Configuration의 git_remote>`로 원격이 연결되어 있어야 한다.
- iCloud 동기화 충돌 파일(`*conflict*`, `.icloud` placeholder)과 `.DS_Store`는 `.gitignore`로 제외 권장.
- 사전 조건이 미충족이면 이 스킬은 **자동 진행하지 않고** 부족한 조건을 한 줄씩 사용자에게 안내한다.
