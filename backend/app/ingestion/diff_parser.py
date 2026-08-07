import re
from typing import List, Dict, Any, Optional

class DiffHunk:
    def __init__(self, old_start: int, old_lines: int, new_start: int, new_lines: int, header: str):
        self.old_start = old_start
        self.old_lines = old_lines
        self.new_start = new_start
        self.new_lines = new_lines
        self.header = header
        self.lines: List[Dict[str, Any]] = []

class FileDiff:
    def __init__(self, old_path: str, new_path: str, is_new: bool = False, is_deleted: bool = False):
        self.old_path = old_path
        self.new_path = new_path
        self.is_new = is_new
        self.is_deleted = is_deleted
        self.hunks: List[DiffHunk] = []

    @property
    def filename(self) -> str:
        return self.new_path if self.new_path != "/dev/null" else self.old_path

    def get_changed_line_ranges(self) -> List[tuple[int, int]]:
        ranges = []
        for hunk in self.hunks:
            new_lines = [l["new_line"] for l in hunk.lines if l["new_line"] is not None]
            if new_lines:
                ranges.append((min(new_lines), max(new_lines)))
            elif hunk.new_start > 0:
                ranges.append((hunk.new_start, hunk.new_start + max(0, hunk.new_lines - 1)))
        return ranges

def parse_unified_diff(diff_text: str) -> List[FileDiff]:
    files: List[FileDiff] = []
    current_file: Optional[FileDiff] = None

    hunk_header_re = re.compile(r'@@\s*-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s*@@')

    lines = diff_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("diff --git"):
            parts = line.split(" ")
            old_path = parts[2][2:] if len(parts) > 2 and parts[2].startswith("a/") else ""
            new_path = parts[3][2:] if len(parts) > 3 and parts[3].startswith("b/") else ""
            current_file = FileDiff(old_path=old_path, new_path=new_path)
            files.append(current_file)
            i += 1
            continue

        if not current_file:
            i += 1
            continue

        if line.startswith("new file mode"):
            current_file.is_new = True
            i += 1
            continue
        elif line.startswith("deleted file mode"):
            current_file.is_deleted = True
            i += 1
            continue
        elif line.startswith("--- "):
            raw_path = line[4:].strip()
            if raw_path.startswith("a/"):
                current_file.old_path = raw_path[2:]
            i += 1
            continue
        elif line.startswith("+++ "):
            raw_path = line[4:].strip()
            if raw_path.startswith("b/"):
                current_file.new_path = raw_path[2:]
            i += 1
            continue

        match = hunk_header_re.search(line)
        if match:
            old_start = int(match.group(1))
            old_lines = int(match.group(2)) if match.group(2) is not None else 1
            new_start = int(match.group(3))
            new_lines = int(match.group(4)) if match.group(4) is not None else 1
            header = line[match.end():].strip()

            current_hunk = DiffHunk(old_start, old_lines, new_start, new_lines, header)
            current_file.hunks.append(current_hunk)

            old_curr = old_start
            new_curr = new_start
            i += 1

            while i < len(lines):
                hline = lines[i]
                if hline.startswith("diff --git") or hunk_header_re.search(hline):
                    break
                
                if hline.startswith("+"):
                    current_hunk.lines.append({
                        "type": "+",
                        "content": hline[1:],
                        "old_line": None,
                        "new_line": new_curr
                    })
                    new_curr += 1
                elif hline.startswith("-"):
                    current_hunk.lines.append({
                        "type": "-",
                        "content": hline[1:],
                        "old_line": old_curr,
                        "new_line": None
                    })
                    old_curr += 1
                elif hline.startswith(" ") or hline == "":
                    current_hunk.lines.append({
                        "type": " ",
                        "content": hline[1:] if hline.startswith(" ") else hline,
                        "old_line": old_curr,
                        "new_line": new_curr
                    })
                    old_curr += 1
                    new_curr += 1
                i += 1
            continue

        i += 1

    return files
