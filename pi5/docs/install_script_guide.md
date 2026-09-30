# pi5/scripts/install.sh 詳細ガイド

英語版 / English version: [`install_script_guide_en.md`](install_script_guide_en.md)

`install.sh`は、まっさらなRaspberry Pi OS(Debian trixie系)にshonan-pi5一式
(Shonan_Lite本体・受信用GNU Radio・Langstone V3・起動メニュー)を
セットアップするための単一スクリプトである。本ドキュメントは各処理の内容と、
なぜその手順が必要かを詳しく説明する。手順そのものの一次情報は
`docs/qtvirtualkeyboard_ja_build.md`(Qt Virtual Keyboardのビルド部分)も参照。

## 想定環境

- Raspberry Pi 5 + Raspberry Pi OS(Debian trixie相当、apt/systemd/eglfs前提)
- ADALM-Pluto+(DATVファームウェア)がEthernet同一ネットワークに接続済み
- `pi`ユーザーなど、`sudo`が使えるユーザーで実行する(スクリプト自体は`sudo`を
  個別コマンドの前に付けて実行するので、スクリプト自体をrootで起動する必要はない)

## 実行条件(前提条件)

一般ユーザーが実行して`install.sh`が正常完了するには、以下がすべて揃っている必要がある。

**必須**

1. **Raspberry Pi OS 64bit(aarch64)であること** — スクリプト内でQtライブラリの
   差し替え先を`/usr/lib/aarch64-linux-gnu/`に決め打ちしているため、32bit
   (armhf)版OSでは動作しない。
2. **インターネット到達性** — GitHub(ソース取得・Qt Virtual Keyboard・gr-dvbs2rx・
   libiioのclone)とDebianのapt配布ミラー両方に到達できること。
   `install_local.sh`でローカルクローンから導入する場合もソース取得以外
   (aptと各ビルド)には必要。
3. **sudoが使える対話的な実行** — apt/tee/systemctl等で何度も`sudo`を呼ぶため、
   パスワード入力を求められた際に応答できるttyでの実行が前提(SSH経由でも
   対話ttyがあれば問題ない)。完全無人実行にしたい場合は事前に
   `/etc/sudoers.d/`へNOPASSWDルールを用意しておく必要がある。
4. **`patch`コマンドが使えること** — 3/9のダークテーマパッチ適用に使用する。
   Raspberry Pi OSには通常プリインストールされているが、最小構成イメージでは
   無い場合がある。

**事前導入が不要になったもの**

- **`git`** — 1/9のソース取得(`git clone`/`git fetch`)自体が`git`コマンドに
  依存するが、0/9で未導入なら`sudo apt-get install -y git`を自動実行する
  (2026-08-20、新規OS実機での検証で追加)。
- **GitHubの認証** — リポジトリはpublicのため、既定のHTTPS cloneで認証なしに取得できる。
  SSHでcloneしたい場合は`install_ssh.sh`を使う(実機にSSH鍵が無ければ0/9が鍵を生成し、
  GitHubへの登録手順を表示して一旦終了する。公開鍵の登録はブラウザ操作が必要なため
  自動化できない。登録後に同じコマンドを再実行すれば続行する)。

**時間・リソース**

5. 日本語入力ビルド(`SKIP_JA_KEYBOARD=1`未指定時)・gr-dvbs2rxビルド・Langstone V3用
   libiioのビルドはそれぞれ数分〜20分程度かかるため、途中で通信・電源が切れない
   環境であること。

**不要な条件**

- 実行時点でPluto+実機がネットワーク上にある必要はない(あくまでソフトウェア
  導入のみ。実運用時に別途必要)。
- USBカメラ・オーディオ機器も導入時点では不要。

## 実行方法

```sh
./pi5/scripts/install.sh          # HTTPSでclone/fetch(既定。publicなので認証不要)
./pi5/scripts/install_ssh.sh      # SSHでclone/fetch(GitHubにSSH鍵を登録済みの場合)
./pi5/scripts/install_local.sh    # 既にあるローカルクローンから展開(GitHubからのソース取得なし)
```

- `install_ssh.sh`は`REPO_URL`を`git@github.com:kazushinjo/Shonan_Lite-RasPI5.git`に
  設定してから`install.sh`を呼び出すだけの薄いラッパーで、それ以外の処理は完全に同一である。
- `install_local.sh`は`LOCAL_SOURCE_DIR`(既定はスクリプトが置かれたクローン自身)を
  設定して`install.sh`を呼び出す。GitHubからのソース取得の代わりに、ローカルの
  クローンを`rsync`でインストール先へコピーする。
- PC側から実行する`pi5/scripts/deploy_to_pi5.sh`は、PC上の作業フォルダーを
  `tar`+`ssh`でPi5の`~/shonan-pi5-src`へ転送し、Pi5上で`install_local.sh`を実行する
  (SSHのパスワード入力は最初の1回だけ)。

環境変数で挙動を変更できる。

| 変数 | 既定値 | 効果 |
| --- | --- | --- |
| `REPO_URL` | `https://github.com/kazushinjo/Shonan_Lite-RasPI5.git` | clone元(`install_ssh.sh`はSSHのURLに変える) |
| `REPO_BRANCH` | `main` | clone/fetchするブランチ |
| `SHONAN_INSTALL_DIR` | `$HOME/shonan-pi5` | リポジトリのインストール先ディレクトリ |
| `LOCAL_SOURCE_DIR` | (未設定) | 設定するとGitHubの代わりにこのローカルクローンからコピーする(`install_local.sh`が設定する) |
| `QTVK_BUILD_DIR` | `/tmp/qtvirtualkeyboard-src` | Qt Virtual Keyboardのビルド作業ディレクトリ |
| `GR_DVBS2RX_BUILD_DIR` | `$HOME/gr-dvbs2rx` | gr-dvbs2rxのビルド作業ディレクトリ |
| `LANGSTONE_INSTALL_DIR` | `$HOME/Langstone` | Langstone V3の配置先 |
| `LANGSTONE_LIBIIO_PREFIX` | `/opt/langstone-libiio` | Langstone V3専用libiioのインストール先 |
| `SKIP_JA_KEYBOARD` | `0` | `1`にすると日本語入力ビルド(3/9)を丸ごとスキップする |
| `SKIP_GNURADIO_BUILD` | `0` | `1`にすると受信(RX)用GNU Radio/gr-dvbs2rxビルド(4/9)を丸ごとスキップする(受信機能は動作しなくなる) |
| `SKIP_LANGSTONE_BUILD` | `0` | `1`にするとLangstone V3のビルド(5/9)と`langstone.service`の作成をスキップする(Home画面のLangstoneは動作しなくなる) |

`set -euo pipefail`が先頭にあるため、いずれかのコマンドが失敗した時点でスクリプトは
即座に停止する(中途半端な状態のまま先へ進まない)。

---

## 事前準備: Raspberry Pi OSのインストール

`install.sh`実行対象のPi5に、あらかじめRaspberry Pi OSをインストールしておく
必要がある(このインストール自体は`install.sh`の範囲外)。

### 準備するもの

- Raspberry Pi 5本体
- microSDカードまたはNVMe SSD(Pi5の起動ストレージ)
- 書き込み用PC(Windows/Mac/Linuxいずれか)とmicroSDカードリーダー等
- Raspberry Pi Imager(公式書き込みツール、
  https://www.raspberrypi.com/software/ から入手)

### 手順

1. PCでRaspberry Pi Imagerを起動する。
2. 「デバイスを選択」で **Raspberry Pi 5** を選ぶ。
3. 「OSを選択」で **Raspberry Pi OS (64-bit)** を選ぶ(★32bit版は不可。
   「実行条件(前提条件)」参照)。OS名に必ず"64-bit"と表示されているものを
   選ぶこと(一覧に32bit/64bit両方が並ぶ場合があるため)。
4. 「ストレージを選択」で書き込み先のmicroSD/NVMeを選ぶ。
5. 歯車アイコン(詳細設定)を開き、以下を事前設定しておくと、初回起動後すぐ
   SSH接続して`install.sh`を実行できる。
   - ホスト名
   - ユーザー名・パスワード
   - Wi-Fi(有線LANのみで運用する場合は不要)
   - SSHを有効化(公開鍵認証 or パスワード認証)
6. 「書き込む」を実行し、完了を待つ。
7. microSD/NVMeをPi5に取り付け、電源を入れる。初回起動は数分かかる。
8. PCから`ssh <ユーザー名>@<ホスト名>.local`(またはPi5に割り当てられた
   IPアドレス)で接続できることを確認する。

以降の手順(0/9〜9/9)は、この時点でSSH接続できているPi5上で実行する。

## 0/9 前提条件の確認

- `LOCAL_SOURCE_DIR`指定時(`install_local.sh`)は、GitHubへアクセスしないため
  このチェックを省略し、`rsync`が無ければ導入するだけにする。
- それ以外で`git`が無ければ`sudo apt-get install -y git`で導入する。
- `REPO_URL`がSSH(`git@...`、`install_ssh.sh`)の場合は、`~/.ssh/id_ed25519`が無ければ
  生成し、`ssh -T git@github.com`で認証を確認する。認証できなければ公開鍵と登録先
  (https://github.com/settings/ssh/new)を表示して終了する。
  - ★GitHubはshellアクセスを許可しないため、認証に成功してもsshは必ず終了コード1を返す。
    `set -o pipefail`下でパイプに直接つなぐと誤判定するため、出力を変数で受けてから
    "successfully authenticated"の有無で判定している(実機で確認した不具合の対策)。
- `REPO_URL`がHTTPS(既定)の場合は、`git ls-remote`でアクセスできるかを確認する。
  リポジトリはpublicのため通常はそのまま進む(アクセスできない場合のみSSH版への切替を案内して終了する)。

## 1/9 ソース取得

```sh
if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" fetch origin "$REPO_BRANCH"
  git -C "$INSTALL_DIR" checkout -B "$REPO_BRANCH" "origin/$REPO_BRANCH"
  git -C "$INSTALL_DIR" reset --hard "origin/$REPO_BRANCH"
else
  git clone --branch "$REPO_BRANCH" --single-branch "$REPO_URL" "$INSTALL_DIR"
fi
```

- `$INSTALL_DIR/.git`が既に存在するか(＝既にcloneされているか)で分岐する。
  - 存在しない場合: GitHub(`kazushinjo/Shonan_Lite-RasPI5`)から`REPO_BRANCH`だけを新規clone。
    これにより、このスクリプト単体を新品のPi5へ`curl`等で転送して実行するだけで
    セットアップを開始できる。
  - 存在する場合: `fetch`してから`reset --hard`で**リモートの内容に正確に合わせる**。
    `install.sh`は配備用スクリプトのため、Pi5上で直接書き換えたファイル等の
    ローカル変更は残さない(残したい変更がある場合は事前に退避すること)。
- `LOCAL_SOURCE_DIR`指定時は、そのディレクトリに`pi5/`があることを確認し、
  `rsync -a --delete --exclude='.git'`でインストール先へコピーする(インストール先に
  しか無いファイルは削除される)。

## 2/9 実行時依存パッケージ

GUI本体(`pi5/gui/main.py`)を動かすために必要な、Debianパッケージ一式を`apt`で
導入する。

| パッケージ | 用途 |
| --- | --- |
| `git`, `curl` | ソース取得・HTTP通信に使用 |
| `python3-pyqt5` | GUI本体のQtバインディング |
| `python3-pyqt5.qtquick` | `QQuickWidget`(オンスクリーンキーボードの埋め込みに使用) |
| `python3-pyqt5.sip` | PyQt5の内部依存 |
| `python3-pil` | Pillow。カメラ映像へのコールサイン・備考オーバーレイ合成に使用 |
| `ffmpeg` | 映像/音声のエンコード・多重化・オーバーレイ合成・受信映像デコード全般 |
| `v4l-utils` | USBカメラの解像度・フォーマット確認(`v4l2-ctl`) |
| `alsa-utils` | 音声デバイス列挙・音量調整(`aplay`/`arecord`/`amixer`) |
| `libiio-utils` | `iio_attr`等。RSSI測定・送信LOの復元などPlutoの属性の読み書きに使用 |
| `sshpass` | Plutoの再起動(アプリ起動時・「アプリ再起動」等)でPluto+へパスワード付きSSHするために使用 |
| `fonts-droid-fallback` | オーバーレイの日本語グリフ描画用フォント(DroidSansFallbackFull) |
| `fonts-dejavu-core` | オーバーレイの英数字グリフ描画用フォント(DejaVuSans-Bold) |
| `qtvirtualkeyboard-plugin`, `qml-module-qtquick-virtualkeyboard` | オンスクリーンキーボード本体(apt版。3/9で日本語対応版に差し替える) |
| `qml-module-qt-labs-folderlistmodel`, `qml-module-qtquick-window2`, `qml-module-qtquick-layouts`, `qml-module-qtquick-controls2`, `qml-module-qtquick2` | オンスクリーンキーボードのQML実装が依存する補助モジュール群(不足しているとキーボードパネルのQML読み込みに失敗する) |

あわせて`usermod -aG video,audio`で、実行ユーザーをカメラ・マイク用のグループに加える。

★`SKIP_JA_KEYBOARD=1`でも2/9は必ず実行される(英語キーボード自体はここで
入るapt版で動作するため)。

## 3/9 日本語入力(OpenWnn)対応版Qt Virtual Keyboardのビルド

`SKIP_JA_KEYBOARD=1`の場合はこのブロック全体をスキップし、「英語配列のみ利用可」
というメッセージだけ表示して4/9へ進む。

### なぜソースからビルドする必要があるのか

Debian(Raspberry Pi OS)がapt配布している`qtvirtualkeyboard-plugin`には、
日本語入力エンジンが同梱されていない(実機で確認できたエンジンはHangul/
Hunspell(欧文系)/Thaiのみ)。Qt Virtual KeyboardはOSS版でもOpenWnn
(Android由来のオープンソースかな漢字変換エンジン、Apacheライセンス)を
ビルドに含めることができるが、Debianのパッケージビルドではこれが有効化
されていない。そのためQt公式ソースを取得し、`CONFIG+=openwnn`を指定して
自前でビルドし、apt版のファイルを差し替える。

### ビルド用開発パッケージの追加導入

```sh
sudo apt-get install -y \
  qtbase5-dev qtbase5-private-dev qtdeclarative5-dev qtdeclarative5-private-dev \
  qtquickcontrols2-5-dev qt5-qmake build-essential libqt5svg5-dev
```

`libqt5svg5-dev`が特に重要。Qt Virtual Keyboardのトップレベル`.pro`ファイルは
`requires(qtHaveModule(svg))`を宣言しており、これが満たされないと**エラーメッセージ
すら出さずに**ビルド全体が空振りする(`qmake`は`Some of the required modules
(qtHaveModule(svg)) are not available. Skipped.`とだけ出力し、続く`make`は
一瞬で正常終了してしまう)。実機で一度ハマった問題なので、パッケージリストから
外さないこと。

### Qtバージョンの一致

```sh
QT_VERSION="$(qmake -query QT_VERSION)"
QT_TAG="v${QT_VERSION}-lts-lgpl"
```

Pi5にインストール済みのQt本体(`libQt5Core`等)とQt Virtual Keyboardのビルドは
**ABIレベルで完全に一致するバージョン**でなければならない。バージョンがずれると
実行時にクラッシュする、または起動すらしない。そのため、決め打ちのタグではなく
`qmake -query QT_VERSION`で実機のQtバージョンを動的に取得し、対応する
`v<バージョン>-lts-lgpl`タグ(Qt公式リポジトリのLTS/LGPLライセンスブランチの
命名規則)でcloneする。

### ダークテーマパッチの適用

```sh
STYLE_PATCH="$INSTALL_DIR/pi5/docs/patches/qtvirtualkeyboard_style_dark_language_popup.patch"
if [ -f "$STYLE_PATCH" ]; then
  patch -p1 -d "$QTVK_BUILD_DIR" < "$STYLE_PATCH"
fi
```

Qt Virtual Keyboードのオンスクリーンキーボードで、globeアイコンをタップすると
出る言語切替ポップアップ(既定ではBritish English / American English / 日本語 /
한글 / ไทย等がビルドに含まれるフォールバックレイアウトの数だけ並ぶ。実際に
アプリで表示される一覧は`pi5/gui/qml/InputPanelWrapper.qml`で
English GB/US・日本語の3つに絞り込んでいる。後述「言語一覧の絞り込み」参照)は、
既定では**白背景+緑文字**で、shonan-pi5アプリ全体の黒背景+白文字のダーク
テーマと見た目が合わない。`pi5/docs/patches/
qtvirtualkeyboard_style_dark_language_popup.patch`は、Qt Virtual Keyboardの
`src/virtualkeyboard/content/styles/default/style.qml`内の
`languageListDelegate`(文字色)・`languageListBackground`(背景色)・選択中の
アイテムの強調色を、アプリと同じダーク配色に書き換える差分である。
`patch`コマンドが利用できない/パッチファイルが見当たらない場合は単にスキップし、
既定配色のままビルドを継続する(致命的な問題ではない)。

★このパッチファイルがリポジトリに存在しない状態(=手元でcloneしたばかりの
古いコミット等)でも、`if [ -f ... ]`のガードにより安全にスキップされる。

### ビルド本体

```sh
(
  cd "$QTVK_BUILD_DIR"
  qmake CONFIG+=openwnn CONFIG+=lang-ja_JP CONFIG+=lang-en_GB CONFIG+=lang-en_US \
    qtvirtualkeyboard.pro
  make -j"$(nproc)"
)
```

- `CONFIG+=openwnn`: 日本語かな漢字変換エンジン(OpenWnn)を含める。
  `src/config.pri`の`contains(CONFIG, lang-ja.*)|lang-all: CONFIG += openwnn`
  というルールにより、`lang-ja_JP`を指定すれば暗黙的にも有効化されるが、
  明示しておくことで意図を明確にしている。
- `CONFIG+=lang-ja_JP CONFIG+=lang-en_GB CONFIG+=lang-en_US`: ビルドに含める
  キーボード配列を絞り込む(指定しない場合は既定で全言語=`lang-all`が
  ビルドされ、時間もリソースも余分にかかる)。
- サブシェル`( ... )`で囲んでいるのは、`cd`によるスクリプトのカレント
  ディレクトリ変化を、この処理の外へ漏らさないため。
- `make -j"$(nproc)"`は搭載コア数ぶん並列ビルドする。Pi5(4コア)で
  examplesも含めて概ね10〜20分程度かかる(実機での実測ベース)。

★日本語がキーボードの既定選択言語にはならない(起動直後は英語)点は既知の
挙動で、`docs/qtvirtualkeyboard_ja_build.md`の「ハマりどころ」に詳細がある。
globeアイコンで手動切替が必要。

### 言語一覧の絞り込み

`CONFIG+=lang-ja_JP CONFIG+=lang-en_GB CONFIG+=lang-en_US`を指定しても、
ビルドには韓国語(한글)・タイ語(ไทย)向けのフォールバックレイアウトが
含まれてしまい、globeアイコンの言語切替ポップアップにこの2つが不要に
表示される。これはビルド設定では除外できないため、実行時に
`QtQuick.VirtualKeyboard.Settings`の`VirtualKeyboardSettings.activeLocales`
プロパティで表示対象を絞り込む。

`pi5/gui/main.py`は素の`InputPanel.qml`ではなく`pi5/gui/qml/
InputPanelWrapper.qml`をキーボードパネルとして読み込む。このQMLは
`InputPanel`を継承し、`Component.onCompleted`で
`VirtualKeyboardSettings.activeLocales = ["en_GB", "en_US", "ja_JP"]`を
設定することで、言語切替ポップアップの一覧をEnglish GB/US・日本語の3つに
限定する。

★この絞り込みは`install.sh`側の処理ではなく、リポジトリに含まれる
`pi5/gui/qml/InputPanelWrapper.qml`と`pi5/gui/main.py`のコード側の対応であり、
`install.sh`はリポジトリを`git clone`/`pull`するだけなのでそのまま反映される
(`install.sh`自体の変更は不要)。

### apt版ファイルのバックアップと差し替え

```sh
BACKUP_DIR="$HOME/qtvk_backup_$(date +%Y%m%d%H%M%S)"
...
sudo cp -a "$QT5_LIB_DIR"/libQt5VirtualKeyboard.so* "$BACKUP_DIR/" 2>/dev/null || true
...
```

差し替え前に、2/9でaptインストールされた既存ファイル一式を
`~/qtvk_backup_<タイムスタンプ>/`へコピーしておく。`|| true`が付いているのは、
(通常発生しないはずだが)コピー元ファイルが万一存在しない場合でも
`set -e`によってスクリプト全体が止まらないようにするため。

差し替え対象は次の5系統:

1. `libQt5VirtualKeyboard.so.<バージョン>` — コア共有ライブラリ本体
   (キーボードのレイアウト・スタイルQMLもリソースとしてここにコンパイルされている)
2. `qml/QtQuick/VirtualKeyboard/libqtquickvirtualkeyboardplugin.so`
   および`plugins.qmltypes` — QMLモジュール`QtQuick.VirtualKeyboard`本体
3. `qml/QtQuick/VirtualKeyboard/Settings/libqtquickvirtualkeyboardsettingsplugin.so`
   — `QtQuick.VirtualKeyboard.Settings`(アクティブロケール等の設定用)
4. `qml/QtQuick/VirtualKeyboard/Styles/libqtquickvirtualkeyboardstylesplugin.so`
   — `QtQuick.VirtualKeyboard.Styles`
5. `plugins/platforminputcontexts/libqtvirtualkeyboardplugin.so` —
   `QT_IM_MODULE=qtvirtualkeyboard`で読み込まれるプラットフォーム入力
   コンテキストプラグイン本体
6. `plugins/virtualkeyboard/libqtvirtualkeyboard_openwnn.so` — 今回の主目的である
   日本語入力エンジン本体(apt版には存在しないため`mkdir -p`してから新規配置)

最後に`sudo ldconfig`で共有ライブラリキャッシュを更新し、変更を即座に
反映させる。

### 復元(切り戻し)したい場合

```sh
BK=~/qtvk_backup_<タイムスタンプ>   # 実際のディレクトリ名に置き換える
sudo cp -a $BK/libQt5VirtualKeyboard.so* /usr/lib/aarch64-linux-gnu/
sudo cp -a $BK/VirtualKeyboard_qml/. /usr/lib/aarch64-linux-gnu/qt5/qml/QtQuick/VirtualKeyboard/
sudo cp -a $BK/libqtvirtualkeyboardplugin.so /usr/lib/aarch64-linux-gnu/qt5/plugins/platforminputcontexts/
sudo cp -a $BK/virtualkeyboard_plugins/. /usr/lib/aarch64-linux-gnu/qt5/plugins/virtualkeyboard/
sudo ldconfig
sudo systemctl restart shonan-gui.service
```

または単純に`sudo apt-get install --reinstall qtvirtualkeyboard-plugin
qml-module-qtquick-virtualkeyboard libqt5virtualkeyboard5`でもapt版へ戻せる
(この場合は日本語入力ができなくなる)。

## 4/9 受信(RX)用GNU Radio + gr-dvbs2rxの導入

`SKIP_GNURADIO_BUILD=1`の場合はこのブロック全体をスキップする(受信機能は動作しない)。

```sh
sudo apt-get install -y gnuradio gnuradio-dev cmake pkg-config
git clone https://github.com/igorauad/gr-dvbs2rx.git "$GR_DVBS2RX_BUILD_DIR"   # 既にあればpull --ff-only
git -C "$GR_DVBS2RX_BUILD_DIR" submodule update --init --recursive
git -C "$GR_DVBS2RX_BUILD_DIR" apply "$RX_PATCH"   # 存在し未適用の場合のみ
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j"$(nproc)" && sudo make install
```

`pi5/rx/shonan_rx.py`は`from gnuradio import gr, analog, blocks, iio, dvbs2rx`を
実行時に必要とする。`gnuradio`本体(gr-iio機能を含む`libgnuradio-iio*`も同梱)は
Debianのaptで導入できるが、`dvbs2rx`(DVB-S2復調のOOT module、
[igorauad/gr-dvbs2rx](https://github.com/igorauad/gr-dvbs2rx))はapt未配布のため、
ソースを取得しビルド・インストールする。実機での受信安定化のために加えた修正は
`pi5/docs/patches/gr-dvbs2rx_pi5_bringup.patch`として適用する(既に適用済みなら
自動でスキップされる)。参考実装として`pi5/third_party/rpi-dvbs2-receiver-gui/`
(kazushinjo/rpi-dvbs2-receiver-guiより取り込み)も参照。

★これがないとRX開始時に`ModuleNotFoundError: No module named 'gnuradio'`または
`ImportError: cannot import name 'dvbs2rx'`で受信が失敗する(実機の新規インストール
で発見・修正)。

## 5/9 Langstone V3(SDRトランシーバー)のビルド

`SKIP_LANGSTONE_BUILD=1`の場合はこのブロック全体をスキップする。

- Langstone V3(`pi5/third_party/Langstone-V3`、g4eml/Langstone-V3に改造を加えたもの。
  改造内容は`pi5/docs/patches/langstone_v3_shonan_lite.patch`)は新しめのlibiio APIを要求するが、
  apt版libiio(gnuradio/gr-iioが依存)は旧APIのため、同じ`/usr`配下に混在させると
  互いのヘッダ・共有ライブラリを上書きして双方が壊れる(実機で確認済みの事故)。
  そのため**Langstone専用のlibiioを`/opt/langstone-libiio`へ隔離ビルド**し、
  コンパイル時に`-I`/`-L`/RPATHで明示的にそちらだけを参照させる。
- ビルド用に`libusb-1.0-0-dev libavahi-client-dev libxml2-dev bison flex libaio-dev
  libzstd-dev liblgpio-dev libfreetype-dev`を導入する(`libfreetype-dev`は大きな
  周波数表示をTTFフォントで描画するため、`liblgpio-dev`はPTT入力・TX出力等のGPIO用)。
- `pi5/third_party/Langstone-V3/`を`~/Langstone`へコピーし、`GUI_Pluto`と
  `Screen_Message`をビルドする。
- ★`~/Langstone`は丸ごと上書きされる。Langstoneの設定ファイル
  (`~/Langstone/Langstone_Pluto.conf`)はLangstoneが終了時に書き出すもので、
  リポジトリには含まれないため上書きされない。

## 6/9 起動時コンソール表示の抑制

素のRaspberry Pi OSのままだと、Pi5の起動時にカーネルの起動ログやログインプロンプトが
実機LCDに一瞬映り込む(実機で確認)。`getty@tty1`を無効化し、
`/boot/firmware/cmdline.txt`に`quiet loglevel=3 logo.nologo vt.global_cursor_default=0`
を追記する(既に`quiet`があれば何もしない。反映には再起動が必要)。

## 7/9 reboot/shutdown/起動アプリ切替のパスワード無し実行を許可

Home画面の「電源オフ」、起動メニューでのアプリ選択、Shonan_Lite⇔Langstoneの切替は、
TTYの無いsystemdサービスから`sudo`を実行する。標準のsudo設定ではパスワード入力を
求められてPAM会話が成立せず(`pam_unix: conversation failed`)、処理が実行されない
不具合を実機で確認した。そこで`/etc/sudoers.d/shonan-pi5-reboot`に、実行ユーザーが
次のコマンドだけをパスワード無しで実行できるルールを書き込み、`visudo -c`で検証する。

- `/sbin/reboot`、`/sbin/shutdown`、`/usr/sbin/poweroff`
- `/bin/systemctl start --no-block shonan-gui.service`
- `/bin/systemctl start --no-block langstone.service`
- `/bin/systemctl stop shonan-display-off.service`

## 8/9 電源電圧警告(稲妻アイコン)表示の抑制

```sh
if [ -f "$BOOT_CONFIG" ] && ! grep -q '^avoid_warnings=' "$BOOT_CONFIG"; then
  echo "avoid_warnings=1" | sudo tee -a "$BOOT_CONFIG" > /dev/null
fi
```

`/boot/firmware/config.txt`に`avoid_warnings=1`が無ければ追記する(既にあれば
何もしない、冪等)。反映には`sudo reboot`が必要。これは画面上の稲妻アイコン・
ログ警告の表示を抑制するだけで、実際の電圧不足自体を解消するものではない
(恒久対策は正規の27W USB-C PD電源・良質なUSBケーブルの使用。
`vcgencmd get_throttled`で実際のスロットリング有無を確認できる)。

## 9/9 systemdサービス登録

次の4つのサービスを`/etc/systemd/system/`に作成する(`sudo tee`を使うのは、
リダイレクト`>`自体は`sudo`の権限を引き継がないため)。

| サービス | 内容 | 自動起動 |
| --- | --- | --- |
| `shonan-boot-menu.service` | 起動時に「Shonan_Lite / Langstone V3」を選ぶ全画面メニュー(`pi5/gui/boot_menu.py`)。選んだ側のサービスを`systemctl start`で起動する | 有効 |
| `shonan-gui.service` | Shonan_Lite本体(`pi5/gui/main.py`、`QT_QPA_PLATFORM=eglfs`)。異常終了時は3秒後に再起動 | 無効(起動メニューから起動) |
| `langstone.service` | Langstone V3(`~/Langstone/run_pluto`)。`SKIP_LANGSTONE_BUILD=1`なら作らない | 無効(起動メニュー・切替から起動) |
| `shonan-display-off.service` | シャットダウン時にDSI画面を消灯する(`pi5/systemd/shonan-display-off.service`) | 有効 |

- `shonan-gui.service`・`langstone.service`・`shonan-boot-menu.service`は`Conflicts=`で
  互いに排他制御される。LCD(DRM/KMS)は1つのプロセスしか使えないため、どれか1つを
  `systemctl start`すると他は自動的に停止する。アプリの切替はこの仕組みで行い、Pi5自体は
  再起動しない。
- マーカーファイル`~/.pi5_boot_mode_langstone`の有無を`ConditionPathExists`で見て、
  起動すべきでない側は何もせず正常終了(skipped)扱いになる。
- `langstone.service`は`Environment=HOME=...`を実際の値で埋め込み、`run_pluto`を
  `/bin/bash`経由で起動する(systemdは`User=`だけでは`$HOME`を設定せず、`%h`は
  rootのホームに解決される場合があること、`run_pluto`の先頭行がシェバングでないことへの対策。
  いずれも実機で確認)。
- 最後に`daemon-reload`し、稼働中の`shonan-gui.service`/`langstone.service`を明示的に
  `stop`してから(稼働中のまま起動メニューを起動するとLCDを掴めず描画に失敗するため)、
  `shonan-boot-menu.service`と`shonan-display-off.service`を`enable`・`restart`する。

## インストール内容の検証

完了前に次を確認し、1つでも欠けていればエラーで終了する。

- 必須ファイル(`main.py`・`backend.py`・`boot_menu.py`・主要画面・QML・テストパターン画像)があること
- 必須コマンド(`ffmpeg`・`v4l2-ctl`・`arecord`・`iio_attr`・`sshpass`)があること
- PyQt5(`QtCore`・`QtQuickWidgets`・`QtWidgets`)をimportできること、GUIのPythonファイルが構文エラーなくコンパイルできること
- `shonan-boot-menu.service`が起動していること

## 完了後の表示

`shonan-boot-menu.service`の状態を表示し、続けて次の注意書きを表示する。

1. **パスワードなしsudo/sshの前提**: 設定画面の「システム日時」設定(`timedatectl`)や、
   開発時に使う`kmsgrab`による実機画面キャプチャ等は、`sudo`をパスワードなしで
   実行できることを前提にしている。7/9で許可するのは上記のコマンドだけで、それ以外の
   `/etc/sudoers.d/`への変更は行わない(セキュリティに関わる設定をスクリプトが無断で
   行うべきではないため)。必要であれば運用者が判断して個別に設定する。
2. **日本語入力の既定言語**: オンスクリーンキーボードは起動直後は英語配列で、
   globeアイコンをタップすることで日本語(ローマ字入力)へ切り替えられる
   (自動では切り替わらない、既知の仕様)。
3. **avoid_warnings**: 8/9で新規に追記した場合、反映には`sudo reboot`が必要。

## 関連ドキュメント

- `pi5/docs/qtvirtualkeyboard_ja_build.md` — 3/9のビルド手順の一次情報、
  実機で遭遇したハマりどころの詳細
- `pi5/docs/patches/qtvirtualkeyboard_style_dark_language_popup.patch` —
  3/9で適用されるダークテーマパッチの実体(unified diff形式、`git diff`相当)
- `pi5/docs/patches/gr-dvbs2rx_pi5_bringup.patch` — 4/9で適用される受信安定化
  パッチの実体
- `pi5/docs/patches/langstone_v3_shonan_lite.patch` — 5/9でビルドするLangstone V3への改造内容
  (g4eml/Langstone-V3との差分)
- `pi5/docs/shonan_pi5_operation_manual.docx` / `pi5/gui/manual_content.py` —
  GUIの操作方法そのもの(インストール後の使い方)
- `pi5/third_party/rpi-dvbs2-receiver-gui/` — GNU Radio/gr-dvbs2rx受信フロー
  グラフの参考実装(kazushinjo/rpi-dvbs2-receiver-guiより取り込み)
