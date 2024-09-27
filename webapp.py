from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from backend import *
import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)
app.secret_key = 'R3GOSvdQzavh--Jyg1AJyg'

# The Assistant Credentials.
api_key = 'rBIYB7dMd6d7c9rnEgWtEBZPgznXSeZs8CO1KSI420aJ'
assistant_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/d55febdc-eb9f-44fc-bff4-25e4933161d9'
assistant_id = '4ee1b957-2c16-47da-99f4-50dfada0fdc2'

# Authenticator.
authenticator = IAMAuthenticator(api_key)
# Instance.
assistant = AssistantV2(
    version = '2021-06-14',
    authenticator = authenticator
)
# Service URL.
assistant.set_service_url(assistant_url)

# Arrow symbols: 🡨 🡩 🡪 🡫

global CURRENT_USER
global NEW_USER

CURRENT_USER = None
NEW_USER = None

@app.route('/')
def home():
    return render_template('index.html', nav_items={'':('🡪', 'login')})

@app.route('/login')
def login():
    return render_template('login.html', nav_items={'Sign Up':('🡫', 'signup')})

@app.route('/signup')
def signup():
    return render_template('signup.html', nav_items={'Login':('🡩', 'login')})

@app.route('/create')
def create():
    global NEW_USER
    if not NEW_USER:
        flash(('You need to sign up first before creating a profile', 'danger'))
        return redirect(url_for('signup'))
    return render_template('create.html')

@app.route('/profile')
def profile():
    global CURRENT_USER
    if not CURRENT_USER:
        flash(('You need to login first before accessing SkillsGuild', 'danger'))
        return redirect(url_for('login'))
    stats = getStats(CURRENT_USER)
    level = getLevel(CURRENT_USER)
    exp = getXP(CURRENT_USER)
    name = getName(CURRENT_USER)
    return render_template('profile.html', nav_items={'Find Courses':('🡫', 'chatbot'), 'Equipment':('🡪', 'equipment')}, stats=stats, level=level, exp=exp, name=name)

@app.route('/equipment')
def equipment():
    global CURRENT_USER
    if not CURRENT_USER:
        flash(('You need to login first before accessing SkillsGuild', 'danger'))
        return redirect(url_for('login'))
    name = getName(CURRENT_USER)
    inventory = getInventory(CURRENT_USER)
    equipment = getEquipment(CURRENT_USER)
    return render_template('equipment.html', nav_items={'Profile':('🡨', 'profile'), 'Courses':('🡪', 'courses')}, name=name, inventory=inventory, equipment=equipment)

@app.route('/equip', methods=['POST'])
def equip():
    data = request.json.get('data', '')
    data = request.json
    item_id = data.get('item_id')
    item_type = data.get('item_type')
    if item_id and item_type:
        global CURRENT_USER
        equipItem(CURRENT_USER, item_id, item_type)
        return jsonify({"status": "success", "message": f"Item {item_id} equipped successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "Item ID and Type is required"}), 400

@app.route('/courses')
def courses():
    global CURRENT_USER
    if not CURRENT_USER:
        flash(('You need to login first before accessing SkillsGuild', 'danger'))
        return redirect(url_for('login'))
    courses = getRecommended(CURRENT_USER)
    return render_template('courses.html', nav_items={'Equipment':('🡨', 'equipment')}, courses=courses)

@app.route('/comp', methods=['POST'])
def comp():
    data = request.json.get('data', '')
    data = request.json
    course = data.get('course')
    courseType = data.get('course_type')
    if course:
        global CURRENT_USER
        addCourseStats(CURRENT_USER, course)
        addNewItem(CURRENT_USER, courseType)
        completeCourse(CURRENT_USER, course)
        return jsonify({"status": "success", "message": f"Course {course} successfully completed"}), 200
    else:
        return jsonify({"status": "error", "message": "Course name is required"}), 400

@app.route('/chatbot')
def chatbot():
    global CURRENT_USER
    if not CURRENT_USER:
        flash(('You need to login first before accessing SkillsGuild', 'danger'))
        return redirect(url_for('login'))    
    return render_template('chatbot.html')

@app.route('/recommendations')
def recommendations():
    global CURRENT_USER
    if not CURRENT_USER:
        flash(('You need to login first before accessing SkillsGuild', 'danger'))
        return redirect(url_for('login'))
    
    courses = getRecommended(CURRENT_USER)
    return render_template('recommendations.html', nav_items={'':('🡪', 'profile')}, courses=courses)

@app.route('/trylogin', methods=['POST'])
def trylogin():
    username = request.form['username']
    password = request.form['password']

    user = userExist(username, password)

    if user:
        global CURRENT_USER
        CURRENT_USER = user
        return redirect(url_for('profile'))
    else:
        flash(('Login failed. Check your username and password.', 'danger'))
        return redirect(url_for('login'))

@app.route('/trysignup', methods=['POST'])
def trysignup():
    username = request.form['username']
    password = request.form['password']

    user = userExist(username, password)

    if not user:
        global NEW_USER
        NEW_USER = (username, password)
        return redirect(url_for('create'))
    else:
        flash(('Sign Up failed. An account with these details already exists.', 'danger'))
        return redirect(url_for('signup'))
    
@app.route('/submitprof', methods=['POST'])
def submitprof():
    global CURRENT_USER
    global NEW_USER
    CURRENT_USER = signUp(NEW_USER[0], NEW_USER[1])
    NEW_USER = None
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    global CURRENT_USER
    CURRENT_USER = None
    return redirect(url_for('login'))

@app.route('/endchat')
def endchat():
    print("Chat Ended")
    return redirect(url_for('recommendations'))

@app.route('/session_start', methods=['POST'])
def session_start():
    # Create Service.
    response = assistant.create_session(
        assistant_id=assistant_id
    ).get_result()
    session_id = response['session_id']
    return session_id

# Handles post requests for the chat bot.
@app.route('/assistant_message', methods=['POST'])
def assistant_message():
    # Initiates messages and selects if the post request was made.
    messages = []
    if request.method == 'POST':
        # Localizes arguments.
        user_input = request.form['user_input']
        session_id = request.form['sessionID']
        # Sends the messages and gathers the result.
        response = assistant.message(
            assistant_id=assistant_id,
            session_id=session_id,
            input={
                "message_type": "text",
                "text": user_input
            }
        ).get_result()
        # Appends the users message to the array.
        messages.append({'u_content': user_input})
        # Iterates through the json response and selects the suitable output.
        for each in response['output']['generic']:
            # This is for general messages type (No options provided).
            if each['response_type'] == 'text':
                watson_reply = each['text']
                # Iterate through message and see if course has been recommended.
                courseID_counter = 1
                watson_courses = ["https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/INFORMATION_TECHNOLOGY_(IT)", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/INTERNET_OF_THINGS_-IOT-", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/OPEN_SOURCE_TECHNOLOGY", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/CODING_AND_PROGRAMMING", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/QUANTUM_COMPUTING", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/SCIENCE_AND_TECH", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/USER_EXPERIENCE_(UX)_DESIGN", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/VIRTUAL_REALITY", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/WEB_DEVELOPMENT", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/AI_-ARTIFICIAL_INTELLIGENCE-", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/CLOUD_COMPUTING", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/CYBERSECURITY", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/DATA_SCIENCE_101", "https://students.yourlearning.ibm.com/recommended/aoi/TECHNICAL_SKILLS/EMERGING_TECH_INTRO"]
                for course in watson_courses:
                    if course in watson_reply:
                        global CURRENT_USER
                        # Calls function to append the course recommendation to the user.
                        addRecommendedCourse(CURRENT_USER, courseID_counter)
                    courseID_counter += 1
                # This appends the message to the output.
                messages.append({'b_content':watson_reply})
            # Selects if the response provides options.
            if each['response_type'] == 'option':
                messages.append({"option_flag": "True"})
                counter = 1
                # Iterates through each option.
                for option in each['options']:
                    messages.append({'b_content':option['label']})
                    counter += 1
        
       # Returns the processed message.
        return messages

if __name__ == '__main__':
    app.run(port=8090,debug=True)
