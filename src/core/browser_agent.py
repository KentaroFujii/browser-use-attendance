"""
勤怠管理システム自動確認用ブラウザエージェント
YAML設定からLLMモデルとプロンプトを読み込み、エージェントを実行する
"""
import os
import yaml  # type: ignore
import time
from datetime import datetime
from pathlib import Path
from browser_use import Agent
# LLMモデルのインポート
from browser_use import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

class AttendanceAgent:
    """
    勤怠管理システム自動確認エージェント
    YAML設定からLLMモデルとプロンプトを読み込み、エージェントを実行する
    """

    def __init__(self):
        self.models_config = None
        self.prompts_config = None
        self.messages_config = None
        self.browser_config = None
        self.llm = None
        self.selected_model = None
        self.start_time = None
        self.end_time = None

    def load_yaml_config(self, filename):
        """
        YAMLファイルから設定を読み込む
        """
        config_path = Path(__file__).parent.parent / 'config' / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"設定ファイル {filename} が見つかりません")
            return None
        except yaml.YAMLError as e:
            print(f"YAML読み込みエラー: {e}")
            return None

    def load_configs(self):
        """
        必要な設定ファイルを読み込む
        """
        self.models_config = self.load_yaml_config('modes_setting.yaml')
        self.prompts_config = self.load_yaml_config('prompt.yaml')
        self.messages_config = self.load_yaml_config('app_messages.yaml')
        self.browser_config = self.load_yaml_config('browser_setting.yaml')

        if not self.models_config or not self.prompts_config or not self.messages_config or not self.browser_config:
            print("設定ファイルの読み込みに失敗しました")
            return False
        return True

    def setup_llm(self):
        """
        設定からLLMオブジェクトを設定
        YAML設定のenabledフラグで制御
        """
        models = self.models_config.get('models', {})
        settings = self.models_config.get('settings', {})
        default_model = settings.get('default_model', 'openai')

        # 有効なモデルを順番に試す
        model_order = [default_model] + [k for k in models.keys() if k != default_model]

        for model_name in model_order:
            model_config = models.get(model_name, {})
            if not model_config.get('enabled', False):
                continue

            api_key_env = model_config.get('api_key_env')
            if not os.getenv(api_key_env):
                continue

            model = model_config.get('model')
            temperature = model_config.get('temperature', 0.7)

            try:
                if model_name == 'openai':
                    self.llm = ChatOpenAI(model=model, temperature=temperature)
                    self.selected_model = model_name
                    return True

                elif model_name == 'anthropic':
                    self.llm = ChatAnthropic(model=model, temperature=temperature)
                    self.selected_model = model_name
                    return True

                elif model_name == 'google':
                    self.llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
                    self.selected_model = model_name
                    return True

            except ImportError as e:
                print(f"{model_name}のライブラリが見つかりません: {e}")
                print("pip install が必要な可能性があります")
                continue

        return False

    def show_api_key_error(self):
        """
        APIキーエラーメッセージを表示
        """
        errors = self.messages_config.get('errors', {})
        print(errors.get('no_api_key', 'APIキーが設定されていません'))
        print(errors.get('env_setup_instruction', '設定を確認してください'))

        # 利用可能なAPIキー設定を表示
        models = self.models_config.get('models', {})
        for model_name, config in models.items():
            api_key_env = config.get('api_key_env')
            print(f"   - {api_key_env}")

    def show_header(self):
        """
        プログラムヘッダーを表示
        """
        if self.messages_config:
            headers = self.messages_config.get('headers', {})
            separator_length = headers.get('separator_length', 60)
            program_title = headers.get('program_title', 'Browser-use テストプログラム')

            print("=" * separator_length)
            print(program_title)
            print("=" * separator_length)

    def log_execution_time(self, message: str, show_elapsed: bool = False):
        """
        実行時間をログ出力
        """
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        if show_elapsed and self.start_time:
            elapsed = time.time() - self.start_time
            print(f"[{timestamp}] {message} (経過時間: {elapsed:.2f}秒)")
        else:
            print(f"[{timestamp}] {message}")

    def format_duration(self, duration_seconds: float) -> str:
        """
        秒数を時分秒形式にフォーマット
        """
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = duration_seconds % 60

        if hours > 0:
            return f"{hours}時間{minutes}分{seconds:.2f}秒"
        elif minutes > 0:
            return f"{minutes}分{seconds:.2f}秒"
        else:
            return f"{seconds:.2f}秒"

    def get_task_with_env_variables(self):
        """
        環境変数を使用してタスクテンプレートを展開
        """
        # 必要な環境変数を取得
        target_url = os.getenv('TARGET_URL')
        login_email = os.getenv('LOGIN_EMAIL')
        login_password = os.getenv('LOGIN_PASSWORD')
        expected_name = os.getenv('EXPECTED_NAME')

        if target_url:
            # browser_setting.yamlからテンプレート名を取得
            prompt_selection = self.browser_config.get('prompt_selection', {})
            template_name = prompt_selection.get('task_template', 'meta_attendance_task_template')

            # 指定されたテンプレートを取得
            task_template = self.prompts_config.get(template_name)
            if task_template:
                return task_template.format(
                    target_url=target_url,
                    login_email=login_email or '[メールアドレスが設定されていません]',
                    login_password=login_password or '[パスワードが設定されていません]',
                    expected_name=expected_name or '[期待する名前が設定されていません]'
                )

        # デフォルトタスクを使用
        return self.prompts_config.get('default_task', 'デフォルトタスク')

    def check_required_env_variables(self):
        """
        必要な環境変数の確認
        """
        errors = self.messages_config.get('errors', {})
        missing_vars = []

        # 必須環境変数のチェック
        target_url = os.getenv('TARGET_URL') or os.getenv('JOBCAN_URL')
        if not target_url:
            missing_vars.append('TARGET_URL')

        login_email = os.getenv('LOGIN_EMAIL')
        if not login_email:
            missing_vars.append('LOGIN_EMAIL')

        login_password = os.getenv('LOGIN_PASSWORD')
        if not login_password:
            missing_vars.append('LOGIN_PASSWORD')

        expected_name = os.getenv('EXPECTED_NAME')
        if not expected_name:
            missing_vars.append('EXPECTED_NAME')

        if missing_vars:
            print(errors.get('missing_env_vars', '以下の環境変数が設定されていません:'))
            for var in missing_vars:
                print(f"  - {var}")
            print(errors.get('env_setup_instruction', '.envファイルに以下の設定を行ってください:'))
            print("TARGET_URL=https://your-attendance-system-url")
            print("LOGIN_EMAIL=your-email@example.com")
            print("LOGIN_PASSWORD=your-password")
            print("EXPECTED_NAME=期待するユーザー名")
            return False

        return True

    async def run_agent(self):
        """
        ブラウザエージェントを実行
        """
        messages = self.messages_config.get('messages', {})
        troubleshooting = self.messages_config.get('troubleshooting', {})

        # エージェント実行開始ログ
        self.log_execution_time(messages.get('start', 'テストを開始します'))
        print(f"利用可能なLLM: {self.selected_model}")

        # 設定情報をログ出力
        browser_settings = self.browser_config.get('browser', {})
        prompt_selection = self.browser_config.get('prompt_selection', {})
        print(f"ブラウザモード: {'ヘッドレス' if browser_settings.get('headless', True) else '表示'}")
        print(f"使用プロンプト: {prompt_selection.get('task_template', 'meta_attendance_task_template')}")

        # 環境変数チェック
        if not self.check_required_env_variables():
            self.log_execution_time("環境変数チェック失敗により終了")
            return

        try:
            # 環境変数を使用してタスクを取得
            task = self.get_task_with_env_variables()

            # エージェント実行開始時刻を記録
            self.start_time = time.time()
            self.log_execution_time("エージェント実行開始")


            agent = Agent(
                task=task,
                llm=self.llm
            )

            self.log_execution_time(messages.get('agent_start', 'エージェントを開始します'), show_elapsed=True)
            print(messages.get('task_description', 'タスク: 指定されたURLにアクセスして勤怠情報を確認する'))

            # エージェントを実行
            result = await agent.run()

            # 実行完了時刻を記録
            self.end_time = time.time()
            total_duration = self.end_time - self.start_time

            self.log_execution_time(messages.get('task_complete', 'タスクが完了しました'))
            self.log_execution_time(f"総実行時間: {self.format_duration(total_duration)}")
            print(f"結果: {result}")

        except Exception as e:
            # エラー発生時も実行時間をログ
            if self.start_time:
                error_time = time.time()
                error_duration = error_time - self.start_time
                self.log_execution_time(f"エラー発生により終了 (実行時間: {self.format_duration(error_duration)})")
            else:
                self.log_execution_time("エラー発生により終了")

            print(f"{messages.get('error_occurred', 'エラーが発生しました')}: {e}")
            print(troubleshooting.get('title', 'ヒント'))
            print(f"   - {troubleshooting.get('api_key_check', 'APIキーを確認してください')}")
            print(f"   - {troubleshooting.get('target_url_check', 'アクセス先URLを確認してください')}")
            print(f"   - {troubleshooting.get('internet_check', 'インターネット接続を確認してください')}")
            print(f"   - {troubleshooting.get('browser_check', 'ブラウザの確認をしてください')}")

    async def run(self):
        """
        エージェント実行のメインフロー
        """
        # プログラム全体の開始時刻を記録
        program_start_time = time.time()
        start_datetime = datetime.now()

        print(f"プログラム開始: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        # 設定ファイル読み込み
        if not self.load_configs():
            self.log_execution_time("設定ファイル読み込み失敗により終了")
            return

        # ヘッダー表示
        self.show_header()

        # LLMセットアップ
        if not self.setup_llm():
            self.show_api_key_error()
            self.log_execution_time("LLMセットアップ失敗により終了")
            return

        # エージェント実行
        await self.run_agent()

        # プログラム全体の終了時刻とログ
        program_end_time = time.time()
        end_datetime = datetime.now()
        total_program_duration = program_end_time - program_start_time

        print(f"プログラム終了: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"プログラム総実行時間: {self.format_duration(total_program_duration)}")
        print("=" * 60)
