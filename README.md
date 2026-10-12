# TaikoNavigation

太鼓达人的导航页。纯静态站点，没有构建步骤：把目录丢给任意静态服务器（或 GitHub Pages）就能跑。

## 目录结构

```
index.html            唯一一个源文件（结构、样式、脚本都在里面）
data.xlsx             所有网站数据；一个工作表 = 一个页面标签
img/
  Panel.png           面板外框（九宫格拉伸）
  Panel_Side.png      面板左右装饰条（精灵图，6 帧）
  MiniPlate.png       网站挂牌（精灵图，6 帧，对应 6 种底板样式）
  Plate_Arrow.png     翻页箭头（单张左箭头，右箭头靠镜像）
  GaugeCondition_Bar.png  预览卡片的卡框
  title.png           卡片顶部的备注条
  background.webp     背景图（宽屏用）
  background.jpg      背景图（窄屏用，竖版）
  icon/               每个网站的小图标（显示在挂牌的圆里）
  intro/              每个网站的预览图，见下
font/
  FZCuYuan-GBK.woff2  方正粗圆_GBK（转成 WOFF2，供没装这字体的机器兜底）
vendor/
  xlsx.full.min.js    解析 data.xlsx 用的 SheetJS，本地自带，不走 CDN
tools/
  compress-intro.py   批量压缩 img/intro 下的预览图
  compress-icons.py   批量压缩 img/icon 下的图标
```

## 加一个网站

在 `data.xlsx` 里加一行。列的含义（脚本按列下标读）：

| 列 | 内容 |
|---|---|
| A | 网站名。**必须与 `img/intro/` 下的文件夹名完全一致** |
| B | 网址 |
| C | 简介，显示在弹窗标题下面 |
| D | 图标文件名，例如 `TaikoImager.png`，对应 `img/icon/` 下那个文件 |
| E | 底板样式 1~6，决定挂牌用哪一帧、什么颜色 |

工作表名就是页面顶部的标签文字。

## 加预览图

在 `img/intro/<网站名>/` 下放 `1.png`、`2.png`、`3.png`（16:9 截图，最多三张），
再放一份可选的 `desc.txt`：

- 第 1 行是第 1 张图的备注，第 2 行配第 2 张，依此类推
- **有备注**的卡片：套 `GaugeCondition_Bar.png` 卡框，顶部用 `title.png` 写备注
- **没有备注**的卡片：不套卡框，图片直接铺满并描一圈 `rgb(148,128,95)`
- 备注文件可以没有；一张图都没有的网站，弹窗里「网页速览」照样显示，只是空的

## 压缩素材

原始截图很大（一张 16:9 截图两三 MB，图标甚至有 2547×2547 的），务必先压缩再提交：

```bash
python tools/compress-intro.py     # 预览图 -> 宽 1280 的 WebP
python tools/compress-icons.py     # 图标   -> 最长边 256 的 WebP
```

两个脚本都是**增量且幂等**的：已经压过的会跳过，只处理新丢进来的文件，
压缩完默认删掉原图（想保留加 `--keep`，只想看效果加 `--dry-run`）。
页面取值时会先试 `.webp`，失败再回落到原始文件名，所以压过的和没压过的都能显示。

## 本地预览

**不要双击 `index.html` 用 `file://` 打开**——脚本要用 `fetch` 读 `data.xlsx`，
`file://` 下会被 CORS 拦掉。起一个静态服务器：

```bash
python -m http.server 8000
# 或 VS Code 的 Live Server
```

然后访问 <http://127.0.0.1:8000/>。

## 上传到 GitHub Pages 的注意事项

- Pages 跑在 Linux 上，**路径区分大小写**。`img/intro/` 下的文件夹名必须和
  `data.xlsx` A 列的名字逐字符一致（包括全角/半角、空格）。
- 仓库里只应包含 `index.html`、`data.xlsx`、`img/`、`font/`、`vendor/`、`tools/`
  和本说明；`.gitignore` 已挡掉 Excel 锁文件与本地调试产物。
- 全部资源都是相对路径，放在仓库根目录即可，无需额外配置。

## 调试

- 点开任意挂牌会弹出「网页速览」；← → 翻页（单页内循环）、Esc 或点空白处退出、
  点预览图放大、手机上左右滑动翻页。
- `Ctrl + Shift + P`（或网址后加 `?icondebug=1`）打开图标微调面板，
  里面还有弹窗翻页动画的速度倍率，会记在 `localStorage`。
