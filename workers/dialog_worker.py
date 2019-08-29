from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync

from programy.clients.events.console.client import ConsoleBotClient
import programy.clients.args as args

from channels.layers import get_channel_layer
import os

from coinCatalog.models import DialogUser
from vef.settings import LINGVO_DIR


class Args(args.ClientArguments):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.args = None
        self._bot_root = os.path.join(LINGVO_DIR, "storage")
        config_dir = os.path.join(LINGVO_DIR, "config")
        platform = "xnix" if os.name == "posix" else "windows"
        self._logging = os.path.join(config_dir, platform, "logging.yaml")
        self._config_name = os.path.join(config_dir, platform, "config.yaml")
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
        print("creating dialog worker..", flush=True)
        self.bot = BotClientMod("1")
        self.clients = {}
        self.asking_name = False
        print("dialog worker created", flush=True)

    def dialog_answer(self, message):
        try:
            uid = message["uid"]
            text = message["text"]
            if "меня зовут" in text.lower() or self.asking_name:
                current_user_uid = message.get("dialog_uid", "")
                name_raw = text.lower().strip().split("меня зовут")[-1] if "меня зовут" in text.lower() else text.lower().strip()
                name = " ".join([part.capitalize() for part in name_raw.split()])
                self.asking_name = False
                try:
                    user = DialogUser.objects.get(uid=current_user_uid)
                    user.name = name
                    user.save()
                except:
                    pass
            if uid not in self.clients:
                self.clients[uid] = self.bot.create_client_context(uid)
            answer = self.clients[uid].bot.ask_question(self.clients[uid], text, responselogger=self.bot)
            self.asking_name = "меня зовут" in answer.lower()
            conversation = self.clients[uid].bot.get_conversation(self.clients[uid])
            topic = conversation.property("topic")
            client_statement = self.clients[uid].brain.rdf.matched_as_tuples("КЛИЕНТ", None, None)
            # topic = self.bot.client_context.bot.ask_question(self.bot.client_context, "topic", responselogger=self.bot)[:-1].lower()
            print(f"answer = {answer}")
            print(f"topic = {topic}")
            print(f"client_statement = {client_statement}")
            async_to_sync(server_channel_layer.group_send)(
                "dialog",
                {
                    "type": "dialog_answer_ready",
                    "text": answer,
                    "topic": topic,
                    "uid": uid,
                    "client_statement": client_statement,
                },
            )
        except Exception as e:
            print(e)



