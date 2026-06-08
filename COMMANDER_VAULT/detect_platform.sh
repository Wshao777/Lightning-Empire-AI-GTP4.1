# ---- 环境检测 ----
detect_platform() {
    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
        PLATFORM="termux"
        LIBC_TYPE="bionic"
    elif command -v ldd >/dev/null 2>&1 && ldd --version 2>&1 | grep -qi musl; then
        PLATFORM="linux-musl"
        LIBC_TYPE="musl"
    else
        PLATFORM="linux-glibc"
        LIBC_TYPE="glibc"
    fi
}

# ---- 静态链接优先 ----
try_static_binary() {
    local version="$1"
    local arch="$2"
    local static_url="${BASE_URL}/grok-${version}-${arch}-static"
    download_file_parallel "$static_url" "$binary_tmp" && return 0
    return 1
}

# ---- Termux 专用：proot 容器包装 ----
install_via_proot() {
    echo "Termux 环境检测到，尝试在 proot Ubuntu 中安装 Grok..." >&2
    pkg install -y proot-distro || { echo "安装 proot-distro 失败"; return 1; }
    proot-distro install ubuntu
    # 生成包装脚本
    cat > "$BIN_DIR/grok" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
proot-distro login ubuntu -- bash -c "grok \"\$@\""
EOF
    chmod +x "$BIN_DIR/grok"
    # 在容器内安装一次
    proot-distro login ubuntu -- bash -c "curl -fsSL https://x.ai/cli/install.sh | bash"
    echo "Grok 已通过 proot 包装安装。直接使用 'grok' 命令即可。" >&2
    return 0
}

# ---- 修改主安装流程 ----
detect_platform
case "$PLATFORM" in
    termux)
        # 优先尝试静态二进制
        if ! try_static_binary "$version" "$arch"; then
            install_via_proot || exit 1
        fi
        ;;
    linux-musl)
        # 尝试静态，否则普通 glibc 可能也能用（部分兼容）
        try_static_binary "$version" "$arch" || download_file_parallel "$artifact_base" "$binary_tmp"
        ;;
    *)
        # 标准 glibc Linux
        download_file_parallel "$artifact_base" "$binary_tmp"
        ;;
esac
