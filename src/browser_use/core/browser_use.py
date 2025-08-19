"""
Browser-use のテストサンプルコード
このスクリプトは、browser-use を使用してAIエージェントがブラウザを操作するデモです。
"""

import asyncio
from dotenv import load_dotenv
import os
import yaml
from pathlib import Path
from browser_use import Agent

# 環境変数を読み込み
load_dotenv()

# LLMモデルのインポート
from browser_use import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

class BrowserUseTest:
    """
    Browser-use テストクラス
    YAML設定からLLMモデルとプロンプトを読み込み、エージェントを実行する
    """

    def __init__(self):
        self.models_config = None
        self.prompts_config = None
        self.messages_config = None
        self.llm = None
        self.selected_model = None

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

        if not self.models_config or not self.prompts_config or not self.messages_config:
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
                print(f"pip install が必要な可能性があります")
                continue

        return False

    def show_api_key_error(self):
        errors = self.messages_config.get('errors', {})
        print(errors.get('no_api_key', 'APIキーが設定されていません'))
        print(errors.get('env_setup_instruction', '設定を確認してください'))

        # 利用可能なAPIキー設定を表示
        models = self.models_config.get('models', {})
        for model_name, config in models.items():
            api_key_env = config.get('api_key_env')
            print(f"   - {api_key_env}")

    def show_header(self):
        if self.messages_config:
            headers = self.messages_config.get('headers', {})
            separator_length = headers.get('separator_length', 60)
            program_title = headers.get('program_title', 'Browser-use テストプログラム')

            print("=" * separator_length)
            print(program_title)
            print("=" * separator_length)

    def get_task_with_env_variables(self):
        """
        環境変数を使用してタスクテンプレートを展開
        """
        # TARGET_URLを環境変数から取得
        target_url = os.getenv('TARGET_URL')

        if target_url:
            # テンプレートがある場合は環境変数で展開
            task_template = self.prompts_config.get('attendance_task_template')
            if task_template:
                return task_template.format(target_url=target_url)

        # デフォルトタスクを使用
        return self.prompts_config.get('default_task', 'デフォルトタスク')

    def check_required_env_variables(self):
        """
        必要な環境変数の確認
        """
        target_url = os.getenv('TARGET_URL') or os.getenv('JOBCAN_URL')
        if not target_url:
            errors = self.messages_config.get('errors', {})
            print(errors.get('no_target_url', 'アクセス先URLが設定されていません'))
            print(errors.get('env_setup_instruction', '.envファイルに設定を行ってください'))
            print(errors.get('target_url_instruction', 'TARGET_URL=your_url_here'))
            return False
        return True

    async def run_agent(self):
        messages = self.messages_config.get('messages', {})
        troubleshooting = self.messages_config.get('troubleshooting', {})

        print(messages.get('start', 'テストを開始します'))
        print(f"利用可能なLLM: {self.selected_model}")

        # 環境変数チェック
        if not self.check_required_env_variables():
            return

        try:
            # 環境変数を使用してタスクを取得
            task = self.get_task_with_env_variables()

            agent = Agent(
                task=task,
                llm=self.llm,
            )

            print(messages.get('agent_start', 'エージェントを開始します'))
            print(messages.get('task_description', f'タスク: 指定されたURLにアクセスして勤怠情報を確認する'))

            # エージェントを実行
            result = await agent.run()

            print(messages.get('task_complete', 'タスクが完了しました'))
            print(f"結果: {result}")

        except Exception as e:
            print(f"{messages.get('error_occurred', 'エラーが発生しました')}: {e}")
            print(troubleshooting.get('title', 'ヒント'))
            print(f"   - {troubleshooting.get('api_key_check', 'APIキーを確認してください')}")
            print(f"   - {troubleshooting.get('target_url_check', 'アクセス先URLを確認してください')}")
            print(f"   - {troubleshooting.get('internet_check', 'インターネット接続を確認してください')}")
            print(f"   - {troubleshooting.get('browser_check', 'ブラウザの確認をしてください')}")

    async def run(self):
        # 設定ファイル読み込み
        if not self.load_configs():
            return
        # ヘッダー表示
        self.show_header()
        # LLMセットアップ
        if not self.setup_llm():
            self.show_api_key_error()
            return

        # エージェント実行
        await self.run_agent()

def main():
    test = BrowserUseTest()
    asyncio.run(test.run())

if __name__ == "__main__":
    main()