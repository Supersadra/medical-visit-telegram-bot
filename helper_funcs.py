import psycopg2
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
        message = f"{times_lst.index(time)+1}. روز هفته: {time[2]}\nشیفت: {time[3]}\nساعت: {time[4]}\nتاریخ: {time[5]}"
        messages.append(message)
    return '\n\n'.join(messages)

def show_myvisits_results(visits,ordered=False):
    messages = []
    for visit in visits:
        if ordered:
            identifier = visits.index(visit)+1
            message = f"{identifier}.  کدملی: {visit[2]}\nشماره تلفن: {visit[3]}\nنام پزشک: {visit[4]}\nکلینیک: {visit[5]}\nروز هفته: {visit[7]}\nساعت: {visit[6]}\nتاریخ: {visit[8]}"        
        else: 
            identifier = '🟢'
            message = f"{identifier}  کدملی: {visit[2]}\nشماره تلفن: {visit[3]}\nنام پزشک: {visit[4]}\nکلینیک: {visit[5]}\nروز هفته: {visit[7]}\nساعت: {visit[6]}\nتاریخ: {visit[8]}"
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