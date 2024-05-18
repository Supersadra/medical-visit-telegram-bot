from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes, Application
from telegram.ext.filters import MessageFilter
import helper_funcs
import psycopg2
from datetime import datetime
import pandas as pd

# VARIABLES ###############################################################################

clinics_dict = {}
doctors_dict = {}

# Define states
command_visit , command_removevisit = range(2)

############################################################################################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('''
    مراجعه‌کننده عزیز، شما می‌توانید برای تهیه نوبت پزشک موردنظر خود از دستور /visit استفاده کنید.
    
    نکته قابل توجه: این ربات در حال حاضر صرفا برای تست اولیه است و به همین دلیل پایگاه داده مورد استفاده آن بصورت کامل تکمیل نشده است.
    در حال حاضر تنها بخشی از کلینیک‌ها برای تست قابل استفاده هستند.
    ''')
    context.user_data['user_id'] = update.message.from_user.id

async def visit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    ########################## UPDATE VARIABLES ##########################
    # Connect to database
    conn = helper_funcs.connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    print('App connected to database!')
    cur = conn.cursor()
    context.user_data['cursur'] = cur
    context.user_data['connection'] = conn
    
    # Get clinics table from the database
    cur.execute('SELECT clinic FROM public.clinics')
    clinics = cur.fetchall()
    cur.execute('SELECT section FROM public.clinics')
    sections = cur.fetchall()

    for clinic in list(set(clinics)):
        clinics_dict[clinic[0]] = []
        for section in sections:
            clinics_dict[clinic[0]].append(section[0])

    
    # Get doctors table from the database
    cur.execute('SELECT * FROM public.doctors')
    doctors = cur.fetchall()

    for row_index in range(len(doctors)):
        row_lst = list(doctors[row_index])
        doctors_dict[row_lst[0]] = [row_lst[1],row_lst[2],row_lst[3],row_lst[4]]
    
    
    for key in doctors_dict.keys():
        if len(doctors_dict[key][3]) > 3:
            if ',' in list(doctors_dict[key][3]):
                doctors_dict[key][3] = doctors_dict[key][3].split(',')
            elif '،' in list(doctors_dict[key][3]):
                doctors_dict[key][3] = doctors_dict[key][3].split('،')
            else:
                print('Shifts are not correct in doctors database.')
        else:
            shift_lst = []
            shift_lst.append(doctors_dict[key][3])
            doctors_dict[key][3] = shift_lst

    # Get times table from the database
    cur.execute('SELECT * FROM public.times')
    context.user_data['times'] = cur.fetchall()
    
    
    await update.message.reply_text('🩺 فهرست کلینیک‌ها' + f'\n\n{'\n'.join(helper_funcs.ordered_text(list(clinics_dict.keys())))}\n\n' + '✅ شماره کلینیک موردنظر خود را وارد کنید.')
    
    context.user_data['level'] = 1

    return command_visit

async def visit_command_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Visit command for getting visit times
    if context.user_data.get('level') == 1: # Level 1: Select the clinic
        try:
            user_clinic = int(update.message.text)

            if user_clinic-1 in range(len(clinics_dict.keys())):
                selected_clinic = list(clinics_dict.keys())[user_clinic-1]
                await update.message.reply_text(f'💠  بخش‌های {selected_clinic}\n\n' + '\n'.join(helper_funcs.ordered_text(clinics_dict[selected_clinic])) + '\n\n ✅ شماره بخش موردنظر خود را وارد کنید.')
                context.user_data['level'] = 2
                context.user_data['user_choice_level_1'] = selected_clinic
            else:
                await update.message.reply_text('❌ پیام اشتباه! لطفا در وارد کردن شماره کلینیک موردنظر دقت فرمایید.') 
        
        except:
            await update.message.reply_text('❌ پیام اشتباه! لطفا شماره کلینیک موردنظر خود را وارد کنید.')

    elif context.user_data.get('level') == 2: # Level 2: Select the section of clinic
        try:
            user_section = int(update.message.text)

            if user_section-1 in range(len(clinics_dict[context.user_data['user_choice_level_1']])):
                selected_section = clinics_dict[context.user_data['user_choice_level_1']][user_section-1]
                doctors = helper_funcs.find_doctors(selected_section,doctors_dict)
                await update.message.reply_text('👨‍⚕️👩‍⚕️  فهرست پزشکان\n\n' + helper_funcs.show_doctor_results(doctors,doctors_dict) + '\n\n ✅ شماره پزشک و شیفت موردنظر خود را مطابق نمونه وارد کنید.(نمونه متن ارسالی: 2/صبح)')
                context.user_data['level'] = 3
                context.user_data['user_choice_level_2'] = selected_section
                context.user_data['user_doctors'] = doctors
            else:
                await update.message.reply_text('❌ پیام اشتباه! لطفا در وارد کردن شماره بخش موردنظر دقت فرمایید.') 
        
        except:
            await update.message.reply_text('❌ پیام اشتباه! لطفا شماره بخش موردنظر خود را وارد کنید.')
    
    elif context.user_data.get('level') == 3: # Level 3: Select the doctor
        user_doctorandshift = update.message.text.split('/')
        try:
            if int(user_doctorandshift[0])-1 in range(len(context.user_data['user_doctors'])):
                selected_doctor = context.user_data['user_doctors'][int(user_doctorandshift[0])-1]

                if user_doctorandshift[1] in doctors_dict[selected_doctor][3]:
                    times = []
                    for item in context.user_data['times']:
                        if (list(item)[1] == selected_doctor) and (list(item)[3] == user_doctorandshift[1]):
                            times.append(list(item))
                    await update.message.reply_text('💠 نوبت های موجود\n\n'+ helper_funcs.show_times_results(times) +'\n\n✅ شماره نوبت مورد نظر خود را وارد کنید.' )
                    context.user_data['level'] = 4
                    context.user_data['user_choice_level_3'] = times
                    context.user_data['selected_doctor'] = selected_doctor
                else:
                    await update.message.reply_text('☹️ نوبت موردنظر شما برای پزشک انتخاب شده موجود نمی‌باشد.')
            
            else:
                await update.message.reply_text('❌ پیام اشتباه! لطفا در تایپ کردن شماره پزشک موردنظرتان دقت فرمایید.')
        
        except:
            await update.message.reply_text('❌  پیام اشتباه! متن ارسالی را مطابق نمونه داده شده وارد کنید.')                  
    
    elif context.user_data.get('level') == 4: # Level 4: Select the visit time
        try:
            user_time = int(update.message.text)-1     
            if user_time in range(0,len(context.user_data['user_choice_level_3'])):
                if context.user_data['user_choice_level_3'][user_time][6] > context.user_data['user_choice_level_3'][user_time][7]:
                    await update.message.reply_text('''
                    📞🔢 جهت تایید نهایی نوبت، شماره تلفن و کدملی خود را با اعداد انگلیسی وارد کنید.
                    (فرمت ارسال: شماره تلفن/کدملی)
                    ''')
                    selected_time = context.user_data['user_choice_level_3'][user_time]
                    context.user_data['level'] = 5
                    context.user_data['user_choice_level_4'] = selected_time

                else:
                    await update.message.reply_text('☹️ متاسفانه نوبت موردنظر شما در حال حاضر پر است.') 
            else:
                await update.message.reply_text('❌ پیام اشتباه! لطفا در وارد کردن شماره نوبت موردنظر خود دقت فرمایید.') 
        except:
            await update.message.reply_text('❌ پیام اشتباه! لطفا یک شماره به عنوان نوبت موردنظرتان وارد کنید.') 
    
    elif context.user_data.get('level') == 5: # Level 5: Get personal info from user
        user_personal_info = update.message.text.split('/')
        if (str(user_personal_info[0])[0:2] == '09' and len(str(user_personal_info[0])) == 11) and len(str(user_personal_info[1])) == 10:
            
            # Combine the time and date of the selected time
            combined = datetime.combine(context.user_data['user_choice_level_4'][5],context.user_data['user_choice_level_4'][4])
            # Calculate the approximate hour of visitor attendance in hospital
            approximate_visit_time = helper_funcs.approx_hour(context.user_data['user_choice_level_4'][7],combined)

            await update.message.reply_text('✅ درخواست شما جهت تهیه نوبت با این اطلاعات ثبت شد.\n\nکدملی: %s\nشماره تلفن: %s\nنام پزشک: %s\nکلینیک: %s\nروز هفته: %s\nساعت تقریبی حضور: %s\nتاریخ: %s' % (user_personal_info[1],user_personal_info[0],context.user_data['selected_doctor'],context.user_data['user_choice_level_2'],context.user_data['user_choice_level_4'][2],str(approximate_visit_time).split(' ')[1],str(approximate_visit_time).split(' ')[0]))
            
            data_to_save = [update.message.from_user.id, # Telegram ID
                            user_personal_info[1], # National code
                            user_personal_info[0], # Phone number
                            context.user_data['selected_doctor'], # Selected doctor for visit
                            context.user_data['user_choice_level_2'], # Selected clinic(section)
                            str(approximate_visit_time).split(' ')[1], # Visit hour
                            context.user_data['user_choice_level_4'][2], # Visit weekday
                            str(approximate_visit_time).split(' ')[0], # Visit date
                            context.user_data['user_choice_level_4'][0] # Time ID
                            ]
            
            sql_query = 'INSERT INTO public.visits (telegram_id, national_code, phone_number, doctor, section, visit_hour, visit_weekday, visit_date, time_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            context.user_data['cursur'].execute(sql_query,data_to_save)
            
            # Changing visit_count column in times table
            context.user_data['cursur'].execute(f'UPDATE public.times SET visit_count = visit_count+1 WHERE id={context.user_data['user_choice_level_4'][0]}')
            
            # Commit changes
            context.user_data['connection'].commit()

            # Closing the cursur and connection
            context.user_data['cursur'].close()
            context.user_data['connection'].close()

            context.user_data.clear()

        else:
            await update.message.reply_text('❌ .پیام اشتباه! شماره تلفن باید با 09 شروع شود و کدملی هم می بایست 10 رقم باشد. همچنین اعداد باید انگلیسی وارد شده باشند.')
    else:
        pass

    return ConversationHandler.END

async def removevisit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('🔵 با استفاده از این دستور می‌توانید نوبت موردنظر خود را حذف کنید.')
    # Connect to database
    conn = helper_funcs.connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    print('App connected to database!')
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM public.visits')
    visits = cur.fetchall()
    user_id = update.message.from_user.id

    user_visits = []
    for visit in visits:
        if user_id == visit[1]:
            user_visits.append(visit)
    
    if len(user_visits) != 0:
        await update.message.reply_text('💠  نوبت‌های تهیه شده توسط این اکانت تلگرام:\n\n' + helper_funcs.show_myvisits_results(user_visits,True) + '\n\n✅ شماره نوبت یا نوبت های موردنظر خود را جهت لغو کردن وارد کنید. اگر قصد حذف چندین نوبت را دارید، شماره آنها را با اسلش جدا کنید.')
        context.user_data['user_visits'] = user_visits
    else:
        await update.message.reply_text('در حال حاضر نوبتی تهیه نکرده‌اید. ☹️')
    
    # Closing the cursur and connection
    cur.close()
    conn.close()

    return command_removevisit

async def removevisit_command_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Remove visit command for cancelling visits
    entered_indexes = str(update.message.text).split('/')
    valid_indexes = [str(i+1) for i in range(len(context.user_data['user_visits']))]

    if set(entered_indexes).issubset(set(valid_indexes)):
        conn = helper_funcs.connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
        
        for entered_index in entered_indexes:
            selected_visit = context.user_data['user_visits'][int(entered_index)-1]
            
            cur = conn.cursor()
            cur.execute(f'DELETE FROM public.visits WHERE id = {selected_visit[0]}')
            cur.execute(f'UPDATE public.times SET visit_count = visit_count - 1 WHERE id = {selected_visit[9]}')
            conn.commit()
        
        # Closing the cursur and connection + Clearing user data
        cur.close()
        conn.close()
        context.user_data.clear()
        
        await update.message.reply_text('❎ نوبت موردنظر شما با موفقیت لغو شد.')
    else:
        await update.message.reply_text('❌ پیام اشتباه! شماره نوبت وارد شده در فهرست نوبت‌های تهیه شده موجود نمی‌باشد یا محتوای خواسته شده را ارسال نکرده‌اید.')        
    
    return ConversationHandler.END

async def myvisits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('🔵 شما با استفاده از این دستور می‌توانید تمام نوبت‌های تهیه شده توسط این اکانت تلگرام را مشاهده کنید.')
    # Connect to database
    conn = helper_funcs.connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    print('App connected to database!')
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM public.visits')
    visits = cur.fetchall()
    user_id = update.message.from_user.id

    user_visits = []
    for visit in visits:
        if user_id == visit[1]:
            user_visits.append(visit)
    
    if len(user_visits) != 0:
        await update.message.reply_text('💠  نوبت‌های تهیه شده توسط این اکانت تلگرام:\n\n' + helper_funcs.show_myvisits_results(user_visits))
    else:
        await update.message.reply_text('در حال حاضر نوبتی تهیه نکرده‌اید. ☹️')

    # Closing the cursur and connection
    cur.close()
    conn.close()
     
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        # Closing the cursur and connection and resetting variables
        context.user_data['cursur'].close()
        context.user_data['connection'].close()
        context.user_data.clear()
        await update.message.reply_text('❎ فرآیند نوبت‌دهی لغو شد.')
    
    except:
        await update.message.reply_text('☹️ فرآیند نوبت‌دهی‌ای آغاز نشده است که قصد لغو آن را دارید.')

    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('''
    💠 دستورات قابل اجرا:
    
    ⚪ دستور /visit
    تهیه نوبت جدید

    ⚪ دستور /myvisits
    مشاهده نوبت‌های فعال در حال حاضر که توسط این اکانت تلگرام تهیه شده‌اند

    ⚪ دستور /removevisit
    لغو نوبت یا نوبت‌ های تهیه شده

    ⚪ دستور /cancel
    لغو فرآیند نوبت‌دهی (برای زمانی که شما در حال تهیه نوبت هستید)
    
    ''')

def main():
    application = Application.builder().token("7047332494:AAEsLSu5OJqCYQ1VBleQevBqEbOxQ_Sx_B0").build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myvisits", myvisits_command))
    application.add_handler(CommandHandler("help", help_command))

    # Conversation Handler
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('visit', visit_command),
                      CommandHandler('removevisit', removevisit_command)],
        states={
            command_visit: [MessageHandler(filters.TEXT & ~filters.COMMAND, visit_command_process)],
            command_removevisit: [MessageHandler(filters.TEXT & ~filters.COMMAND, removevisit_command_process)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    ))
    


    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()