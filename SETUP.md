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
