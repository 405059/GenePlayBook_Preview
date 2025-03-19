import json
import config
import net
import argparse
from Abstract.abstract_content_pipeline import AbstractTopicPipeline, Agent
from Concrete.concrete_content_pipeline import ConcreteTopicPipeline
from speech_reader import Dialogue2Topic
import classify_topics


class GameRuler:
    def __init__(self, game_root):
        self.game_id = config.game_id
        self.abstract_topic_pipeline = AbstractTopicPipeline(game_root)
        self.concrete_topic_pipeline = ConcreteTopicPipeline(game_root)
        self.agent = None

    def parse_topics(self, cur_topic):
        if cur_topic.tag == "Science Popularization" or cur_topic.tag == "Narrative":
            self.concrete_topic_pipeline.process(cur_topic, self.game_id)
            self.game_id += 1
        elif (cur_topic.tag == "Opinion Discussion" or cur_topic.tag == "Emotional Exchange" or
              cur_topic.tag == "Comparative Analysis"):
            self.abstract_topic_pipeline.process(cur_topic, self.game_id)
            self.game_id += 1
        else:
            print('error type')


def convert_dialogue(background, dialogue_path, game_data_path):
    d = Dialogue2Topic(background, clip=120, begin=0)
    cur_topics = d.process_dialogue(dialogue_path)
    # topics = classify_topics.load_topics("topics_tag.json") # Load pre-processed topics
    cur_topics = classify_topics.classify_topics(cur_topics)
    classify_topics.save_classified_topics(cur_topics)  # Save topic files
    return cur_topics


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process dialogue into game content')
    parser.add_argument('--game_path', type=str, required=True,
                        help='Path to game data directory')
    parser.add_argument('--dialogue_path', type=str, required=True,
                        help='Path to dialogue file')
    parser.add_argument('--init_message_path', type=str, required=True,
                        help='Path to initialization message file')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    with open(args.init_message_path, 'r', encoding='utf-8') as f:
        init_data = f.read()
        init_message = json.loads(init_data)
    # topics = convert_dialogue(
    #     init_message['background'],
    #     args.dialogue_path,
    #     ''
    # )
    topics = classify_topics.load_topics('topics_tag.json')
    config.game_id = init_message["current_game_id"]
    ruler = GameRuler(args.game_path)
    i = 0
    for topic in topics:
        ruler.parse_topics(topic)  # Convert topic into game content
        i = i + 1
        if i > 3:
            break
    if config.enable_cloud_services:
        net.upload(args.game_path)


