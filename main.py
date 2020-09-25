if __name__ != "__main__":
    raise RuntimeError("don't import this!")

import os
import traceback

from extension.structures import Marjorie

bot = Marjorie(';')

for path, _, files in os.walk("extension/cogs"):
    for file in files:
        path = os.path.join(path, file)
        if not os.path.isfile(path):
            continue

        path, ext = os.path.splitext(path)
        if ext != ".py":
            continue

        path = path.replace("\\", '.').replace('/', '.')
        try:
            bot.load_extension(path)
        except Exception:
            traceback.print_exc()
            # Se utilizar `raise error` a inicialização do BOT é
            # cancelada, utilizando dessa forma, isso não acontece.
        else:
            print(f"-> [Cog loaded] {path}")

bot.run(os.getenv("DISCORD_TOKEN"))
