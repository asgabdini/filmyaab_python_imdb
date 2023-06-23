from telegram import Update, constants, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
from datetime import date
from IMDB import IMDB
import translators as ts
from uuid import uuid4
import logging
import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

imdb = IMDB()


# dictionary containing button values
selectionDict = {
    "genres": {
        "Action": "اکشن" + " " + "🔫",
        "Comedy": "کمدی" + " " + "😂",
        "Family": "خانوادگی" + " " + "👨‍👩‍👦‍👦",
        "History": "تاریخ" + " " + "📜",
        "Mystery": "راز آلود" + " " + "🕵️‍♀️",
        "Sci-Fi": "علمی تخیلی" + " " + "🚀",
        "War": "جنگ" + " " + "⚔️",
        "Adventure": "ماجرا جویی" + " " + "🗺️",
        "Crime": "جرم و جنایت" + " " + "👮‍♂️",
        "Fantasy": "فانتزی" + " " + "🧙‍♂️",
        "Horror": "وحشت" + " " + "👻",
        "News": "اخبار" + " " + "📰",
        "Sport": "ورزش" + " " + "🏀",
        "Western": "وسترن" + " " + "🤠",
        "Animation": "انیمیشن" + " " + "🎬",
        "Documentary": "مستند" + " " + "📹",
        "Film-Noir": "فبلم نوآور" + " " + "🎥",
        "Music": "آهنگ" + " " + "🎵",
        "Reality-TV": "ریئلیتی" + " " + "📺",
        "Talk-Show": "گفتگو" + " " + "💬",
        "Biography": "زندگینامه" + " " + "📚",
        "Drama": "درام" + " " + "🎭",
        "Game-Show": "گیم" + " " + "🎮",
        "Musical": "موزیکال" + " " + "🎤",
        "Romance": "رمانتیک" + " " + "💕",
        "Thriller": "دلهره آور" + " " + "🔪",
    },

    "title_type": {
        "feature": "فیلم بلند",
        "tv_episode": "قسمت تلوزیونی",
        "short": "فیلم کوتاه",
        "podcast_episode": "قسمت پادکست",
        "music_video": "موزیک ویدیو",
        "tv_short": "کوتاه تلوزیونی",
        "podcast_series": "مجموعه پادکست",
        "video_game": "بازی ویدیویی",
        "tv_series": "سریال تلوزیونی",
        "tv_movie": "فیلم تلوزیونی",
        "tv_miniseries": "سریال کوتاه تلوزیونی",
        "documentary": "مستند",
        "video": "ویدیو"
    }
}

advanceSearchItems = ['🎥 نوع فیلم', '🎭 ژانر',  '🎞️ نام اثر',
                      '📅 تاریخ انتشار', '⏰ مدت زمان', '⭐️ امتیاز', 'یافتن 🔍']

# dictionary for set filtering values
filtersOfTitle = {"genres": [], "release_date": [],
                  "user_rating": [], "runtime": [], "title_type": [], "title": ""}

# function to arrange the buttons


def splitButtons(buttons, row, confirmKeyboard):
    rowSplit = []
    keyboard = []
    for button in buttons:
        rowSplit.append(button)
        if len(rowSplit) == row:
            keyboard.append(rowSplit)
            rowSplit = []
    if len(rowSplit) > 0:
        keyboard.append(rowSplit)
    if confirmKeyboard:
        keyboard.append(["لغو", "تایید"])
    return (keyboard)


# dictionary for managing levels of bot
levels = {
    "شروع": {
        "name": "شروع"
    },
    "خانه": {
        "name": "خانه",
        "type": "level",
        "title": "از بین گزینه های زیر انتخاب کنید",
        "nxt": ["جستجوی پیشرفته", 'لیست شما', 'دانلود ها', 'برترین ها', 'نظرات', 'حمایت از ما'],
        "keyboard": [["جستجوی پیشرفته"], ["لیست شما",
                                          "دانلود ها", "برترین ها"], ["نظرات", "حمایت از ما"]],
        "selectedItems": [],
    },
    "جستجوی پیشرفته": {
        "name": "جستجوی پیشرفته",
        "type": "level",
        "title": "از دکمه های زیر جهت فیلتر نتایج استفاده کنید",
        "nxt": advanceSearchItems,
        "keyboard": splitButtons(advanceSearchItems, 2, False),
        "selectedItems": [],
        "pre_level": "خانه",
    },
    advanceSearchItems[1]: {
        "name": "genres",
        "type": "selection",
        "title": "ژانر های مورد علاقه خود را انتخاب کنید",
        "selections": [*selectionDict["genres"].values()],
        "maxOfselection": len(selectionDict["genres"]),
        "minOfselection": 1,
        "selectedItems": [],
        "keyboard": splitButtons([*selectionDict["genres"].values()], 3, True),
        "pre_level": "جستجوی پیشرفته",
    },
    advanceSearchItems[3]: {
        "name": "release_date",
        "type": "selection",
        "title": "بازه انتشار فیلم را انتخاب کنید!",
        "selections": [str(i) for i in range(date.today().year, 1926, -1)],
        "maxOfselection": 2,
        "minOfselection": 2,
        "selectedItems": [],
        "keyboard": splitButtons([str(i) for i in range(date.today().year, 1926, -1)], 6, True),
        "pre_level": "جستجوی پیشرفته",

    },
    advanceSearchItems[5]: {
        "name": "user_rating",
        "type": "selection",
        "title": "بازه امتیاز فیلم را انتخاب کنید!",
        "selections": [str(i) for i in range(0, 11, 1)],
        "maxOfselection": 2,
        "minOfselection": 2,
        "selectedItems": [],
        "keyboard": splitButtons([str(i) for i in range(0, 11, 1)], 4, True),
        "pre_level": "جستجوی پیشرفته",

    },
    advanceSearchItems[4]: {
        "name": "runtime",
        "type": "selection",
        "title": "بازه زمانی فیلم را انتخاب کنید",
        "selections": [str(i) for i in range(0, 301, 20)],
        "maxOfselection": 2,
        "minOfselection": 2,
        "selectedItems": [],
        "keyboard": splitButtons([str(i) for i in range(0, 301, 20)], 6, True),
        "pre_level": "جستجوی پیشرفته",
    },
    advanceSearchItems[0]: {
        "name": "title_type",
        "type": "selection",
        "title": "نوع فیلم را انتخاب کنید",
        "selections": [*selectionDict["title_type"].values()],
        "maxOfselection": len(selectionDict["title_type"]),
        "minOfselection": 1,
        "selectedItems": [],
        "keyboard": splitButtons([*selectionDict["title_type"].values()], 2, True),
        "pre_level": "جستجوی پیشرفته",
    },
    advanceSearchItems[2]: {
        "name": "title",
        "type": "text",
        "title": "نام فیلم را وارد کنید (انگلیسی یا فینگلیش)",
        "maxOfselection": 50,
        "minOfselection": 1,
        "input": "",
        "keyboard": splitButtons([], 2, True),
        "pre_level": "جستجوی پیشرفته",
    },
    "results": {
        "name": "results",
        "type": "results",
        "title": "لیست فیلم های مورد نظر شما ارسال شد. جهت انتخاب فیلم مورد نظر میتوانید از کلید های زیر و یا از لیست کشویی استفاده کنید",
        "itemsTitle": [],
        "items": [],
        "keyboard": [],
        "pre_level": "جستجوی پیشرفته",
    },
    "showItem": {
        "name": "showItem",
        "type": "showItem",
        "title": "",
        "photo": "",
        "keyboard": [["بازگشت"]],
        "pre_level": "results",
    }

}

# function to manage toggle buttons


def selectedButtons(buttons, selectedButtons):
    newButtons = []
    for row in buttons:
        rowlist = []
        for button in row:
            if button in selectedButtons:
                rowlist.append(button + " ✅")
            else:
                rowlist.append(button)
        newButtons.append(rowlist)
    return newButtons


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['level'] = "خانه"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=levels["خانه"]["title"], reply_markup=ReplyKeyboardMarkup(levels["خانه"]["keyboard"]))

# unction to display the selected filters


def showfilters():
    # TODO ریتینگ درست مزتب نمیشه
    filtersOfTitle["release_date"].sort()
    filtersOfTitle["runtime"].sort()
    filtersOfTitle["user_rating"].sort()
    return "{} جستجو بر اساس: \n\n🎞️ عنوان: {} \n🎭 ژانر ها: {} \n🎥 نوع فیلم: {} \n📅 تاریخ انتشار:از {} تا {} \n⏰ مدت زمان: از {} تا {} \n⭐️ امتیاز: از {} تا {} ".format(
        "🔎", filtersOfTitle["title"] if filtersOfTitle["title"] != "" else "---", " ، ".join(filtersOfTitle["genres"]) if len(filtersOfTitle["genres"]) > 0 else "---", " ، ".join(filtersOfTitle["title_type"]) if len(filtersOfTitle["title_type"]) > 0 else "---", filtersOfTitle["release_date"][0] if len(filtersOfTitle["release_date"]) > 0 else "---", filtersOfTitle["release_date"][1] if len(
            filtersOfTitle["release_date"]) > 0 else "---", filtersOfTitle["runtime"][0] if len(filtersOfTitle["runtime"]) > 0 else "---", filtersOfTitle["runtime"][1] if len(filtersOfTitle["runtime"]) > 0 else "---", filtersOfTitle["user_rating"][0] if len(filtersOfTitle["user_rating"]) > 0 else "---", filtersOfTitle["user_rating"][1] if len(filtersOfTitle["user_rating"]) > 0 else "---"
    )

#  function to display found titles


async def showTitleListMessage(update, context):
    titles = context.user_data['lastSearchResult']
    if len(titles) == 0:
        return False
    text = "نتایج یافت شده طبق درخواست شما: \n\n"
    for i, title in enumerate(titles):
        text += "{}- <pre>{}</pre> \n".format(str(i+1), title.fullTitle)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=constants.ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("نمایش کشویی", switch_inline_query_current_chat="lastSearchList")]]))

# function to display a message, button and picture for the selected level


async def showLevel(levelName, update, context):
    context.user_data['level'] = levelName
    level = levels[levelName]

    if level.get("selectedItems") != None:
        keyboards = selectedButtons(level["keyboard"], level["selectedItems"])
    else:
        keyboards = level["keyboard"]

    text = level["title"]
    if levelName == "جستجوی پیشرفته":
        text = showfilters()
    elif levelName == "results":
        await showTitleListMessage(update, context)

    if level["type"] == "text":
        if level["input"] != "":
            text = "شما قبلا نما {} را وارد کردید در صورت اصلاح نام جدید را وارد کنید".format(
                level["input"])

    if "photo" in level.keys():
        if level["photo"] != "":
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=level["photo"], caption=text, reply_markup=ReplyKeyboardMarkup(keyboards))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardMarkup(keyboards))

# function to handle the levels with the selected method


async def selectionsHandler(item, update, context):
    level = levels[context.user_data['level']]
    items = filtersOfTitle[level["name"]]
    if item in items:
        items.remove(item)
    else:
        if level["maxOfselection"] <= len(items):

            items.pop(0)
        items.append(item)
    filtersOfTitle[level["name"]] = items
    levels[context.user_data['level']]["selectedItems"] = items
    keyboards = selectedButtons(level["keyboard"], items)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="انتخاب شما: \n" + " | ".join(items), reply_markup=ReplyKeyboardMarkup(keyboards))

# function to handle the levels with the text input method


async def textInputHandler(input, update, context):
    level = levels[context.user_data['level']]
    level["input"] = input
    filtersOfTitle["title"] = input
    await context.bot.send_message(chat_id=update.effective_chat.id, text="انتخاب شما: \n" + input, reply_markup=ReplyKeyboardMarkup(level["keyboard"]))

# function to find search results


async def findResult(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="در حال یافتن فیلم های مورد نظر شما هستیم.\n لطفا منتظر بمانید...", reply_markup=ReplyKeyboardMarkup([["لغو"]]))
    filterStr = ""
    if len(filtersOfTitle["release_date"]) > 0:
        years = filtersOfTitle["release_date"]
        years.sort()
        filtersOfTitle["release_date"] = [
            "{}-01-01".format(years[0]), "{}-12-30".format(years[1])]
    for key, value in filtersOfTitle.items():
        if len(value) > 0:
            filterStr += "{}{}={}".format("?" if filterStr == "" else "&", key, value if isinstance(value, str) else ",".join(
                value) if key not in selectionDict.keys() else ",".join(map(lambda x: dict(zip(selectionDict[key].values(), selectionDict[key].keys())).get(x), value)))

    titles = imdb.searchTitles(filterStr)
    keyboard = [["بازگشت"]]
    context.user_data['lastSearchResult'] = []
    if len(titles) > 0:
        context.user_data['lastSearchResult'] = titles
        rowSplit = []
        for title in titles:
            rowSplit.append(title.fullTitle)
            if len(rowSplit) == 1:
                keyboard.append(rowSplit)
                rowSplit = []
        if len(rowSplit) > 0:
            keyboard.append(rowSplit)
        # await context.bot.send_message(chat_id=update.effective_chat.id, text="لیست فیلم های مورد نظر شما . لطفا فیلم مورد نظر را انتخاب کنید.", reply_markup=ReplyKeyboardMarkup(keyboard))
    context.user_data['level'] = "results"
    levels["results"]["itemsTitle"] = list(map(
        lambda title: title.fullTitle, titles))
    levels["results"]["items"] = titles
    levels["results"]["keyboard"] = keyboard
    if (len(titles) > 0) & (context.user_data['level'] == "results"):
        await showLevel("results", update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="نتیجه ای یافت نشد 🤷‍♂️")
        await showLevel("جستجوی پیشرفته", update, context)

# function to handle inline requests


async def inline_query(update, context):
    query = update.inline_query.query
    results = []
    if query == "lastSearchList":
        for i, title in enumerate(context.user_data['lastSearchResult'][:50]):
            results.append(
                InlineQueryResultArticle(
                    str(i),
                    title.title,
                    InputTextMessageContent(title.fullTitle),
                    # description=ts.translate_text(
                    #     title.story, translator="google", to_language="fa"),
                    description=title.story,
                    thumbnail_url=title.cover.replace(
                        ".jpg", "._V1_UX67_CR0,0,67,98_AL_.jpg"),
                )
            )
    await context.bot.answer_inline_query(update.inline_query.id, results)

# function to manage messages


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    level = levels[context.user_data['level']]
    message = update.message.text.replace("✅", "").strip()

    levelType = level["type"]
    if message == "بازگشت":
        match level:
            case "results":
                if context.user_data.get("lastSearchList"):
                    context.user_data["lastSearchList"] = []
        await showLevel(level["pre_level"], update, context)
    elif message == "لغو":
        if levelType not in ["selection", "text", "results"]:
            return False
        match levelType:
            case "selection":
                filtersOfTitle[levels[context.user_data['level']]["name"]] = []
                level["selectedItems"] = []
            case "text":
                filtersOfTitle[levels[context.user_data['level']]["name"]] = ""
                level["selectedItems"] = ""

        if context.user_data['level'] in levels[level["pre_level"]]["selectedItems"]:
            levels[level["pre_level"]
                   ]["selectedItems"].remove(context.user_data['level'])

        await showLevel(level["pre_level"], update, context)
    elif message == "تایید":
        if levelType not in ["selection", "text"]:
            return False
        items = filtersOfTitle[level["name"]]
        if len(items) >= level["minOfselection"] & len(items) <= level["maxOfselection"]:
            levels[level["pre_level"]
                   ]["selectedItems"].append(context.user_data['level'])
            await showLevel(level["pre_level"], update, context)
        else:
            pass

    elif message == advanceSearchItems[6]:
        await findResult(update, context)

    elif levels.get(context.user_data['level']).get("type") == "level":
        if message in levels.get(context.user_data['level']).get("nxt"):
            await showLevel(message, update, context)
    elif levels.get(context.user_data['level']).get("type") == "results":
        if message in levels.get(context.user_data['level']).get("itemsTitle"):
            context.user_data['level'] = "showItem"
            item = list(filter(lambda title: title.fullTitle ==
                        message, levels["results"]["items"]))[0]
            levels["showItem"]["title"] = "{} نام فیلم: {} \n {} تاریخ انتشار: {} \n {} ژانر: {} \n {} مدت زمان: {} \n {} خلاصه داستان: {}".format(
                "🎬", item.title, "📅", item.release_date, "🎭", " ، ".join(map(lambda item: selectionDict["genres"][item.strip()], item.genre.split(","))), "⏱️", item.runtime, "📝", ts.translate_text(item.story, translator="google", to_language="fa"))
            levels["showItem"]["photo"] = item.cover
            await showLevel("showItem", update, context)
    elif levels.get(context.user_data['level']).get("type") == "selection":
        if message in levels.get(context.user_data['level']).get("selections"):
            await selectionsHandler(message, update, context)
    elif levels.get(context.user_data['level']).get("type") == "text":
        await textInputHandler(message, update, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.environ.get('BOT_API')).build()
    start_handler = CommandHandler('start', start)
    message_handelr = MessageHandler(filters.TEXT, message)
    application.add_handler(start_handler)
    application.add_handler(message_handelr)
    application.add_handler(InlineQueryHandler(inline_query))
    application.run_polling()
