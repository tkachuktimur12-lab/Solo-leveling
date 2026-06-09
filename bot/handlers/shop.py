from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..constants import SHOP_ITEMS
from ..db import conn, cursor
from ..game_logic import generate_item


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{item} - 💰{price}", callback_data=f"buy_{item}")]
        for item, price in SHOP_ITEMS
    ]
    await update.message.reply_text(
        "🛒 SHOP 🛒", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_buy_callback(q, user_id, action, ctx):
    item_name = action.replace("buy_", "")
    price = dict(SHOP_ITEMS).get(item_name)
    gold = ctx["gold"]

    if price is None:
        await q.edit_message_text("Item not found")
        return
    if gold < price:
        await q.edit_message_text("❌ Not enough gold")
        return

    gold -= price
    item = generate_item({"sense": ctx["total_sense"]})

    cursor.execute(
        """
        INSERT INTO inventory (
            user_id, item_name, slot, rarity,
            strength, intelligence, agility, vitality, sense, equipped
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            user_id,
            item["name"],
            "weapon",
            item["rarity"],
            item["strength"],
            item["intelligence"],
            item["agility"],
            item["vitality"],
            item["sense"],
        ),
    )
    cursor.execute("UPDATE users SET gold=? WHERE user_id=?", (gold, user_id))
    conn.commit()

    await q.edit_message_text(
        f"🛒 Purchased {item_name}\n\n"
        f"🎁 Loot received:\n"
        f"{item['rarity'].upper()} {item['name']}\n"
        f"+STR {item['strength']} +AGI {item['agility']}"
    )


async def handle_shop_callback(q, user_id, action, ctx):
    text = "🛒 HUNTER SHOP 🛒\n\n"
    keyboard = []
    for item_name, price in SHOP_ITEMS:
        text += f"{item_name} — 💰 {price} Gold\n"
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Buy {item_name}", callback_data=f"buy_{item_name}"
                )
            ]
        )
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
