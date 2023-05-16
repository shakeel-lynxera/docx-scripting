import json
import mysql.connector

def configure_db():
    HOST = ''
    USER = ''
    PASSWORD = ''
    DATABASE = ''
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database = DATABASE
        )
    mycursor = db.cursor()
    return db, mycursor


def load_database(json_file):
    stim_d = { "images": [{ "image": "engenn1le01ob01re2img01.jpg", "time": "0", "id": 0, "text": "" }, { "image": "engenn1le01ob01re2img01.jpg", "time": "100", "id": 1, "text": "<span class=\"strong\">Bill</span>: Good morning, Miss Smith. My name is Bill.<br />\n<span class=\"strong\">Miss Smith</span>: Good morning, Bill. <br />" }, { "image": "engenn1le01ob01re2img02.jpg", "time": "7000", "id": 2, "text": "<span class=\"strong\">Angela</span>: Good afternoon, Kenji. <br />\n<span class=\"strong\">Kenji</span>: Good afternoon to you too, Angela. <br" }, { "image": "engenn1le01ob01re2img03.jpg", "time": "13000", "id": 3, "text": "<span class=\"strong\">Dad</span>: Hey, Jenny.<br />\n<span class=\"strong\">Jenny</span>: Hi, Dad." }, { "image": "engenn1le01ob01re2img04.jpg", "time": "19000", "id": 4, "text": "<span class=\"strong\">Alan</span>: George!<br />\n<span class=\"strong\">George</span>: What's up, Alan!" }, { "image": "engenn1le01ob01re2img05.jpg", "time": "25000", "id": 5, "text": "<span class=\"strong\">Receptionist</span>: Good morning, Tech City.<br />\n<span class=\"strong\">Caller</span>: Hello." }, { "image": "engenn1le01ob01re2img06.jpg", "time": "35000", "id": 6, "text": "<span class=\"strong\">Amy</span>: Good night, Carly. See you tomorrow." }], "audiosrc": "7225_mainstimaudaud2", "coverimg": "engenn1le01ob01re2img01.jpg" }
    text_text = "TEXT-TEXT"
    text_images = "TEXT-IMAGE"
    text_audio = "TEXT-AUDIO"
    images_text = "IMAGE-TEXT"
    images_audio = "IMAGE-AUDIO"
    audio_text = "AUDIO-TEXT"
    audio_images = "AUDIO-IMAGE"
    db_question_type = ""

    try:
        db, mycursor = configure_db()
    except Exception as e:
        print(e)
        return False
    with open(('export-files/'+json_file), 'r') as j:
        json_data = json.load(j)
        level = json_data['level']
        score = json_data['sco']
        unit = json_data['unit']
        title = json_data['title']
        exercise = json_data['exercises']
        y = 1
        mycursor.execute('TRUNCATE studyapp.levels')
        mycursor.execute('TRUNCATE studyapp.level_units')
        mycursor.execute('TRUNCATE studyapp.level_units_lessons')
        mycursor.execute('TRUNCATE studyapp.lesson_questions')
        mycursor.execute('TRUNCATE studyapp.lesson_question_responses')

        try:
            sql = """INSERT INTO levels (title, sort_order, description, score, status, is_active) VALUES (%s,%s,%s,%s,%s,%s)"""
            val = ('Level'+' '+f'{level}', 0,'null', '0', 'null', 0)
            mycursor.execute(sql, val)
            db.commit()
            level_id = (mycursor.lastrowid)
            sql = """INSERT INTO level_units (level_id, title, sort_order, description, score, status, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            val = ( level_id, 'Unit'+' '+f'{unit}', 0, 'null', '0', 'null', 0)
            mycursor.execute(sql, val)
            db.commit()
            unit_id = (mycursor.lastrowid)
        except Exception as e:
            print(e)

        qs_counter = 1
        for i in exercise:
                try:
                    if i['type'] == 'DMC':
                        for lenes in i['data']:
                            sql = """INSERT INTO level_units_lessons (unit_id, sort_order,title, description, score, status, stim_data, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                            val = ( unit, qs_counter, 'Lesson '+str(qs_counter), "null", '0', 'null', json.dumps(stim_d), 1)
                            mycursor.execute(sql, val)
                            db.commit()
                            level_units_lession_id = (mycursor.lastrowid)
                            qs_counter = qs_counter + 1

                        count_qs_sort = 1
                        for ques in i['questions']:
                            res_question = len(ques['responses'])
                            q_type = ques['data'][0]['type']
                            q_content = ques['data'][0]['content']
                            q_res_type = ques['responses'][0]['type']
                            q_res_content = ques['responses'][0]['content']
                            q_res_is_correct = ques['responses'][0]['correct']

                            if q_type.upper()+'-'+q_res_type.upper() == text_text:
                                db_question_type = text_text

                            elif q_type.upper()+'-'+q_res_type.upper() == text_images:
                                db_question_type = str(text_images+"S")

                            elif q_type.upper()+'-'+q_res_type.upper() == text_audio:
                                db_question_type = text_audio

                            elif q_type.upper()+'-'+q_res_type.upper() == images_text:
                                db_question_type = images_text

                            elif q_type.upper()+'-'+q_res_type.upper() == images_audio:
                                db_question_type = images_audio

                            elif q_type.upper()+'-'+q_res_type.upper() == audio_text:
                                db_question_type = audio_text

                            elif q_type.upper()+'-'+q_res_type.upper() == audio_images:
                                db_question_type = audio_images
                            else:
                                continue

                            if q_type == 'text':
                                q_title = ques['data'][0]['content']
                                q_content = 'null'
                            elif q_type == 'image':
                                q_title = ques['data'][0]['content'].split('.')[0].capitalize()
                                q_content = ques['data'][0]['content']
                            else:
                                q_title =str('play').capitalize()
                                q_content = ques['data'][0]['content']

                            sql = """INSERT INTO lesson_questions (
                                    lesson_id, question, question_type, 
                                    question_title, question_content, 
                                    response_count, sort_order, score, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                            val = (level_units_lession_id, 'null', db_question_type, q_title, q_content, res_question, count_qs_sort, 0, 0)
                            mycursor.execute(sql, val)
                            db.commit()
                            ques_id = (mycursor.lastrowid)
                            count_qs_sort+=1

                            count_response = 1
                            for dat in ques['responses']:
                                rest = dat['type']
                                res_content = dat['content']
                                if rest == 'text':
                                    if res_content.isupper():
                                        res_type = 'BIG-TEXT'
                                    else:
                                        res_type ="TEXT"
                                else:
                                    res_type = rest.upper()

                                is_correct = dat['correct']
                                if is_correct:
                                    is_correct = 1
                                else:
                                    is_correct = 0
                                sql = """INSERT INTO lesson_question_responses (
                                lesson_id, question_id, 
                                sort_order, response_type,
                                response_content, response_content_label, 
                                is_correct, is_selected ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                                val = (level_units_lession_id, ques_id , count_response, res_type, res_content , 'null', is_correct, 0)
                                mycursor.execute(sql, val)
                                db.commit()
                                count_response+=1

                except Exception as e:
                    print(e)
    return True
