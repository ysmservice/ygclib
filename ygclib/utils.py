from discord.ext import commands
from typing import TYPE_CHECKING, Optional
import ujson
import discord

if TYPE_CHECKING:
    from discord.types.message import Message as MessageType ,Attachment as AttachmentPayload


class YGC():  
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_json(self, message: discord.Message):
        dic = {} 
        dic.update({"type": "message"})
        dic.update({"userId": str(message.author.id)}) 
        dic.update({"userName": message.author.name})
        dic.update({"userDiscriminator": message.author.discriminator})
        if not message.author.avatar == None:
            dic.update({"userAvatar": message.author.avatar.key})
        else:
            dic.update({"userAvatar": None})
        dic.update({"isBot": message.author.bot}) 
        dic.update({"guildId": str(message.guild.id)}) 
        dic.update({"guildName": message.guild.name}) 
        if not message.guild.icon == None:
            dic.update({"guildIcon": message.guild.icon.key}) 
        else:
            dic.update({"guildIcon": None})
        dic.update({"channelId": str(message.channel.id)}) 
        dic.update({"channelName": message.channel.name}) 
        dic.update({"messageId": str(message.id)}) 
        dic.update({"content": message.content.replace("@everyone","[everyone]").replace("@here","[here]")}) 
        if message.attachments != []: 
            arr = [] 
            for attachment in message.attachments: 
                arr.append(attachment.url) 
            dic.update({"attachmentsUrl": arr})
        if message.embeds != []: 
            arr = [] 
            for embed in message.embeds: 
                arr.append(embed.to_dict()) 
            dic.update({"embeds": arr})
        if message.reference: 
            reference_msg = await message.channel.fetch_message(message.reference.message_id) 
            reference_mid = 0
            r = ujson.loads(await self.create_json(reference_msg))
            if reference_msg.webhook_id != None:  
                arr = reference_msg.author.name.split(":")
                reference_mid = arr[len(arr)-1].replace(")", "")
            else: 
               reference_mid = str(reference_msg.id) 
               dic.update({"reference": reference_mid})
            r["messageId"] = str(reference_mid)
        dic["reference"] = r
        jsondata = ujson.dumps(dic, ensure_ascii=False)
        return  jsondata
      
    async def create_message(self, dic: dict):
        first_message = self.bot.cached_messages[0]
        channel_id = first_message.channel.id
        channel = first_message.channel
        user = await self.bot.fetch_user(int(dic["userId"]))
        atch = list()
        dic.setdefault("attachmentsUrl",list())
        c = 0
        if dic["attachmentsUrl"] != []:
            for fb in dic["attachmentsUrl"]:
                atch.append(await self.filefromurl(fb,c))
                c = c + 1
        dic.setdefault("embeds", list())
        payload: MessageType = {
        "id": dic["messageId"], "content": dic["content"], "tts": False,
        "mention_everyone": False, "attachments": atch, "embeds":  dic["embeds"],
        "author": {
            "bot": user.bot, "id": user.id, "system": user.system,
            "username": user.name, "discriminator": user.discriminator,
            "avatar": user.display_avatar.url
        },
        "edited_timestamp": None, "type": 0, "pinned": False,
        "mentions": [], "mention_roles": [], "channel_id": channel_id, #このbotが入ってないサーバーからだとバグりそうなのでjsonチャンネルをセット
        "timestamp": ""
        }
        if not channel or not isinstance(channel, discord.abc.Messageable):
            raise ValueError("Unknown Channel Id.")
        message1 = discord.Message(
        data=payload, state=self.bot._get_state(), channel=channel
        )
        if channel.guild is not None:
            message1.author = channel.guild.get_member(user.id)  # type: ignore
        else:
            message1.author = user
        message1.id = dic["messageId"]
        dic.setdefault("reference", "")
        if dic["reference"] != "":
            try:
                past_dic = dic["reference"]
            except:
                return message1
            if "type" in past_dic and past_dic["type"] == "message" and "messageId" in past_dic and str(past_dic["messageId"]) == str(reference_mid):
                user = await self.bot.fetch_user(int(past_dic["userId"]))
                atch = list()
                c = 0
                past_dic.setdefault("attachmentsUrl", list())
                if past_dic["attachmentsUrl"] != []:
                    for fb in past_dic["attachmentsUrl"]:
                        atch.append(await self.filefromurl(fb,c))
                        c = c + 1
                past_dic.setdefault("embeds", list())
                payload: MessageType = {
                "id": past_dic["messageId"], "content": past_dic["content"], "tts": False,
                "mention_everyone": False, "attachments": atch, "embeds":  past_dic["embeds"],
                "author": {
                    "bot": user.bot, "id": user.id, "system": user.system,
                    "username": user.name, "discriminator": user.discriminator,
                    "avatar": user.display_avatar.url
                },
                "edited_timestamp": None, "type": 0, "pinned": False,
                "mentions": [], "mention_roles": [], "channel_id": channel_id, #このbotが入ってないサーバーからだとバグりそうなのでjsonチャンネルをセット
                "timestamp": ""
                }
                if not channel or not isinstance(channel, discord.abc.Messageable):
                    raise ValueError("Unknown Channel Id.")
                message2 = discord.Message(
                data=payload, state=self.bot._get_state(), channel=channel
                )
                if channel.guild is not None:
                    message2.author = channel.guild.get_member(user.id)  # type: ignore
                else:
                    message2.author = user
                message2.id = past_dic["messageId"]
                message1.reference = CustmizedReference.from_message(message=message2)
                message1.reference.cached_message1 = message2
        return message1

class CustmizedReference(discord.MessageReference):
    def __init__(self, *, message_id: int, channel_id: int, guild_id: Optional[int] = None, fail_if_not_exists: bool = True):
        self._state = None
        self.resolved = None
        self.message_id: Optional[int] = message_id
        self.channel_id: int = channel_id
        self.guild_id: Optional[int] = guild_id
        self.fail_if_not_exists: bool = fail_if_not_exists
        self.cached_message1 = None
