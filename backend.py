import pandas as pd
import os
import random
import math
""" 
!!DB RELATIONS!!
On the left is a table and on the right are table that need to be updated alongside the one on the left
users: chatbot_sessions, courses_completed,(leaderboard),recommended_courses
chatbot_sessions: n/a
courses_completed: n/a
courses: courses_completed,recommended_courses
equipment: n/a
leaderboard: n/a
profiles: n/a
recommended_courses: n/a
"""

global USERS_FILEPATH
global USER_COLS
global CHATBOT_SESSIONS_FILEPATH
global CHATBOT_SESSIONS_COLS
global COURSES_FILEPATH
global COURSES_COLS
global EQUIPMENT_FILEPATH
global EQUIPMENT_COLS
global LEADERBOARD_FILEPATH
global LEADERBOARD_COLS
global RECOMMENDED_COURSES_FILEPATH
global RECOMMENDED_COURSES_COLS
global COURSES_COMPLETED_FILEPATH
global COURSES_COMPLETED_COLS


datapath = os.path.join(os.getcwd(), "database")

USERS_FILEPATH = os.path.join(datapath, "users.txt")
USER_COLS = ['userID','username','password','AI','dataScience','cloud','security','quantum','fundamentals','webDev','IT','weapon','helmet','chestplate','leggings','boots','inventory','level','exp']

CHATBOT_SESSIONS_FILEPATH = os.path.join(datapath, "chatbot_sessions.txt")
CHATBOT_SESSIONS_COLS = ['sessionID','userID','timestamp','interactionData']

COURSES_FILEPATH = os.path.join(datapath, "courses.txt")
COURSES_COLS = ['courseID','courseName','AI','dataScience','cloud','security','quantum','fundamentals','webDev','IT','exp','equipmentType','url']

EQUIPMENT_FILEPATH = os.path.join(datapath, "equipment.txt")
EQUIPMENT_COLS = ['equipmentName','type']

LEADERBOARD_FILEPATH = os.path.join(datapath, "leaderboard.txt")
LEADERBOARD_COLS = ['leaderboardID','scope','userID']

RECOMMENDED_COURSES_FILEPATH = os.path.join(datapath, "recommended_courses.txt")
RECOMMENDED_COURSES_COLS = ['userID','courseID','completedID']



def readDF(filepath,colNames):
    """Reads in csv files and converts to a pandas dataframe
    
    Args:
        filepath (str): The path to the table in the database
        colNames (list): The names of each column in the specified table
    
    Returns:
        pd.Dataframe: The specified dataframe
    """
    
    df = pd.read_csv(filepath, header=0, names=colNames)
    return df



def writeCSV(df,filepath):
    """Writes the updated dataframe to the CSV files

    Args:
        df (pd.Dataframe): The updated dataframe
        filepath (str): The path to the desired table in the database
    """
    # df = addNewUser(newUser, newPass)
    df.to_csv(filepath, index=False)
    


def userExist(username, password):
    """Checks if the combination of username and password already exists

    Args:
        username (str): The given username of the user
        password (str): The given password of the user
    
    Returns:
        Int: The corresponding userID if it exists and False if it doesn't
    """

    df = readDF(USERS_FILEPATH,USER_COLS)
    user = df['userID'].loc[(df['username'] == username) & (df['password'] == password)]
    if user.empty:
        return False
    return user.squeeze()



def getRecommended(userID):
    """Get all recommended courses and their stats + xp gain

    Args:
        userID (int): The value of the primary key for a record in users table

    Returns:
        responses (array): An array with a dictionary of values to be displayed.
    """
    # Load the courses and recommended courses relations.
    recommedations_df = readDF(RECOMMENDED_COURSES_FILEPATH, RECOMMENDED_COURSES_COLS)
    courses_df = readDF(COURSES_FILEPATH, COURSES_COLS)
    # Initialise the IDs of the recommendations.
    courseIDs = recommedations_df["courseID"].loc[recommedations_df['userID'] == userID]
    responses = []
    # Select if empty.
    if courseIDs.empty or courseIDs.isna().any():
        return responses
    courseIDs = str(courseIDs.squeeze())
    course_list = courseIDs.split("-")
    # Selects if the first value is stored as a float.
    if len(course_list) == 1 and "." in course_list:
        course_list[0] = course_list[0][:-2]
    # Definitely iterates through and collects data to output.
    for courses in course_list:
        course = int(courses)
        name = courses_df["courseName"].loc[courses_df['courseID'] == course].squeeze()
        xp = courses_df["exp"].loc[courses_df['courseID'] == course].squeeze()
        item = courses_df["equipmentType"].loc[courses_df['courseID'] == course].squeeze()
        url = courses_df["url"].loc[courses_df['courseID'] == course].squeeze()
        responses.append({"name": name, "xp": str(xp), "type": item, "url": url, "id":course})
    return responses



def getName(userID):
    """Gets a user's username

    Args:
        userID (int): The value of the primary key for the record
        
    Returns:
        String: The user's username
    """

    df = readDF(USERS_FILEPATH,USER_COLS)
    return df['username'].loc[df['userID'] == userID].squeeze()



def getStats(userID):
    """Gets a user's stats

    Args:
        userID (int): The value of the primary key for the record
        
    Returns:
        dict: A dictionary of the user's stats
    """

    df = readDF(USERS_FILEPATH,USER_COLS)
    user = df.loc[df['userID'] == userID]
    user = user.squeeze()
    stats = {'AI': 0, 'dataScience': 0, 'cloud': 0, 'security': 0, 'quantum': 0, 'fundamentals': 0, 'webDev': 0, 'IT': 0}
    for stat in stats:
        stats[stat] = user[stat]
    return stats



def getLevel(userID):
    """Gets a user's level

    Args:
        userID (int): The value of the primary key for the record
        
    Returns:
        Int: The user's current level
    """

    df = readDF(USERS_FILEPATH,USER_COLS)
    return df['level'].loc[df['userID'] == userID].squeeze()



def getXP(userID):
    """Gets a user's experience value

    Args:
        userID (int): The value of the primary key for the record in users
        
    Returns:
        Int: The user's current experience value
    """

    df = readDF(USERS_FILEPATH,USER_COLS)
    return df['exp'].loc[df['userID'] == userID].squeeze()



def getInventoryItems(userID):
    """Gets a user's inventory and outputs the items present

    Args:
        userID (int): The value of the primary key for the record
    
    Returns:
        list: The names of all items in the user's inventory
    """
    df = readDF(USERS_FILEPATH,USER_COLS)
    inventory_items =  df['inventory'].loc[df['userID'] == userID].squeeze().split("-")
    return inventory_items



def getInventory(userID):
    """Finds the items in an inventory and their equipment type

    Args:
        userID (int): The primary key for the record in the users table

    Returns:
        dict(list): Dictionary with item types where each entry is a list of items
    """
    inventory_items = getInventoryItems(userID)
    inventory_items.remove("No Weapon")
    inventory_items.remove("No Chestplate")
    inventory_items.remove("No Leggings")
    inventory_items.remove("No Helmet")
    inventory_items.remove("No Boots")
    df = readDF(EQUIPMENT_FILEPATH,EQUIPMENT_COLS)
    inventory_dict = {"weapon":[], "helmet":[], "chestplate":[], "leggings":[], "boots":[]}
    for item in inventory_items:
        item_type = df['type'].loc[df['equipmentName'] == item].squeeze()
        inventory_dict[item_type].append(item)
    return inventory_dict

def getEquipment(userID):
    """Gets all of the users equipment in a dictionary

    Args:
        userID (int): The value of the primary key for a record in users

    Returns:
        dict: type-to-name dictionary
    """
    df = readDF(USERS_FILEPATH,USER_COLS)
    row = df.loc[df['userID'] == userID]
    equip_dict = dict()
    equip_dict["weapon"] = row["weapon"].squeeze()
    equip_dict["helmet"] = row["helmet"].squeeze()
    equip_dict["chestplate"] = row["chestplate"].squeeze()
    equip_dict["leggings"] = row["leggings"].squeeze()
    equip_dict["boots"] = row["boots"].squeeze()
    return equip_dict
    
def getRandomItem(userID, itemType):
    """Generates a random item and its type to be given to a user

    Returns:
        tuple(str, str): The name and type of the item being given to the user
    """
    df = readDF(EQUIPMENT_FILEPATH,EQUIPMENT_COLS)
    inventoryItems = getInventoryItems(userID)
    df = df.loc[(df['type'] == itemType) & (~df['equipmentName'].isin(inventoryItems))]
    if not df.empty:
        randomItem = df.sample(n=1)
        return randomItem['equipmentName'].squeeze()
    else:
        return ''


def equipItem(userID, itemName, itemType):
    """Equips a specified item

    Args:
        userID (int): The value of the primary key for a record in users
        itemName (string): The name/id of the item to be equipped
        itemType (string): The type of the item to be equipped
    """
    df = readDF(USERS_FILEPATH,USER_COLS)
    df[itemType].loc[df['userID'] == userID] = itemName
    # index = df[df['userID'] == userID].index[0]
    # df.loc[index, itemType] = itemName
    writeCSV(df,USERS_FILEPATH)
    
    
    
def addNewItem(userID, itemType):
    """Adds a newly obtained item to a users inventory if not already there

    Args:
        userID (int): The value of the primary key for a record in users
        newItemInfo (tuple(str,str)): The name and type of new equipment

    Returns:
        int: 1 for early return, 0 for full completion of subroutine
    """
    df = readDF(USERS_FILEPATH, USER_COLS)
    itemName = getRandomItem(userID, itemType)

    if itemName == '':
        return 0

    # Extract the inventory for the specified userID
    inventory = df.loc[df['userID'] == userID, 'inventory'].squeeze()
    
    # Append the new item to the inventory
    inventory += f"-{itemName}"

    # Update the table with the new inventory
    df.loc[df['userID'] == userID, 'inventory'] = inventory
    
    # Write to database
    writeCSV(df, USERS_FILEPATH)
    return 0 # Flag to signal that function completed successfully
    
    
    
def addCourseStats(userID, courseID):
    """Gives user stats for completing course

    Args:
        userID (int): The value of the primary key for a record in users table
        courseID (int): The value of the primary key for a record in courses table
        
    """
    courses_df = readDF(COURSES_FILEPATH,COURSES_COLS)
    user_df = readDF(USERS_FILEPATH,USER_COLS)

    # List of all values to be updated
    stats = ['AI','dataScience','cloud','security','quantum','fundamentals','webDev','IT','exp']

    # Iterates through all stats and updates them in the dataframe
    for stat in stats:
        current_value = user_df.loc[user_df['userID'] == userID, stat].squeeze()
        integer_to_add = courses_df.loc[courses_df['courseID'] == courseID, stat].squeeze()
        updated_value = current_value + integer_to_add
        user_df.loc[user_df['userID'] == userID, stat] = updated_value
    
    # Updates user's exp value and their level
    while user_df.loc[user_df['userID'] == userID,'exp'].squeeze() >= 100:
       current_level = user_df.loc[user_df['userID'] == userID,'level'].squeeze()
       new_level = current_level + 1
       user_df.loc[user_df['userID'] == userID,'level'] = new_level
       
       current_exp = user_df.loc[user_df['userID'] == userID,'exp'].squeeze()
       new_exp_val = current_exp - 100
       user_df.loc[user_df['userID'] == userID,'exp'] = new_exp_val
       
    writeCSV(user_df, USERS_FILEPATH)



def completeCourse(userID, courseID):
    """Adds course to completed course table. Removes course from recommended

    Args:
        userID (int): The value of the primary key for a record in users table
        courseID (int): The value of the primary key for a record in courses table
    """
    # Loads the df and assigns the recommendations and completed.
    df = readDF(RECOMMENDED_COURSES_FILEPATH, RECOMMENDED_COURSES_COLS)
    courses = df["courseID"].loc[df["userID"] == userID]
    completed_courses = df["completedID"].loc[df["userID"] == userID]
    # Squeezese the course so its a string.
    courses = str(courses.squeeze())
    course_list = courses.split("-")
    # Selects if empty.
    if not (completed_courses.empty or completed_courses.isna().any()):
        completed_courses = str(completed_courses.squeeze())
        completed_list = completed_courses.split("-")
        completed_list.append(str(courseID))
        completed_courses = '-'.join(completed_list)
    else:
        completed_courses = str(courseID)
    course_list.remove(str(courseID))
    courses = '-'.join(course_list)
    df["courseID"].loc[df["userID"] == userID] = courses
    df["completedID"].loc[df["userID"] == userID] = completed_courses

    writeCSV(df, RECOMMENDED_COURSES_FILEPATH)



def addRecommendedCourse(userID, courseID):
    """Adds a recommended course for the user

    Args:
        userID (int): The value of the primary key for a record in users table
        courseID (int): The value of the primary key for a record in courses table
    """
    # Load database and extract the users and the previous recommendations for the user.
    df = readDF(RECOMMENDED_COURSES_FILEPATH, RECOMMENDED_COURSES_COLS)
    # Selects if the user has no recommendations.
    if userID not in df["userID"].values:
        new_user = {"userID": userID, "courseID": str(courseID), "completedID" : ""}  # Assigns the courseid to the user.
        df.loc[len(df)] = new_user
    # Selects if the user already has recommendations.
    else:
        courses = df["courseID"].loc[df["userID"] == userID]
        completed_courses = df["completedID"].loc[df["userID"] == userID]
        flag = False
        if not completed_courses.empty:
            completed_courses = str(completed_courses.squeeze())
            completed_list = completed_courses.split("-")
            if str(courseID) in completed_list:
                flag = True
        if not (courses.empty or courses.isna().any()):
            courses = str(courses.squeeze())
            course_list = courses.split("-")
            # Selects if float is stored.
            if len(course_list) == 1 and "." in course_list:
                course_list[0] = course_list[0][:-2]

            if str(courseID) in course_list:
                flag = True
            # If the flag is still false the course is not in the users history and then can be added.
            if flag == False:
                course_list.append(str(courseID))
                if len(course_list) > 3:
                    del course_list[0]
                courses = '-'.join(course_list)
                df["courseID"].loc[df["userID"] == userID] = courses
        else:
            if flag == False:
                df["courseID"].loc[df["userID"] == userID] = str(courseID)

    
    writeCSV(df, RECOMMENDED_COURSES_FILEPATH)



def addNewCompletedCourse(newCompletionData):
    """Add a new completed course to the courses_completed table

    Args:
        newCompletionData (list): The attribute values for the record

    Returns:
        pd.Dataframe: The updated dataframe with the new completion
    """
    
    df = readDF(COURSES_COMPLETED_FILEPATH,COURSES_COMPLETED_COLS)
    newCompletionID = (max(df['completionID']))+1
    newCompletionData = [newCompletionID]+newCompletionData
    
    newRecord = dict(zip(COURSES_COMPLETED_COLS,newCompletionData))
    new_df = pd.DataFrame([newRecord])
    df = pd.concat([df,new_df], ignore_index=True)
    return df



def addNewUser(newUserData):
    """Adds a new user to the users table in the database

    Args:
        newUserData (list): The attributes values for the record

    Returns:
        pd.Dataframe: The update dataframe with the new user
        int: The value of the primary key for the new user
    """
    
    df = readDF(USERS_FILEPATH,USER_COLS)
    newUserID = (max(df['userID']))+1
    newUserData = [newUserID]+newUserData
    
    newRecord = dict(zip(USER_COLS,newUserData))
    new_df = pd.DataFrame([newRecord])
    df = pd.concat([df, new_df], ignore_index=True)
    return (df, newUserID)
   
   
    
def signUp(username, password):
    """Allows user to signup

    Args:
        username (str): The username of the user being created
        password (str): The password of ther user being created
        
    Returns:
        int: The value of the primary key of the record
    """
    df, userID = addNewUser([username,password,0,0,0,0,0,0,0,0,"No Weapon","No Helmet","No Chestplate","No Leggings","No Boots","No Weapon-No Helmet-No Chestplate-No Leggings-No Boots",1,0])
    writeCSV(df, USERS_FILEPATH)
    return userID




    
    



