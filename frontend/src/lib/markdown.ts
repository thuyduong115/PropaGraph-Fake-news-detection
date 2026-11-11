// Đọc file diễn giải do nhóm viết (src/content/*.md): tách theo tiêu đề "## <tên>".
// Chỉ hỗ trợ đoạn văn thường; bỏ comment HTML và đoạn placeholder "_Chờ nhóm viết._".

export function parseSections(md: string): Map<string, string[]> {
  const sections = new Map<string, string[]>();
  const clean = md.replace(/<!--[\s\S]*?-->/g, "");
  let current: string | null = null;
  let buf: string[] = [];
  const flush = () => {
    if (current === null) return;
    const paragraphs = buf
      .join("\n")
      .split(/\n\s*\n/)
      .map((p) => p.replace(/\s+/g, " ").trim())
      .filter((p) => p && !/^_.*_$/.test(p));
    sections.set(current, paragraphs);
  };
  for (const line of clean.split(/\r?\n/)) {
    const m = /^##\s+(.+?)\s*$/.exec(line);
    if (m) {
      flush();
      current = m[1];
      buf = [];
    } else {
      buf.push(line);
    }
  }
  flush();
  return sections;
}

/** Diễn giải cho bảng `name`: khớp tiêu đề bằng tiền tố (vd "E0" khớp "E0_main"). */
export function sectionFor(sections: Map<string, string[]>, name: string): string[] {
  for (const [key, paragraphs] of sections) {
    if (name === key || name.toUpperCase().startsWith(key.toUpperCase())) return paragraphs;
  }
  return [];
}
