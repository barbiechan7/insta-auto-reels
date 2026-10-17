# insta-auto
毎日19:00(JST)に、占い風ランキングのリール動画を作ってInstagramに自動投稿します。

流れ: Claude APIで台本 → assets/bg.mp4(固定背景)に文字を合成 → GitHub Releasesに置く → Instagram Graph APIで投稿

## 必要なSecrets (Settings > Secrets and variables > Actions)
ANTHROPIC_API_KEY / IG_USER_ID / IG_ACCESS_TOKEN (長期トークンは約60日で更新)

## 注意
Instagramは動画URLを取得するため、リポジトリを公開(public)にする必要があります。

## 背景を変えたい
assets/bg.mp4 を縦長(1080x1920推奨)の動画に差し替える。
