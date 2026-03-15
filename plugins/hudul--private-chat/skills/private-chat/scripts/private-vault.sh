#!/bin/bash

# Private Vault - AES-256-CBC 加密工具
# 用于私密聊天技能的加密存储

set -e

# 显示帮助
show_help() {
    echo "Private Vault - AES-256-CBC 加密工具"
    echo ""
    echo "用法:"
    echo "  $0 encrypt <password> <plaintext>     - 加密文本"
    echo "  $0 decrypt <password> <encrypted>     - 解密文本"
    echo "  $0 interactive                         - 交互式模式"
    echo ""
    echo "加密格式: ENC[v1:SALT:BASE64]"
    echo ""
    echo "示例:"
    echo "  $0 encrypt \"mypassword\" \"secret text\""
    echo "  $0 decrypt \"mypassword\" \"ENC[v1:abc123:def456...]\""
}

# 生成随机盐值
generate_salt() {
    openssl rand -hex 8
}

# 加密函数
encrypt_text() {
    local password="$1"
    local plaintext="$2"
    local salt=$(generate_salt)
    
    # 使用 AES-256-CBC 加密
    local encrypted=$(echo -n "$plaintext" | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$password" -base64 | tr -d '\n')
    
    # 输出格式: ENC[v1:SALT:BASE64]
    echo "ENC[v1:$salt:$encrypted]"
}

# 解密函数
decrypt_text() {
    local password="$1"
    local encrypted="$2"
    
    # 检查格式
    if [[ ! "$encrypted" =~ ^ENC\[v1:([a-f0-9]+):(.+)\]$ ]]; then
        echo "错误: 无效的加密格式" >&2
        return 1
    fi
    
    local salt="${BASH_REMATCH[1]}"
    local ciphertext="${BASH_REMATCH[2]}"
    
    # 解密
    echo "$ciphertext" | openssl enc -aes-256-cbc -d -salt -pbkdf2 -pass pass:"$password" -base64 2>/dev/null || {
        echo "错误: 解密失败，可能是密码错误" >&2
        return 1
    }
}

# 交互式模式
interactive_mode() {
    echo "=== Private Vault 交互式模式 ==="
    echo ""
    
    read -s -p "请输入密码: " password
    echo ""
    
    echo "选择操作:"
    echo "1) 加密"
    echo "2) 解密"
    read -p "> " choice
    
    case "$choice" in
        1)
            read -p "请输入要加密的文本: " plaintext
            echo ""
            echo "加密结果:"
            encrypt_text "$password" "$plaintext"
            ;;
        2)
            read -p "请输入要解密的文本 (ENC[...]): " encrypted
            echo ""
            echo "解密结果:"
            decrypt_text "$password" "$encrypted"
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
}

# 主程序
case "${1:-}" in
    encrypt)
        if [ $# -ne 3 ]; then
            echo "用法: $0 encrypt <password> <plaintext>" >&2
            exit 1
        fi
        encrypt_text "$2" "$3"
        ;;
    decrypt)
        if [ $# -ne 3 ]; then
            echo "用法: $0 decrypt <password> <encrypted>" >&2
            exit 1
        fi
        decrypt_text "$2" "$3"
        ;;
    interactive)
        interactive_mode
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
