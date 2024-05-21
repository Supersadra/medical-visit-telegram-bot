import psycopg2
import pandas as pd
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from persiantools.jdatetime import JalaliDate

def find_doctors(section,doctors_dict):
    doctors_list = []
    for doctor, details in doctors_dict.items():
        if section == details[1]:
            doctors_list.append(doctor)
    return doctors_list

def show_doctor_results(doctors,doctors_dict):
    messages = []
    for doctor in doctors:
        message = f"{doctors.index(doctor)+1}. {doctor}\nکد نظام پزشکی:{doctors_dict[doctor][0]}\nتخصص:{doctors_dict[doctor][2]}\nشیفت ها:{' , '.join(doctors_dict[doctor][3])}"
        messages.append(message)
    return '\n\n'.join(messages)

def show_times_results(times_lst):
    messages = []
    for time in times_lst:
        combined = datetime.combine(time[5],time[4])
        approximate_visit_time = approx_hour(time[7],combined)
        
        message = f"{times_lst.index(time)+1}. روز هفته: {time[2]}\nشیفت: {time[3]}\nساعت: {str(approximate_visit_time).split(' ')[1]}\nتاریخ: {time[5]}"
        messages.append(message)
    return '\n\n'.join(messages)

def show_myvisits_results(visits,ordered=False):
    messages = []
    for visit in visits:
        if ordered:
            identifier = visits.index(visit)+1
            message = f"{identifier}.  کدملی: {visit[2]}\nشماره تلفن: {visit[3]}\nنام پزشک: {visit[4]}\nکلینیک: {visit[5]}\nروز هفته: {visit[7]}\nساعت: {visit[6]}\nتاریخ: {visit[8]}\nیادآور: {visit[10]}"        
        else: 
            identifier = '🟢'
            message = f"{identifier}  کدملی: {visit[2]}\nشماره تلفن: {visit[3]}\nنام پزشک: {visit[4]}\nکلینیک: {visit[5]}\nروز هفته: {visit[7]}\nساعت: {visit[6]}\nتاریخ: {visit[8]}\nیادآور: {visit[10]}"
        messages.append(message)
    return '\n\n'.join(messages)

def ordered_text(text_lst):
    ordered_text = []
    for i in range(len(text_lst)):
        text = f'{i+1}. {text_lst[i]}'
        ordered_text.append(text)
    return ordered_text

def connect_db(database_name,user,host,password,port):
    conn = psycopg2.connect(database = database_name, 
                            user = user, 
                            host = host,
                            password = password,
                            port = port)
    return conn

def approx_hour(visit_count,primary_hour):
    duration = 10
    time_change = pd.DateOffset(minutes = visit_count * duration)
    approximate_visit_time = primary_hour + time_change
    return approximate_visit_time

def main_menu_keyboard():
    # Define the inline keyboard
    keyboard = [
        [InlineKeyboardButton("ایجاد یادآور جدید", callback_data='create')],
        [InlineKeyboardButton("مشاهده یادآورهای ساخته شده", callback_data='see')],
        [InlineKeyboardButton("حذف یادآور", callback_data='remove')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def second_menu_keyboard():
    # Define the inline keyboard
    keyboard = [
        [InlineKeyboardButton('سه ساعت قبل', callback_data='three_hour')],
        [InlineKeyboardButton('یک روز قبل', callback_data='day')],
        [InlineKeyboardButton('یک هفته قبل', callback_data='week')],
        [InlineKeyboardButton('دو هفته قبل', callback_data='two_week')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def set_reminder(selected_visit,time):
    visit_time = datetime.strptime(selected_visit[6],"%H:%M:%S").time()
    visit_date = datetime.strptime(selected_visit[8],"%Y-%m-%d").date()
    # Combine the time and date of the selected visit
    combined = datetime.combine(visit_date,visit_time)
    if time == 'hour':
        time_change = pd.DateOffset(hours = 3)
    elif time == 'day':
        time_change = pd.DateOffset(days = 1)
    elif time == 'one_week':
        time_change = pd.DateOffset(days = 7)
    elif time == 'two_week':
        time_change = pd.DateOffset(days = 14)
    else:
        pass
    
    reminder_time = combined - time_change
    # Convert Hijri Shamsi to Gregorian date
    jalali_date = JalaliDate(reminder_time.year, reminder_time.month, reminder_time.day)
    gregorian_date = jalali_date.to_gregorian()
    # Construct Gregorian datetime object with the same time components
    gregorian_datetime = datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day,
                                reminder_time.hour, reminder_time.minute).strftime("%Y-%m-%d %H:%M")
    # Save the reminder
    conn = connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    print('App connected to database!')
    cur = conn.cursor()
    cur.execute(f"UPDATE public.visits SET reminder = '{gregorian_datetime}' WHERE id={selected_visit[0]}")
    conn.commit()
    
    cur.close()
    conn.close()
    
def get_reminders():
    conn = connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    cur = conn.cursor()

    cur.execute('SELECT * FROM public.visits WHERE reminder IS NOT NULL')
    reminders = cur.fetchall()
    return reminders

    cur.close()
    conn.close()

def delete_reminder(visit_id):
    conn = connect_db("Hospital Database (Sadra Hosseini)",'postgres','a2ba86d2-669b-4bf8-ab7d-1b63a3e1f1db.hsvc.ir',"KzPRmunw4j9hCdlkmXIpOkEzhenL3Jvh",30500)
    cur = conn.cursor()

    cur.execute(f"UPDATE public.visits SET reminder = NULL WHERE id = {visit_id}")
    conn.commit()

    cur.close()
    conn.close()