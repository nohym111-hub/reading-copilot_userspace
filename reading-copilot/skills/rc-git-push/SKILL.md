---
name: rc-git-push
description: Reading Copilot 파일의 변경사항을 GitHub에 스냅샷으로 푸시한다
---

# rc-git-push

Reading Copilot 파일을 GitHub에 버전 기록으로 푸시하는 스킬.

`/Users/sojung.noh/Library/Mobile Documents/iCloud~md~obsidian/Documents/reading-copilot_Claude` 경로의 변경사항을 감지해 커밋 메시지와 함께 `https://github.com/nohym111-hub/reading-copilot_Claude`에 자동 푸시한다.

## 실행 순서

아래 단계를 순서대로 실행한다. 각 단계는 이전 단계가 성공해야 진행한다.

### 1. 변경사항 확인

```bash
git -C "/Users/sojung.noh/Library/Mobile Documents/iCloud~md~obsidian/Documents/reading-copilot_Claude" status --short
```

변경사항이 없으면 "변경된 파일이 없습니다. 푸시를 건너뜁니다." 메시지를 출력하고 종료한다.

### 2. 변경된 파일 목록 출력

변경된 파일 목록을 사용자에게 보여준다.

### 3. 스테이징

```bash
git -C "/Users/sojung.noh/Library/Mobile Documents/iCloud~md~obsidian/Documents/reading-copilot_Claude" add -A
```

### 4. 커밋

커밋 메시지는 `[snapshot] YYYY-MM-DD HH:MM` 형식으로 오늘 날짜와 현재 시각을 사용한다.

```bash
git -C "/Users/sojung.noh/Library/Mobile Documents/iCloud~md~obsidian/Documents/reading-copilot_Claude" commit -m "[snapshot] $(date '+%Y-%m-%d %H:%M')"
```

### 5. 푸시

```bash
git -C "/Users/sojung.noh/Library/Mobile Documents/iCloud~md~obsidian/Documents/reading-copilot_Claude" push origin main
```

### 6. 완료 메시지

성공 시: "✓ GitHub 푸시 완료 — [snapshot] YYYY-MM-DD HH:MM"
실패 시: 오류 내용을 출력하고 원인을 분석해 사용자에게 알린다.
