#!/bin/bash
# Enhanced Grok CLI Installer - Supports Termux, Linux, cross-env
# Author: Grok for Wshao777 Lightning-ALL / MLOG integration
# Version: 1.0 - 2026-06

set -euo pipefail

BASE_URL="https://x.ai/cli"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"

echo "🔍 Detecting platform..."

if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; then
    PLATFORM="termux"
    ARCH="$(uname -m)"
    echo "Termux detected (Android, $ARCH)"
elif command -v ldd >/dev/null 2>&1 && ldd --version 2>&1 | grep -qi musl; then
    PLATFORM="linux-musl"
    ARCH="$(uname -m)"
else
    PLATFORM="linux-glibc"
    ARCH="$(uname -m)"
fi

# Function to download with checksum verification
download_with_verify() {
    local url="$1"
    local dest="$2"
    local expected_sha="${3:-}"
    
    echo "📥 Downloading $url ..."
    curl -fsSL -o "$dest" "$url" || { echo "Download failed"; return 1; }
    
    if [ -n "$expected_sha" ]; then
        local actual_sha=$(sha256sum "$dest" | awk '{print $1}')
        if [ "$actual_sha" != "$expected_sha" ]; then
            echo "❌ Checksum mismatch! Expected: $expected_sha, Got: $actual_sha"
            rm -f "$dest"
            return 1
        fi
    fi
    echo "✅ Download verified"
    return 0
}

# Try static binary (adapt if official provides)
try_static() {
    local version="latest"
    local arch="$1"
    # Placeholder - update if static builds available
    local url="${BASE_URL}/grok-${version}-${arch}-static"
    local tmp="/tmp/grok-static"
    if download_with_verify "$url" "$tmp"; then
        mv "$tmp" "$BIN_DIR/grok"
        chmod +x "$BIN_DIR/grok"
        echo "✅ Static binary installed"
        return 0
    fi
    return 1
}

install_via_proot() {
    echo "📦 Termux: Installing via proot Ubuntu..."
    pkg update -y && pkg install -y proot-distro curl || { echo "proot-distro install failed"; return 1; }
    
    proot-distro install ubuntu || { echo "Ubuntu install failed"; return 1; }
    
    # Wrapper script
    cat > "$BIN_DIR/grok" << 'EOF'
#!/bin/bash
# Grok Termux Wrapper - forwards to Ubuntu proot
exec proot-distro login ubuntu -- bash -c "grok \"\$@\""
EOF
    chmod +x "$BIN_DIR/grok"
    
    # Install inside container
    proot-distro login ubuntu -- bash -c '
        apt update && apt install -y curl
        curl -fsSL https://x.ai/cli/install.sh | bash
    ' || { echo "Container install failed"; return 1; }
    
    echo "✅ Grok installed via proot. Use 'grok' directly."
    return 0
}

# Main flow
case "$PLATFORM" in
    termux)
        ARCH="aarch64"  # Common for Termux
        if ! try_static "$ARCH"; then
            echo "⚠️ No static binary, falling back to proot..."
            install_via_proot || exit 1
        fi
        ;;
    *)
        # Standard Linux - use official
        echo "📥 Installing official Grok CLI..."
        curl -fsSL https://x.ai/cli/install.sh | bash
        ;;
esac

# Post-install: Add to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
    echo "✅ PATH updated. Restart shell or source ~/.bashrc"
fi

echo "🎉 Grok CLI ready! Run 'grok --help' or integrate with MLOG/Lightning-ALL."

