#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量压缩 img/intro/ 下的预览图。

用法（在工作区根目录执行）：
    python tools/compress-intro.py                    # 默认：压到宽 800、WebP q82，删掉原 png
    python tools/compress-intro.py --dry-run          # 只看会压哪些、能省多少，不动文件
    python tools/compress-intro.py --keep             # 保留原始文件
    python tools/compress-intro.py --max-width 1000 --quality 88
    python tools/compress-intro.py --force            # 已压过的也重压

约定：img/intro/<网站名>/1.png、2.png、3.png —— 压缩后写成同名 .webp。
网页那边探测顺序是 .webp → .png，所以压过的和没压过的都能显示。
"""
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRO = os.path.join(ROOT, "img", "intro")
SRC_EXT = (".png", ".jpg", ".jpeg", ".webp")
SKIP_NAMES = {"desc.txt"}


def human(n):
    return "%.1f KB" % (n / 1024.0) if n < 1024 * 1024 else "%.2f MB" % (n / 1048576.0)


def collect():
    if not os.path.isdir(INTRO):
        return []
    out = []
    for folder in sorted(os.listdir(INTRO)):
        d = os.path.join(INTRO, folder)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn in SKIP_NAMES:
                continue
            stem, ext = os.path.splitext(fn)
            if ext.lower() not in SRC_EXT:
                continue
            out.append((folder, d, stem, ext.lower(), os.path.join(d, fn)))
    return out


def main():
    ap = argparse.ArgumentParser(description="批量压缩 img/intro 下的预览图")
    ap.add_argument("--max-width", type=int, default=800, help="最长边/宽度上限，默认 800")
    ap.add_argument("--quality", type=int, default=82, help="WebP 质量，默认 82")
    ap.add_argument("--keep", action="store_true", help="保留原始文件")
    ap.add_argument("--force", action="store_true", help="已存在的 .webp 也重新压")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写文件")
    args = ap.parse_args()

    items = collect()
    if not items:
        print("img/intro/ 下没找到图片")
        return

    total_before = total_after = 0
    rows = []
    for folder, d, stem, ext, src in items:
        dst = os.path.join(d, stem + ".webp")
        before = os.path.getsize(src)
        # 已经是压缩产物（源就是 webp）就跳过，避免二次压
        if ext == ".webp":
            print("跳过（本身已是 webp）: %s/%s" % (folder, os.path.basename(src)))
            continue
        if os.path.exists(dst) and not args.force and os.path.getmtime(dst) >= os.path.getmtime(src):
            print("跳过（已压过）: %s/%s" % (folder, os.path.basename(dst)))
            continue

        with Image.open(src) as im:
            w, h = im.size
            scale = min(1.0, float(args.max_width) / w)
            nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
            conv = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
            if scale < 1.0:
                conv = conv.resize((nw, nh), Image.LANCZOS)

        if args.dry_run:
            rows.append((folder, stem, before, before * 0.06, w, h, nw, nh, True))
            total_before += before
            total_after += int(before * 0.06)
            continue

        conv.save(dst, "WEBP", quality=args.quality, method=6)
        after = os.path.getsize(dst)
        total_before += before
        total_after += after
        rows.append((folder, stem, before, after, w, h, nw, nh, False))
        if not args.keep:
            os.remove(src)

    print()
    print("%-18s %-6s %10s %10s  %s" % ("网站", "文件", "原大小", "压缩后", "尺寸"))
    print("-" * 72)
    for folder, stem, before, after, w, h, nw, nh, dry in rows:
        print("%-18s %-6s %10s %10s  %dx%d -> %dx%d%s" %
              (folder[:18], stem, human(before), human(after), w, h, nw, nh,
               "  (dry-run)" if dry else ""))
    print("-" * 72)
    if rows and total_before:
        print("合计 %.2f MB -> %.2f MB（省 %.0f%%）" %
              (total_before / 1048576.0, total_after / 1048576.0,
               (1 - total_after / float(total_before)) * 100))


if __name__ == "__main__":
    main()
