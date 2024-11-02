import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
import random
import psutil
import asyncio

TOKEN = 'tooooooooooooooooooooken' # 토큰

talk_channel_id = 6974892 # 대화 채널 ID
verification_channel_id = 6974892 # 인증 태널 ID
system_message_channel_id = 6974892 # 시스템 메세지 채널 ID
performance_channel_id = 6974892 # 성능 상태 채널 ID

theme_color = discord.Color.orange() # 테마 색

intents = discord.Intents.all()
intents.members = True

file_path = "C:/Users/user/Desktop/igubot_custom_responses.txt" # 답변 데이터 파일
class iguBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=intents) # 원하는 프리픽스로 변경하세요 ('$', '!' 등등)
        self.edit_message = None

    async def send_performance_update(self):
        performance_channel = self.get_channel(performance_channel_id)
        message = await performance_channel.send(embed=self.create_performance_embed())
        task = asyncio.create_task(self.update_performance(message))

    async def update_performance(self, edit_message):
        system_message_channel = self.get_channel(system_message_channel_id)
        
        while True:
            try:
                await asyncio.sleep(10)
                new_embed = self.create_performance_embed()
                await edit_message.edit(embed=new_embed)
            except:
                await system_message_channel.send("성능 상태를 업데이트 하는 중 오류가 발생했어요! >﹏<") # 원하는 문장으로 변경하세요

    def create_performance_embed(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent

        cpu_bar = self.create_bar(cpu_usage)
        memory_bar = self.create_bar(memory_usage)

        embed = discord.Embed(title="이구봇 성능 상태", color=theme_color) # 원하는 봇 이름으로 변경하세요
        embed.add_field(name="CPU: Intel Pentium G850", value=f"{cpu_usage}% 사용중\n{cpu_bar}", inline=False) # 봇 컴퓨터 CPU 모델로 변경하세요
        embed.add_field(name="RAM: 8GB", value=f"{memory_usage}% 사용중\n{memory_bar}", inline=False) # 봇 컴퓨터 메모리 용량으로 변경하세요

        return embed

    def create_bar(self, usage):
        filled = round(usage // 10)
        empty = 10 - filled
        return "■" * filled + "□" * empty
    
    async def setup_verification(self):
        verification_channel = self.get_channel(verification_channel_id)
        system_message_channel = self.get_channel(system_message_channel_id)

        if verification_channel is not None:
            button1 = discord.ui.Button(label="인증하기", style=discord.ButtonStyle.secondary)

            async def button_callback1(interaction):
                role = interaction.guild.get_role(1295701978902564915)
                if role is not None:
                    if role not in interaction.user.roles:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message("인증되었어요! ≥ω≤", ephemeral=True) # 원하는 문장으로 변경하세요
                        await system_message_channel.send(f"<@{interaction.user.id}> 인증되었어요! >ω<") # 원하는 문장으로 변경하세요
                    else:
                        await interaction.response.send_message("이미 인증된 유저에요!", ephemeral=True) # 원하는 문장으로 변경하세요
                        await system_message_channel.send(f"<@{interaction.user.id}> 이미 인증된 유저에요! ●‿●") # 원하는 문장으로 변경하세요
                else:
                    await interaction.response.send_message("지급할 역할을 찾지 못했어요! >﹏<", ephemeral=True) # 원하는 문장으로 변경하세요
                    await system_message_channel.send(f"<@{interaction.user.id}> 지급할 역할을 찾지 못했어요! >﹏<") # 원하는 문장으로 변경하세요

            button1.callback = button_callback1

            view = discord.ui.View(timeout=None)
            view.add_item(button1)

            await verification_channel.send(embed=discord.Embed(title='인증', description="버튼을 눌러 인증해주세요!", color=theme_color), view=view) # 원하는 문장으로 변경하세요
        
    async def on_ready(self):
        await self.tree.sync()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("이구아나 스튜디오 전용 봇입니다!")) # 원하는 문장으로 변경하세요
        await self.setup_verification()
        await self.send_performance_update()
        await load_custom_responses()
        print(f'Logged in as {self.user.name}')

igubot = iguBot()

custom_responses = {}

@igubot.event
async def on_message(message):
    if message.author == igubot.user:
        return
    await igubot.process_commands(message)
    if message.channel.id == talk_channel_id:
        if message.content.startswith("이구봇"): # 원하는 이름으로 변경하세요
            command = message.content[4:].strip()
            if command == "":
                response = random.choice(["넵!", "네!!", "하잇!"]) # 원하는 문장으로 변경하세요
                await message.channel.send(response)
            elif command in custom_responses:
                response = random.choice(custom_responses[command])[0]
                await message.channel.send(response)
            else:
                await message.channel.send(f"전 아직 '{command}'은(는) 답변할 줄 몰라요... '/가르치기' 커맨드로 답변을 가르쳐주세요! >ω<") # 원하는 문장으로 변경하세요

@igubot.tree.command(name="가르치기", description="이구봇에게 답변 가르치기!") # 원하는 설명으로 변경하세요
async def teach_command(interaction: discord.Interaction, 질문: str, 답변: str):
    유저 = str(interaction.user)
    userId = interaction.user.id
    if 질문 in custom_responses:
        custom_responses[질문].append([답변, 유저])
    else:
        custom_responses[질문] = [[답변, 유저]]
    
    with open(file_path, "w", encoding="utf-8") as f:
        for key, value in custom_responses.items():
            formatted_entries = "|".join([f"{답변},{유저}" for 답변, 유저 in value])
            f.write(f"{key}:{formatted_entries}\n")
    
    await interaction.response.send_message(f'<@{userId}>님께 "{질문}"에 대한 답변을 배웠어요! >ω<') # 원하는 문장으로 변경하세요

async def load_custom_responses(file_path: str = file_path):
    system_message_channel = igubot.get_channel(system_message_channel_id)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                질문, 데이터 = line.strip().split(":", 1)
                entries = 데이터.split("|")
                custom_responses[질문] = [entry.split(",") for entry in entries]
    except FileNotFoundError:
        await system_message_channel.send("답변 데이터 파일을 찾지 못했어요! >﹏<") # 원하는 문장으로 변경하세요
        await system_message_channel.send("새로운 파일을 생성할게요! ●‿●") # 원하는 문장으로 변경하세요

@igubot.tree.command(name="완장호출", description="멍청한 이구아나 부르기!") # 원하는 설명으로 변경하세요
async def 완장호출(interaction):
    await interaction.response.send_message("<@6974892>") # 서버 관리자 ID로 변경하세요
    await interaction.response.send_message("<@6974892>") # 서버 관리자 ID로 변경하세요
    await interaction.response.send_message("<@6974892>") # 서버 관리자 ID로 변경하세요

igubot.run(TOKEN)
