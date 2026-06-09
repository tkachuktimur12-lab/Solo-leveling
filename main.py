from bot.app import build_app


def main():
    app = build_app()
    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
