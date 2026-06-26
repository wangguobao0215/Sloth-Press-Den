#!/bin/bash
# ============================================================
# 同步脚本：Obsidian / 笔记系统 → sloth-books 构建目录
# 用途：方案B双目录工作流的同步桥梁
# 用法：
#   ./sync-to-build.sh            # 同步所有章节
#   ./sync-to-build.sh 3          # 只同步第3章
#   ./sync-to-build.sh all         # 全量同步（含附录）
#
# 前置条件：按以下命名规范写稿：
#   Obsidian端：第X章——标题.md
#   sloth-books端：src/chapter-XX/section-01.md
# ============================================================

# === 用户需修改的两个路径 ===
OBSIDIAN_DIR="/Users/username/Documents/Obsidian/01-写作/书名/章节"
SLOTH_DIR="/Users/username/Desktop/sloth-books/书名/src"
TOTAL_CHAPTERS=10
# ============================

sync_chapter() {
    local num=$1
    local padded=$(printf '%02d' $num)
    
    # 匹配 Obsidian 端中文命名（如"第3章——中层不死的逻辑.md"）
    local obsidian_file=$(ls "$OBSIDIAN_DIR" | grep "^第${num}章" | head -1)
    
    if [ -z "$obsidian_file" ]; then
        echo "⚠️  未找到第${num}章的 Obsidian 文件"
        return 1
    fi
    
    local src="$OBSIDIAN_DIR/$obsidian_file"
    local dst="$SLOTH_DIR/chapter-${padded}/section-01.md"
    
    # 备份已存在的文件
    if [ -f "$dst" ]; then
        cp "$dst" "${dst}.bak"
        echo "  ↳ 已备份原文件至 section-01.md.bak"
    fi
    
    cp "$src" "$dst"
    echo "✅ 第${num}章已同步: $obsidian_file"
}

sync_appendix() {
    local letter=$1
    local obsidian_file=$(ls "$OBSIDIAN_DIR" | grep "^附录${letter}" | head -1)
    
    if [ -z "$obsidian_file" ]; then
        echo "  ⚠️  未找到附录${letter}的 Obsidian 文件"
        return 1
    fi
    
    local src="$OBSIDIAN_DIR/$obsidian_file"
    local dst_dir="$SLOTH_DIR/appendix-${letter}"
    mkdir -p "$dst_dir"
    
    if [ -f "$dst_dir/section-01.md" ]; then
        cp "$dst_dir/section-01.md" "$dst_dir/section-01.md.bak"
    fi
    
    cp "$src" "$dst_dir/section-01.md"
    echo "✅ 附录${letter}已同步"
}

# === 主逻辑 ===
echo "📖 同步 Obsidian → sloth-books"
echo "源: $OBSIDIAN_DIR"
echo "目标: $SLOTH_DIR"
echo "---"

case "${1:-all}" in
    all|"")
        echo "全量同步章节..."
        for i in $(seq 1 $TOTAL_CHAPTERS); do
            sync_chapter $i
        done
        echo "---"
        echo "同步附录..."
        for l in A B C D E F; do
            sync_appendix $l
        done
        ;;
    [0-9]|[0-9][0-9])
        sync_chapter $1
        ;;
    appendix|ap)
        sync_appendix "${2:-A}"
        ;;
    *)
        echo "用法: $0 [all|章节号]"
        echo "   $0        → 全量同步"
        echo "   $0 3      → 只同步第3章"
        exit 1
        ;;
esac

echo "---"
echo "✅ 同步完成。构建命令："
echo "   cd \"$SLOTH_DIR/..\" && bash scripts/build-pdf.sh"
