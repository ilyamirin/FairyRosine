from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync

from programy.clients.events.console.client import ConsoleBotClient
import programy.clients.args as args

from channels.layers import get_channel_layer


class Args(args.ClientArguments):
    def __init__(self):
        self.args = None
        self._bot_root = "C:\Projects\FairyRosine\workers\\NosferatuZodd\storage"
        self._logging = 'C:\Projects\FairyRosine\workers\\NosferatuZodd\config\windows\logging.yaml'
        self._config_name = 'C:\Projects\FairyRosine\workers\\NosferatuZodd\config\windows\config.yaml'
        self._config_format = 'yaml'
        self._no_loop = False
        self._substitutions = None

    def parse_args(self, client):
        pass


class BotClientMod(ConsoleBotClient):

    def parse_arguments(self, *args, **kwargs):
        client_args = Args()
        client_args.parse_args(self)
        return client_args


server_channel_layer = get_channel_layer("server")


class DialogConsumer(SyncConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("dialog worker created", flush=True)
        print(1111)
        self.bot = BotClientMod("1")
        self.bot.client_context = self.bot.create_client_context(self.bot._configuration.client_configuration.default_userid)
        print()

    def dialog_answer(self, message):
        try:
            uid = message["uid"]
            answer = self.bot.client_context.bot.ask_question(self.bot.client_context, message["text"], responselogger=self.bot)
            topic = 'hello'
            #topic = self.bot.client_context.bot.ask_question(self.bot.client_context, "topic", responselogger=self.bot)[:-1].lower()
            print(f"answer = {answer}")
            print(f"topic = {topic}")
            async_to_sync(server_channel_layer.group_send)(
                "dialog",
                {
                    "type": "dialog_answer_ready",
                    "text": answer,
                    "topic": topic,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)



