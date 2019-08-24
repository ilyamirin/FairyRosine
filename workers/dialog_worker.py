from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync

from programy.clients.events.console.client import ConsoleBotClient
import programy.clients.args as args

from channels.layers import get_channel_layer
from os import getcwd

from coinCatalog.models import DialogUser

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
        self.clients = {}

    def dialog_answer(self, message):
        try:
            uid = message["uid"]
            text = message["text"]
            if "меня зовут" in text.lower():
                current_user_uid = message.get("dialog_uid", "")
                name = " ".join([part.capitalize() for part in text.lower().split("меня зовут")[-1].split()])
                try:
                    user = DialogUser.objects.get(uid=current_user_uid)
                    user.name = name
                    user.save()
                except:
                    pass
            if uid not in self.clients:
                self.clients[uid] = self.bot.create_client_context(uid)
            answer = self.clients[uid].bot.ask_question(self.clients[uid], text, responselogger=self.bot)
            conversation = self.clients[uid].bot.get_conversation(self.clients[uid])
            topic = conversation.property("topic")
            # topic = self.bot.client_context.bot.ask_question(self.bot.client_context, "topic", responselogger=self.bot)[:-1].lower()
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



