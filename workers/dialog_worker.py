from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

server_channel_layer = get_channel_layer("server")

class DialogConsumer(SyncConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("dialog worker created", flush=True)

    def dialog_answer(self, message):
        try:
            uid = message["uid"]
            answer = message["text"] + "hello"
            print(f"answer = {answer}")
            async_to_sync(server_channel_layer.group_send)(
                "dialog",
                {
                    "type": "dialog_answer_ready",
                    "text": answer,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)