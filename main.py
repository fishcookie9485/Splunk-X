import discord
import re
import os
from keep_alive import keep_alive

# Start the keep-alive server
keep_alive()

# Get bot token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

SOURCE_CHANNEL_ID = 1414236802876968985  # Source channel
TARGET_CHANNEL_ID = 1414237079013163091  # Target channel
PREFIX = "."  # command prefix

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

def clean_embed(embed: discord.Embed) -> discord.Embed:
    original_title = embed.title or "Live Hits"
    new_embed = discord.Embed(
        title=original_title,
        color=embed.color or discord.Color.blue()
    )

    if embed.thumbnail:
        new_embed.set_thumbnail(url=embed.thumbnail.url)
    if embed.image:
        new_embed.set_image(url=embed.image.url)

    emoji_pattern = re.compile(r":[^:]+:|<a?:\w+:\d+>")
    description = embed.description or ""

    description = emoji_pattern.sub("", description).strip()
    new_embed.description = description

    for field in embed.fields:
        name_clean = emoji_pattern.sub("", field.name)
        value_clean = emoji_pattern.sub("", field.value)
        new_embed.add_field(name=name_clean, value=value_clean, inline=field.inline)

    if embed.footer and embed.footer.text:
        new_embed.set_footer(text=emoji_pattern.sub("", embed.footer.text))
    if embed.author and embed.author.name:
        new_embed.set_author(name=emoji_pattern.sub("", embed.author.name))

    return new_embed

@bot.event
async def on_message(message):
    if message.channel.id == SOURCE_CHANNEL_ID and message.embeds:
        embed = message.embeds[0]
        cleaned = clean_embed(embed)
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if target_channel:
            await target_channel.send(embed=cleaned)

    if message.content.strip().lower() == f"{PREFIX}test":
        source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
        if not source_channel:
            await message.channel.send("Source channel not found.")
            return

        async for msg in source_channel.history(limit=50):
            if msg.embeds:
                embed = msg.embeds[0]
                cleaned = clean_embed(embed)
                target_channel = bot.get_channel(TARGET_CHANNEL_ID)
                if target_channel:
                    await target_channel.send(embed=cleaned)
                    await message.channel.send("✅ Sent latest embed.")
                return

        await message.channel.send("No embeds found in recent messages.")

bot.run(TOKEN)


