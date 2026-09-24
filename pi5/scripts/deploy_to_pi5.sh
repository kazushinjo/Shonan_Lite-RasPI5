#!/usr/bin/env bash
# ローカルの作業フォルダー(このクローン自身)をRaspberry Pi 5へtar+ssh転送し、
# Pi5上でinstall_local.shを実行する。PC側(Windows Git Bash/Mac/Linux)から実行する。
# 追加ツール(sshpass/rsync)は使わず、標準のssh/scp/tarのみで動かす。
#
# ★セキュリティ上、SSHログイン自体(パスワード入力)は必ず人間が手動で行う
# (sshpassでパスワードをスクリプト/コマンドラインに埋め込むようなことは
# しない)。ただし、都度パスワードを求められるのは不便なため、OpenSSHの
# ControlMaster(接続多重化)を使い、最初の1回だけ手動でパスワードを入力
# すれば、以後の転送・インストール実行は同じ認証済み接続を使い回して自動で
# 継続する(2回目以降のパスワード再入力は発生しない)。多重化用の接続は
# スクリプト終了時に閉じる。
#
# 使い方:
#   ./pi5/scripts/deploy_to_pi5.sh
#     (IPアドレス・ユーザー名を対話的に入力する)
#   PI5_HOST=192.168.1.50 PI5_USER=pi ./pi5/scripts/deploy_to_pi5.sh
#     (IP/ユーザー名を環境変数で指定する場合。パスワードは最初の1回だけssh自体が聞く)
#   SKIP_JA_KEYBOARD=1 SKIP_GNURADIO_BUILD=1 ./pi5/scripts/deploy_to_pi5.sh
#     (install_local.sh側のビルド省略オプションをそのまま転送先の実行にも反映する)
set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
LOCAL_REPO_DIR="$(readlink -f "$SCRIPT_DIR/../..")"
REMOTE_SRC_DIR="shonan-pi5-src"

if [ -z "${PI5_HOST:-}" ]; then
  read -rp "Pi5のIPアドレス/ホスト名: " PI5_HOST
fi
: "${PI5_HOST:?IPアドレス/ホスト名が必要です}"

if [ -z "${PI5_USER:-}" ]; then
  read -rp "Pi5のユーザー名 [pi]: " PI5_USER
  PI5_USER="${PI5_USER:-pi}"
fi

CONTROL_PATH="/tmp/shonan-deploy-ssh-$$-%C"
SSH_OPTS=(-o StrictHostKeyChecking=accept-new
          -o ControlMaster=auto -o ControlPath="$CONTROL_PATH" -o ControlPersist=10m)

cleanup() {
  ssh -o ControlPath="$CONTROL_PATH" -O exit "${PI5_USER}@${PI5_HOST}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== ${PI5_USER}@${PI5_HOST}へSSH接続します。パスワードを手動で入力してください ==="
echo "    (この1回のみ。以後の転送・インストールは自動で継続します)"
ssh -MNf "${SSH_OPTS[@]}" "${PI5_USER}@${PI5_HOST}"

echo "=== ${PI5_USER}@${PI5_HOST}:~/${REMOTE_SRC_DIR} へソースを転送しています ==="
tar --exclude='.git' -C "$LOCAL_REPO_DIR" -cf - . \
  | ssh "${SSH_OPTS[@]}" "${PI5_USER}@${PI5_HOST}" \
      "mkdir -p ~/${REMOTE_SRC_DIR} && tar -C ~/${REMOTE_SRC_DIR} -xf -"

# ★install_local.sh側の省略オプションをローカルの環境変数から拾い、リモート
# 実行時のコマンド文字列に安全に埋め込む(値は%qでシェルクォートする)。
REMOTE_ENV=""
for var in SHONAN_INSTALL_DIR SKIP_JA_KEYBOARD SKIP_GNURADIO_BUILD SKIP_LANGSTONE_BUILD; do
  if [ -n "${!var:-}" ]; then
    REMOTE_ENV="${REMOTE_ENV}${var}=$(printf '%q' "${!var}") "
  fi
done

echo "=== Pi5上でinstall_local.shを実行しています(自動継続、パスワード再入力不要) ==="
ssh -t "${SSH_OPTS[@]}" "${PI5_USER}@${PI5_HOST}" \
  "cd ~/${REMOTE_SRC_DIR} && ${REMOTE_ENV}./pi5/scripts/install_local.sh"
