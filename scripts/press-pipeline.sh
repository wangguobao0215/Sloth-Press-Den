#!/bin/bash
"""
Sloth-Press-Den — 一键成书编排器
用法:  press-pipeline.sh <book-dir> [options]

将 lovstudio 写作流程 + BookSmith 排版 + 审校 整合为一条流水线。
"""

BOOK_DIR=""
MODE="pdf"
PRESET="publishing-classic"
OUTPUT_DIR="output"

show_usage() {
    echo "用法: press-pipeline.sh <book-dir> [选项]"
    echo ""
    echo "选项:"
    echo "  --init           初始化新书（交互式）"
    echo "  --format FORMAT  输出格式: pdf|html (默认: pdf)"
    echo "  --preset NAME    主题预设 (默认: publishing-classic)"
    echo "  --output DIR     输出目录 (默认: output)"
    echo "  --merge          合并所有章节为单文件Markdown"
    echo "  --build          构建输出"
    echo "  --review         审校+构建"
    echo "  --all            全流程（审校→合并→构建）(默认)"
    echo ""
    echo "示例:"
    echo "  press-pipeline.sh my-book --init          # 新书初始化"
    echo "  press-pipeline.sh my-book                 # 全流程"
    echo "  press-pipeline.sh my-book --format html   # 输出HTML"
    echo "  press-pipeline.sh my-book --preset tech-modern  # 科技主题"
}

# ─── 合并所有章节为单文件 ───
merge_chapters() {
    local book_dir="$1"
    local output_file="${book_dir}/merged-manuscript.md"
    
    echo "Merging chapters:"
    > "$output_file"
    
    # Add frontmatter
    {
        echo "---"
        echo "title: \"$(grep -m1 '^# ' "${book_dir}/OUTLINE.md" 2>/dev/null | sed 's/^# //' || echo 'Untitled')\""
        echo "author: \"$(grep '作者' "${book_dir}/OUTLINE.md" 2>/dev/null | head -1 | sed 's/.*：//' || echo '')\""
        echo "date: $(date +%Y-%m-%d)"
        echo "---"
        echo ""
    } >> "$output_file"
    
    # Read SUMMARY.md if exists, otherwise scan directories
    if [ -f "${book_dir}/src/SUMMARY.md" ]; then
        # Extract chapter files from SUMMARY.md
        local md_files=$(grep -o '([^)]*\.md)' "${book_dir}/src/SUMMARY.md" | sed 's/[()]//g')
        local chapter_count=0
        for f in $md_files; do
            local full_path="${book_dir}/$f"
            if [ -f "$full_path" ]; then
                cat "$full_path" >> "$output_file"
                echo "" >> "$output_file"
                chapter_count=$((chapter_count + 1))
                echo "  + $f"
            fi
        done
        echo "  -> $chapter_count chapters merged"
    else
        # Scan chapter directories in order
        local chapter_count=0
        for d in $(ls -d "${book_dir}/src/chapter-"* 2>/dev/null | sort); do
            local ch_name=$(basename "$d")
            local section_file="${d}/section-01.md"
            if [ -f "$section_file" ]; then
                cat "$section_file" >> "$output_file"
                echo "" >> "$output_file"
                chapter_count=$((chapter_count + 1))
                echo "  + ${ch_name}/section-01.md"
            fi
        done
        echo "  -> $chapter_count chapters merged"
    fi
    
    local wc_out=$(wc -c < "$output_file")
    echo "  Size: $(echo "scale=1; $wc_out/1024" | bc) KB"
}

# ─── 构建输出 ───
build_output() {
    local book_dir="$1"
    local format="$2"
    local preset="$3"
    local output_dir="${book_dir}/${OUTPUT_DIR}"
    
    mkdir -p "$output_dir"
    
    case "$format" in
        pdf)
            python3 "${SCRIPT_DIR}/press-typeset.py" \
                --input "${book_dir}/merged-manuscript.md" \
                --preset "$preset" \
                --output "${output_dir}/book.pdf"
            ;;
        html)
            python3 "${SCRIPT_DIR}/press-typeset.py" \
                --input "${book_dir}/merged-manuscript.md" \
                --preset "$preset" \
                --format html \
                --output "${output_dir}/book.html"
            ;;
        epub|mobi|azw3)
            python3 "${SCRIPT_DIR}/press-typeset.py" \
                --input "${book_dir}/merged-manuscript.md" \
                --preset "$preset" \
                --format "$format" \
                --output "${output_dir}/book.${format}"
            ;;
        all)
            python3 "${SCRIPT_DIR}/press-typeset.py" \
                --input "${book_dir}/merged-manuscript.md" \
                --preset "$preset" \
                --output "${output_dir}/book.pdf"
            python3 "${SCRIPT_DIR}/press-typeset.py" \
                --input "${book_dir}/merged-manuscript.md" \
                --preset "$preset" \
                --format epub \
                --output "${output_dir}/book.epub"
            ;;
    esac
}

# ─── 审校 ───
run_review() {
    local book_dir="$1"
    python3 "${SCRIPT_DIR}/press-review.py" --book-dir "$book_dir"
}

# ─── Main ───
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

BOOK_DIR="$1"
shift

# Parse options
ACTION="all"
while [ $# -gt 0 ]; do
    case "$1" in
        --init) ACTION="init"; shift ;;
        --format) MODE="$2"; shift 2 ;;
        --preset) PRESET="$2"; shift 2 ;;
        --output) OUTPUT_DIR="$2"; shift 2 ;;
        --merge) ACTION="merge"; shift ;;
        --build) ACTION="build"; shift ;;
        --review) ACTION="review"; shift ;;
        --all) ACTION="all"; shift ;;
        --help) show_usage; exit 0 ;;
        *) echo "Unknown option: $1"; show_usage; exit 1 ;;
    esac
done

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Sloth-Press-Den v3.0 — Book Pipeline      ║"
echo "╚══════════════════════════════════════════════╝"
echo "  Book: $BOOK_DIR"
echo ""

case "$ACTION" in
    init)
        echo "Run: press-draft.py --init \"$BOOK_DIR\""
        echo "(Interactive setup — use press-draft.py directly)"
        ;;
    merge)
        merge_chapters "$BOOK_DIR"
        ;;
    build)
        if [ ! -f "${BOOK_DIR}/merged-manuscript.md" ]; then
            echo "No merged manuscript found. Merging first..."
            merge_chapters "$BOOK_DIR"
        fi
        build_output "$BOOK_DIR" "$MODE" "$PRESET"
        ;;
    review)
        run_review "$BOOK_DIR"
        ;;
    all)
        echo "Phase 1: Review"
        run_review "$BOOK_DIR"
        echo ""
        echo "Phase 2: Merge chapters"
        merge_chapters "$BOOK_DIR"
        echo ""
        echo "Phase 3: Build output"
        build_output "$BOOK_DIR" "$MODE" "$PRESET"
        ;;
esac

echo ""
echo "Done! 📚"
