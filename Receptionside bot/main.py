from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ContextTypes, Application
from telegram.ext.filters import MessageFilter

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('''
    شما با این ربات می‌توانید اطلاعات مربوط به نوبت‌ها را دریافت و تغییراتی را در فایل های مربوط به آن ثبت کنید.
    در حال حاضر امکانات زیر در اختیار شماست:
    1. دریافت فایل مربوط به وقت‌های نوبت ثبت شده
    2. تغییر فایل مربوط به پزشکان بیمارستان
    3. تغییر فایل مربوط به کلینیک‌ها و بخش‌های مختلف بیمارستان
    ''')

async def send_visits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('Userside bot\\visits.xlsx', 'r') as visits_file:
        await update.message.reply_document(visits_file)


async def get_doctors_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('Userside bot\\doctors.xlsx', 'r') as doctors_file:
        await update.message.reply_document(doctors_file)
    await update.message.reply_text(
    '''
    .اطلاعات فایل جدید اکسل را مانند فایل فرستاده شده وارد کنید.سپس فایل اکسلی را که ساخته‌اید ارسال کنید
    توجه کنید که اسم فایل ارسالی حتما باید doctors.xlsx باشد.
    ''')

async def get_clinics_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('Userside bot\\clinics.xlsx', 'r') as clinics_file:
        await update.message.reply_document(clinics_file)
    await update.message.reply_text(
    '''
    .اطلاعات فایل جدید اکسل را مانند فایل فرستاده شده وارد کنید.سپس فایل اکسلی را که ساخته‌اید ارسال کنید
    توجه کنید که اسم فایل ارسالی حتما باید clinics.xlsx باشد.
    ''')   

async def file_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.document.file_name == 'doctors.xlsx':
        file_id = update.message.document.file_id
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(custom_path=f'Userside bot\\doctors.xlsx')
        await update.message.reply_text('فایل با موفقیت ذخیره شد!')
    
    elif update.message.document.file_name == 'clinics.xlsx':
        file_id = update.message.document.file_id
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(custom_path=f'Userside bot\\clinics.xlsx')
        await update.message.reply_text('فایل با موفقیت ذخیره شد!')        



def main():
    application = Application.builder().token("7103695194:AAHG5e0s9bGwS-03DiirvXOuOau15GMQoDc").build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("changedoctorsinfo", get_doctors_file))
    application.add_handler(CommandHandler("changeclinicsinfo", get_clinics_file))
    application.add_handler(CommandHandler("getvisitsfile", send_visits))

    # Message Handlers
    application.add_handler(MessageHandler(filters.Document.ALL, file_process))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()