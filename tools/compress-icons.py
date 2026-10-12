#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量压缩 img/icon/ 下的网站图标。

用法（在工作区根目录执行）：
    python tools/compress-icons.py                 # 默认：最长边 256、WebP q88，删掉原图
    python tools/compress-icons.py --dry-run
    python tools/compress-icons.py --keep          # 保留原始文件
    python tools/compress-icons.py --max-size 320 --quality 92
    python tools/compress-icons.py --force

为什么是 256：图标在页面上是 57px 的圆（挂牌里那个），弹窗里的挂牌最大也就一百多 px，
256 足够覆盖到 4 倍屏，再大纯属浪费 —— 现在有的图是 2547×2547。

输出同名 .webp（0.png -> 0.webp）。网页那边 <img> 的 src 先试 .webp，
onerror 再回落到 data.xlsx 里写的原始文件名，所以压过的和没压过的都能显示。
"""
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "img", "icon")
SRC_EXT = (".png", ".jpg", ".jpeg", ".ico", ".webp", ".bmp", ".gif")


def human(n):
    return "%.1f KB" % (n / 1024.0) if n < 1048576 else "%.2f MB" % (n / 1048576.0)


def collect():
    if not os.path.isdir(ICON):
        return []
    out = []
    for fn in sorted(os.listdir(ICON)):
        p = os.path.join(ICON, fn)
        if not os.path.isfile(p):
            continue
        stem, ext = os.path.splitext(fn)
        if ext.lower() in SRC_EXT:
            out.append((stem, ext.lower(), p))
    return out


def main():
    ap = argparse.ArgumentParser(description="批量压缩 img/icon 下的网站图标")
    ap.add_argument("--max-size", type=int, default=256, help="最长边上限，默认 256")
    ap.add_argument("--quality", type=int, default=88, help="WebP 质量，默认 88")
    ap.add_argument("--keep", action="store_true", help="保留原始文件")
    ap.add_argument("--force", action="store_true", help="已存在的 .webp 也重压")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写文件")
    args = ap.parse_args()

    items = collect()
    if not items:
        print("img/icon/ 下没找到图片")
        return

    rows = []
    total_before = total_after = 0
    for stem, ext, src in items:
        if ext == ".webp":
            continue
        dst = os.path.join(ICON, stem + ".webp")
        before = os.path.getsize(src)
        if os.path.exists(dst) and not args.force and os.path.getmtime(dst) >= os.path.getmtime(src):
            print("跳过（已压过）: %s" % os.path.basename(dst))
            continue

        with Image.open(src) as im:
            w, h = im.size
            scale = min(1.0, float(args.max_size) / max(w, h))
            nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
            has_alpha = im.mode in ("RGBA", "LA", "P") or (im.mode == "P" and "transparency" in im.info)
            conv = im.convert("RGBA" if has_alpha else "RGB")
            if scale < 1.0:
                conv = conv.resize((nw, nh), Image.LANCZOS)

        if args.dry_run:
            rows.append((stem, before, int(before * 0.12), w, h, nw, nh, True))
            total_before += before
            total_after += int(before * 0.12)
            continue

        conv.save(dst, "WEBP", quality=args.quality, method=6)
        after = os.path.getsize(dst)
        total_before += before
        total_after += after
        rows.append((stem, before, after, w, h, nw, nh, False))
        if not args.keep:
            os.remove(src)

    print()
    print("%-22s %10s %10s  %s" % ("图标", "原大小", "压缩后", "尺寸"))
    print("-" * 68)
    for stem, before, after, w, h, nw, nh, dry in rows:
        print("%-22s %10s %10s  %dx%d -> %dx%d%s" %
              (stem, human(before), human(after), w, h, nw, nh, "  (dry-run)" if dry else ""))
    print("-" * 68)
    if rows and total_before:
        print("合计 %.2f MB -> %.2f MB（省 %.0f%%）" %
              (total_before / 1048576.0, total_after / 1048576.0,
               (1 - total_after / float(total_before)) * 100))


if __name__ == "__main__":
    main()
