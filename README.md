# Shonan for RasPI5

Raspberry Pi 5 + ADALM-PlutoによるDVB-S2 DATV送受信タッチGUIシステム。
本体は`pi5/`配下(Python/PyQt5、eglfs直描画)。

## 主な機能

- **送信**: 周波数・シンボルレート(333〜2000 kS/s)・FEC・変調方式(QPSK/8PSK)・TX出力を画面で設定し、
  Pluto内蔵の`pluto_dvb`でDVB-S2送信する。FECは変調方式ごとに実際に動作する組み合わせだけを選べる
  (QPSK: 1/2・3/5・8/9、8PSK: 3/5・8/9)。送信映像はフルHD(1920x1080)固定。
- **映像ソース**: USBカメラ・画像ファイル(静止画を反復送信)・テストパターンから選ぶ。カメラ選択時は
  「撮影」ボタンで静止画(JPG、`~/Pictures/Shonan_Lite/`)を撮り、そのまま送信画像に使える。
  コールサイン・備考を文字サイズ・文字色を選んで映像へ焼き込める(日時も表示)。
- **受信**: GNU Radio(gr-dvbs2rx)によるPi 5上での復調。LOCK状態・ビットレート・パケット数/エラー数を表示。
- **RSSI測定**: 周波数を掃引して受信レベルをグラフ表示する。オンデバイス復調OFF(通常運用)では
  相手局の電波を測り、ON(テスト用)では自局もテストパターンで自動送信して自分の信号を測る。
- **プリセット**: 現在の設定を5件まで登録・呼び出し(プリセット1は未登録の間RFループバック試験用)。
- **その他**: Pluto URIの自動検出、日本語/英語表示、日本語オンスクリーンキーボード、アプリ内Help、
  機器試験、起動時のアプリ選択(Shonan_Lite / Langstone V3)。

## スクリーンショット

実機(7インチLCD、800x480)の画面。映像はすべてテストパターンで撮影している。

| Home画面 | 送信画面(TX) | 受信画面(RX) | RSSI測定 |
| --- | --- | --- | --- |
| ![Home画面](pi5/docs/images/screenshot_home.png) | ![送信画面](pi5/docs/images/screenshot_tx.png) | ![受信画面](pi5/docs/images/screenshot_rx.png) | ![RSSI測定](pi5/docs/images/screenshot_rssi.png) |

| 映像ソース | 変調方式 | 出力設定 | プリセット |
| --- | --- | --- | --- |
| ![映像ソース](pi5/docs/images/screenshot_videosource.png) | ![変調方式](pi5/docs/images/screenshot_modulation.png) | ![出力設定](pi5/docs/images/screenshot_streamoutput.png) | ![プリセット](pi5/docs/images/screenshot_presets.png) |

各画面の操作方法は、アプリ内の「ヘルプ」または操作説明書
[`pi5/docs/shonan_pi5_operation_manual.docx`](pi5/docs/shonan_pi5_operation_manual.docx)を参照。

## インストール

### 事前に準備するもの

- Raspberry Pi 5本体
- microSDカードまたはNVMe SSD(Pi5の起動ストレージ)
- 書き込み用PC(Windows/Mac/Linuxいずれか)とmicroSDカードリーダー等
- ADALM-Pluto(DATVファームウェア導入済み)がPi5とEthernet同一ネットワークに
  接続されていること(★`install.sh`実行時点では未接続でもよい。あくまで
  ソフトウェア導入のみで、実運用時に必要)
- 送信映像用USBカメラ・オーディオ機器(任意、無くてもテストパターン映像で
  動作確認できる)

### 0. Raspberry Pi OSのインストール

Pi5本体に、あらかじめRaspberry Pi OSをインストールしておく。

1. PCで[Raspberry Pi Imager](https://www.raspberrypi.com/software/)を起動する。
2. 「デバイスを選択」で **Raspberry Pi 5** を選ぶ。
3. 「OSを選択」で **Raspberry Pi OS (64-bit)** を選ぶ
   (★32bit版は不可。下記「実行条件」参照)。
4. 「ストレージを選択」で書き込み先のmicroSD/NVMeを選ぶ。
5. 歯車アイコン(詳細設定)で、ホスト名・ユーザー名/パスワード・Wi-Fi・SSH有効化を
   事前設定しておくと、初回起動後すぐSSH接続できる。
6. 「書き込む」を実行し、完了後microSD/NVMeをPi5に取り付けて起動する。
7. PCから`ssh <ユーザー名>@<ホスト名>.local`で接続できることを確認する。

### 0.5 Plutoのネットワーク設定(USB_ETHERNET)

ADALM-Pluto(DATVファームウェア導入済み)をPi5と同じEthernetネットワークに
接続するには、あらかじめPluto側のUSB_ETHERNETインターフェースに固定IPを
設定しておく。

1. PlutoをPCとUSBケーブルで接続する(USB Mass Storageとして認識される)。
2. Plutoのドライブ直下にある`config.txt`をテキストエディタで開く。
3. `[USB_ETHERNET]`セクションの`ipaddr_eth`と`netmask_eth`を、Pi5と同じ
   サブネット内の値に設定する(例、Pi5が`192.168.0.80/24`の場合)。

   ```ini
   [USB_ETHERNET]
   ipaddr_eth = 192.168.0.51
   netmask_eth = 255.255.255.0
   ```

4. `config.txt`を保存し、PlutoのドライブをPCから安全に取り出す(eject)。
   Plutoが自動的に再起動し、新しいIPアドレスで起動する。
5. Pi5の設定画面「送信先 (Pluto Tx)」に、ここで設定した`ipaddr_eth`の値
   (上記例では`192.168.0.51`)を入力する。

★USB直結時のUSB CDCネットワーク(`[NETWORK]`セクション、既定`192.168.2.1`)
とは別の設定である。`[USB_ETHERNET]`は、Pluto(Pluto+)のUSB OTGポートに
挿したUSB-Ethernetアダプタに割り当てるIPアドレスで、これによりPlutoが
Pi5と同じLAN(Ethernet)上のノードとして直接通信できるようになる。
設定ファイルの詳細は
[ADI公式Wiki](https://wiki.analog.com/university/tools/pluto/users/customizing)
を参照。

### 1. install.shの実行

本リポジトリはpublicのため、HTTPS clone(`install.sh`既定)でそのまま取得できる。
まずPi5へSSHでログインする(`<...>`の部分はご自身の環境の値に置き換える):

```sh
ssh <Pi5のユーザー名>@<Pi5のIPアドレスまたはホスト名>
# 例: ssh pi@192.168.0.80
```

ログイン後、Pi5上で:

```sh
# gitが未導入の場合は先に用意する(初回のみ)
sudo apt-get update && sudo apt-get install -y git

git clone https://github.com/kazushinjo/Shonan_Lite-RasPI5.git
cd Shonan_Lite-RasPI5
./pi5/scripts/install.sh
```

`install.sh`自身も0/9でgit未導入の場合は自動導入する。以降のアップデート時も
このコマンドを再実行するだけでよい(`REPO_BRANCH`環境変数で取得するブランチを
指定できる。既定は`main`)。

★自分のフォークやプライベートなミラーからSSH経由で取得したい場合は、
`REPO_URL=git@github.com:<user>/<repo>.git ./pi5/scripts/install_ssh.sh`を使う
(SSH鍵が未登録ならその場で生成し、GitHubへの登録案内を表示して終了する)。

Pi5がGitHubへ到達できない環境(オフライン現場等)では、scp/USB等で転送済みの
ローカルクローンから展開する`install_local.sh`を使う(GitHubへのアクセスは
一切発生しない)。ソース取得部分がgit clone/pullではなくrsyncでのローカル
コピーに変わる以外は`install.sh`と同じ:

```sh
./pi5/scripts/install_local.sh
```

さらに、PC側(Windows Git Bash/Mac/Linux)にあらかじめ作っておいたローカル
クローンから、Pi5への転送とインストールを1コマンドで行う`deploy_to_pi5.sh`
もある。PC側でこのリポジトリをclone済みの状態で:

```sh
./pi5/scripts/deploy_to_pi5.sh
# Pi5のIPアドレス/ホスト名: 192.168.1.50   ← 入力
# Pi5のユーザー名 [pi]:                    ← 入力(空Enterでpi)
```

を実行すると、Pi5のIPアドレス・ユーザー名の入力だけで、
1. ローカルクローンの中身(`.git`除く)をtar+ssh経由でPi5の`~/shonan-pi5-src`へ転送
2. Pi5上で`install_local.sh`を実行

まで自動で進む。追加ツール(sshpass/rsync)は使わず標準のssh/scp/tarのみで
動くため、Pi5への接続が発生する上記1・2のタイミングでそれぞれ標準のsshパス
ワードプロンプトが表示され、都度パスワードの入力が必要(合計2回。ビルドが
長時間に及ぶ場合、`sudo`のキャッシュが切れて追加でパスワードを求められる
こともある)。都度の入力自体を無くしたい場合はPi5にSSH公開鍵を登録し、
パスワード認証を使わない構成にする。

`SHONAN_INSTALL_DIR`・`SKIP_JA_KEYBOARD`・`SKIP_GNURADIO_BUILD`・
`SKIP_LANGSTONE_BUILD`をPC側で環境変数指定すると、Pi5側の`install_local.sh`
実行にもそのまま反映される:

```sh
SKIP_JA_KEYBOARD=1 SKIP_GNURADIO_BUILD=1 ./pi5/scripts/deploy_to_pi5.sh
```

日本語入力ビルド・受信(RX)用GNU Radio/gr-dvbs2rxビルド・Langstone V3ビルドは
それぞれ省略して時間短縮できる(省略した機能は使えなくなる):

```sh
SKIP_JA_KEYBOARD=1 SKIP_GNURADIO_BUILD=1 SKIP_LANGSTONE_BUILD=1 ./pi5/scripts/install.sh
```

環境変数で挙動を変更できる。

| 変数 | 既定値 | 効果 |
| --- | --- | --- |
| `SHONAN_INSTALL_DIR` | `$HOME/shonan-pi5` | リポジトリのclone/pull(またはコピー)先ディレクトリ |
| `LOCAL_SOURCE_DIR` | (未設定) | 設定時、ソース取得をGitHubのclone/pullではなく指定ディレクトリからのrsyncコピーに切り替える(`install_local.sh`が自動設定) |
| `QTVK_BUILD_DIR` | `/tmp/qtvirtualkeyboard-src` | Qt Virtual Keyboardのビルド作業ディレクトリ |
| `GR_DVBS2RX_BUILD_DIR` | `$HOME/gr-dvbs2rx` | gr-dvbs2rxのビルド作業ディレクトリ |
| `SKIP_JA_KEYBOARD` | `0` | `1`で日本語入力ビルド(3/9)を省略 |
| `SKIP_GNURADIO_BUILD` | `0` | `1`で受信(RX)用GNU Radio/gr-dvbs2rxビルド(4/9)を省略(受信機能は動作しなくなる) |
| `SKIP_LANGSTONE_BUILD` | `0` | `1`でLangstone V3のビルド(5/9)を省略 |

`install.sh`は以下の9ステップを順に実行する(`set -euo pipefail`のため、
いずれかが失敗した時点で即座に停止する)。

| ステップ | 内容 |
| --- | --- |
| 0/9 | 前提条件の確認(git/SSH鍵の有無を確認し、無ければ案内して終了) |
| 1/9 | ソース取得(`git clone`または`git pull`) |
| 2/9 | 実行時依存パッケージのインストール(apt) |
| 3/9 | 日本語入力(OpenWnn)対応版Qt Virtual Keyboardのビルド(既定で実施、実測10〜20分程度) |
| 4/9 | 受信(RX)用GNU Radio + gr-dvbs2rxの導入 |
| 5/9 | Langstone V3(SDRトランシーバー)のビルド |
| 6/9 | 起動時コンソール表示の抑制 |
| 7/9 | reboot/shutdown/起動アプリ切替のパスワード無し実行を許可(sudoers.d) |
| 8/9 | 電源電圧警告(稲妻アイコン)表示の抑制(`/boot/firmware/config.txt`) |
| 9/9 | systemdサービス登録(`shonan-gui.service`/`langstone.service`/`shonan-boot-menu.service`) |

途中で通信・電源が切れない環境で実行すること。完了後、起動のたびに
「Shonan_Lite / Langstone V3」を選ぶ全画面メニュー
(`shonan-boot-menu.service`)が自動起動する。選んだ側の`shonan-gui.service`/
`langstone.service`をsystemdに登録・起動する。あわせて
`/boot/firmware/config.txt`へ`avoid_warnings=1`(電源電圧警告アイコンの表示抑制)
を未設定なら自動で追記する(反映には再起動が必要)。

### インストール後の確認

インストールが終わったら、まず実機のホーム画面から「ヘルプ」を開いて
使い方を確認する。画面構成、送受信の基本操作、設定項目、トラブルシュー
ティング等の各章が実機の現在の仕様に合わせてまとまっている。

## 実機LCDの画面キャプチャー

### アプリ内蔵のスクリーンショット機能(推奨)

Shonan_Lite(GUI)は起動中、Unixドメインソケット`/tmp/shonan-pi5-gui.sock`でコマンドを受け付ける。
`screenshot`を送ると、表示中の画面を`/tmp/shonan_lcd_actual.png`に保存する(GUIは止まらない)。
`navigate:<画面名>`で任意の画面へ移動できる(画面名: `home` `tx` `rx` `frequency` `rssi`
`symbolrate` `fec` `modulation` `videosource` `streamoutput` `rxgain` `txpower` `manual`
`settings` `testequipment` `presets`)。

```bash
python3 -c "import socket,sys; s=socket.socket(socket.AF_UNIX); s.connect('/tmp/shonan-pi5-gui.sock'); s.sendall(sys.argv[1].encode()); s.close()" navigate:rssi
python3 -c "import socket,sys; s=socket.socket(socket.AF_UNIX); s.connect('/tmp/shonan-pi5-gui.sock'); s.sendall(sys.argv[1].encode()); s.close()" screenshot
```

起動直後は「アプリ起動時にPlutoも再起動しています…」の表示(最大25秒)が写ることがあるので、
起動から30秒ほど待ってから撮る。

### kmsgrabによる取得

Shonan_LiteはLCDへQt/DRMで直接描画しているため、`/dev/fb0`を読み出す方法では
起動コンソールなど、最終合成前の内容になることがある(素の色1色などになる)。
実際にLCDへ表示されている画面を取得する場合は、KMSのCRTC/Planeを指定して
`ffmpeg`の`kmsgrab`を使う。

★`/dev/dri/card0`はモードセッティング非対応のスタブデバイスで、これを指定すると
`kmsgrab`が`Failed to set universal planes capability`/`Operation not supported`
で失敗する(実機で確認)。DSIパネルを実際に駆動しているのは**`/dev/dri/card1`**
なので、必ずこちらを指定する。

まず実機で現在のCRTC/Plane IDを確認する(再起動などでIDが変わる場合がある):

```bash
kmsprint
```

現在の実機ではCRTC IDが`36`、Plane IDが`34`なので、以下でLCD画面をPNG化できる。
`sudo`のパスワード入力が必要になる。

```bash
sudo ffmpeg -y -hide_banner \
  -f kmsgrab -device /dev/dri/card1 \
  -crtc_id 36 -plane_id 34 -framerate 1 -i - \
  -vf hwdownload,format=bgr0 -frames:v 1 -update 1 /tmp/shonan_lcd_actual.png
```

MacなどのPCへコピーする:

```bash
scp pi@<Pi5のIPアドレス>:/tmp/shonan_lcd_actual.png \
  ~/Desktop/shonan_lcd_actual.png
```

`/dev/fb0`の直接取得は、LCDの最終表示を取得できない場合があるため、実機LCDの
スクリーンショットには使用しない。

### 実行条件

一般ユーザーが実行して`install.sh`が正常完了するには、以下が必要。

- **Raspberry Pi OS 64bit(aarch64)であること**(32bit版不可)
- **`git`が事前にインストール済み**であること
- **GitHub/apt配布ミラーへのインターネット到達性**
- **sudoが使える対話的な実行**(パスワード入力に応答できるtty)
- **`patch`コマンドが使えること**

詳細な各手順の解説・トラブルシュートは
[`pi5/docs/install_script_guide.md`](pi5/docs/install_script_guide.md)
(DOCX版: `pi5/docs/install_script_guide.docx`)を参照。

## Langstone V3(SDRトランシーバー)への切替

Pi5起動後にまず表示される「起動するアプリを選択してください」メニュー
(`shonan-boot-menu.service`)、またはShonan_Lite Home画面の「Langstone V3」
ボタンから、[g4eml/Langstone-V3](https://github.com/g4eml/Langstone-V3)
(VHF/UHF/マイクロ波帯SDRトランシーバー、ADALM-Pluto対応)へ切り替えられる。
Langstone V3はQt eglfsとは別に`/dev/fb0`を直接描画する独立アプリのため、
DATV送受信アプリとは同時起動できないが、**`shonan-gui.service`/
`langstone.service`/`shonan-boot-menu.service`がsystemdの`Conflicts=`で
互いに排他制御されているため、Pi5自体のrebootは不要**で
`systemctl start`だけで即座に切り替わる(以前はPi5ごとrebootしていたが、
`shonan-boot-menu.service`導入により不要になった)。

- Shonan_Lite Home画面の「Langstone V3」ボタン → Langstone V3が起動
  (現在稼働中のShonan_Liteプロセスはsystemdが自動停止)
- Langstone V3の設定メニュー内「BACK TO SHONAN_LITE」ボタン →
  Shonan_Lite Home画面に戻る

切替時にPluto(とPA_Power/PTTコントローラの12V電源)は**再起動しない**
(以前は切替のたびにPlutoを再起動しており、数十秒かかっていた)。実機試験で、
DATV→Langstone→DATVとPlutoを再起動せずに切り替えても、Langstoneの送受信と
DATVの送受信(オンデバイス復調による自局信号のロック)が正常に動くことを確認した。
ただしLangstoneは受信中にPlutoの送信LO(`altvoltage1`)をpowerdownしたまま終了し、
そのままではDATV送信の電波が出ないため、「GOTO SHONAN_LITE」で戻るときは
Langstone側とShonan_Lite側の両方で送信LOを元に戻す。
Langstoneからの切替であることは`/tmp/shonan_switch_from_langstone`で伝え、
Shonan_Liteはこれがあるときだけ起動時のPluto再起動を省く(使ったら消すので、
その後のアプリ再起動やPi5の電源投入時は従来どおり再起動する)。Langstone側の
`run_pluto`は`/tmp/langstone_goto_shonan`があるとき、終了後のPluto再起動を省く。Plutoが`fmcomms2_source: Unable to refill buffer`のように
詰まった場合は、Home画面の「アプリ再起動」(Plutoも再起動する)で復旧できる。

内部的には`~/.pi5_boot_mode_langstone`マーカーファイルの有無をsystemdの
`ConditionPathExists`で判定し、`shonan-gui.service`/`langstone.service`の
どちらを起動すべきかを決める(ブート時だけでなく、アプリ内からの切替時にも
マーカーを書き換えてから対象サービスを直接startする)。

ウォーターフォール/スペクトラム表示は幅約512px→約790pxへ拡張済み
(FFT点数自体はGNU Radio側のfft_size=512のまま、SCALEPX()マクロで描画のみ
引き伸ばしている。帯域インジケータ・目盛り・タッチ判定も含め一貫して変換)。
横方向にはSQLボタン(x=30〜130)/Volボタン(x=660〜)と同じY帯で重なり広げる
余地が無かったため、スペクトラム欄の高さ(80→55px)とウォーターフォールの
表示履歴行数(130→90行)を縮めて表示位置を上に詰め、SQL/Vol/RITいずれとも
Y方向に重ならない帯(Y=130〜295)に収めることで横方向をほぼ画面全幅まで
広げた(実機で確認、詳細は下記パッチ参照)。
詳細は
[`pi5/docs/patches/langstone_v3_shonan_lite.patch`](pi5/docs/patches/langstone_v3_shonan_lite.patch)
(upstream差分)を参照。

`g4eml/Langstone-V3`本家が更新された場合、`pi5/third_party/Langstone-V3/`を
直接上書きすると上記の改造が失われる。
[`pi5/scripts/update_langstone_from_upstream.sh`](pi5/scripts/update_langstone_from_upstream.sh)
を実行すると、本家を読み取り専用でclone → このパッチを適用 →
成功した場合のみ`pi5/third_party/Langstone-V3/`を置き換える(本家への
書き込みは一切行わない)。パッチが当たらない場合は改造箇所と本家の変更が
衝突しているため、エラーで止まり手動マージが必要になる。

## 関連ドキュメント

- [`pi5/docs/install_script_guide.md`](pi5/docs/install_script_guide.md) — install.shの詳細ガイド
- [`pi5/docs/qtvirtualkeyboard_ja_build.md`](pi5/docs/qtvirtualkeyboard_ja_build.md) — 日本語オンスクリーンキーボードのビルド手順・ハマりどころ
- [`pi5/docs/shonan_pi5_operation_manual.docx`](pi5/docs/shonan_pi5_operation_manual.docx) — 操作説明書(各画面のスクリーンショット付き)
- [`pi5/gui/manual_content.py`](pi5/gui/manual_content.py) — アプリ内Helpの内容(章データ)。操作説明書もこれから生成する
- [`pi5/docs/build_operation_manual.py`](pi5/docs/build_operation_manual.py) — 操作説明書(DOCX)の生成スクリプト
  (`python pi5/docs/build_operation_manual.py`、python-docxが必要)
- [`pi5/third_party/rpi-dvbs2-receiver-gui/`](pi5/third_party/rpi-dvbs2-receiver-gui/) — GNU Radio/gr-dvbs2rx受信フローグラフの参考実装(kazushinjo/rpi-dvbs2-receiver-guiより取り込み)

## クレジット

- 受信部の方式考案・受信部原システム設計: 山崎慎慈氏(JE1BTA)
  rpi-dvbs2-receiver-guiの設計に基づきます
- 受信部安定化調査修正・再捕捉修正・本アプリ開発: 真城和一
- Langstone V3(SDRトランシーバー): [g4eml/Langstone-V3](https://github.com/g4eml/Langstone-V3)
  (オリジナルから一部変更しています。差分は
  [`pi5/docs/patches/langstone_v3_shonan_lite.patch`](pi5/docs/patches/langstone_v3_shonan_lite.patch)を参照)

## License

This software is licensed under the GNU General Public License v3.0 (GPLv3).
Full license text: [LICENSE](LICENSE)

- Langstone V3 (SDR transceiver, [g4eml/Langstone-V3](https://github.com/g4eml/Langstone-V3)): GPLv3
- Reception subsystem design (Shinji Yamazaki, JE1BTA): GPLv3
- Application development, reception stability fixes (Kazuichi Shinjo): GPLv3
