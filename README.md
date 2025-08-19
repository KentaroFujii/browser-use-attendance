# Browser-use テストプロジェクト
このプロジェクトは、browser-useライブラリを使用してAIエージェントがブラウザを自動操作するテストを行うためのものです。

## プロジェクト構造
```
browser-use/
├── src/
│   └── browser_use_test/
│       ├── core/
│       │   └── test_browser_use.py  # メインテストスクリプト
│       └── config/
│           ├── modes_setting.yaml   # LLMモデル設定
│           └── prompt.yaml          # プロンプト設定
├── pyproject.toml                   # 依存関係管理
├── .env.example                    # 環境変数設定例
├── .env                            # 環境変数設定（.env.exampleをコピーして作成）
├── .gitignore
└── README.md                       # このファイル
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
`.env`ファイルを作成し、使用するLLMのAPIキーを設定してください：
```bash
# OpenAI APIキー（推奨）
OPENAI_API_KEY=your_openai_api_key_here
# または以下のいずれか
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
# テスト用ログイン情報（オプション）
TEST_USERNAME=your_test_username
TEST_PASSWORD=your_test_password
```

## 実行方法
### メインテストの実行

```bash
uv run src/browser_use_test/core/test_browser_use.py
```

このコマンドで、GitHubのトップページにアクセスしてbrowser-useを検索するテストが実行されます。
## 設定ファイル
### modes_setting.yaml
LLMモデルの設定を管理します：
- 使用するモデル（OpenAI、Anthropic、Google）
- 各モデルの有効/無効
- 温度設定
- APIキー環境変数名
### prompt.yaml
プロンプトとメッセージの設定を管理します：
- デフォルトタスク
- システムメッセージ
- エラーメッセージ
- ヘッダー表示設定

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
2. **ブラウザエラー**
   - Chromiumのインストール: `uv run playwright install chromium --with-deps`
3. **依存関係エラー**
   - 再インストール: `uv sync --reinstall`

### 参考リンク
- [Browser-use 公式GitHub](https://github.com/browser-use/browser-use)
- [Browser-use ドキュメント](https://docs.browser-use.com/)
- [Browser-use Cloud版](https://cloud.browser-use.com/)
