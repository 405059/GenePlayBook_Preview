import json
from http import HTTPStatus
import requests
from dashscope import ImageSynthesis
import os
import chat
import config


class ConcreteTopicPipeline:
    def __init__(self, game_root):
        # Read two prompt files
        with open('Concrete/Topic2Story.txt', 'r', encoding='utf-8') as f:
            self.topic2story = f.read()
            self.topic2story = self.topic2story.replace('{speaker_identifier}', config.speaker_identifier)
        with open('Concrete/Story2Node.txt', 'r', encoding='utf-8') as f:
            self.story2node = f.read()
        self.is_init = False
        self.story_talker = None
        self.game_root = game_root

    def process(self, cur_topic, game_id):
        command = {}
        topic_input = f"Dialogue content:{cur_topic.content}, Dialogue description:{cur_topic.description}"
        story_content = chat.chat_bot_format(system=self.topic2story, user=topic_input, bot="qwen-max")
        print(f'Got story:{story_content}')
        node_response = chat.chat_bot_format(system=self.story2node, user=story_content, bot="qwen-max")
        print("Story nodes have been parsed")
        command.update({"code": "null", "mark": "narrative", "parameters": "null"})
        with open('Prompt/background.txt', 'r', encoding='utf-8') as f:
            back = f.read()
        game_des = chat.chat_bot_format(system="",
                                        user="Story content nodes are as follows:\n" +
                                             node_response + "Please write a game introduction, "
                                                             "no more than 100 words",
                                        bot="qwen-max")
        game_name = chat.chat_bot_format(system="",
                                         user="Story content nodes are as follows:\n" + node_response +
                                              "Please name the game, no more than 10 characters ",
                                         bot="qwen-max")
        game_name = chat.incorrect_str_detect(game_name)
        game_file = f"{game_name}_{game_id}"
        directory = os.path.dirname(self.game_root)
        d_root = os.path.join(directory, game_file)
        if not os.path.exists(d_root):
            os.makedirs(d_root)
        game_message = {}
        self.story_talker = StoryTalker(story_node_json=node_response,
                                        background=back, topic_input=topic_input, is_expand=True,
                                        data_path=self.game_root + "\\" + game_file + "\\")
        game_message.update({"game_des": game_des, "game_name": game_name,
                             "game_data": "$".join(self.story_talker.story_tree.data)})
        with open(d_root + "\\game_message.txt", 'w', encoding='utf-8') as f:
            json.dump(game_message, f, ensure_ascii=False, indent=4)
        with open(d_root + "\\command.txt", 'w', encoding='utf-8') as f:
            json.dump(command, f, ensure_ascii=False, indent=4)

    def parse_with_no_expand(self, story, path):
        node_response = chat.chat_bot_format(system=self.story2node, user=story, bot="qwen-max")
        self.story_talker = StoryTalker(story_node_json=node_response,
                                        background="", topic_input="", is_expand=False,
                                        data_path=path)


class StoryTalker:
    def __init__(self, story_node_json, background, topic_input, is_expand, data_path):
        with open('Concrete/NodeConvert.txt', 'r', encoding='utf-8') as f:
            self.prompt = f.read()
        self.prompt = self.prompt.replace("{leading_actor_message}", background)
        self.prompt = self.prompt.replace("{dialogue}", topic_input)
        self.story_node_json = story_node_json
        self.story_tree = MultiTree(story_node_json, system_prompt=self.prompt)
        print("Starting to expand nodes")
        if is_expand:
            self.story_tree.expand()
        generate_story_board(background, self.story_tree, data_path)


def debug_main_tree(tree):
    cur = tree.get_root()
    cur = cur.get_main_child()
    while cur is not None:
        for child in cur.children:
            print(f"Node type:{child.type} Content:{child.content}" )
        cur = cur.get_main_child()


class MultiTreeNode:
    def __init__(self, type_, content, parent=None, is_main=False):
        self.type = type_
        self.content = content
        self.parent = parent
        self.children = []
        self.is_main = is_main  # Whether it's the main child node of the parent

    def add(self, type_, content):
        """Add a non-main node as a child node"""
        new_node = MultiTreeNode(type_, content, parent=self, is_main=False)
        self.children.append(new_node)
        return new_node

    def get_main_sibling(self):
        """Get the main node at the same level (parent's main child node)"""
        if self.parent is None:
            return None  # Root node has no siblings
        for child in self.parent.children:
            if child.is_main:
                return child
        return None

    def get_main_child(self):
        for child in self.children:
            if child.is_main:
                return child
        return None

    def to_json(self):
        """Generate a JSON array of all main nodes on the path from root to current node"""
        path = []
        current = self
        # Traverse up to the root node
        while current.parent is not None:
            if current.is_main:
                # Only collect main nodes
                path.append({'type': current.type, 'content': current.content})
            current = current.parent
        # Reverse the path, root node's main node first
        path.reverse()
        return path


class MultiTree:
    def __init__(self, json_data, system_prompt):
        self.root = MultiTreeNode(type_=None, content=None, parent=None, is_main=False)
        self.system = system_prompt
        self.json_data = json_data
        self.data = []
        current_parent = self.root
        item_content = json.loads(self.json_data)
        for item in item_content:
            # Create main node, is_main=True
            new_node = MultiTreeNode(
                type_=item['type'],
                content=item['content'],
                parent=current_parent,
                is_main=True
            )
            current_parent.children.append(new_node)
            current_parent = new_node

    def get_root(self):
        return self.root

    def expand(self):
        cur = self.get_root()
        while cur.children is not None and len(cur.children) > 0:
            cur = cur.get_main_child()
            if cur.type == "action":
                print(f"expanding node:{cur.content}")
                reason_input = [{"role": "system", "content": self.system},
                                {"role": "user",
                                 "content": f"Story line:{self.json_data}\nSpecific paragraph:\ntype:{cur.type} content:{cur.content}"}]
                reason_content = chat.chat_bot(reason_input, bot="qwen-max")
                print(f"Question raised: {reason_content}")
                expansion_user = (
                    f"{self.json_data}\nThe specific paragraph in the story is:\nSpecific paragraph:\ntype:{cur.type} content:{cur.content}\n"
                    f"The reason for this action is: \n{reason_content}")
                with open('Concrete/ChoiceExpansion.txt', 'r', encoding='utf-8') as f:
                    expansion_system = f.read()
                choices_input = [{"role": "system", "content": expansion_system},
                                 {"role": "user", "content": expansion_user}]
                print("Creating new branch stories.....")
                choices = chat.chat_bot(choices_input, "qwen-json")
                print("Creation successful!")
                choices_data = json.loads(choices)
                # Save the next main node of the current node
                next_main = cur.get_main_child()
                # Remove the original main node from the current node's children
                if next_main in cur.children:
                    cur.children.remove(next_main)
                # Modify the current node to choice type
                choices_content = "|".join([c["choice"] for c in choices_data["choices"]])
                choices_content = choices_data["scene"] + "%" + choices_content
                cur.type = "choice"
                cur.content = choices_content
                # Find the choice that continues the plot
                new_main = None
                for choice in choices_data["choices"]:
                    if choice["end"] == "Story Continuation":
                        new_main = MultiTreeNode(
                            type_="narration",
                            content=choice["content"],
                            parent=cur,
                            is_main=True
                        )
                        cur.children.append(new_main)
                    else:
                        cur.add("narration", choice["content"])
                    # Link the original main node to the new main node
                if next_main:
                    next_main.parent = new_main
                    new_main.children.append(next_main)
            else:
                continue


def get_story_str(story_tree):
    if not isinstance(story_tree, MultiTree):
        return "",[]
    story_string = []
    story_index = 1
    cur = story_tree.get_root()
    while cur.children is not None and len(cur.children) > 0:
        if len(cur.children) == 1:
            tmp = cur.get_main_child()
            value = {"key": f"{tmp.type}*{tmp.content}*main", "content": f"{story_index}.Story node type:{tmp.type} Content:{tmp.content}" }
            story_string.append(value)
            story_index += 1
        else:
            child_index = 1
            for child in cur.children:
                main_signal = "main" if child.is_main else "other"
                value = {"key": f"{child.type}*{child.content}*{main_signal}",
                         "content": f"{story_index}-{child_index}.Story node type:{child.type} Content:{child.content}"}
                story_string.append(value)
                child_index += 1
        story_index += 1
        cur = cur.get_main_child()
    total = ""
    for node in story_string:
        total += node["content"]
    return total, story_string


def generate_story_board(background, story_tree, story_board_path):
    with open('Concrete/StoryDrawSystem.txt', 'r', encoding='utf-8') as f:
        system = f.read()
    with open('Concrete/StoryDrawInput.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{background}", background)
    # Get story line
    story_str,nodes = get_story_str(story_tree)
    prompt = prompt.replace("{story_line}", story_str)
    current_prompt = ""
    p_index = 1
    for node in nodes:
        tmp_prompt = prompt.replace("{current_prompt}", current_prompt)
        tmp_prompt = tmp_prompt.replace("{current_node}", node["content"])
        draw_input = [{"role": "system", "content": system},
                         {"role": "user", "content": tmp_prompt}]
        draw_prompt = chat.chat_bot(draw_input, "qwen-json")
        current_prompt = draw_prompt
        draw_json = json.loads(draw_prompt)
        print(f'----Generating image, prompt is {draw_prompt}----')
        rsp = ImageSynthesis.call(api_key="sk-f0b45ac98a574f91869883831792f294",
                                  model="wanx2.1-t2i-turbo",
                                  prompt=draw_json["positive"],
                                  negative_prompt=draw_json["negative"],
                                  n=1,
                                  size='1440*768')
        print('response: %s' % rsp)
        if rsp.status_code == HTTPStatus.OK:
            # Save the image in the current directory
            for result in rsp.output.results:
                file_name = story_board_path + f"{p_index}picture.png"
                p_index += 1
                with open(file_name, 'wb+') as f:
                    f.write(requests.get(result.url).content)
                story_tree.data.append(f"{node['key']}^{file_name}")
        else:
            print('sync_call Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))