# 自動投稿の準備(あなたが行う部分)

## 1. Instagram側(最初の1回だけ) ※Instagramログイン方式(Facebookページ不要)
1. Metaの開発者サイト > アプリ「インスタインサイト分析用」> ユースケース > カスタマイズ > 「Instagramログインによる API設定」
2. 左メニュー「アクセス許可と機能」で `instagram_business_basic` と `instagram_business_content_publish` を追加
3. アプリの役割 > 「役割」で、runa_uranai777 を「Instagramテスター」に追加 → Instagramアプリ側(設定 > ウェブサイトのアクセス許可 > テスターの招待)で承認
4. API設定のステップ2「アカウントを追加」で runa_uranai777 を追加(ログインして許可)
5. 追加されたアカウント横の数字が **IG_USER_ID**。「トークンを生成」で出るトークンが **IG_ACCESS_TOKEN**(約60日で期限切れ)

## 2. Anthropic APIキー
https://console.anthropic.com/ でAPIキーを発行 → **ANTHROPIC_API_KEY**

## 3. GitHubにSecretsを登録(自分のターミナルで)
    gh secret set ANTHROPIC_API_KEY -R barbiechan7/insta-auto-reels
    gh secret set IG_USER_ID -R barbiechan7/insta-auto-reels
    gh secret set IG_ACCESS_TOKEN -R barbiechan7/insta-auto-reels
(実行すると値の入力を求められる。貼り付けてEnter)

## 4. 動作確認
- テスト(投稿しない): Actions > daily-reel > Run workflow > dry_run に true
- 本番: dry_run を空のまま実行すると、その日の20:05〜20:55の指定時刻まで待って実際に投稿する

## 5. Slack通知(任意・設定すると有効)
- 毎週月曜 9:00(日本時間): 直近7日の投稿の再生数(ビュー)・リーチ、アーカイブ候補をSlackに投稿
- エラー時: 自動投稿の失敗をすぐSlackに通知
1. Slackで通知したいチャンネルを決め、「Incoming Webhook」のURLを発行する(https://api.slack.com/apps > Create New App > Incoming Webhooks > Add New Webhook to Workspace)
2. 自分のターミナルで登録(実行後にURLを貼り付ける)
       gh secret set SLACK_WEBHOOK_URL -R barbiechan7/insta-auto-reels
3. 動作確認: Actions > weekly-report > Run workflow

## 二重投稿の防止
同じ日・同じ枠(昼/夜)はすでに投稿済みなら実行をスキップします。GitHubの定期実行が遅れた場合の保険として、各枠で2回起動します。
