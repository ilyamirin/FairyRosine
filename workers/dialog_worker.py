from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync

from programy.clients.events.console.client import ConsoleBotClient
import programy.clients.args as args

from channels.layers import get_channel_layer
from os import getcwd


cwd = getcwd()


class Args(args.ClientArguments):
    def __init__(self):
        self.args = None
        self._bot_root = cwd + "\workers\\NosferatuZodd\storage"
        self._logging = cwd + '\workers\\NosferatuZodd\config\windows\logging.yaml'
        self._config_name = cwd + '\workers\\NosferatuZodd\config\windows\config.yaml'
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
        self.bot = BotClientMod("1")
        self.bot.client_context = self.bot.create_client_context(self.bot._configuration.client_configuration.default_userid)
        print()

    def dialog_answer(self, message):
        try:
            uid = message["uid"]
            answer = self.bot.client_context.bot.ask_question(self.bot.client_context, message["text"], responselogger=self.bot)

            conversation = self.bot.client_context.bot.get_conversation(self.bot.client_context)
            topic = conversation.property("topic")

            #topic = self.bot.client_context.brain.dynamics.dynamic_var(self.bot.client_context, "topic")

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



