from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from ._helpers import load_button_context
from .awakening import awakening, choose_class, handle_awakening_callback
from .daily import handle_claim_callback, handle_daily_callback, handle_task_callback
from .dungeon import (
    handle_boss_callback,
    handle_boss_defeat_callback,
    handle_dungeon_enter_callback,
    handle_dungeon_task_callback,
    handle_dungeons_callback,
)
from .inventory import (
    handle_equip_callback,
    handle_equipment_callback,
    handle_inventory_callback,
    inventory,
)
from .jobchange import handle_jobchange_callback, jobchange
from .menu import menu
from .roll import handle_claim_hidden_callback, handle_dungeon_roll_callback, handle_roll_callback
from .shop import handle_buy_callback, handle_shop_callback, shop
from .spend import handle_spend_callback, spend
from .start import start
from .stats import handle_stats_callback, stats


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    action = q.data
    ctx = load_button_context(user_id)

    if action.startswith("class1_"):
        await handle_awakening_callback(q, user_id, action, ctx)
    elif action.startswith("class2_"):
        await handle_jobchange_callback(q, user_id, action, ctx)
    elif action.startswith("equip_"):
        await handle_equip_callback(q, user_id, action, ctx)
    elif action == "dungeons":
        await handle_dungeons_callback(q, user_id, action, ctx)
    elif action.startswith("buy_"):
        await handle_buy_callback(q, user_id, action, ctx)
    elif action in ("dungeon_E", "dungeon_D", "dungeon_C"):
        await handle_dungeon_enter_callback(q, user_id, action, ctx)
    elif action == "class":
        await handle_awakening_callback(q, user_id, action, ctx)
    elif action.startswith("dungeon_task_"):
        await handle_dungeon_task_callback(q, user_id, action, ctx)
    elif action == "boss":
        await handle_boss_callback(q, user_id, action, ctx)
    elif action == "boss_defeat":
        await handle_boss_defeat_callback(q, user_id, action, ctx)
    elif action == "daily":
        await handle_daily_callback(q, user_id, action, ctx)
    elif action.startswith("task_"):
        await handle_task_callback(q, user_id, action, ctx)
    elif action == "done_disabled":
        await q.answer()
    elif action == "claim":
        await handle_claim_callback(q, user_id, action, ctx, context)
    elif action == "roll":
        await handle_roll_callback(q, user_id, action, ctx)
    elif action.startswith("claim_hidden_"):
        await handle_claim_hidden_callback(q, user_id, action, ctx)
    elif action == "dungeon_roll":
        await handle_dungeon_roll_callback(q, user_id, action, ctx)
    elif action == "stats":
        await handle_stats_callback(q, user_id, action, ctx)
    elif action == "inventory":
        await handle_inventory_callback(q, user_id, action, ctx)
    elif action == "equipment":
        await handle_equipment_callback(q, user_id, action, ctx)
    elif action == "shop":
        await handle_shop_callback(q, user_id, action, ctx)
    elif action in ("spend_str", "spend_int", "spend_agi", "spend_vit", "spend_sense"):
        await handle_spend_callback(q, user_id, action, ctx)


def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("class", choose_class))
    app.add_handler(CommandHandler("awakening", awakening))
    app.add_handler(CommandHandler("jobchange", jobchange))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("spend", spend))
    app.add_handler(CallbackQueryHandler(button))
