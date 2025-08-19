# Browser-use 勤怠管理システム自動確認プロジェクト
このプロジェクトは、browser-useライブラリを使用してAIエージェントが勤怠管理システムにアクセスし、勤怠情報を自動確認するためのものです。

## プロジェクト構造
```
browser-use/
├── src/
│   ├── main.py                     # メインエントリーポイント
│   ├── core/
│   │   └── browser_agent.py        # ブラウザエージェントクラス
│   └── config/
│       ├── modes_setting.yaml      # LLMモデル設定
│       ├── prompt.yaml             # LLMプロンプト設定
│       └── app_messages.yaml       # アプリケーションメッセージ設定
├── pyproject.toml                  # 依存関係管理
├── .env                           # 環境変数設定
├── .gitignore
└── README.md                      # このファイル
```

## 環境構築
### 1. 依存関係のインストール
```bash
# uvを使用して依存関係をインストール
uv sync
# Chromiumブラウザをインストール
uv run playwright install chromium --with-deps --no-shell
```

### 2. 環境変数の設定
`.env`ファイルを作成し、以下の設定を行ってください：
```bash
# 勤怠管理システムのURL（必須）
TARGET_URL=https://your-attendance-system.com/

# OpenAI APIキー（推奨）
OPENAI_API_KEY=your_openai_api_key_here
# または以下のいずれか
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

注意:
- `TARGET_URL`には使用する勤怠管理システムのURLを設定してください

## 実行方法
### 勤怠管理システム確認の実行

```bash
uv run src/main.py
```

このコマンドで、環境変数で設定された勤怠管理システムにアクセスして勤怠情報を確認するタスクが実行されます。

### 実行の流れ
1. 環境変数で設定されたURLにアクセス
2. ログインページでログイン処理
3. 勤怠情報のダッシュボードに移動
4. 本日の出勤・退勤時刻を確認
5. 今月の勤怠状況を確認
6. 必要に応じて勤怠の修正や申請状況を確認
## 設定ファイル
### modes_setting.yaml
LLMモデルの設定を管理します：
- 使用するモデル（OpenAI、Anthropic、Google）
- 各モデルの有効/無効
- 温度設定
- APIキー環境変数名

### prompt.yaml
LLMプロンプトの設定を管理します：
- デフォルトタスク
- 勤怠管理システム確認タスクテンプレート（環境変数対応）

### app_messages.yaml
アプリケーションメッセージの設定を管理します：
- プログラム実行中のメッセージ
- エラーメッセージとトラブルシューティング
- プログラムヘッダー表示設定

### core/browser_agent.py
ブラウザエージェントのコアロジック：
- LLM設定の読み込みと初期化
- 環境変数を使った動的プロンプト生成
- ブラウザエージェントの実行制御

## カスタマイズ
設定ファイルを編集することで、コードを変更せずに以下をカスタマイズできます：
- 使用するLLMモデル
- タスク内容
- メッセージ表示
- モデルパラメータ

## トラブルシューティング
### よくある問題
1. **APIキーエラー**
   - `.env`ファイルにAPIキーが正しく設定されているか確認
2. **アクセス先URLエラー**
   - `.env`ファイルに`TARGET_URL`が正しく設定されているか確認
   - 勤怠管理システムの正確なURLを使用
3. **ログインエラー**
   - 勤怠管理システムのログイン情報が正しいか確認
   - 二段階認証が有効な場合は事前に設定を確認
4. **ブラウザエラー**
   - Chromiumのインストール: `uv run playwright install chromium --with-deps`
5. **依存関係エラー**
   - 再インストール: `uv sync --reinstall`

### 参考リンク
- [Browser-use 公式GitHub](https://github.com/browser-use/browser-use)
- [Browser-use ドキュメント](https://docs.browser-use.com/)
- [Browser-use Cloud版](https://cloud.browser-use.com/)
