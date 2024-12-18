import io
import os
import re
import sys
from urllib.parse import urlparse
import aiohttp
from discord.ext import commands
from typing import TYPE_CHECKING, Optional
import ujson
import discord

if TYPE_CHECKING:
    from discord.types.message import Message as MessageType, Attachment as AttachmentPayload

class YGC():  
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ws_url = "ws://ysmserv.com:8765"

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
            reference_msg = message.reference.cached_message
            reference_mid = 0
            if reference_msg == None and hasattr(message.reference, "cached_message1"):
                reference_msg = message.reference.cached_message1
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
        return jsondata
    
    async def create_json_from_raw(self, message_data: dict):
        pattern = r"<:([a-zA-Z0-9_]+):\d+>"
        # :絵文字名: に置き換える
        message_data["author"].setdefault("bot", False)
        replaced_text = re.sub(pattern, r":\1:", message_data["content"])
        dic = {} 
        dic.update({"userId": str(message_data["author"]["id"])}) 
        dic.update({"userName": message_data["author"]["username"]})
        dic.update({"userDiscriminator": message_data["author"]["discriminator"]})
        if message_data["author"]["avatar"]:
            dic.update({"userAvatar": message_data["author"]["avatar"]})
        else:
            dic.update({"userAvatar": None})
        dic.update({"isBot": message_data["author"]["bot"]}) 
        try:
            guild = self.bot.get_guild(int(message_data["guild_id"]))
            channel = guild.get_channel(int(message_data["channel_id"]))
        except:
            guild = discord.Guild(state=self.bot._get_state(), data={"id": int(message_data["guild_id"]), "name": message_data["guild_name"], "icon": message_data["guild_icon"]})
            channel = discord.TextChannel(guild=guild, state=self.bot._get_state(), data={"id": int(message_data["channel_id"]), "name": message_data["channel_name"], "type": 0,"position": 0,"permission_overwrites": [],"nsfw": False,"parent_id": None})
        dic.update({"guildId": str(guild.id)}) 
        dic.update({"guildName": guild.name}) 
        if guild.icon:
            dic.update({"guildIcon": guild.icon.key})
        else:
            dic.update({"guildIcon": None})
        dic.update({"channelId": str(channel.id)}) 
        dic.update({"channelName": channel.name}) 
        dic.update({"messageId": str(message_data["id"])}) 
        dic.update({"content": replaced_text.replace("@everyone","[everyone]").replace("@here","[here]")}) 
        if message_data["attachments"] != []: 
            arr = [] 
            for attachment in message_data["attachments"]: 
                arr.append(attachment["url"]) 
            dic.update({"attachmentsUrl": arr})
        if message_data["embeds"] != []: 
            arr = [] 
            for embed in message_data["embeds"]: 
                arr.append(embed) 
            dic.update({"embeds": arr})
        if message_data.get("message_reference"): 
            try:
                reference_msg = await self.bot.get_channel(int(message_data["channel_id"])).fetch_message(int(message_data["message_reference"]["message_id"])) 
                reference_mid = 0 
                if reference_msg.webhook_id != None:  
                    arr = reference_msg.author.name.split(":")
                    reference_mid = arr[len(arr)-1].replace(")", "")
                else: 
                    reference_mid = str(reference_msg.id) 
                r = ujson.loads(await self.create_json(reference_msg))
                r["messageId"] = str(reference_mid)
                r["channelId"] = str(message_data["channel_id"])
                r["guildId"] = str(message_data["guild_id"])
                r["guildName"] = message_data["guild_name"]
                r["channelName"] = message_data["channel_name"]
                r["guildIcon"] = message_data["guild_icon"]
                dic.update({"reference": r})
            except:
                r = {}
                r["content"] = "取得できませんでした"
                try:
                    reference_msg = await self.bot.get_channel(int(message_data["channel_id"])).fetch_message(int(message_data["message_reference"]["message_id"])) 
                    reference_mid = 0 
                    if reference_msg.webhook_id != None:  
                        arr = reference_msg.author.name.split(":")
                        reference_mid = arr[len(arr)-1].replace(")", "")
                    else: 
                        reference_mid = str(reference_msg.id) 
                    r["content"] = reference_msg.content
                except:
                    reference_mid = str(message_data["message_reference"]["message_id"])
                r["messageId"] = str(reference_mid)
                dic.update({"reference": r})
        # Extract emojis from content
        emojis = {}
        matches = re.findall(r"<a?:(\w+):(\d+)>", message_data["content"])
        for emoji_name, emoji_id in matches:
            emojis[f":{emoji_name}:"] = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        dic["emojis"] = emojis
        jsondata = ujson.dumps(dic, ensure_ascii=False)
        return jsondata
    
    async def filefromurl(self, url: str, c: int):
        async with aiohttp.ClientSession() as session:  # セッションを作成
            async with session.get(url) as resp:  # URLからファイルを取得
                if resp.status != 200:
                    raise discord.HTTPException(resp, f'Failed to get asset from {url}')
                
                file_data = await resp.read()  # ファイルの内容を読み込む

                # URLからファイル名を抽出
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)

                with io.BytesIO(file_data) as file:
                    # ファイル名をURLから取得したものに設定
                    f = discord.File(file, filename)
                    fd = f.to_dict(index=c)
                    ap: AttachmentPayload = {
                        "id": fd["id"],
                        "size": sys.getsizeof(file),
                        "filename": fd["filename"],
                        "url": url,
                        'proxy_url': url
                    }
                    return ap
      
    async def create_message(self, dic: dict, needref = True):
        try:
            first_message = self.bot.cached_messages[0]
            channel_id = first_message.channel.id
            channel = first_message.channel
        except:
            guild = discord.Guild(state=self.bot._get_state(), data={"id": int(dic["guildId"]), "name": dic["guildName"], "icon": dic["guildIcon"]})
            channel_id = int(dic["channelId"])
            channel = discord.TextChannel(state=self.bot._get_state(), guild=guild, data={"id": channel_id, "name": dic["channelName"], "type": 0,"position": 0,"permission_overwrites": [],"nsfw": False,"parent_id": None})
        try:
            user = await self.bot.fetch_user(int(dic["userId"]))
        except:
            user = discord.User(state=self.bot._get_state(), data={"id": int(dic["userId"]), "username": dic["userName"], "discriminator": dic["userDiscriminator"], "avatar": dic["userAvatar"]})
        atch = list()
        dic.setdefault("attachmentsUrl", list())
        c = 0
        if dic["attachmentsUrl"] != []:
            for fb in dic["attachmentsUrl"]:
                atch.append(await self.filefromurl(fb, c))
                c = c + 1
        dic.setdefault("embeds", list())
        payload: MessageType = {
            "id": dic["messageId"], "content": dic["content"], "tts": False,
            "mention_everyone": False, "attachments": atch, "embeds": dic["embeds"],
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
            if message1.author == None:
                message1.author = user
        else:
            message1.author = user
        message1.id = dic["messageId"]
        dic.setdefault("reference", "")
        if dic["reference"] != "" and needref:
            try:
                past_dic = dic["reference"]
            except:
                return message1
            if "type" in past_dic and past_dic["type"].find("message") != -1 and "messageId" in past_dic:
                try:
                    user = await self.bot.fetch_user(int(past_dic["userId"]))
                except:
                    user = discord.User(state=self.bot._get_state(), data={"id": int(dic["userId"]), "username": dic["userName"], "discriminator": dic["userDiscriminator"], "avatar": dic["userAvatar"]})
                atch = list()
                c = 0
                past_dic.setdefault("attachmentsUrl", list())
                if past_dic["attachmentsUrl"] != []:
                    for fb in past_dic["attachmentsUrl"]:
                        atch.append(await self.filefromurl(fb, c))
                        c = c + 1
                past_dic.setdefault("embeds", list())
                payload: MessageType = {
                    "id": past_dic["messageId"], "content": past_dic["content"], "tts": False,
                    "mention_everyone": False, "attachments": atch, "embeds": past_dic["embeds"],
                    "author": {
                        "bot": user.bot, "id": user.id, "system": user.system,
                        "username": user.name, "discriminator": user.discriminator,
                        "avatar": user.display_avatar.url
                    },
                    "edited_timestamp": None, "type": 0, "pinned": False,
                    "mentions": [], "mention_roles": [], "channel_id": channel_id, #このbotが入ってないサーバーからだとバグりそうなのでjsonチャンネルをセット
                    "timestamp": ""
                }
                if not channel:
                    raise ValueError("Unknown Channel Id.")
                message2 = discord.Message(
                    data=payload, state=self.bot._get_state(), channel=channel
                )
                if channel.guild is not None:
                    message2.author = channel.guild.get_member(user.id)  # type: ignore
                    if message2.author == None:
                        message2.author = user
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
