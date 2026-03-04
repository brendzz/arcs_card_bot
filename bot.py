import yaml
import json
import os
import random
import schedule
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

webhookUrl = os.environ.get("DISCORD_WEBHOOK_URL")
if not webhookUrl:
    raise ValueError("DISCORD_WEBHOOK_URL is missing or not loaded from .env")
    
cardsFile = "cards.yml"
usedCardsFile = "used_cards.json"
baseImageUrl = "https://cardcdn.buriedgiantstudios.com/cards/arcs/en-US/"
timeToPost = "11:00"

def load_cards():
    with open(cardsFile, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_used_cards():
    if not os.path.exists(usedCardsFile):
        return []
    with open(usedCardsFile, "r", encoding="utf-8") as f:
        return json.load(f)

def save_used_cards(used):
    with open(usedCardsFile, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2)

def pick_card(cards, used):
    unused = [c for c in cards if c["id"] not in used]

    # Reset if all cards have been used
    if not unused:
        used.clear()
        unused = cards

    card = random.choice(unused)
    used.append(card["id"])
    save_used_cards(used)
    return card

def send_card(card):
    image_url = f"{baseImageUrl}{card['image']}.webp"

    webhook = DiscordWebhook(url=str(webhookUrl))
    embed = DiscordEmbed(
        title=card["name"],
        description=card["text"],
        color=0x3498db
    )
    embed.set_image(url=image_url)
    embed.add_embed_field(name="ID", value=card["id"])
    embed.add_embed_field(name="Tags", value=", ".join(card.get("tags", [])))

    webhook.add_embed(embed)
    webhook.execute()

def daily_task():
    cards = load_cards()
    used = load_used_cards()
    card = pick_card(cards, used)
    send_card(card)
    print(f"Sent card: {card['id']}")

schedule.every().day.at(timeToPost).do(daily_task)

print("Daily card bot running...")
while True:
    schedule.run_pending()
    time.sleep(1)
