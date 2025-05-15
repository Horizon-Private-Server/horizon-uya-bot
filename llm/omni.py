import os
import discord
from llama_cpp import Llama
from formatter import OmniPromptFormatter

TOKEN = os.getenv("OMNI_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("OMNI_CHANNEL_ID"))
KNOWLEDGE_ADD_CHANNEL_ID = int(os.getenv("OMNI_KNOWLEDGE_ADD_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

llm = Llama(
#    model_path="models/mistral-7b-instruct-v0.2/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    model_path="final_model/mistral7b_uya_Q4_K_M.gguf",
    n_gpu_layers=35,
    n_ctx=4096,
    n_threads=6,
    use_mlock=True
)

channel_histories = {}
formatter = OmniPromptFormatter()

def replace_bot_mentions(content: str, bot_user: discord.User) -> str:
    return content.replace(f"<@{bot_user.id}>", "@Omni")

def replace_discord_mentions(content: str, message: discord.Message) -> str:
    for user in message.mentions:
        content = content.replace(f"<@{user.id}>", f"@{user.display_name}")
    for role in message.role_mentions:
        content = content.replace(f"<@&{role.id}>", f"@[{role.name}]")
    for channel in message.channel_mentions:
        content = content.replace(f"<#{channel.id}>", f"#{channel.name}")
    return content

def build_prompt(channel_id, username, user_input, max_prompt_tokens=3000):
    history = channel_histories.get(channel_id, [])

    recent = [f"{line}" for line in history[-20:]]

    # Join previous exchanges into a single input (if desired). Or just use latest.
    full_input = "\n".join(recent)

    chat_log = f"{username}: {user_input}"

    # Build the prompt in the **exact fine-tune format**:
    prompt = formatter.assemble_inference_prompt(chat_log=chat_log)
    prompt_tokens = llm.tokenize(prompt.encode("utf-8"))
    print(f"🔢 Prompt token count: {len(prompt_tokens)}")

    return prompt, history


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != TARGET_CHANNEL_ID:
        return

    channel_id = str(message.channel.id)
    username = message.author.display_name
    content = message.content.strip()

    # Handle "!knowledge" command
    if content.startswith("!knowledge"):
        knowledge_content = content[len("!knowledge"):].strip()
        knowledge_channel = bot.get_channel(KNOWLEDGE_ADD_CHANNEL_ID)
        if knowledge_channel:
            await knowledge_channel.send(knowledge_content)
        await message.reply("Thanks! I'll add this to be reviewed before making this permanent knowledge for my model!")
        return

    # Ignore all other commands starting with "!"
    if content.startswith("!"):
        return

    # Normal message processing
    content = replace_bot_mentions(content, bot.user)
    content = replace_discord_mentions(content, message)

    history = channel_histories.get(channel_id, [])
    history.append(f"{username}: {content}")
    channel_histories[channel_id] = history[-40:]

    if bot.user in message.mentions:
        print(f"🔔 Mentioned by {username} in channel {channel_id}: {content}")

        prompt, trimmed_history = build_prompt(channel_id, username, content)
        print("=========================================== Prompt:")
        print(prompt)

        try:
            stop_tokens = ["\n" + name + ":" for name in set(h.split(":")[0] for h in trimmed_history)]
            stop_tokens = []
            print(f"Stop tokens: {stop_tokens}")
            response = llm(prompt, max_tokens=1024, stop=stop_tokens)
            output = response["choices"][0]["text"].strip()

            print("=== LLM OUTPUT ===========================================")
            print(output)
            print("==========================================================")
 
            command = output.split("\n")[0].split("command: ")[-1]
            chat_resp = output.split("\n")[-1].removeprefix("chat_response:: ").strip()
            print(command, chat_resp)

            # Update history AFTER generating response
            history = channel_histories.get(channel_id, [])
            history.append(f"Omni: {chat_resp}")
            channel_histories[channel_id] = history[-40:]

            await message.reply(output)
        except Exception as e:
            print("⚠️ LLM error:", e)
            await message.reply(f"❌ Error: {str(e)}")

bot.run(TOKEN)

