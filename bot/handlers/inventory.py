from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..db import conn, cursor


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM inventory WHERE user_id=?", (user_id,))
    items = cursor.fetchall()

    if not items:
        await update.message.reply_text("🎒 Inventory is empty")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{item['item_name']} ({item['rarity']})",
                callback_data=f"equip_{item['item_id']}",
            )
        ]
        for item in items
    ]
    await update.message.reply_text(
        "🎒 INVENTORY", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_equip_callback(q, user_id, action, ctx):
    item_id = int(action.split("_")[1])
    cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
    item = cursor.fetchone()

    if not item:
        await q.edit_message_text("❌ Item not found")
        return

    cursor.execute(
        "INSERT OR IGNORE INTO equipment (user_id) VALUES (?)", (user_id,)
    )
    if item["slot"] == "weapon":
        cursor.execute(
            "UPDATE equipment SET weapon_id=? WHERE user_id=?", (item_id, user_id)
        )
    elif item["slot"] == "armor":
        cursor.execute(
            "UPDATE equipment SET armor_id=? WHERE user_id=?", (item_id, user_id)
        )
    elif item["slot"] == "charm":
        cursor.execute(
            "UPDATE equipment SET charm_id=? WHERE user_id=?", (item_id, user_id)
        )

    conn.commit()
    await q.edit_message_text(f"⚔ Equipped: {item['item_name']}")


async def handle_inventory_callback(q, user_id, action, ctx):
    cursor.execute(
        """
        SELECT * FROM inventory
        WHERE user_id=?
        ORDER BY rarity DESC
        """,
        (user_id,),
    )
    items = cursor.fetchall()

    if not items:
        await q.edit_message_text("🎒 Inventory is empty")
        return

    text = "🎒 INVENTORY\n\n"
    keyboard = []
    for item in items:
        text += (
            f"{item['item_id']}. {item['rarity'].upper()} {item['item_name']}\n"
            f"⚔ STR {item['strength']} | "
            f"🧠 INT {item['intelligence']} | "
            f"⚡ AGI {item['agility']} | "
            f"❤️ VIT {item['vitality']} | "
            f"👁 SENSE {item['sense']}\n\n"
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Equip {item['item_name']}",
                    callback_data=f"equip_{item['item_id']}",
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("🛡 Equipped Gear", callback_data="equipment")]
    )
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_equipment_callback(q, user_id, action, ctx):
    cursor.execute("SELECT * FROM equipment WHERE user_id=?", (user_id,))
    equipment = cursor.fetchone()

    if not equipment:
        await q.edit_message_text("❌ No equipment")
        return

    def get_item(item_id):
        if not item_id:
            return None
        cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        return cursor.fetchone()

    weapon = get_item(equipment["weapon_id"])
    armor = get_item(equipment["armor_id"])
    charm = get_item(equipment["charm_id"])

    await q.edit_message_text(
        "🛡 EQUIPPED GEAR 🛡\n\n"
        f"⚔ Weapon: {weapon['item_name'] if weapon else 'None'}\n"
        f"🛡 Armor: {armor['item_name'] if armor else 'None'}\n"
        f"💍 Charm: {charm['item_name'] if charm else 'None'}\n"
    )
