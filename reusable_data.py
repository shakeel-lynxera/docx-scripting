import re


#MAJOR COMPONENTS

#main stimulas
def main_stimulas(tables, j, i):
    try:
        data_list_2 = []
        #get first object
        object = tables[j+1].cell(i+2, 1).text.strip()
        separate_object = object.split("\n")
        type = separate_object[0]
        content = separate_object[1]
        
        data_list_2.append({
            "type": type,
            "content": content
        })
        
        
        object = tables[j+1].cell(i+3, 1).text.strip()
        result = list(filter(lambda x : x != '', object.split('\n')))
        if "Audio" in result[0]:
            type = "Audio"
        content = result[-1]
        data_list_2.append({
            "type": type,
            "content": content
        })
    except Exception as e:
        print('unable to procced main stimulas section, error: ',e)
    return data_list_2
    
#Content - text or Dialogue'
def content_text_dialogue(tables,j,i, data_list_2):
    try:
        content_list = []
        object = tables[j].cell(i, 1).text.strip()
        result = object.split('\n')
        for i in result:
            i=i.strip()
            if i:
                content_list.append({
                    "text" : i,
                    "time" : 100
                })
            else:
                if content_list:
                    data_list_2.append({
                        "type" : "paragraph",
                        "content" : content_list
                    })
                content_list = []
        if content_list:
            data_list_2.append({
                        "type" : "paragraph",
                        "content" : content_list
                    })
    except Exception as e:
        print('unable to procced content or dailogue section, error: ',e)        
    return data_list_2

#MRW
def MRW(tables, j, i):
    data_list_3 = []
    question_list_3 = []
    try:
        img_name = tables[j].cell(i+1, 1).text.strip()
        data_list_3.append({
                "type":"image",
                "content" : img_name
            }
        )
        
        data_list_4 = []
        response_list_4 = []
        try:
            data = tables[j].cell(i+2, 1)
            corrected_answers_list = get_corrected_answers_list(data)
        except Exception as e:
            print('unable to get answers')
        questions = tables[j].cell(i+2, 1).text.strip()
        questions = questions.split('\n')
        total_concate_key_words, response = concate_mrw_question(questions)
        if not response:
            print('something went wrong while concatination MRW questions')
            exit()                
        
        #get images link
        raw_images_links = tables[j].cell(i+3, 1).text.strip()
        raw_images_links = raw_images_links.split('\n')
        get_images_links_list, response = extract_images_links(raw_images_links)
        if not response:
            print('something went wrong while exracting images link for MRW section')
        
        #get audio link
        raw_audio_links = tables[j].cell(i+4, 1).text.strip()
        raw_audio_links = raw_audio_links.split('\n')
        get_audio_links_list, response = extract_audio_links(raw_audio_links)
        if not response:
            print('something went wrong while exracting audio link for MRW section')
        
        for nested_list in total_concate_key_words:
            count_first_index = 0
            for index in nested_list:
                index = index.replace(":","").upper()
                try:
                    list_ = index.split('+')
                    if "IMG" in list_[0] or "AUD" in list_[0]:
                        index = list_[0]
                    else:
                        index = list_[1]
                except Exception as e:
                    pass
                if "IMG" in index.upper():
                    for img_link in get_images_links_list:
                        key_ = img_link['key'].split('.')[0].upper()
                        if index == key_:
                            if count_first_index < 1:
                                data_list_4.append({"type":"image", "content":img_link['value']})
                            else:
                                response_list_4.append({"type":"image", "content":img_link['value'], "correct": False})                                        
                        
                elif "AUD" in index.upper():
                    for audio_link in get_audio_links_list:
                        key_ = audio_link['key'].upper()
                        if key_ == index:
                            if count_first_index < 1:
                                data_list_4.append({"type":"audio", "content":audio_link['value']})
                            else:
                                response_list_4.append({"type":"audio", "content":audio_link['value'], "correct": False})
                else:
                    if not count_first_index < 1:
                        if not "AUD" in index and not "IMG" in index:
                            # if "aud" in response_list_4[0]['content'] or "img" in response_list_4[0]['content']:
                            #     data_list_4.append(response_list_4[0])
                            #     response_list_4.pop(0)
                            response_list_4.append({"type":"text", "content":index.lower(),"correct": False})
                    else:
                        data_list_4.append({"type":"text", "content":index.lower()})
                count_first_index+=1
            question_list_3.append({"data" : data_list_4, 'responses':response_list_4})
            
            for index in range(len(question_list_3)):
                response_list = question_list_3[index]['responses']
                for response in response_list:
                    if corrected_answers_list[index].lower() in response['content']:
                        response['correct'] = True
                        break
                    
            response_list_4 = []
            data_list_4 = []
    except Exception as e:
        print('unable to procced MRW section, error: ',e)
        
    return data_list_3, question_list_3

#get SRI section contents
def SRI(tables, j, i):
    data_list_5 = []
    question_list_5 = []
    img_name_ = ""
    try:
        img_name = tables[j].cell(i+1, 1).text.split('\n')
        for img in img_name:
            try:
                if "PNG" in img.upper() or "JPG" in img.upper() or "JPEG" in img.upper():
                    img_name_ = img.replace(" ",".")
                    break
            except Exception as e:
                pass
        data_list_5.append({
                "type":"image",
                "content" : img_name_
            }
        )
        
        raw_data = tables[j].cell(i+4, 1).text
        raw_data_list = raw_data.split('\n')
        
        # data = tables[j].cell(i+4, 1)
        # for paragraph in data.paragraphs:
        #     for run in paragraph.runs:
        #         p = ''.join(run.text.split())
        #         print(p)
        # # exit()
                                    
        data_list = []
        for i in range(len(raw_data_list)):
            if "aud" in raw_data_list[i+1]:
                break
            raw_data_list[i] = ""
            continue
        
        data_list = list(filter(lambda x: x!="", raw_data_list))
        question_data_list = []
        question_response_list = []
        for index in data_list:
            if not "aud" in index:
                question_data_list.append({"type": "text", "content" : index})
            else:
                question_data_list.append({"type": "audio", "content" : index})
                question_response_list.append({"type": "rec","content": "","correct": True})
                question_list_5.append({"data":question_data_list, "responses":question_response_list})
                question_data_list = []
                question_response_list = []
    except Exception as e:
        print('unable to procced SRI section, error: ',e)
    return data_list_5, question_list_5


#get data from DMC section
def DMC(tables,j,i):
    try:
        data_list_3 = []
        question_list_3 = []
        img_name = tables[j].cell(i+1, 1).text.strip()
        data_list_3.append({
                "type":"image",
                "content" : img_name
            }
        )
        
        try:
            data = tables[j].cell(i+2, 1)
            corrected_answers_list = get_corrected_answers_list(data)
        except Exception as e:
            print('unable to get answers')
        
        data_list_4 = []
        response_list_4 = []
        raw_data = tables[j].cell(i+4, 1).text
        questions = tables[j].cell(i+2, 1).text.strip()
        questions = questions.split('\n')
        total_concate_key_words, response = concate_mrw_question(questions)
        
        #get images link
        raw_images_links = tables[j].cell(i+3, 1).text.strip()
        raw_images_links = raw_images_links.split('\n')
        get_images_links_list, response = extract_images_links(raw_images_links)
        if not response:
            print('something went wrong while exracting images link for MRW section')
        
        #get audio link
        raw_audio_links = tables[j].cell(i+4, 1).text.strip()
        raw_audio_links = raw_audio_links.split('\n')
        get_audio_links_list, response = extract_audio_links(raw_audio_links)
        if not response:
            print('something went wrong while exracting audio link for MRW section')
            
        for nested_list in total_concate_key_words:
            count_first_index = 0
            for index in nested_list:
                index = index.replace(":","").upper()
                try:
                    list_ = index.split('+')
                    if "IMG" in list_[0] or "AUD" in list_[0]:
                        index = list_[0]
                    else:
                        index = list_[1]
                except Exception as e:
                    pass
                if "IMG" in index.upper():
                    for img_link in get_images_links_list:
                        key_ = img_link['key'].split('.')[0].upper()
                        if index == key_:
                            if count_first_index < 1:
                                data_list_4.append({"type":"image", "content":img_link['value']})
                            else:
                                response_list_4.append({"type":"image", "content":img_link['value'], "correct": False})                                        
                        
                elif "AUD" in index.upper():
                    for audio_link in get_audio_links_list:
                        key_ = audio_link['key'].upper()
                        if key_ == index:
                            if count_first_index < 1:
                                data_list_4.append({"type":"audio", "content":audio_link['value']})
                            else:
                                response_list_4.append({"type":"audio", "content":audio_link['value'], "correct": False})
                else:
                    if not count_first_index < 1:
                        if not "AUD" in index and not "IMG" in index:
                            response_list_4.append({"type":"text", "content":index.lower(),"correct": False})
                    else:
                        data_list_4.append({"type":"text", "content":index.lower()})
                count_first_index+=1
            question_list_3.append({"data" : data_list_4, 'responses':response_list_4})
            response_list_4 = []
            data_list_4 = []
        
        for index in range(len(question_list_3)):
            response_list = question_list_3[index]['responses']
            for response in response_list:
                if corrected_answers_list[index].lower() in response['content']:
                    response['correct'] = True
                    break
    except Exception as e:
        print('unable to procced DMC section, error: ',e)
    return data_list_3, question_list_3




#UTILITIES
#seperate unit number from string e.g. unit 1 => 1
def seprate_unit_number_from_string(unit):
    try:
        match = re.match(r"([a-z]+) ([0-9]+)", unit, re.I)
        if match:
            items = match.groups()
    except Exception as e:
        match = re.match(r"([a-z]+)([0-9]+)", unit, re.I)
        if match:
            items = match.groups()
    return items[1]


#get corrected answers listed, where bold.
def get_corrected_answers_list(data):
    answers_list =[]
    for paragraph in data.paragraphs:
        if paragraph.text.strip():
            if "AUD" in paragraph.text.strip().upper() or "IMAG" in paragraph.text.strip().upper():
                for run in paragraph.runs:
                    if run.bold:
                        text = ''.join(run.text.split()).upper().replace("AUDIO", "AUD0")
                        # text = ''.join(run.text.split()).upper().replace("IMAGE", "IMG0")
                        # answers_list.append(text)
                        # break
                answers_list.append(text)
    return answers_list


#concate MRW questions
def concate_mrw_question(questions):
    try:
        concate_key_words = []
        total_concate_key_words = []
        for i in questions:
            strip_ = ''.join(i.split()).upper()
            
            if not strip_:
                continue
            if not 'IMA' in strip_ and not 'AUD' in strip_:
                continue
            join_words = ' '.join(i.split())
            # list_  = re.split('(\d+)',join_words)
            list_ = join_words.split(' ')
            #concate string with int (image1 image 2 audio 3) = > IMAGE1 IMAGE2 AUDIO3
            for x in range(len(list_)):
                try:
                    int(list_[x])
                    concate_broken_key = list_[x-1]+list_[x]
                    concate_key_words.pop()
                    concate_broken_key = concate_broken_key.replace(":","").upper().replace("IMAGE","IMG")
                    concate_broken_key = concate_broken_key.replace(":","").upper().replace("AUDIO","AUD")
                    
                    concate_key_words.append(concate_broken_key)
                except Exception as e:
                    concate_broken_key = list_[x]
                    concate_broken_key = concate_broken_key.replace(":","").upper().replace("IMAGE","IMG")
                    concate_broken_key = concate_broken_key.replace(":","").upper().replace("AUDIO","AUD")
                    concate_key_words.append(concate_broken_key)
            total_concate_key_words.append(concate_key_words)
            concate_key_words = []
        # print(total_concate_key_words)
        return total_concate_key_words, True
    except Exception as e:
        print(e)
        return total_concate_key_words, False


def extract_images_links(images_link):
    images_link_list = []
    try:
        for link in images_link:
            if not link or not len(link) > 15 or not 'img' in link:
                continue
            
            key = link.split('_')[-1].replace('img0','img') #110020_stim1set1_img03.png => IMG3.png
            if not "img" == key[:3]:
                key = re.split('\d+', str(link), 3)[-1].split('.')[0].replace('img0','img')
            value = link
            images_link_list.append({"key":key,"value":value})
        return images_link_list, True
    except Exception as e:
        print(e)
        return images_link_list, False
    
def extract_audio_links(audio_link):
    audio_link_list = []
    try:
        for link in audio_link:
            if not link or not len(link) > 15 or not 'aud' in link:
                continue
            key = link.split('_')[-1].replace('aud0','aud') #110020_stim1set1_aud03.png => AUD3.png
            if not "aud" == key[:3]:
                key = re.split('\d+', str(link), 3)[-1].split('.')[0].replace('aud0','aud')
            value = link
            audio_link_list.append({"key":key,"value":value})
        return audio_link_list, True
    except Exception as e:
        print(e)
        return audio_link_list, False