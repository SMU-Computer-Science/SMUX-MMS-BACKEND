from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)
from database import db, storage
from logger import logger
import re

userinfo = {
    "name" : "",
    "date" : "",
    "location" : "",
    "description" : "",
}

def menu(update, context):
    update.message.reply_text(text=main_menu_message(),
                            reply_markup=main_menu_keyboard())

def back_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=main_menu_message(),
                            reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton("View Existing", callback_data='callback_view_existing')],
    [InlineKeyboardButton("Create New", callback_data='callback_create_new')],
    [InlineKeyboardButton("FAQ", callback_data='callback_faq')]]
    return InlineKeyboardMarkup(keyboard)

def main_menu_message():
    return 'Welcome to the Main Menu. You may create activities and events here or check for existing information.'

#Create New Menu
def create_new_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=create_new_menu_message(), reply_markup=create_new_menu_keyboard())

def create_new_menu_keyboard():
    keyboard = [[InlineKeyboardButton("New Activity", callback_data='callback_activities')],
    [InlineKeyboardButton("New Event", callback_data='callback_events')],
    [InlineKeyboardButton("Back", callback_data='callback_menu')]]
    return InlineKeyboardMarkup(keyboard)

def create_new_menu_message():
    return 'What would you like to create?'

#View Existing Menu
def view_existing_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=view_existing_menu_message(), reply_markup=view_existing_menu_keyboard())

def view_existing_menu_keyboard():
    keyboard = [[InlineKeyboardButton("View Activities", callback_data='callback_view_activities')],
    [InlineKeyboardButton("View Events", callback_data='callback_view_events')],
    [InlineKeyboardButton("Back", callback_data='callback_menu')]]
    return InlineKeyboardMarkup(keyboard)

def view_existing_menu_message():
    return 'Which existing activity/event would you like to view?'

#FAQ Menu
def faq_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=faq_menu_message(), reply_markup=faq_menu_keyboard())

def faq_menu_keyboard():
    keyboard = [[InlineKeyboardButton("How do I create an activity/event?", callback_data='faq1')],
    [InlineKeyboardButton("How do I view created activities/events and registrations?", callback_data='faq2')],
    [InlineKeyboardButton("Return to Menu", callback_data='callback_menu')]]
    return InlineKeyboardMarkup(keyboard)

def faq_menu_message():
    return 'Welcome to the FAQ & Documentations'

def faq1(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='How do I create an activity/event?\n\n\
The process is easily done via /menu and \'Create New\'.')

def faq2(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='How do I view created activities/events and registrations?\n\n\
You may view the information via /menu and \'View Existing\'.')


#Create Event    
EVENT_NAME, EVENT_DATE, EVENT_LOCATION, EVENT_DESC, EVENT_PHOTO = range(5)

def create_event(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter event name. You can exit this feature anytime by using the /cancel command.'
    )
    
    return EVENT_NAME
 
def event_name(update, context):
    name_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = name_v + ' has been created.')
    update.message.reply_text(
        'Please input date of event in the following format: YYYY-MM-DD <SPACE> HH:MM.'
    )

    userinfo["name"] = str(name_v)
    
 
    return EVENT_DATE

def event_date(update, context):
    date_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your event will begin at ' + date_v + '.')
    update.message.reply_text(
        'Please enter the event venue.'
    )

    userinfo["date"] = str(date_v)

    return EVENT_LOCATION

def event_location(update, context):
    location_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your event will be held at ' + location_v + '.')
    update.message.reply_text(
        'Please include an event description, you may add the time period of it lasts longer than a day.'
    )
    
    userinfo["location"] = str(location_v)
    
 
    return EVENT_DESC

def event_desc(update, context):
    desc_v = update.message.text
    
    userinfo["description"] = str(desc_v)

    str_code = hash(userinfo["name"] + userinfo["date"]) % 10**8

    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }

    db.child("Events").child(str_code).set(data_db_new)

    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your description has been recorded.')
    update.message.reply_text(
        '(OPTIONAL) Please attach an image or marketing material if available/relevant. Otherwise, you may /skip to complete the event creation process.'
    )
 
    return EVENT_PHOTO
 
def event_photo(update, context):
    photo_file = update.message.photo[-1].get_file()    
    photo_file.download("image.jpg")

    path_on_cloud = 'images/events/' + userinfo["name"] + '.jpg'
    storage.child(path_on_cloud).put("image.jpg")

    update.message.reply_text('Thank you! The event details have been recorded.')
 
    return ConversationHandler.END
 
def event_skip_photo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'You have not added a photo for the event. If you wish to do so in the future, please do so via the edit menu.')
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The event details have been recorded.')

    return ConversationHandler.END
 
def event_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the event creation process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

event_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_event, pattern='callback_events')],
        states={
            EVENT_NAME: [
                MessageHandler(Filters.text & ~Filters.command, event_name)
            ],
            EVENT_DATE: [
                MessageHandler(Filters.regex('[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]'), event_date)
            ],
            EVENT_LOCATION: [ 
                MessageHandler(Filters.text & ~Filters.command, event_location)
            ],
            EVENT_DESC: [
                MessageHandler(Filters.text & ~Filters.command, event_desc),
            ],
            EVENT_PHOTO: [
                MessageHandler(Filters.photo, event_photo),
                CommandHandler('skip', event_skip_photo),
            ],
        },
        fallbacks=[CommandHandler('cancel', event_cancel)],
    )

#Create Activities
ACTIVITY_NAME, ACTIVITY_DATE, ACTIVITY_LOCATION, ACTIVITY_DESC, ACTIVITY_PHOTO = range(5)

def create_activity(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter activity name. You can exit this feature anytime by using the /cancel command.'
    )
    
    return ACTIVITY_NAME
 
def activity_name(update, context):
    name_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = name_v + ' has been created.')
    update.message.reply_text(
        'Please input date of activity in the following format: YYYY-MM-DD <SPACE> HH:MM.'
    )

    userinfo["name"] = str(name_v)
    
 
    return ACTIVITY_DATE

def activity_date(update, context):
    date_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your activity will begin at ' + date_v + '.')
    update.message.reply_text(
        'Please enter the activity venue.'
    )

    userinfo["date"] = str(date_v)

    return ACTIVITY_LOCATION

def activity_location(update, context):
    location_v = update.message.text
    
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your activity will be held at ' + location_v + '.')
    update.message.reply_text(
        'Please include an activity description, you may add the time period of it lasts longer than a day.'
    )
    
    userinfo["location"] = str(location_v)
    
 
    return ACTIVITY_DESC

def activity_desc(update, context):
    desc_v = update.message.text
    
    userinfo["description"] = str(desc_v)

    str_code = hash(userinfo["name"] + userinfo["date"]) % 10**8

    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }

    db.child("Activities").child(str_code).set(data_db_new)

    context.bot.send_message(chat_id=update.effective_chat.id, text = 'Your description has been recorded.')
    update.message.reply_text(
        '(OPTIONAL) Please attach an image or marketing material if available/relevant. Otherwise, you may /skip to complete the activity creation process.'
    )
 
    return ACTIVITY_PHOTO
 
def activity_photo(update, context):
    photo_file = update.message.photo[-1].get_file()    
    photo_file.download("image.jpg")

    path_on_cloud = 'images/activities/' + userinfo["name"] + '.jpg'
    storage.child(path_on_cloud).put("image.jpg")

    update.message.reply_text('Thank you! The activity details have been recorded.')
 
    return ConversationHandler.END
 
def activity_skip_photo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'You have not added a photo for the activity. If you wish to do so in the future, please do so via the edit menu.')
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The activity details have been recorded.')

    return ConversationHandler.END
 
def activity_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the event creation process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

activity_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_activity, pattern='callback_activities')],
        states={
            ACTIVITY_NAME: [
                MessageHandler(Filters.text & ~Filters.command, activity_name)
            ],
            ACTIVITY_DATE: [
                MessageHandler(Filters.regex('[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]'), activity_date)
            ],
            ACTIVITY_LOCATION: [ 
                MessageHandler(Filters.text & ~Filters.command, activity_location)
            ],
            ACTIVITY_DESC: [
                MessageHandler(Filters.text & ~Filters.command, activity_desc),
            ],
            ACTIVITY_PHOTO: [
                MessageHandler(Filters.photo, activity_photo),
                CommandHandler('skip', activity_skip_photo),
            ],
        },
        fallbacks=[CommandHandler('cancel', activity_cancel)],
    )

#################################################################################################

def display_activities(update, context):
    output = ""
    activities_dict = db.child("Activities").get().val()
    if not activities_dict:
        context.bot.send_message(chat_id=update.effective_chat.id, text='There are currently no upcoming activities.')
    else:
        for event_id in activities_dict.keys():
            output += f"{activities_dict[event_id]['Name']} | /details_{event_id}\n"
            output += f"Date/Time: {activities_dict[event_id]['Date']}\n"
            output += f"Location: {activities_dict[event_id]['Location']}\n"
            output += "\n\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)


def display_events(update, context):
    output = ""
    events_dict = db.child("Events").get().val()
    if not events_dict:
        context.bot.send_message(chat_id=update.effective_chat.id, text='There are currently no upcoming events.')
    else:
        for event_id in events_dict.keys():
            output += f"{events_dict[event_id]['Name']} | /details_{event_id}\n"
            output += f"Date/Time: {events_dict[event_id]['Date']}\n"
            output += f"Location: {events_dict[event_id]['Location']}\n"
            output += "\n\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)


def details(update, context):
    word = str(update.message.text)
    global event_id
    event_id = word.replace('/details_', '')
    photo_folder = "activities/"
    event = db.child("Activities").child(event_id).get().val()
    if not event: #if id not found, search in events
        event =  db.child("Events").child(event_id).get().val()
        photo_folder = "events/"
    
    count = 1
    output = ""
    output += f"{event['Name']}\n"
    output += f"Date/Time: {event['Date']}\n"
    output += f"Location: {event['Location']}\n"
    output += f"Description: {event['Description']}\n\n"
    output += f"Participants:\n"
    ppl_list = db.child("Events").child(event_id).child("Participants").get().val()
    if ppl_list is None:
        output += "There are currently no participants registered."
    else:
        for users in ppl_list:
            tele_h = db.child("Users").child(users).child("Personal Particulars").child("Self").child("telehandle").get().val()
            output += f"{count}. @{tele_h}\n"
            count += 1
    output += "\n\n"
    output += f"Edit the event: /edit_{event_id}\n"
    output += "\n"
    output += f"Delete the event: /delete_{event_id}\n"
    output += "\n\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    storage.child("images/" + photo_folder + event['Name'] + ".jpg").download("edm.jpg")
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('edm.jpg', 'rb'))


def edit(update, context):
    word = str(update.message.text)
    event_id = word.replace('/edit_', '')
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"
    update.message.reply_text(text=edit_menu_message(update, context), reply_markup=edit_menu_keyboard())

def edit_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Name", callback_data='callback_name'),
    InlineKeyboardButton("Date", callback_data='callback_date')],
    [InlineKeyboardButton("Location", callback_data='callback_location')],
    [InlineKeyboardButton("Description", callback_data='callback_desc')],
    [InlineKeyboardButton("Image", callback_data='callback_image')]]
    return InlineKeyboardMarkup(keyboard)

def edit_menu_message(update, context):
    word = str(update.message.text)
    global event_id
    event_id = word.replace('/edit_', '')
    event_type = "Activities"
    global event
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"

    output = ""
    output += f"Name:{event['Name']}\n"
    output += f"Date: {event['Date']}\n"
    output += f"Location: {event['Location']}\n"
    output += f"Description: {event['Description']}\n\n"
    output += f"What would you like to edit?"
    return output

#Edit Name
EDIT_NAME = range(1)

def edit_name(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter a new event/activity name. You can exit this feature anytime by using the /cancel command.'
    )

    return EDIT_NAME
 
def submit_name_edit(update, context):
    name_v = update.message.text

    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"

    userinfo["name"] = str(name_v)
    userinfo["date"] = event['Date']
    userinfo["location"] = event['Location']
    userinfo["description"] = event['Description']
    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }
    db.child(event_type).child(event_id).update(data_db_new)
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The event name has been updated to ' + name_v + '.')

    return ConversationHandler.END
 
def edit_name_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the edit process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

edit_name_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_name, pattern='callback_name')],
        states={
            EDIT_NAME: [
                MessageHandler(Filters.text & ~Filters.command, submit_name_edit)
            ],
        },
        fallbacks=[CommandHandler('cancel', edit_name_cancel)],
    )

#Edit Date
EDIT_DATE = range(1)

def edit_date(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter a new event/activity date. You can exit this feature anytime by using the /cancel command.'
    )
    
    return EDIT_DATE
 
def submit_date_edit(update, context):
    date_v = update.message.text
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"

    userinfo["name"] = event['Name']
    userinfo["date"] = str(date_v)
    userinfo["location"] = event['Location']
    userinfo["description"] = event['Description']
    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }
    db.child(event_type).child(event_id).update(data_db_new)
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The event date has been updated to ' + date_v + '.')

    return ConversationHandler.END
 
def edit_date_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the edit process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

edit_date_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_date, pattern='callback_date')],
        states={
            EDIT_DATE: [
                MessageHandler(Filters.regex('[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]'), submit_date_edit)
            ],
        },
        fallbacks=[CommandHandler('cancel', edit_date_cancel)],
    )

#Edit Location
EDIT_LOCATION = range(1)

def edit_location(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter a new event/activity location. You can exit this feature anytime by using the /cancel command.'
    )
    
    return EDIT_DATE
 
def submit_location_edit(update, context):
    location_v = update.message.text
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"

    userinfo["name"] = event['Name']
    userinfo["date"] = event['Date']
    userinfo["location"] = str(location_v)
    userinfo["description"] = event['Description']
    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }
    db.child(event_type).child(event_id).update(data_db_new)
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The event location has been updated to ' + location_v + '.')

    return ConversationHandler.END
 
def edit_location_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the edit process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

edit_location_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_location, pattern='callback_location')],
        states={
            EDIT_LOCATION: [
                MessageHandler(Filters.text & ~Filters.command, submit_location_edit)
            ],
        },
        fallbacks=[CommandHandler('cancel', edit_location_cancel)],
    )

#Edit Description
EDIT_DESC = range(1)

def edit_desc(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please enter a new event/activity description. You can exit this feature anytime by using the /cancel command.'
    )
    
    return EDIT_DESC
 
def submit_desc_edit(update, context):
    desc_v = update.message.text
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event: #if id not found, search in activities
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"

    userinfo["name"] = event['Name']
    userinfo["date"] = event['Date']
    userinfo["location"] = event['Location']
    userinfo["description"] = str(desc_v)
    data_db_new = {
        "Name": userinfo["name"],
        "Date": userinfo["date"],
        "Location": userinfo["location"],
        "Description": userinfo["description"]
    }
    db.child(event_type).child(event_id).update(data_db_new)
    context.bot.send_message(chat_id=update.effective_chat.id, text = 'The event description has been updated to:\n\n ' + desc_v)

    return ConversationHandler.END
 
def edit_desc_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the edit process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

edit_desc_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_desc, pattern='callback_desc')],
        states={
            EDIT_DESC: [
                MessageHandler(Filters.text & ~Filters.command, submit_desc_edit)
            ],
        },
        fallbacks=[CommandHandler('cancel', edit_desc_cancel)],
    )

#Edit Image
EDIT_IMAGE = range(1)

def edit_image(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text =
        'Please submit a new event/activity image. You can exit this feature anytime by using the /cancel command.'
    )
    
    return EDIT_IMAGE
 
def submit_image_edit(update, context):
    image_v = update.message.photo[-1].get_file()
    image_v.download("image.jpg")
    photo_folder = "activities/"
    event = db.child("Activities").child(event_id).get().val()
    if not event: #if id not found, search in events
        event =  db.child("Events").child(event_id).get().val()
        photo_folder = "events/"
    path_on_cloud = 'images/' + photo_folder + event['Name'] + '.jpg'
    storage.child(path_on_cloud).put("image.jpg")

    update.message.reply_text('Thank you! The image has been updated accordingly.')

    return ConversationHandler.END
 
def edit_image_cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'You have cancelled the edit process. Please use /menu if you wish to repeat.'
    )
 
    return ConversationHandler.END

edit_image_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_image, pattern='callback_image')],
        states={
            EDIT_IMAGE: [
                MessageHandler(Filters.photo, submit_image_edit)
            ],
        },
        fallbacks=[CommandHandler('cancel', edit_image_cancel)],
    )

def delete(update, context):
    word = str(update.message.text)
    event_id = word.replace('/delete_', '')
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event:
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"
    update.message.reply_text(text=delete_menu_message(), reply_markup=delete_menu_keyboard())

def delete_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Yes", callback_data='callback_delete'),
    InlineKeyboardButton("No", callback_data='callback_no_delete')]]
    return InlineKeyboardMarkup(keyboard)

def delete_menu_message():
    return 'You are about to delete the above entry, are you sure?'

def execute_delete(update, context):
    event_type = "Activities"
    event = db.child(event_type).child(event_id).get().val()
    if not event:
        event =  db.child("Events").child(event_id).get().val()
        event_type = "Events"
    db.child(event_type).child(event_id).remove()
    context.bot.send_message(chat_id=update.effective_chat.id, text='The entry has been deleted successfully.')

def cancel_delete(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='You have cancelled the delete request.')