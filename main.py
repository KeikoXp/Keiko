if __name__ != "__main__":
    raise RuntimeError("don't import this!")

import os
import re
import traceback

from extension.structures import Marjorie

bot = Marjorie('-')

regex = re.compile(r"\\\/")

for path, _, files in os.walk("extension/cogs"):
    for file in files:
        path = os.path.join(path, file)
        if not os.path.isfile(path):
            continue

        path, ext = os.path.splitext(path)
        if ext != ".py":
            continue

        path = re.sub(regex, '.', path)
        try:
            bot.load_extension(path)
        except BaseException as error:
            traceback.print_exc()
            # se utilizar `raise` error a inicialização do BOT é
            # cancelada, utilizando dessa forma, isso não acontece.
        else:
            print(f"-> [Cog loaded] {path}")

bot.run("NTQwNjA0MDAzMTA1Mzc0MjEw.XFNCtg.KAZLlGFt4OjgN3THPGJ49_yHl7w")
