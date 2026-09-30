"""現行Mac風GUIのHelpとDOCX操作説明書で共有する章データ。"""

MANUAL_SCREENSHOTS = {
    "1. 画面構成": ["screenshot_home.png", "test1_langstone.png"],
    "2. 起動・終了と安全": ["screenshot_boot_menu.png", "pi5-startup-message-updated.png"],
    "3. 設定画面": ["screenshot_settings.png"],
    "4. 送信前の設定": ["screenshot_frequency.png", "screenshot_streamoutput.png", "screenshot_symbolrate.png",
                    "screenshot_fec.png", "screenshot_modulation.png", "screenshot_videosource.png",
                    "screenshot_rxgain.png", "screenshot_txpower.png", "screenshot_presets.png"],
    "5. RSSI測定": "screenshot_rssi.png",
    "6. 送信画面": "screenshot_tx.png",
    "7. 受信画面": "screenshot_rx.png",
    "9. Help・機器試験・再起動": ["screenshot_manual.png", "screenshot_testequipment.png",
                             "shonan-pi5-startup-pluto-restarting.png"],
}

MANUAL_SECTIONS = [
    ("重要", [
        ("Plutoのユーザー名・パスワード", "Plutoのユーザー名(root)・パスワード(analog)はデフォルト値のまま変更しないでください。本アプリとLangstone V3は、SSHでPlutoにログインしてリブートしています(アプリ起動時・アプリ再起動・機器試験・Langstone終了時)。変更するとPlutoをリブートできなくなります。"),
    ]),
    ("クレジット", [
        ("クレジット",
         "受信部の方式考案・受信部原システム設計: 山崎慎慈氏(JE1BTA) rpi-dvbs2-receiver-guiの設計に基づきます\n"
         "受信部安定化調査修正・再捕捉修正・本アプリ開発: 真城和一\n"
         "本アプリは、Dave Crump氏(G8GKQ)が開発したDATV送受信機プロジェクト「Portsdown」に啓発され、"
         "開発したものです。同氏の先駆的な取り組みに感謝いたします。"),
        ("免責事項",
         "本プログラムを使用して生じたいかなる損害についても、開発者は一切の責任を負いません。"
         "ご自身の責任においてご利用ください。"),
    ]),
    ("クイックスタート", [
        ("1. 送信周波数の設定", "ホーム画面の「周波数」を押し、実際に送信する周波数を設定します。"),
        ("2. シンボルレートの設定", "ホーム画面の「シンボルレート」を押し、送信信号のシンボルレートを設定します。まずは333 kS/sから試すことをおすすめします。"),
        ("3. FECの設定", "ホーム画面の「誤り訂正(FEC)」を押し、FEC 3/5を選びます。変調方式はQPSKのままでかまいません。"),
        ("4. 映像ソースの選択", "ホーム画面の「映像ソース」を押し、映像ソースを選びます。最初はカメラの代わりにカラーバー(テストパターン)を選ぶと、配線や設定だけを手早く確認できます。"),
        ("5. 送信開始", "ホーム画面の「送信」を押すと送信画面が開きます(この時点ではまだ送信されません)。送信画面のプレビューを確認し、「送信開始」を押すと実際に送信が始まります。停止するときは同じ位置に表示される「送信停止」を押します。"),
    ]),
    ("1. 画面構成", [
        ("ホーム画面", "ホーム画面は各機能への入口です。「送信」「受信」「周波数」「RSSI測定」「シンボルレート」「誤り訂正(FEC)」「変調方式」「映像ソース」「出力設定」「RXゲイン」「TX出力」「設定」「機器試験」「ヘルプ」「アプリ再起動」「電源オフ」に加え、「Langstone(SDRトランシーバー)」「プリセット」への入口も表示します。"),
        ("Pluto電源カード（オプション機能）", "「Pluto電源」カードは、PA_Power/PTTコントローラ(ESP32、hardware/W5500_PA_PTT_Control)を接続した環境専用のオプション機能です。押すとPTTコントローラ経由でPluto+含む12V系統をOFF→3秒待機→ONする電源サイクル操作を行います。PTTコントローラ未設定の環境では使用できません(設定画面で「ESP32 W5500を使用する」がOFF、またはIPアドレス未設定の場合はエラー表示になります)。"),
        ("画面の共通操作", "各画面のボタンをタップして操作します。画面内の「ホームへ戻る」でホーム画面に戻ります。"),
    ]),
    ("2. 起動・終了と安全", [
        ("起動アプリの選択", "Pi 5起動後、まず「起動するアプリを選択してください」画面が表示されます。「Shonan_Lite (DATV)」または「Langstone V3(SDRトランシーバー)」を選択して起動します。この画面でPluto IP設定の確認・変更も行えます。"),
        ("起動", "Plutoを先に起動し、Pi 5とEthernet接続します。起動アプリ選択でShonan_Liteを選ぶとShonan_Liteが起動し、「アプリ起動時にPlutoも再起動しています…」を表示します。Plutoの再起動確認に25秒以上かかる場合は確認をスキップしてホーム画面を表示します。Plutoの接続先は設定画面で指定します。"),
        ("RF接続の注意", "TXとRXを直結しないでください。室内で確認する場合は、TX → 40 dB以上の外部アッテネータ → RXの順に接続します。"),
        ("終了", "送信中・受信中の場合は、それぞれの画面で停止してからホーム画面の「電源オフ」を使用します。"),
    ]),
    ("3. 設定画面", [
        ("表示言語", "画面の表示言語を「日本語」「English」から選びます。選ぶとすぐに全画面の表示が切り替わり、設定は保存されます。"),
        ("送信先（Pluto Tx）", "PlutoのIPアドレスを入力します。UDP-TSポートは8282固定(Pluto側)です。"),
        ("PA_Power/PTTコントローラ（ESP32）", "PA_Power/PTTコントローラ(ESP32+W5500、hardware/W5500_PA_PTT_Control)を使用するかどうかを「ESP32 W5500を使用する」で選び、IPアドレスを入力します。OFFまたは空欄なら連携しません(OFFにしてもIPアドレスは保持されます)。使用する場合、送信開始/終了に連動してPTTを、アプリ起動/終了に連動して12V電源(Pluto+含む)を自動でON/OFFします。ホーム画面の「Pluto電源」カード(オプション機能)から手動での電源サイクル(OFF→3秒待機→ON)も行えます。"),
        ("オンデバイス復調",
         "オンデバイス復調は開発時の動作確認用の機能です。ONにする操作をすると、まず確認ポップアップが表示されます。"
         "PlutoのTX端子とRX端子の間に40 dB以上の外部アッテネータが入っていない状態で送信するとPlutoを破損する恐れがある"
         "旨が赤字で表示され、「はい」を選んだ場合のみオンデバイス復調がONになります。「いいえ」を選ぶとチェックは自動的に"
         "OFFへ戻ります。ONのときだけ送信画面に「受信画面へ」ボタンが表示されます。OFFの場合は送信画面から受信画面へ"
         "直接移動できません。OFFの間は送信中の受信開始・受信中の送信開始がエラーになります(送受信を同時に使うには"
         "ONにしてください)。"),
        ("受信診断 / RX Diagnostics", "「IIOプリフライト試験を実施する」をONにすると、受信開始前にIIOコンテキストの疎通確認を行います。"),
        ("システム日時 / System Date & Time", "このPi 5にはRTCバッテリが無いため、ネットワーク接続が無い現場運用では起動のたびに日時がリセットされます。カレンダーから日時を選び「この日時を設定 / Set」を押すと、NTP同期を止めた上でシステム日時に反映します。"),
    ]),
    ("4. 送信前の設定", [
        ("周波数", "周波数画面で運用周波数を選択または入力します。現在のRFループバック試験例は437,000 kHz（437.000 MHz）です。"),
        ("出力設定", "出力設定画面の「Pluto URI」にPlutoのIPアドレスを入力します。「自動検出」を押すと、同一LAN上のPlutoを自動的に探して入力欄へ反映します(見つからない場合は電源とLAN配線を確認してください)。「送信先ポート(Pluto側固定)」は8282固定で変更できません。「受信TSポート」「ステータスポート」は必要に応じて変更します。"),
        ("シンボルレート", "送信信号のシンボルレートを設定します。RFループバック試験例は500 kS/sです。"),
        ("FEC・変調方式", "送信側と受信側でFECと変調方式を一致させます。試験例はQPSK、FEC 3/5です。変調方式はQPSK・8PSKから選び、FECの選択肢は選択中の変調方式で実際に動作する組み合わせのみに絞り込まれます(QPSK: 1/2・3/5・8/9、8PSK: 3/5・8/9。9/10は未実装のため選択肢に出ません)。"),
        ("映像ソース", "映像ソース画面でUSBカメラ、画像ファイル(png/jpg/jpeg/bmp、静止画を反復送信)、またはテストパターン(カラーバー)を選びます。RF切り分けではテストパターンを使用します。映像ソースが「カメラ」のときは「撮影」ボタンでカメラ映像をJPG(1920x1080)として撮影でき、ホームフォルダのPictures/Shonan_Liteに保存されます。保存した画像は「ファイル選択」(このフォルダから開きます)で送信画像として選べます。送信中は撮影できません。画面下部の「コールサイン」「備考」(任意)欄に入力した文字は映像に焼き込まれ、日時も右下に表示されます。各入力欄の右の選択欄で文字サイズ(コールサイン36〜256px、備考16〜64px)と文字色(白・黄・赤・緑・青・水色・橙・黒)を選べます。カメラ映像と画像ファイルに適用されます(テストパターンには元々コールサインが描かれているため適用されません)。送信映像の解像度はフルHD(1920x1080)固定で、縦横比が異なる映像は黒帯を付けて収めます。"),
        ("RXゲイン", "AGCをONにすると自動ゲイン、OFFにすると手動ゲインを使用します。手動時は受信状態を見ながらゲインを調整します。"),
        ("TX出力", "TX出力は接続先とアッテネータに合わせて設定します。0 dBが最大出力です。"),
        ("プリセット", "ホーム画面の「プリセット」で、周波数・シンボルレート・FEC・変調方式・映像ソース・コールサイン等の現在の設定を5件まで登録できます。「登録/変更」を押して名前を付けると現在の設定を保存し、プリセット名を押すとその設定を呼び出してPlutoにも反映します。「削除」は確認のあと登録を消します。プリセット1は未登録の間「RFループバック」(437.000 MHz / 500 kS/s / QPSK / FEC 3/5、テストパターン、オンデバイス復調ON)として使えます。送受信中は登録・呼び出し・削除はできません。"),
    ]),
    ("5. RSSI測定", [
        ("RSSI測定とは", "指定した範囲の周波数をスキャンして受信レベル(RSSI)をグラフ表示する機能です。中心周波数は周波数画面で設定した値です(未設定の場合は先に周波数画面で設定してください)。設定画面の「オンデバイス復調」がOFF(通常運用)のときは送信せず、相手局の電波のRSSIを測って相手局の実際の周波数を素早く特定します(相手局が送信していなければ雑音だけなのでグラフは平らです)。ONのときはテスト用の機能で、自局も自動的に送信し、自分が送信した信号のRSSIを測ります。"),
        ("検索条件", "検索レンジを「±5MHz」「±10MHz」「±20MHz」から選びます(選択中のレンジは水色で強調されます)。ステップ(kHz)はテンキーで入力し、1 kHz以上を指定します。"),
        ("RXゲイン", "画面右側の「RXゲイン」で、AGC(自動調整)のON/OFFと手動ゲイン(0〜73 dB、「−」「+」ボタン。長押しで連続変更)を調整できます。設定はRXゲイン画面と共通で、検索中でも変更できます。ゲインを変えるとRSSIの値が変わるため、検索中に変更した場合はその周回を最初からやり直します。AGCがONの間は手動ゲインは変更できません。"),
        ("検索の実行", "「検索開始」を押すとスキャンを開始し、進行中はステータスに現在の周波数とRSSIが表示されます。画面右側の「検索方法」で、「連続」(既定)を選ぶと、スキャンは範囲の終わりまで進むと最初に戻り、「検索停止」を押すまで繰り返し実行されます。「1回」を選ぶと、範囲の終わりまで1回スキャンして自動で停止します。検索中に切り替えた場合は、実行中の周回が終わった時点から反映されます。どちらの場合も、他の画面へ移ると停止します。"),
        ("検索結果", "1回分のスキャンが終わるたびに「最も強い周波数」が更新されて表示されます(RSSIは値が小さいほど信号が強いことを示します)。"),
        ("送信の自動開始について", "設定画面の「オンデバイス復調」がONの場合、「検索開始」を押すと自動的に送信を開始します(送信が既に始まっている場合は、一旦停止してから検索開始時点の設定でやり直します)。この自動送信は、映像ソースの選択に関係なくテストパターンで行います(カメラが接続されていなくても送信でき、保存済みの映像ソースの設定は変わりません)。送信開始(またはやり直し)から3秒待ってからスキャンを始めます。この自動送信は「検索停止」を押すか、「1回」で範囲の終わりまで進むか、他の画面へ移ると自動的に停止します。TXとRXを直結せず、必ず40 dB以上のアッテネータを介して接続してください。"),
    ]),
    ("6. 送信画面", [
        ("送信画面の見方", "上部に映像プレビュー、下部に送信状態、シンボルレート、音声レベル、通信統計を表示します。テストパターン選択時はカラーバーが表示されます。送信停止中は「送信開始」ボタンが表示されます。"),
        ("送信開始", "ホーム画面の「送信」は送信画面を開くだけです。送信を開始するには、送信画面の「送信開始」を押します。"),
        ("送信停止", "送信中に同じ位置へ表示される「送信停止」を押します。停止表示を確認してから周波数・出力・配線を変更します。"),
        ("画面移動", "設定画面でオンデバイス復調をONにしている場合のみ「受信画面へ」が表示されます。常に「設定」「ホームへ戻る」が利用できます。"),
    ]),
    ("7. 受信画面", [
        ("受信開始", "受信設定を送信条件に合わせ、「受信開始」を押します。試験例では437.000 MHz、500 kS/s、QPSK、FEC 3/5を使用します。受信中はLOCK、実測ビットレート、パケット数、エラー数を確認できます。"),
        ("受信停止", "受信を終了するときは「受信停止」を押します。送信も行っている場合は、受信停止後に送信停止を押します。"),
        ("オンデバイス復調表示", "オンデバイス復調が有効な場合、受信画面にオレンジ色の状態表示が出ます。受信映像が黒い場合は、まず周波数、シンボルレート、FEC、変調方式、配線、TX状態を確認します。"),
        ("音量", "受信画面の音量スライダーで再生音量を調整します。初期値は50%です。"),
    ]),
    ("8. 基本運用手順", [
        ("送信のみ", "1) ホームで「周波数」「シンボルレート」「FEC」「変調方式」「映像ソース」「TX出力」を設定、2)「送信」を押す、3) 送信画面で映像プレビューを確認、4)「送信開始」を押す、5) 終了時に「送信停止」を押す。"),
        ("受信のみ", "1) 受信条件を送信側に合わせる、2) ホームで「受信」を押す、3) 受信画面で「受信開始」を押す、4) 映像・音声・統計を確認、5) 終了時に「受信停止」を押す。"),
        ("RF確認", "TX → アッテネータ → RXの接続を確認し、送信開始後に受信開始します。直結やアッテネータなしの接続は行わないでください。"),
    ]),
    ("9. Help・機器試験・再起動", [
        ("Help", "Help画面左側の「ヘルプ項目」一覧から章を選ぶと、右側に本文が表示されます。"),
        ("機器試験", "機器試験は接続やプロセスの確認に使用します。診断結果はRF環境やアンテナ性能を保証するものではありません。"),
        ("アプリ再起動", "送受信を停止してから「アプリ再起動」を使用します。ホーム画面を隠して再起動メッセージを表示し、Plutoの確認を最大25秒待ちます。確認できない場合はホーム画面へ進みます。"),
    ]),
    ("10. トラブルシューティング", [
        ("送信が始まらない", "送信画面へ移動しただけでは送信されません。「送信開始」を押し、映像ソース、Pluto IP、周波数、TX出力を確認します。"),
        ("受信できない", "送信側と受信側の周波数437.000 MHz、シンボルレート500 kS/s、FEC 3/5、変調QPSKを一致させ、TXが送信中であること、アッテネータと配線、RXゲインを確認します。"),
        ("カメラ映像が出ない", "USBカメラ(C920等)の接続、映像ソース設定、カメラ権限を確認します。映像ソース画面のプレビューで映るか確認できます。カラーバーへ切り替えて送信系だけを切り分けることもできます。"),
        ("映像は黒いが受信している", "受信画面の状態表示と通信統計を確認し、映像ソース、H.264映像、送信開始状態を確認します。"),
        ("オンデバイス復調がONにならない", "ONにする操作をすると40 dBアッテネータの確認ポップアップが出ます。「いいえ」を選ぶとOFFへ戻る仕様です。アッテネータの接続を確認してから「はい」を選んでください。"),
    ]),
    ("11. 現在の接続情報", [
        ("Pi 5", "SSHユーザー: pi / IPアドレスは環境に合わせて設定"),
        ("Pluto", "IPアドレスは環境に合わせて設定 / SSHユーザー: root"),
        ("運用例", "周波数437.000 MHz、映像ソースはカメラまたはテストパターン、シンボルレート500 kS/s、QPSK、FEC 3/5、オンデバイス復調ON。"),
    ]),
    ("12. RFループバック試験用設定", [
        ("試験パラメータ一覧", "周波数: 437.000 MHz\nシンボルレート: 500 kS/s\n変調方式: QPSK\nFEC: 3/5\nロールオフ: 0.35\nフレーム: Long Frame\nRXゲイン: 60 dB\n映像ソース: テストパターン\nオンデバイス復調: ON\nTX/RX同時動作: ON"),
        ("パイロット信号", "パイロット信号は常にONで固定です(設定画面に切り替えはありません)。送信側(Pluto、pilots=On固定)・受信側(Pi 5、--pilots固定)とも同じ設定になっているため、ユーザー側での操作は不要です。"),
        ("接続と確認", "TXとRXを直結せず、TX → 40 dB以上のアッテネータ → RXの順に接続します。送信開始後に受信を開始し、受信画面でLOCK、SOF、フレーム数、パケット数、エラー数、映像表示を確認します。"),
    ]),
    ("13. Plutoファームウェア", [
        ("使用ファームウェア", "Pluto無印でF5OEO製DATVカスタムファームウェア datvplutofrm v0.32-dirtyを使用します。送信はPluto内蔵のDVB-S2変調デーモンpluto_dvbを使用します。"),
        ("ファームウェア確認時の注意", "ファームウェアを変更した場合は、pluto_dvb、UDP TS受信経路、周波数、変調方式、FEC、ロールオフ、フレーム長、パイロット設定の互換性を確認してからRF試験を行います。"),
        ("Plutoのユーザー名・パスワード", "Plutoのユーザー名(root)とパスワード(analog)は工場出荷時のデフォルト値のまま変更しないでください。本アプリとLangstone V3は、Plutoの再起動(アプリ起動時・アプリ再起動・機器試験・Langstone終了時)と設定の読み出しに、このデフォルト値でSSH接続しています。変更するとPlutoを再起動できなくなります。"),
    ]),
]

# English chapters for the Help screen. Mirrors MANUAL_SECTIONS chapter for
# chapter and item for item; keep the two in sync when either changes.
MANUAL_SCREENSHOTS_EN = {
    "1. Screen Overview": ["screenshot_home.png", "test1_langstone.png"],
    "2. Startup, Exit and Safety": ["screenshot_boot_menu.png", "pi5-startup-message-updated.png"],
    "3. Settings Screen": ["screenshot_settings.png"],
    "4. Settings Before Transmitting": ["screenshot_frequency.png", "screenshot_streamoutput.png",
                                        "screenshot_symbolrate.png", "screenshot_fec.png",
                                        "screenshot_modulation.png", "screenshot_videosource.png",
                                        "screenshot_rxgain.png", "screenshot_txpower.png",
                                        "screenshot_presets.png"],
    "5. RSSI Measurement": "screenshot_rssi.png",
    "6. Transmit Screen": "screenshot_tx.png",
    "7. Receive Screen": "screenshot_rx.png",
    "9. Help, Diagnostic and App Restart": ["screenshot_manual.png", "screenshot_testequipment.png",
                                            "shonan-pi5-startup-pluto-restarting.png"],
}

MANUAL_SECTIONS_EN = [
    ("Important", [
        ("Pluto username and password", "Keep the Pluto's username (root) and password (analog) at their default values. This app and Langstone V3 log in to the Pluto via SSH to reboot it (at app start, app restart, equipment test and Langstone exit). If they are changed, the Pluto cannot be rebooted."),
    ]),
    ("Credits", [
        ("Credits",
         "Receiver method and original receiver system design: Shinji Yamazaki (JE1BTA), "
         "based on the design of rpi-dvbs2-receiver-gui\n"
         "Receiver stabilization investigation and fixes, reacquisition fixes, and "
         "development of this app: Kazuichi Shinjo\n"
         "This app was developed inspired by \"Portsdown\", the DATV transceiver project "
         "created by Dave Crump (G8GKQ). We extend our deep gratitude for his pioneering work."),
        ("Disclaimer",
         "The developers accept no liability whatsoever for any damage arising from the "
         "use of this program. Use it at your own risk."),
    ]),
    ("Quick Start", [
        ("1. Set the TX frequency", "Press \"Frequency\" on the Home screen and set the frequency you will actually transmit on."),
        ("2. Set the symbol rate", "Press \"Symbol Rate\" on the Home screen and set the symbol rate of the transmitted signal. Trying 333 kS/s first is recommended."),
        ("3. Set the FEC", "Press \"FEC\" on the Home screen and choose FEC 3/5. Leave the modulation at QPSK."),
        ("4. Choose the video source", "Press \"Video Source\" on the Home screen and choose a video source. Choosing color bars (test pattern) instead of the camera first lets you quickly check wiring and settings alone."),
        ("5. Start transmitting", "Press \"Transmit\" on the Home screen to open the TX screen (nothing is transmitted yet at this point). Check the preview on the TX screen, then press \"Start TX\" to actually begin transmitting. To stop, press \"Stop TX\", shown in the same position."),
    ]),
    ("1. Screen Overview", [
        ("Home screen", "The Home screen is the entrance to every function. It shows \"Transmit\", \"Receive\", \"Frequency\", \"RSSI Measurement\", \"Symbol Rate\", \"FEC\", \"Modulation\", \"Video Source\", \"Stream Output\", \"RX Gain\", \"TX Power\", \"Config\", \"Diagnostic\", \"Help\", \"App Restart\" and \"Power Off\", plus entrances to \"Langstone (SDR Transceiver)\" and \"Presets\"."),
        ("Pluto Power card (optional feature)", "The \"Pluto Power\" card is an optional feature only for environments with a PA_Power/PTT controller (ESP32, hardware/W5500_PA_PTT_Control) connected. Pressing it performs a power-cycle operation via the PTT controller: OFF → wait 3 seconds → ON for the 12 V line including the Pluto+. It cannot be used in environments without a PTT controller configured (shown as an error if \"Use ESP32 W5500\" is OFF or the IP address is unset on the Settings screen)."),
        ("Common screen operation", "Tap each screen's buttons to operate it. \"Back to Home\" on a screen returns to the Home screen."),
    ]),
    ("2. Startup, Exit and Safety", [
        ("Choosing the app at boot", "After the Pi 5 boots, the \"Choose the app to start\" screen appears first. Choose \"Shonan_Lite (DATV)\" or \"Langstone V3 (SDR Transceiver)\" to start it. You can also check/change the Pluto IP setting on this screen."),
        ("Startup", "Power on the Pluto first and connect it to the Pi 5 via Ethernet. Choosing Shonan_Lite at the app-selection screen starts Shonan_Lite, showing \"Restarting Pluto at app startup…\". If confirming the Pluto restart takes 25 seconds or more, the confirmation is skipped and the Home screen is shown. The Pluto's destination is specified on the Settings screen."),
        ("RF connection caution", "Never connect TX directly to RX. To test indoors, connect TX → external attenuator of 40 dB or more → RX."),
        ("Exit", "If transmitting or receiving, stop it on its own screen first, then use \"Power Off\" on the Home screen."),
    ]),
    ("3. Settings Screen", [
        ("Display Language", "Choose the display language from \"日本語\" (Japanese) and \"English\". All screens switch immediately and the choice is saved."),
        ("Destination (Pluto Tx)", "Enter the Pluto's IP address. The UDP-TS port is fixed at 8282 (on the Pluto side)."),
        ("PA_Power/PTT Controller (ESP32)", "Choose whether to use the PA_Power/PTT controller (ESP32 + W5500, hardware/W5500_PA_PTT_Control) with \"Use ESP32 W5500\", and enter its IP address. The link is disabled when it is OFF or the address is empty (the IP address is kept even when OFF). When used, PTT follows TX start/stop and the 12 V power (including the Pluto+) is switched ON/OFF automatically at app start/exit. A manual power cycle (OFF → wait 3 seconds → ON) is also available from the \"Pluto Power\" card (optional feature) on the Home screen."),
        ("On-device Demodulation",
         "On-device demodulation is a feature for development testing. Turning it ON first shows a "
         "confirmation popup. It states in red that transmitting without a 40 dB or greater external "
         "attenuator between the Pluto's TX and RX ports may damage the Pluto, and on-device "
         "demodulation is turned ON only if you choose \"Yes\". Choosing \"No\" automatically returns "
         "the checkbox to OFF. Only while ON does the TX screen show a \"Go to RX\" button; while OFF "
         "you cannot move directly from the TX screen to the RX screen. While OFF, starting RX during "
         "TX or starting TX during RX is an error (turn it ON to use TX and RX at the same time)."),
        ("RX Diagnostics", "When \"Run IIO preflight test\" is ON, an IIO context connectivity check runs before starting RX."),
        ("System Date & Time", "Since this Pi 5 has no RTC battery, the date and time reset on every boot in field use without a network connection. Choose a date/time from the calendar and press \"Set This Date & Time\" to stop NTP sync and apply it to the system clock."),
    ]),
    ("4. Settings Before Transmitting", [
        ("Frequency", "Select or enter the operating frequency on the Frequency screen. The current RF loopback test example is 437,000 kHz (437.000 MHz)."),
        ("Stream Output", "Enter the Pluto's IP address in \"Pluto URI\" on the Stream Output screen. Pressing \"Detect\" automatically looks for a Pluto on the same LAN and fills it into the field (if not found, check the power and LAN wiring). \"Destination port (fixed on Pluto)\" is fixed at 8282 and cannot be changed. Change \"RX TS port\" and \"Status port\" as needed."),
        ("Symbol Rate", "Set the symbol rate of the transmitted signal. The RF loopback test example is 500 kS/s."),
        ("FEC and Modulation", "Match FEC and modulation between the transmitting and receiving sides. The test example is QPSK, FEC 3/5. Choose the modulation from QPSK and 8PSK, and the FEC choices are narrowed to combinations that actually work with the selected modulation (QPSK: 1/2, 3/5, 8/9; 8PSK: 3/5, 8/9; 9/10 is not implemented so it does not appear as a choice)."),
        ("Video Source", "On the Video Source screen, choose a USB camera, an image file (png/jpg/jpeg/bmp, sent as a repeating still image), or a test pattern (color bars). Use the test pattern for RF isolation testing. When the video source is \"Camera\", the \"Capture\" button takes a still JPG (1920x1080) from the camera and saves it in Pictures/Shonan_Lite in the home folder. You can then choose the saved image as the TX image with \"File\" (it opens in that folder). Capturing is not possible while transmitting. The callsign and optional note entered in the \"Callsign\" and \"Note\" fields at the bottom of the screen are burned into the video, with the date and time shown at the bottom right. The selectors to the right of each field set the font size (callsign 36-256 px, note 16-64 px) and color (white, yellow, red, green, blue, cyan, orange, black). They apply to camera video and to an image file (the test pattern already has a callsign drawn into it, so it is not overlaid). The transmitted video is fixed at Full HD (1920x1080); video with a different aspect ratio is fitted with black bars."),
        ("RX Gain", "With AGC ON the gain is automatic; with AGC OFF, manual gain is used. When manual, adjust the gain while watching the reception state."),
        ("TX Power", "Set TX power to match the destination and attenuator. 0 dB is the maximum output."),
        ("Presets", "With \"Presets\" on the Home screen you can save up to five sets of the current settings (frequency, symbol rate, FEC, modulation, video source, callsign and so on). Press \"Save\" and enter a name to store the current settings; press a preset name to recall it and also apply it to the Pluto. \"Delete\" removes a preset after confirmation. While preset 1 is not registered it works as \"RF Loopback\" (437.000 MHz / 500 kS/s / QPSK / FEC 3/5, test pattern, on-device demodulation ON). Presets cannot be saved, recalled or deleted while transmitting or receiving."),
    ]),
    ("5. RSSI Measurement", [
        ("What RSSI Measurement does", "It scans a range of frequencies and graphs the received level (RSSI). The center frequency is the value set on the Frequency screen (if it is not set, set it there first). When \"On-device demodulation\" in Settings is OFF (normal operation), it does not transmit and measures the RSSI of the other station's signal to quickly identify its actual frequency (if the other station is not transmitting, only noise is received and the graph is flat). When it is ON, this is a test feature: your own station also transmits automatically and the RSSI of your own signal is measured."),
        ("Search conditions", "Choose the search range from ±5 MHz, ±10 MHz and ±20 MHz (the selected range is highlighted in light blue). Enter the step (kHz) with the keypad; specify 1 kHz or more."),
        ("RX gain", "\"RX Gain\" on the right side of the screen lets you turn AGC (automatic adjustment) on or off and set the manual gain (0 to 73 dB with the \"−\" and \"+\" buttons; hold to change continuously). The setting is shared with the RX Gain screen and can be changed even while a search is running. Changing the gain changes the RSSI values, so if you change it during a search the current pass is restarted from the beginning. The manual gain cannot be changed while AGC is on."),
        ("Running a search", "Press \"Start Search\" to begin scanning; while it runs, the status shows the current frequency and RSSI. With \"Search Mode\" on the right side of the screen set to \"Repeat\" (default), the scan returns to the start when it reaches the end of the range and repeats until you press \"Stop Search\". With \"Once\", it scans the range one time and stops by itself. If you switch the mode during a search, it takes effect when the current pass finishes. In both modes the search stops when you move to another screen."),
        ("Search result", "Each time one pass of the scan finishes, the \"Strongest frequency\" is updated and shown (a smaller RSSI value means a stronger signal)."),
        ("About automatic TX start", "When \"On-device demodulation\" in Settings is ON, pressing \"Start Search\" automatically starts transmitting (if TX is already running, it is stopped first and restarted with the settings in effect when the search begins). This automatic transmission always uses the test pattern regardless of the selected video source (it works without a camera, and the saved video source setting is not changed). Scanning starts 3 seconds after TX starts (or restarts). This automatic transmission stops on its own when you press \"Stop Search\", when \"Once\" reaches the end of the range, or when you move to another screen. Never connect TX directly to RX; always use an attenuator of 40 dB or more."),
    ]),
    ("6. Transmit Screen", [
        ("Reading the TX screen", "The video preview is at the top, and TX state, symbol rate, audio level and communication statistics are at the bottom. Color bars are shown when the test pattern is selected. The \"Start TX\" button is shown while TX is stopped."),
        ("Starting TX", "\"Transmit\" on the Home screen only opens the TX screen. To start transmitting, press \"Start TX\" on the TX screen."),
        ("Stopping TX", "While transmitting, press \"Stop TX\", shown in the same position. Check the stopped state before changing the frequency, power or wiring."),
        ("Screen navigation", "\"Go to RX\" is shown only when on-device demodulation is ON in Settings. \"Settings\" and \"Back to Home\" are always available."),
    ]),
    ("7. Receive Screen", [
        ("Starting RX", "Match the receive settings to the transmit conditions and press \"Start RX\". The test example uses 437.000 MHz, 500 kS/s, QPSK, FEC 3/5. While receiving you can check LOCK, the measured bitrate, packet count and error count."),
        ("Stopping RX", "Press \"Stop RX\" to end reception. If also transmitting, press Stop TX after stopping RX."),
        ("On-device demodulation indicator", "When on-device demodulation is enabled, an orange status indicator appears on the RX screen. If the received video is black, first check the frequency, symbol rate, FEC, modulation, wiring and TX state."),
        ("Volume", "Adjust the playback volume with the volume slider on the RX screen. The default is 50%."),
    ]),
    ("8. Basic Operating Procedure", [
        ("TX only", "1) On Home, set Frequency, Symbol Rate, FEC, Modulation, Video Source and TX Power. 2) Press \"Transmit\". 3) Check the video preview on the TX screen. 4) Press \"Start TX\". 5) Press \"Stop TX\" when finished."),
        ("RX only", "1) Match the receive conditions to the transmitting side. 2) Press \"Receive\" on Home. 3) Press \"Start RX\" on the RX screen. 4) Check video, audio and statistics. 5) Press \"Stop RX\" when finished."),
        ("RF check", "Confirm the TX → attenuator → RX connection, then start reception after starting transmission. Never connect directly or without an attenuator."),
    ]),
    ("9. Help, Diagnostic and App Restart", [
        ("Help", "On the Help screen, choosing a chapter from the \"Help Items\" list on the left shows its body text on the right."),
        ("Diagnostic", "Diagnostic is used to check connections and processes. The results do not guarantee the RF environment or antenna performance."),
        ("App Restart", "Stop TX/RX before using \"App Restart\". It hides the Home screen, shows a restart message, and waits up to 25 seconds for the Pluto to be confirmed. If it cannot be confirmed, it proceeds to the Home screen."),
    ]),
    ("10. Troubleshooting", [
        ("TX does not start", "Merely moving to the TX screen does not transmit. Press \"Start TX\" and check the video source, Pluto IP, frequency and TX power."),
        ("Cannot receive", "Match the frequency 437.000 MHz, symbol rate 500 kS/s, FEC 3/5 and modulation QPSK between TX and RX, and check that TX is transmitting, the attenuator and wiring, and the RX gain."),
        ("No camera video", "Check the USB camera (C920 or similar) connection, video source setting and camera permission. You can see whether it works in the preview on the Video Source screen. You can also switch to color bars to isolate the transmit chain."),
        ("Video is black but reception works", "Check the state display and communication statistics on the RX screen, and check the video source, H.264 video and TX start state."),
        ("On-device demodulation will not turn ON", "Turning it ON shows a 40 dB attenuator confirmation popup. Choosing \"No\" returns it to OFF by design. Check the attenuator connection, then choose \"Yes\"."),
    ]),
    ("11. Current Connection Info", [
        ("Pi 5", "SSH user: pi / Set the IP address for your environment"),
        ("Pluto", "Set the IP address for your environment / SSH user: root"),
        ("Example setup", "Frequency 437.000 MHz, video source camera or test pattern, symbol rate 500 kS/s, QPSK, FEC 3/5, on-device demodulation ON."),
    ]),
    ("12. RF Loopback Test Settings", [
        ("Test parameters", "Frequency: 437.000 MHz\nSymbol rate: 500 kS/s\nModulation: QPSK\nFEC: 3/5\nRoll-off: 0.35\nFrame: Long Frame\nRX gain: 60 dB\nVideo source: Test pattern\nOn-device demodulation: ON\nSimultaneous TX/RX: ON"),
        ("Pilot signal", "The pilot signal is always ON and fixed (there is no switch on the Settings screen). Both the transmit side (Pluto, pilots=On fixed) and the receive side (Pi 5, --pilots fixed) use the same setting, so no user action is needed."),
        ("Connection and verification", "Do not connect TX directly to RX; connect TX → an attenuator of 40 dB or more → RX. Start reception after starting transmission, and check LOCK, SOF, frame count, packet count, error count and video display on the RX screen."),
    ]),
    ("13. Pluto Firmware", [
        ("Firmware used", "Uses F5OEO's custom DATV firmware datvplutofrm v0.32-dirty on a plain Pluto. Transmission uses the Pluto's built-in DVB-S2 modulation daemon pluto_dvb."),
        ("Caution when checking firmware", "If you change the firmware, verify compatibility of pluto_dvb, the UDP TS receive path, frequency, modulation, FEC, roll-off, frame length and pilot setting before doing RF testing."),
        ("Pluto username and password", "Do not change the Pluto's username (root) and password (analog) from the factory defaults. This app and Langstone V3 connect to the Pluto via SSH with these defaults to reboot it (at app start, app restart, equipment test and Langstone exit) and to read its settings. If they are changed, the Pluto cannot be rebooted."),
    ]),
]
