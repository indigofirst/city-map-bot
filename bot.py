import os
import tempfile
import telebot
from config import DATABASE, TOKEN
from logic import DBMap


if not TOKEN:
    raise ValueError(
        "Bitte tragen Sie den Bot-Token in der Datei config.py ein."
    )

manager = DBMap(DATABASE)
manager.create_user_table()

bot = telebot.TeleBot(TOKEN)


def get_command_argument(message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return ""
    return parts[1].strip()


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Hallo! 👋\n\n"
        "Ich bin ein Karten-Bot. Ich kann Städte auf einer Weltkarte anzeigen, "
        "Städte in deiner persönlichen Liste speichern und die Entfernung "
        "zwischen zwei Städten berechnen.\n\n"
        "Mit /help siehst du alle verfügbaren Befehle."
    )


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "Verfügbare Befehle:\n\n"
        "/start – Bot starten\n"
        "/help – Befehle anzeigen\n"
        "/show_city <Stadt> – Stadt auf der Karte anzeigen\n"
        "/remember_city <Stadt> – Stadt speichern\n"
        "/show_my_cities – gespeicherte Städte auf einer Karte anzeigen\n"
        "/distance <Stadt1> | <Stadt2> – Entfernung zwischen zwei Städten anzeigen\n\n"
        "Beispiele:\n"
        "/show_city Zurich\n"
        "/remember_city Paris\n"
        "/distance Zurich | Paris\n\n"
        "Die Städtenamen müssen so geschrieben sein, wie sie in der Datenbank gespeichert sind."
    )


@bot.message_handler(commands=["show_city"])
def handle_show_city(message):
    city_name = get_command_argument(message)

    if not city_name:
        bot.send_message(
            message.chat.id,
            "Bitte gib eine Stadt an, zum Beispiel:\n/show_city Paris"
        )
        return

    if not manager.get_coordinates(city_name):
        bot.send_message(
            message.chat.id,
            "Diese Stadt wurde nicht gefunden. Bitte überprüfe den Namen."
        )
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        map_path = os.path.join(temp_dir, "city_map.png")
        manager.create_map(map_path, [city_name])

        with open(map_path, "rb") as map_file:
            bot.send_photo(
                message.chat.id,
                map_file,
                caption=f"📍 {city_name}"
            )


@bot.message_handler(commands=["remember_city"])
def handle_remember_city(message):
    city_name = get_command_argument(message)

    if not city_name:
        bot.send_message(
            message.chat.id,
            "Bitte gib eine Stadt an, zum Beispiel:\n/remember_city Berlin"
        )
        return

    result = manager.add_city(message.from_user.id, city_name)

    if result == "added":
        bot.send_message(
            message.chat.id,
            f"✅ {city_name} wurde gespeichert."
        )
    elif result == "exists":
        bot.send_message(
            message.chat.id,
            f"ℹ️ {city_name} ist bereits in deiner Liste."
        )
    else:
        bot.send_message(
            message.chat.id,
            "Diese Stadt wurde nicht gefunden. Bitte überprüfe den Namen."
        )


@bot.message_handler(commands=["show_my_cities"])
def handle_show_my_cities(message):
    cities = manager.select_cities(message.from_user.id)

    if not cities:
        bot.send_message(
            message.chat.id,
            "Du hast noch keine Städte gespeichert.\n"
            "Verwende /remember_city <Stadt>, um eine Stadt hinzuzufügen."
        )
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        map_path = os.path.join(temp_dir, "my_cities.png")
        manager.create_map(map_path, cities)

        with open(map_path, "rb") as map_file:
            bot.send_photo(
                message.chat.id,
                map_file,
                caption=f"🗺 Gespeicherte Städte: {len(cities)}"
            )


@bot.message_handler(commands=["distance"])
def handle_distance(message):
    argument = get_command_argument(message)

    if "|" not in argument:
        bot.send_message(
            message.chat.id,
            "Bitte verwende dieses Format:\n"
            "/distance Zurich | Paris"
        )
        return

    city1, city2 = [part.strip() for part in argument.split("|", maxsplit=1)]

    if not city1 or not city2:
        bot.send_message(
            message.chat.id,
            "Bitte gib zwei Städte an, zum Beispiel:\n"
            "/distance Zurich | Paris"
        )
        return

    distance = manager.calculate_distance(city1, city2)

    if distance is None:
        bot.send_message(
            message.chat.id,
            "Mindestens eine der beiden Städte wurde nicht gefunden."
        )
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        map_path = os.path.join(temp_dir, "distance_map.png")
        manager.create_distance_map(map_path, city1, city2)

        with open(map_path, "rb") as map_file:
            bot.send_photo(
                message.chat.id,
                map_file,
                caption=(
                    f"📏 {city1} → {city2}\n"
                    f"Luftlinie: {distance:,.0f} km"
                )
            )


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
