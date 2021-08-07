####
#Clean Porn Dataset
#Tianhao
#2021/7/29
####

import pandas as pd
import datetime
import numpy as np
import xlsxwriter

### Read Categories File
pornhub_categories = pd.read_excel(r'C:\Users\raymo\Documents\GitHub\Callander-Research\Porn database\Data\RAW\PH_gay\Categories.xlsx')

### Read xlsx File
local_path = 'C:/Users/raymo/Documents/GitHub/Callander-Research/Porn database/Data/RAW/PH_gay/' #local path of where the raw data stored
store_path = 'C:/Users/raymo/Documents/GitHub/Callander-Research/Porn database/Data/OUTPUT/' #local path of where the output data stored
file_names = ['2021-03-07.xlsx','2021-03-14.xlsx','2021-03-21.xlsx','2021-03-28.xlsx','2021-04-04.xlsx','2021-04-18.xlsx'
             ,'2021-05-16.xlsx','2021-05-30.xlsx','2021-06-13.xlsx','2021-06-20.xlsx','2021-07-18.xlsx','2021-07-25.xlsx'
             ] #file name

datasets = {}
for file in file_names:
    sample = pd.read_excel(local_path+file,engine=None) #read in files
    datasets[file] = sample

#Series types
#This function convert series into correct types and check any null

def convert_types(file_name, data):
    copy_data = data.copy()

    #extract the viewkeys from pornhub urls

    copy_data["url"] = [i.replace("https://www.pornhub.com/view_video.php?viewkey=","") for i in copy_data["url"]]

    #convert views(str) to int
    copy_data["views"] = copy_data["views"].fillna('0')
    copy_data["views"] = [int(str(i).replace(',' , '')) for i in copy_data["views"]]

    #convert approval to int
    copy_data["approval"] = copy_data["approval"].fillna('0')
    copy_data["approval"] = [int(str(i).replace('%',''))/100 for i in copy_data["approval"]]

    #convert upload_date to date_time
    extract_time_str = file_name.replace(".xlsx","").split("-")
    extract_time = datetime.date(int(extract_time_str[0]),int(extract_time_str[1]),int(extract_time_str[2]))
    upload_time = np.array([])
    for i in copy_data["upload_date"]:
        copy_data["upload_date"] = copy_data["upload_date"].fillna('0 years ago')
        temp = i.split(" ")
        if temp[0] == 'Yesterday':
            upload_time = np.append(upload_time,extract_time- datetime.timedelta(days= 1))
        elif temp[1] == 'week' or temp[1] == 'weeks':
            upload_time = np.append(upload_time,extract_time- datetime.timedelta(days= int(temp[0])*7))
        elif temp[1] == 'month' or temp[1] == 'months':
            upload_time = np.append(upload_time,extract_time- datetime.timedelta(days= int(temp[0])*30))
        elif temp[1] == 'year' or temp[1] == 'years':
            upload_time = np.append(upload_time,extract_time- datetime.timedelta(days= int(temp[0])*365))
        elif temp[1] == 'day' or temp[1] == 'days':
            upload_time = np.append(upload_time,extract_time- datetime.timedelta(days= int(temp[0])*1))
        else:
            upload_time = np.append(upload_time,'')
    copy_data["upload_date"] = upload_time

    #Convert all categories into string and check null
    copy_data["categories"] = [str(i) for i in copy_data["categories"]]

    #convert approval_pos and neg to int
    copy_data["approval_pos"] = copy_data["approval_pos"].fillna('0')
    copy_data["approval_pos"] = [int(str(i).replace('%','').replace('K','000')) for i in copy_data["approval_pos"]]
    copy_data["approval_neg"] = copy_data["approval_neg"].fillna('0')
    copy_data["approval_neg"] = [int(str(i).replace('%','').replace(".0","").replace('K','000')) for i in copy_data["approval_neg"]]

    #Clean Actors Column
    copy_data["actors"] = copy_data["actors"].fillna('')
    copy_data["actors"] = [i.replace("Pornstars: ",'').replace("Suggest ",'').replace("\n ",'')
        .replace("Thank you for your suggestions! Our team is reviewing them!","") for i in copy_data["actors"]]
    copy_data["actors"] = ['NaN' if i == '' else i for i in copy_data["actors"]]

    #clean comment number
    copy_data["comments_number"] = copy_data["comments_number"].fillna('0')
    copy_data["comments_number"] = [int(i.replace('(','').replace(')','')) for i in copy_data["comments_number"]]

    #drop related_videos
    copy_data = copy_data.drop(columns = ["related_videos"])

    #drop videostill_image_alt
    copy_data = copy_data.drop(columns = ["videostill_image_alt"])

    comments_data = modify_comments(copy_data)
    return copy_data,comments_data

# This function create the bag of words for comments
def modify_comments(data):
    new_categories = [i.replace("Categories \n ","").replace(" \n Suggest","") for i in data["categories"]]
    bag = np.array([[]])
    for fullstring in data["categories"]:
        temp = np.array([])
        for substring in pornhub_categories["Categories"]:

            if substring in fullstring:
                temp = np.append(temp, 1)
            elif substring not in fullstring:
                temp = np.append(temp, 0)

        bag = np.append(bag,temp)
    bag = bag.reshape(data["categories"].size,pornhub_categories["Categories"].size)
    bag = pd.DataFrame(bag,index = data["url"] ,columns = pornhub_categories["Categories"])
    return bag

#export modified dataset

for k in datasets.keys():
    modified = convert_types(k,datasets[k])

    #write out excel file
    modified[0].to_excel(store_path+"OUTPUT_" + k,sheet_name = 'Sheet 1')
    modified[1].to_excel(store_path+"OUTPUT_Comments_" + k,sheet_name = 'Sheet 2')
    print("Output for file: ", k, " is successful :) ")
