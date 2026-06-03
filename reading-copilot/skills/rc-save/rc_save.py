#!/usr/bin/env python3
"""
rc_save.py — Reading Copilot 하이라이트 저장 스크립트 v2
(Claude OCR JSON → Markdown 변환 → Obsidian 저장)

사용법:
    echo '<JSON>' | python rc_save.py --book "책 제목" --vault "/path/to/vault"
    python rc_save.py --book "책 제목" --vault "/path/to/vault" < ocr_result.json

Claude가 출력한 JSON을 stdin으로 받아서 처리한다.
Claude는 OCR + 마킹 감지만 하고, 이 스크립트가 포맷·저장·검증을 담당한다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


# ── 상수 ─────────────────────────────────────────────────────────────────────

BOOKS_DIR      = "Books"
SECTION_HEADER = "## 하이라이트 & 메모 (Human)"
SENTENCE_END   = re.compile(r'[.?!」"\'。]\s*$')
# 한국어 문장 종결: 한글 뒤 "다"로 끝나는 패턴 (이다/하다/었다/있다 등 포괄)
# 또는 "요"·"죠"·"나"·"군"으로 끝나는 구어체 종결형
KO_SENTENCE_END = re.compile(r'[가-힣]다\s*$|[가-힣][요죠나군]\s*$')


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    """파일명/제목 비교용 정규화: 소문자 + 언더스코어·하이픈 → 공백."""
    return re.sub(r"[_\-]+", " ", s).lower().strip()


def _is_korean_boundary(prev_char: str, next_char: str) -> bool:
    """두 글자가 모두 한글이면 어절 경계 → 공백 없이 붙인다."""
    return ('가' <= prev_char <= '힣') and ('가' <= next_char <= '힣')


# ── JSON 파싱 ─────────────────────────────────────────────────────────────────

def parse_input(raw: str) -> list[dict]:
    """
    stdin에서 받은 JSON을 파싱한다.

    입력 형식 (페이지 배열):
    [
      {
        "page": 84,
        "quotes": [
          {
            "highlighted": "마킹된 텍스트 원문",
            "before":      "하이라이트 직전 1문장 (없으면 빈 문자열)",
            "after":       "하이라이트 직후 1문장 (없으면 빈 문자열)",
            "memo":        "여백 손글씨 메모   (없으면 빈 문자열)"
          }
        ]
      }
    ]
    """
    raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}", file=sys.stderr)
        print(f"입력 원본 (앞 300자):\n{raw[:300]}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict):
        data = [data]

    return data


# ── 페이지 경계 병합 ──────────────────────────────────────────────────────────

def should_merge(prev_hl: str, next_hl: str) -> bool:
    """이전 페이지 마지막 quote와 다음 페이지 첫 quote가 이어지는지 판단. 확신 없으면 False."""
    prev = prev_hl.rstrip()
    nxt  = next_hl.lstrip()

    if not prev or not nxt:
        return False
    if SENTENCE_END.search(prev):       # 종결부호로 끝남 → 새 문장
        return False
    if KO_SENTENCE_END.search(prev):    # 한국어 종결어미로 끝남 → 새 문장
        return False
    if nxt[0].isupper() and prev[-1] not in ("-", "—"):  # 대문자 시작 → 새 문장
        return False
    return True


def merge_two(q1: dict, q2: dict, page1, page2) -> dict:
    t1 = q1["highlighted"].rstrip()
    t2 = q2["highlighted"].lstrip()
    if t1.endswith("-"):
        # 영어 하이픈 분절: 하이픈 제거 후 붙임
        merged_hl = t1[:-1] + t2
    elif t1 and t2 and _is_korean_boundary(t1[-1], t2[0]):
        # 한국어 어절 경계: 공백 없이 붙임
        merged_hl = t1 + t2
    else:
        merged_hl = t1 + " " + t2
    page_range  = f"{page1}–{page2}" if page1 and page2 else (page1 or page2)
    memo1 = q1.get("memo", "").strip()
    memo2 = q2.get("memo", "").strip()
    return {
        "highlighted": merged_hl,
        "before":      q1.get("before", ""),
        "after":       q2.get("after", ""),
        "memo":        " / ".join(filter(None, [memo1, memo2])),
        "page":        page_range,
    }


def flatten_and_merge(pages: list[dict]) -> list[dict]:
    """페이지 배열 → quote 리스트 (페이지 경계 병합 포함)."""
    for pd in pages:
        pnum = pd.get("page")
        for q in pd.get("quotes", []):
            q["page"] = pnum

    final = []
    for i, pd in enumerate(pages):
        quotes = pd.get("quotes", [])
        if not quotes:
            continue

        for j, q in enumerate(quotes):
            is_last   = (j == len(quotes) - 1)
            has_next  = (i < len(pages) - 1)

            if is_last and has_next:
                nq_list = pages[i + 1].get("quotes", [])
                if nq_list and should_merge(q.get("highlighted", ""), nq_list[0].get("highlighted", "")):
                    final.append(merge_two(q, nq_list[0], pd.get("page"), pages[i + 1].get("page")))
                    pages[i + 1]["quotes"] = nq_list[1:]
                    continue

            final.append(q)

    return final


# ── Markdown 포맷 변환 ────────────────────────────────────────────────────────

def format_quote(q: dict, today: str) -> str:
    """
    quote dict → Obsidian 저장 포맷

    > "before **highlighted** after"
    > — p.XX | YYYY-MM-DD
    메모: ...
    """
    highlighted = q.get("highlighted", "").strip()
    before      = q.get("before", "").strip()
    after       = q.get("after", "").strip()
    memo        = q.get("memo", "").strip()
    page        = q.get("page")

    parts = []
    if before:
        parts.append(before)
    parts.append(f"**{highlighted}**")
    if after:
        parts.append(after)

    body     = " ".join(parts)
    page_str = f"p.{page}" if page else "p.?"

    lines = [f'> "{body}"', f"> — {page_str} | {today}"]
    if memo:
        lines.append(f"메모: {memo}")

    return "\n".join(lines)


# ── Obsidian 노트 업데이트 ────────────────────────────────────────────────────

def find_book_file(vault: Path, book_title: str) -> Path | None:
    books_dir = vault / BOOKS_DIR
    if not books_dir.exists():
        print(f"❌ Books 폴더 없음: {books_dir}", file=sys.stderr)
        return None

    needle     = normalize(book_title)
    candidates = [
        f for f in books_dir.glob("*.md")
        if needle in normalize(f.stem) or normalize(f.stem) in needle
    ]

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        print(f"⚠ 후보 여러 개, 첫 번째 사용: {[c.name for c in candidates]}", file=sys.stderr)
        return candidates[0]

    print(f"❌ '{book_title}' 파일 없음", file=sys.stderr)
    return None


def update_note(note_path: Path, entries: list[str], n_quotes: int) -> None:
    content = note_path.read_text(encoding="utf-8")

    # highlights_count 증가
    def inc(m):
        return f"highlights_count: {int(m.group(1)) + n_quotes}"
    content = re.sub(r"highlights_count:\s*(\d+)", inc, content)

    # status: to-read → reading
    content = re.sub(r'(status:\s*)"?to-read"?', r"\1reading", content)

    # 섹션 없으면 파일 끝에 생성
    if SECTION_HEADER not in content:
        content += f"\n\n{SECTION_HEADER}\n"

    insertion = "\n\n".join(entries) + "\n"
    content   = content.replace(
        SECTION_HEADER + "\n",
        SECTION_HEADER + "\n\n" + insertion,
        1
    )

    note_path.write_text(content, encoding="utf-8")


def verify(note_path: Path, entries: list[str]) -> list[str]:
    content = note_path.read_text(encoding="utf-8")
    return [
        e.split("\n")[0][:40]
        for e in entries
        if e.split("\n")[0][:40] not in content
    ]


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="rc_save: Claude OCR JSON → Obsidian 저장")
    parser.add_argument("--book",  required=True, help="책 제목")
    parser.add_argument("--vault", required=True, help="Obsidian vault 루트 경로")
    parser.add_argument("--json-file", default=None, help="OCR JSON 파일 경로 (저장 후 자동 삭제)")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    today = date.today().isoformat()

    if args.json_file:
        json_path = Path(args.json_file).expanduser().resolve()
        raw = json_path.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        print("❌ stdin이 비어 있어요. Claude OCR 결과를 파이프로 전달해주세요.", file=sys.stderr)
        sys.exit(1)

    pages        = parse_input(raw)
    total_images = len(pages)

    note_path = find_book_file(vault, args.book)
    if not note_path:
        sys.exit(1)

    final_quotes = flatten_and_merge(pages)

    if not final_quotes:
        print("ℹ 저장할 하이라이트가 없어요.")
        sys.exit(0)

    entries = [format_quote(q, today) for q in final_quotes]

    update_note(note_path, entries, len(entries))

    failed = verify(note_path, entries)
    if failed:
        print(f"⚠ 저장 검증 실패 ({len(failed)}개):", file=sys.stderr)
        for f in failed:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(2)

    # 임시 JSON 파일 삭제 (저장 성공 후)
    if args.json_file:
        try:
            json_path.unlink()
        except OSError:
            pass

    print(f"✓ {total_images}장 처리 완료 | 하이라이트 {len(entries)}개 저장 | {note_path.stem}")


if __name__ == "__main__":
    main()
