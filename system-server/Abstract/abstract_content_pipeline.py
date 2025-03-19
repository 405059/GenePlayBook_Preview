import json
import yaml
from pyexpat.errors import messages
import re
import chat
import copy
from collections import defaultdict
import uuid
import os
from Concrete.concrete_content_pipeline import ConcreteTopicPipeline
import config


class AbstractTopicPipeline:
    def __init__(self, game_location):
        with open('Abstract/Adapter_e/topic_e_adapter.txt', 'r', encoding='utf-8') as f:
            self.adapter_e = f.read()
            self.adapter_e = self.adapter_e.replace('{speaker_identifier}', config.speaker_identifier)
        with open('Abstract/Adapter_v/topic_v_adapter.txt', 'r', encoding='utf-8') as f:
            self.adapter_v = f.read()
            self.adapter_v = self.adapter_v.replace('{speaker_identifier}', config.speaker_identifier)
        with open('Abstract/Adapter_c/topic_c_adapter.txt', 'r', encoding='utf-8') as f:
            self.adapter_c = f.read()
            self.adapter_c = self.adapter_c.replace('{speaker_identifier}', config.speaker_identifier)
        with open('Abstract/AssetDraw.txt', 'r', encoding='utf-8') as f:
            self.draw = f.read()
        with open('Abstract/voice_selection.txt', 'r', encoding='utf-8') as f:
            self.voice_selection = f.read()
        self.path = game_location

    def process(self, discuss_topic, game_id):
        response = ""
        command = {}
        flag = -1
        if discuss_topic.tag == "Opinion Discussion":
            user_input = f"Dialogue description{discuss_topic.description}"
            response = chat.chat_bot_format(user=user_input, system=self.adapter_v,
                                            bot="qwen-max")  # Get game information
            command.update({"code": "null", "mark": "default", "parameters": "null"})
            flag = 0
        if discuss_topic.tag == 'Emotional Exchange':
            user_input = f"Dialogue content:{discuss_topic.content}, Dialogue description{discuss_topic.description}"
            response = chat.chat_bot_format(user=user_input, system=self.adapter_e,
                                            bot="qwen-max")  # Get game information
            command.update({"code": "random_scenario", "mark": "narrative_first", "parameters": "null"})
            flag = 1
        if discuss_topic.tag == 'Comparative Analysis':
            user_input = f"Dialogue description{discuss_topic.description}"
            response = chat.chat_bot_format(user=user_input, system=self.adapter_e,
                                            bot="qwen-max")  # Get game information
            command.update({"code": "null", "mark": "default", "parameters": "null"})
            flag = 2
        try:
            game_data = json.loads(response)
            scenario = game_data['random_scenario']
            role_info = game_data['intelligent_role_info']
            dialogue_style = game_data['dialogue_style']
            victory_skills = game_data['victory_skills']
            goal = game_data['player_goal_and_victory_conditions']
            sample_dialogue = game_data['sample_dialogue']
            system = (
                "You need to role-play a character, refer to the system's suggestions to respond to user input, "
                "the character information is as follows:\n"
                f"Background: {scenario}\n"
                f"Character information:\n"
                f"- Name: {role_info['name']}\n"
                f"- Gender: {role_info['sex']}\n"
                f"- Identity: {role_info['identity']}\n"
                f"- Personality: {role_info['personality']}\n"
                f"- Speaking style: {dialogue_style}\n"
                "The system's suggestion is {critic_suggestion}"
            )
            game_des_request = (
                "An AI character role-playing dialogue game introduction is as follows:\n"
                f"Game background: {scenario}\n"
                f"AI character information:\n"
                f"- Name: {role_info['name']}\n"
                f"- Gender: {role_info['sex']}\n"
                f"- Identity: {role_info['identity']}\n"
                f"- Personality: {role_info['personality']}\n"
                f"- Speaking style: {dialogue_style}\n"
                f"The player's victory goal is: {goal}\n"
            )
            game_des = chat.chat_bot_format(system="",
                                            user=game_des_request + "Please write a game introduction, "
                                                                    "introducing the game background and "
                                                                    "AI character information, "
                                                                    "no more than 100 words",
                                            bot="qwen-max")
            print('Generating description information')
            game_name = chat.chat_bot_format(system="",
                                             user=game_des_request + "Please name the game, "
                                                                     "no more than 10 characters, "
                                                                     "directly reply with the name",
                                             bot="qwen-max")
            print(f'Generating game name {game_name}')
            game_name = chat.incorrect_str_detect(game_name)
            voice = chat.chat_bot_format(system=self.voice_selection, user=game_des_request, bot="qwen-json")
            game_data['intelligent_role_info']['sex'] = voice
            game_name = f"{game_name}_{game_id}"
            directory = os.path.dirname(self.path)
            d_root = os.path.join(directory, game_name)
            if not os.path.exists(d_root):
                os.makedirs(d_root)
            prompt_json = chat.chat_bot_format(system=self.draw,
                                               user=game_des_request + "Game introduction:" + game_des, bot="qwen-max")
            prompt_data = json.loads(prompt_json)
            for data in prompt_data:
                chat.generate_image(data['positive'], data['negative'], d_root + "\\" + data['object'] + '.png')
            critic = Critic(victory_skills, goal, game_des)
            critic.save_miss_cache(d_root + "\\critic.txt")
            save_game_data(game_data, system, game_des, game_name, d_root + "\\game_message.txt")
            if flag == 1:
                concrete_pipe = ConcreteTopicPipeline(d_root)
                concrete_pipe.parse_with_no_expand(scenario, d_root + "\\")
                game_data = concrete_pipe.story_talker.story_tree.data
                command["parameters"] = "$".join(game_data)
            # Write game extension command
            with open(d_root + "\\command.txt", 'w', encoding='utf-8') as f:
                json.dump(command, f, ensure_ascii=False, indent=4)
        except (ValueError, TypeError, KeyError) as e:
            print('Error parsing game data:', str(e))


def save_game_data(game_data, system, game_des, game_name, filename):
    # Create storage dictionary
    save_dict = {
        "game_data": game_data,
        "system": system,
        "game_des": game_des,
        "game_name": game_name
    }

    # Write to file (using utf-8 encoding to ensure Chinese characters display correctly)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=4)
        print(f"Data has been saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {str(e)}")


def load_game_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"Data loaded from {filename}")
        return loaded_data
    except FileNotFoundError:
        print(f"File {filename} does not exist")
        return None
    except json.JSONDecodeError:
        print(f"File {filename} format error")
        return None
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return None


class Agent:
    def __init__(self, game_path, max_context=10):
        with open(game_path + "\\game_message.txt", 'r', encoding='utf-8') as f:
            message = f.read()
        with open(game_path + "\\critic.txt", 'r', encoding='utf-8') as f:
            self.critic_data = f.read()
        # Build initial dialogue
        self.game_message = json.loads(message)
        self.system = self.game_message["system"]
        self.game_data = self.game_message["game_data"]
        # Extract agent data
        self.critic = Critic.from_cache_file(game_path + "\\critic.txt", self.game_message["game_des"],
                                             self.game_data["player_goal_and_victory_conditions"])
        self.max_context = max_context
        # Initialize dialogue state
        self.dialogue_state = {
            'history': [],
            'player_score': 0
        }

    def start_dialogue(self):
        """Start dialogue, return game scenario and character information"""
        print("Loading viewpoints and content......")
        response_content = chat.chat_bot_format(system=self.system,
                                                user=combine_str('No suggestion', 'Please start with an opening line')
                                                , bot="qwen-max")
        self.add_to_history("assistant", response_content)
        return response_content

    def next_dialogue(self, user_input):
        # assistant_history = self.dialogue_state['history'][-1]
        comments = self.critic.forward(user_input)
        content = combine_str(comments, user_input)
        send_content = self.dialogue_state['history']
        send_content.insert(0, {"role": "system", "content": self.system})
        send_content.insert(-1, {"role": "user", "content": content})
        reply = chat.chat_bot(send_content, "qwen-max")
        self.add_to_history('user', user_input)
        self.add_to_history('assistant', reply)
        reply_message = f"{reply}&{len(self.critic.view_hit_cache)}&{len(self.critic.view_hit_cache) + len(self.critic.view_miss_cache)}"
        return reply_message

    def add_to_history(self, role, content):
        """Add new message to dialogue history"""
        self.dialogue_state['history'].append({"role": role, "content": content})
        # Maintain maximum context for history
        if len(self.dialogue_state['history']) > self.max_context:
            self.dialogue_state['history'].pop(0)


class Critic:
    def __init__(self, viewpoints, goal, background, batch=15):
        self.viewpoints = viewpoints
        with open('Abstract/critic_prompt.txt', 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        with open('Abstract/hit_keyword.txt', 'r', encoding='utf-8') as f:
            self.hit_prompt = f.read()
        self.view_miss_cache = {}
        self.view_hit_cache = {}
        self.batch = batch
        self.trigger_history = defaultdict(list)
        self.last_moved = 0
        self.last_hit = 0
        self.prompt_prefix = f"Game background {background}, player victory goal {goal}\n"

        # Only initialize miss_cache when viewpoints exist
        if viewpoints:
            for viewpoint in viewpoints:
                response_content = chat.chat_bot_format(
                    system=self.system_prompt,
                    user=self.prompt_prefix + viewpoint,
                    bot="qwen-json"
                )
                contents = json.loads(response_content)
                for c in contents:
                    try:
                        keyword = c["keyword"]
                        description = c["description"]
                        self.view_miss_cache.setdefault(keyword, []).append(description)
                    except ():
                        pass

    @classmethod
    def from_cache_file(cls, file_path, goal, background, batch=15):
        """New constructor for creating Critic from cache file"""
        # Initialize empty object
        obj = cls(viewpoints=[], goal=goal, background=background, batch=batch)

        # Load miss_cache from file
        obj.view_miss_cache = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    key_part, desc_part = line.split(':', 1)
                    keyword = key_part.strip()
                    descriptions = [d.strip() for d in desc_part.split(',')]
                    obj.view_miss_cache[keyword] = descriptions
        except FileNotFoundError:
            print(f"Warning: Cache file {file_path} not found")
        return obj

    def save_miss_cache(self, file_path):
        """Save miss_cache to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for keyword, desc_list in self.view_miss_cache.items():
                line = f"{keyword}:{','.join(desc_list)}\n"
                f.write(line)

    def forward(self, user_input):
        # Save snapshot of original hit_cache
        original_hit_cache = copy.deepcopy(self.view_hit_cache)
        original_hit_keys = set(original_hit_cache.keys())
        tmp_dict = {}
        tmp_hit = ""
        # Step 1: Process keywords in miss_cache, count movements and record user_input
        miss_cache_strings = self.load_miss_cache_str(self.batch)
        self.last_moved = 0
        for keyword_list_str in miss_cache_strings:
            prompt_with_keywords = self.hit_prompt.replace("{keyword_list}", keyword_list_str)
            response_content = chat.chat_bot_format(
                system=prompt_with_keywords,
                user=user_input,
                bot="qwen-max"
            )
            hit_keywords = [k.strip() for k in response_content.split(",")]
            for keyword in hit_keywords:
                if keyword in self.view_miss_cache:
                    # Move to hit_cache
                    self.view_hit_cache.setdefault(keyword, []).extend(self.view_miss_cache[keyword])
                    tmp_dict.setdefault(keyword, []).extend(self.view_miss_cache[keyword])
                    del self.view_miss_cache[keyword]
                    self.last_moved += 1
                    # Record user_input that triggered this keyword
                    self.trigger_history[keyword].append(user_input)

        # Step 2: Process keywords in original hit_cache, count hits
        self.last_hit = 0
        original_hit_keys_list = list(original_hit_keys)
        for i in range(0, len(original_hit_keys_list), self.batch):
            batch_keys = original_hit_keys_list[i:i + self.batch]
            entries = []
            for key in batch_keys:
                desc_str = ", ".join(original_hit_cache.get(key, []))
                entries.append(f"{key}: {desc_str}")
            keyword_list_str = "; ".join(entries)
            prompt_with_keywords = self.hit_prompt.replace("{keyword_list}", keyword_list_str)
            response_content = chat.chat_bot_format(
                system=prompt_with_keywords,
                user=user_input,
                bot="deepseek-v3"
            )
            tmp_hit += response_content
            current_hits = [k.strip() for k in response_content.split(",")]
            self.last_hit += sum(1 for k in current_hits if k in original_hit_keys)
        suggestion = ""
        if self.last_moved > 0:
            # Parse transferred viewpoints into string
            keys = list(tmp_dict.keys())
            entries = []
            for key in keys:
                descriptions = tmp_dict.get(key, [])
                desc_str = ", ".join(descriptions)
                entries.append(f"{key}: {desc_str}")
            batch_str = "; ".join(entries)
            suggestion += f"Positive suggestion, user rebutted viewpoints: {batch_str}"
        elif self.last_hit > 0:
            suggestion += f"User has already answered similar viewpoints, viewpoints are: {tmp_hit}"
        else:
            suggestion += f"No suggestion"
        return suggestion

    def load_hit_cache_str(self, batch):
        keys = list(self.view_hit_cache.keys())
        batch_strings = []

        # If batch is -1, process all content as one batch
        if batch == -1:
            batch = len(keys)

        # Iterate through keywords in batches
        for i in range(0, len(keys), batch):
            batch_keys = keys[i:i + batch]
            entries = []

            # Concatenate each keyword and its descriptions in "key: desc1, desc2..." format
            for key in batch_keys:
                descriptions = self.view_hit_cache.get(key, [])
                desc_str = ", ".join(descriptions)
                entries.append(f"{key}: {desc_str}")

            # Merge current batch into string and save
            batch_str = "; ".join(entries)
            batch_strings.append(batch_str)

        return batch_strings

    def load_miss_cache_str(self, batch):
        # Get a list of keywords representing miss_cache
        keys = list(self.view_miss_cache.keys())
        batch_strings = []
        # If batch is -1, process all content as one batch
        if batch == -1:
            batch = len(keys)
        # Iterate through keywords in batches
        for i in range(0, len(keys), batch):
            # Take a batch of keywords
            batch_keys = keys[i:i + batch]
            entries = []
            # Concatenate each keyword and its descriptions in "key: desc1, desc2..." format
            for key in batch_keys:
                # Get the description list for the key
                descriptions = self.view_miss_cache.get(key, [])
                # Merge all linked list properties of a key into one string
                desc_str = ", ".join(descriptions)
                entries.append(f"{key}: {desc_str}")

            # Merge current batch into string and save
            batch_str = "; ".join(entries)
            batch_strings.append(batch_str)

        return batch_strings


def combine_str(critic, user):
    return f"Part one: {critic}, Part two: {user}"

