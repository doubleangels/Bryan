import interactions
import asyncio
import os
import pickledb
import sys
import signal

# Load the bot token from environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Load or create a PickleDB database to store persistent data
db = pickledb.load('db/pickle.db', True)

# Initialize the bot with default intents and MESSAGE_CONTENT to capture messages
bot = interactions.Client(intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT)

# Event listener for when the bot becomes online and is ready
@interactions.listen()
async def on_ready():    
    print("Setting up status and activity...")
    # Set the bot's presence (status and activity)
    await bot.change_presence(
        status=interactions.Status.ONLINE,
        activity=interactions.Activity(
            name="for Bryans!",
            type=interactions.ActivityType.WATCHING
        )
    )

    print("I am online and ready!")


# Event listener to handle message creation (whenever a new message is sent)
@interactions.listen()
async def on_message_create(event: interactions.api.events.MessageCreate):
    saved_channel = db.get('channel')
    if not saved_channel:
        print("No channel has been set up for the bot.")
        return
    if event.message.channel == saved_channel:
        print(f"Message received in the correct channel.")
        print(f"Message: {event.message.author} - {event.message.content}")
        if event.message.content != "<:bryan:1292973952087359501>":
            await event.message.delete()
            print(f"Message deleted.")

# Slash command to set up the bot
@interactions.slash_command(name="setup", description="Setup the role for reminders")
@interactions.slash_option(
    name="channel",
    description="Channel",
    required=True,
    opt_type=interactions.OptionType.CHANNEL
)
async def setup(ctx: interactions.ComponentContext, channel):
    print(f'Setup requested by {ctx.author.username}.')
    channel_id = channel.id
    print(f"Bryan will use <#{channel_id}>!")
    db.set('channel', channel_id)
    db.dump()
    await ctx.send(f"Bryan will use <#{channel_id}>!")

# Slash command to maintain developer tag
@interactions.slash_command(name="dev", description="Maintain developer tag")
async def dev(ctx: interactions.SlashContext):
    print(f'Developer tag maintenance requested by {ctx.author.username}.')
    await ctx.send("Developer tag maintained!")

# Slash command to send the GitHub link for the project
@interactions.slash_command(name="github", description="Send link to the GitHub project for this bot")
async def github(ctx: interactions.SlashContext):
    print(f'Github link requested by {ctx.author.username}.')
    await ctx.send("https://github.com/doubleangels/Bryan")

# Function to handle bot shutdown on SIGINT
def handle_interrupt(signal, frame):
    db.dump()
    sys.exit(0)

# Register the signal handler for SIGINT
signal.signal(signal.SIGINT, handle_interrupt)

# Start the bot using the provided token
bot.start(TOKEN)
