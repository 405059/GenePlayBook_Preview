import json
import re
from openai import OpenAI
import yaml

import chat
import config


class Topic:
    def __init__(self, begin, end, content, description, tag):
        self.begin = begin
        self.end = end
        self.content = content
        self.description = description
        self.tag = tag


def read_speech_as_list(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]


def get_next_content(content, delimiter):
    try:
        range_str = content.split(delimiter)[1]
        return int(range_str.split('-')[1])
    except (IndexError, ValueError):
        return 1


def save_topics_to_json(topics, filename):
    topics_dict = [{
        'begin': topic.begin,
        'end': topic.end,
        'content': topic.content,
        'description': topic.description,
        'tag': topic.tag
    } for topic in topics]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(topics_dict, f, ensure_ascii=False, indent=2)


class Dialogue2Topic:
    def __init__(self, background_init, clip=60, begin=0):
        with open('Prompt/message_extract.txt', 'r', encoding='utf-8') as f:
            message_extract_system_read = f.read()
            self.message_extract_system = message_extract_system_read.replace("{absolute_info}", background_init)
            self.message_extract_system = self.message_extract_system.replace('{speaker_identifier}',
                                                                              config.speaker_identifier)
        self.clip = clip
        self.background = ""
        self.background_init = background_init
        self.system_prompt = '''
        This is a transcript of an interview converted from audio to text. The content may include incomplete expressions or typos. Your task is to infer the intended meaning based on the context. ({speaker_identifier} is the main character, and the summary should primarily be from {speaker_identifier}'s perspective).
        ## Task:
        Identify the topic discussed between the speakers.
        Summarize the content of the topic.
        If the conversation contains multiple topics, indicate which lines correspond to the first topic and ignore all subsequent topics. Summarize only the first topic.
        Example:
        I heard you like A.
        Yes, A is great.
        A has many advantages...
        What about B? B is also nice...
        B is great...
        ...
        n. B...
        ## Response:
        &1-3& is one topic about A...
        If the conversation contains no clear topic or is too vague, still respond in the required format with:
        &1-n& No content
        '''
        self.system_prompt = self.system_prompt.replace('{speaker_identifier}', config.speaker_identifier)

    def process_dialogue(self, path):
        speakers = read_speech_as_list(path)
        topics = []
        begin = 0
        while begin < len(speakers):
            speak_tmp = speakers[begin:begin + self.clip]
            print(f"dealing with topic>>{begin}:{begin + self.clip}")
            result = ""
            for index, speaker in enumerate(speak_tmp):
                result += f"{index + 1}. {speaker}\n"
            response_content = chat.chat_bot_format(system=self.system_prompt, user=result, bot="qwen-max")
            print(response_content)
            next_content = get_next_content(response_content, '&')
            try:
                description = response_content.split('&')[2].strip()
                topic = Topic(
                    begin=begin,
                    end=begin + next_content,
                    content=speakers[begin:begin + next_content],
                    description=description,
                    tag="default"
                )
                topics.append(topic)
                message_extract_input = (f"content:{topic.content}\n"
                                         f"description:{topic.description}")
                message_system = self.message_extract_system.replace("{other_info}", self.background)
                reason_input = [
                    {"role": "system", "content": message_system},
                    {"role": "user", "content": message_extract_input}
                ]
                reason_content = chat.chat_bot(reason_input, "qwen-max")
                info, reason_info = extract_message(reason_content)
                if info is not None:
                    self.background += f"Information:{info}"
                begin += next_content
            except IndexError:
                continue
        # Open file, write content
        with open("Prompt/background.txt", "w", encoding="utf-8") as file:
            file.write(f"Basic information{self.background_init}, Other experience information:{self.background}")
        return topics

def extract_message(json_str, is_first_extract=True):
    try:
        data = json.loads(json_str)
        # Validate required fields exist
        if 'ischange' not in data or 'message' not in data:
            return None, None
        # Check status indicator
        if data['ischange'].lower() == 'true':
            return data['message'], data["reason"]
        return None, None

    except json.JSONDecodeError:
        if is_first_extract:
            new_json_str = chat.chat_bot_format(
                system="Your task is to extract JSON format data from the input, and output it", user=json_str,
                bot="qwen-json")
            return extract_message(new_json_str, False)
        else:
            return None, None
    except Exception as e:
        print(f"Processing exception: {str(e)}")
        return None, None
