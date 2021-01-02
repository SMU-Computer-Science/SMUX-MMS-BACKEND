from events import (
    event_conv_handler, activity_conv_handler,
    menu, event_name, activity_name,
    view_existing_menu, create_new_menu,
    faq_menu, faq1, faq2,
    back_menu, details, edit,
    display_activities, display_events,
    edit_name, edit_date, edit_location, edit_desc,
    edit_name_conv_handler, edit_date_conv_handler,
    edit_location_conv_handler, edit_desc_conv_handler,
    edit_image, edit_image_conv_handler,
    execute_delete, cancel_delete, delete
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from database import db
import pyrebase

#WebHook
PORT = int(os.environ.get('PORT', '5000'))

#Security
def security(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You appear to be using an account not associated with any of the SMUX EXCOs, please email smuxbot.2020@gmail.com with your Unique ID if you believe this is a mistake. \n\n Your Unique ID is: " + str(update.effective_chat.id))

list_of_exco = []
user = db.child('EXCO').get().val()
for uid in user.values():
    list_of_exco.append(uid)
security_handler = MessageHandler(~Filters.chat(chat_id=list_of_exco), security)

#Token
load_dotenv('.env')
updater = Updater(token=os.getenv('SMUX_EXCO_BOT_TOKEN'), use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(security_handler)

#Start
def start(update, context):
    valid_user = False
    for user in list_of_exco:
        if (update.effective_chat.id == user):
            valid_user = True
    if (valid_user):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to SMUX's Membership Management System, You may begin accessing your account via /menu. For more information regarding functionalities, please use /faq.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You appear to be using an account not associated with any of the SMUX EXCOs, please email smuxbot.2020@gmail.com with your Unique ID if you believe this is a mistake. \n\n Your Unique ID is: " + str(update.effective_chat.id))

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(event_conv_handler)
dispatcher.add_handler(activity_conv_handler)
dispatcher.add_handler(edit_name_conv_handler)
dispatcher.add_handler(edit_date_conv_handler)
dispatcher.add_handler(edit_location_conv_handler)
dispatcher.add_handler(edit_desc_conv_handler)
dispatcher.add_handler(edit_image_conv_handler)

#Menu CallBacks
updater.dispatcher.add_handler(CommandHandler('menu', menu))
updater.dispatcher.add_handler(CallbackQueryHandler(back_menu, pattern='callback_menu'))
updater.dispatcher.add_handler(CallbackQueryHandler(view_existing_menu, pattern='callback_view_existing'))
updater.dispatcher.add_handler(CallbackQueryHandler(create_new_menu, pattern='callback_create_new'))
updater.dispatcher.add_handler(CallbackQueryHandler(faq_menu, pattern='callback_faq'))
updater.dispatcher.add_handler(CallbackQueryHandler(faq1, pattern='faq1'))
updater.dispatcher.add_handler(CallbackQueryHandler(faq2, pattern='faq2'))
updater.dispatcher.add_handler(CallbackQueryHandler(event_name, pattern='callback_events'))
updater.dispatcher.add_handler(CallbackQueryHandler(activity_name, pattern='callback_activities'))
updater.dispatcher.add_handler(CallbackQueryHandler(display_events, pattern='callback_view_events'))
updater.dispatcher.add_handler(CallbackQueryHandler(display_activities, pattern='callback_view_activities'))
updater.dispatcher.add_handler(CallbackQueryHandler(edit_name, pattern='callback_name'))
updater.dispatcher.add_handler(CallbackQueryHandler(edit_date, pattern='callback_date'))
updater.dispatcher.add_handler(CallbackQueryHandler(edit_location, pattern='callback_location'))
updater.dispatcher.add_handler(CallbackQueryHandler(edit_desc, pattern='callback_desc'))
updater.dispatcher.add_handler(CallbackQueryHandler(edit_image, pattern='callback_image'))
updater.dispatcher.add_handler(CallbackQueryHandler(execute_delete, pattern='callback_delete'))
updater.dispatcher.add_handler(CallbackQueryHandler(cancel_delete, pattern='callback_no_delete'))

#View existing events/activities
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^(/details_[\d]+)$'), details))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^(/edit_[\d]+)$'), edit))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^(/delete_[\d]+)$'), delete))

updater.start_webhook(listen="0.0.0.0",
                       port=PORT,
                       url_path="SMUX_EXCO_BOT_TOKEN")
updater.bot.setWebhook('https://smux-mms-backend.herokuapp.com/' + "SMUX_EXCO_BOT_TOKEN")
updater.idle()