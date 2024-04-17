def find_doctors(section,doctors_dict):
    doctors_list = []
    for doctor, details in doctors_dict.items():
        if section == details[1]:
            doctors_list.append(doctor)
    return doctors_list

def show_results(doctors,doctors_dict):
    messages = []
    for doctor in doctors:
        message = f"{doctors.index(doctor)+1}. {doctor}\nکد نظام پزشکی:{doctors_dict[doctor][0]}\nتخصص:{doctors_dict[doctor][2]}\nشیفت ها:{' , '.join(doctors_dict[doctor][3])}"

        messages.append(message)
    return '\n\n'.join(messages)

def empty_cell(excel_sheet):
    n = 2
    while True:
        cell_obj = excel_sheet.cell(row = n, column = 1)
        if cell_obj.value == None:
            return n
            break
        else:
            n += 1

def ordered_text(text_lst):
    ordered_text = []
    for i in range(len(text_lst)):
        text = f'{i+1}. {text_lst[i]}'
        ordered_text.append(text)
    return ordered_text
