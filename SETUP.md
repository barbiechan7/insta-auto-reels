# 自動投稿の準備(あなたが行う部分)

## 1. Instagram側(最初の1回だけ)
1. Instagramがプロアカウント(ビジネス/クリエイター)であることを確認(@runa_uranai777 はOK)
2. Facebookページを作り、InstagramアカウントとFacebookページを連携する(Instagramの設定 > アカウントセンター等)
3. https://developers.facebook.com/ で「アプリ」を作成(種類: ビジネス)→ 製品に「Instagram」(Instagram Graph API)を追加
4. 権限 `instagram_basic` `instagram_content_publish` `pages_show_list` `pages_read_engagement` を付けてアクセストークンを発行
   (Graph APIエクスプローラで発行 → 「長期トークン」に交換。約60日で期限切れ)
5. Graph APIエクスプローラで `me/accounts?fields=instagram_business_account` を実行 → 出てきた `instagram_business_account.id` が **IG_USER_ID**

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
