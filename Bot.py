import discord
from discord.ext import commands
from discord import app_commands

# Включаем интенты
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# === ТВОИ ДАННЫЕ ===
TOKEN = 'MTUxODM1MTQxNjI2NjE5OTExMA.Gyp8sr.eV5nZA4O_tVr5srcSRhQ-TVmaY2ow8519wsqFU'

# База радиостанций (теперь их три)
STATIONS = {
    "lofi": "http://lofi.stream.laut.fm/lofi",
    "anime": "http://stream.laut.fm/anime",
    "otaku_world": "http://stream.laut.fm/otaku-world"  # Добавили Otaku World!
}

# Настройки по умолчанию
current_stream_url = STATIONS["lofi"]
current_volume = 0.5  # 50% громкости по умолчанию

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен! Доступны станции: Lo-Fi, Опенинги и Otaku World.')

# Команда /заходи
@bot.tree.command(name="заходи", description="Приказывает боту зайти в канал и включить музыку")
async def join(interaction: discord.Interaction, кодовое_слово: str = None):
    global current_stream_url, current_volume
    
    if кодовое_слово is None or кодовое_слово.lower() != "госпожа":
        await interaction.response.send_message("Я слушаюсь только если назвать меня 'госпожа'...", ephemeral=True)
        return
    
    if interaction.user.voice is None:
        await interaction.response.send_message("Сначала зайди в любой голосовой канал!", ephemeral=True)
        return
    
    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client is not None:
        await voice_client.move_to(voice_channel)
    else:
        voice_client = await voice_channel.connect()

    if not voice_client.is_playing():
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        
        # Защита от беззвучности: принудительно запускаем через ffmpeg.exe в папке бота
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=current_stream_url, **ffmpeg_options)
        volume_audio = discord.PCMVolumeTransformer(audio_source, volume=current_volume)
        
        voice_client.play(volume_audio)
        await interaction.response.send_message(f"Слушаюсь! Зашла в **{voice_channel.name}** и включила музыку.")
    else:
        await interaction.response.send_message(f"Уже играю музыку в **{voice_channel.name}**!", ephemeral=True)

# Команда /выходи
@bot.tree.command(name="выходи", description="Прогоняет бота из канала")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client is not None:
        await voice_client.disconnect()
        await interaction.response.send_message("Отключилась. Пока!")
    else:
        await interaction.response.send_message("Я и так нигде не сижу.", ephemeral=True)

# Команда /радио (теперь 3 станции в меню)
@bot.tree.command(name="радио", description="Сменить радиостанцию")
@app_commands.choices(станция=[
    app_commands.Choice(name="Lo-Fi (Спокойная)", value="lofi"),
    app_commands.Choice(name="Anime OST (Опенинги)", value="anime"),
    app_commands.Choice(name="Otaku World (J-Music / Вокалоиды)", value="otaku_world") # Добавили в список выбора
])
async def change_station(interaction: discord.Interaction, станция: app_commands.Choice[str]):
    global current_stream_url, current_volume
    current_stream_url = STATIONS[станция.value]
    
    voice_client = interaction.guild.voice_client
    
    if voice_client is not None and voice_client.is_playing():
        voice_client.stop()
        
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=current_stream_url, **ffmpeg_options)
        volume_audio = discord.PCMVolumeTransformer(audio_source, volume=current_volume)
        
        voice_client.play(volume_audio)
        await interaction.response.send_message(f"Переключила волну на **{станция.name}**! 📻")
    else:
        await interaction.response.send_message(f"Волна изменена на **{станция.name}**. Используй `/заходи госпожа`, чтобы включить!", ephemeral=True)

# Команда /громкость
@bot.tree.command(name="громкость", description="Изменить громкость музыки (от 1 до 100)")
async def set_volume(interaction: discord.Interaction, уровень: int):
    global current_volume
    
    if уровень < 1 or уровень > 100:
        await interaction.response.send_message("Громкость должна быть от 1 до 100!", ephemeral=True)
        return
        
    current_volume = уровень / 100.0
    
    voice_client = interaction.guild.voice_client
    
    if voice_client is not None and voice_client.is_playing():
        voice_client.source.volume = current_volume
        await interaction.response.send_message(f"Громкость установлена на **{уровень}%** 🔊")
    else:
        await interaction.response.send_message(f"Громкость сохранена ({уровень}%). Музыка заиграет с этой громкостью при следующем запуске.", ephemeral=True)

bot.run(TOKEN)
