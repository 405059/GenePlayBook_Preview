import chat
import json
import speech_reader

SYSTEM_CLASSIFY = '''
I will provide you with a description of a specific topic. Based on the description, classify the topic into one of the following categories:  

## 1. Narrative  
### Definition:  
Describes events, experiences, or backgrounds, or showcases related content such as history, culture, or social phenomena. The primary focus is on conveying information, emphasizing objective description and restoration rather than emotional expression or opinion sharing.  
### Examples:  
- **Event Narration:** Explains the background and details of specific events, such as personal experiences or social events.  
- **History or Cultural Showcase:** Introduces historical events, cultural backgrounds, or specific social phenomena.  
- **Background and Scene Description:** Describes the characteristics of a specific location or environment.  

## 2. Opinion Discussion  
### Definition:  
Focuses on discussing a specific event or abstract issue by expressing personal opinions and stances. Topics may include social phenomena, values, or the meaning of life. This category also encompasses "philosophical or value-based reflections," as both center on expressing viewpoints.  
### Examples:  
- **Social Phenomena or Controversial Topics:** Discussion of societal phenomena or hot-button topics.  
- **Values and Life Meaning:** Exploration of abstract topics like happiness, educational significance, or life values.  
- **Policy or Historical Reflections:** Deep reflections on policies, historical events, or cultural phenomena.  

## 3. Emotional Exchange  
### Definition:  
Centers on sharing emotions, nostalgia, sentiments, or emotional expressions. The focus is on emotional interaction rather than information delivery or opinion sharing.  
### Examples:  
- **Nostalgia and Sentiments:** Recalling happy memories or reflecting on changes in relationships, expressing longing or melancholy.  
- **Appreciation and Gratitude:** Expressing admiration, gratitude, or blessings for someone or something.  
- **Reflections on Changes:** Emotional reactions to changes in society, life, or the times.  

## 4. Science Popularization  
### Definition:  
Focuses on the knowledge dissemination and showcase of objects, technologies, or tools, aiming to introduce their characteristics, functions, or usage methods. Emotional expression or cultural background description is not the focus.  
### Examples:  
- **Technology and Tools:** Explains the features, usage, or history of a specific object or technology.  
- **Object Showcase:** Shares the functionality or uniqueness of a particular object.  

## 5. Comparative Analysis  
### Definition:  
Analyzes changes, differences, or impacts by comparing different times, places, social phenomena, or groups. The focus is on uncovering essence or trends through comparisons, often accompanied by logical analysis.  
### Examples:  
- **Era and Society Comparisons:** Compares past and present living conditions, social relationships, or happiness.  
- **Culture or Regional Comparisons:** Analyzes differences and characteristics of various regions or cultures.  
- **Value Comparisons:** Contrasts the values of different generations or groups.  

## 6. Interaction  
### Definition:  
Highlights casual exchanges focused on interpersonal interaction. Content is usually light and lacks a clear theme, often involving greetings, gratitude, or simple action descriptions. These dialogues do not contain in-depth thematic discussions, typically reflecting everyday life.  
### Examples:  
- **Daily Greetings:** Asking about someone's status or offering help.  
  *Example:* "Do you want some water?"  
- **Simple Interaction:** Casual exchanges related to everyday life.  
  *Example:* "See you next time, let’s chat when you’re free."  

## Response Requirements:  
1. Provide the classification result enclosed in `&` symbols, e.g., `&Science Popularization&`.  
2. Each topic can only be classified into one category and cannot belong to multiple categories.  
'''


def load_topics(path):
    with open(path, 'r', encoding='utf-8') as f:
        topics_dict = json.load(f)
    return [speech_reader.Topic(
        begin=topic['begin'],
        end=topic['end'], 
        content=topic['content'],
        description=topic['description'],
        tag=topic['tag']
    ) for topic in topics_dict]


def classify_topic(topic):
    content = chat.chat_bot_format(system=SYSTEM_CLASSIFY, user=f"{topic.description}\n{topic.content}",
                                   bot="reason")
    start = content.find('&')
    end = content.rfind('&')
    if start != -1 and end != -1 and start < end:
        return content[start+1:end]
    return "default"


def classify_topics(topics):
    """批量分类话题"""
    for topic in topics:
        topic.tag = classify_topic(topic)
        print(f"Topic {topic.begin}-{topic.end} classified as: {topic.tag}")
    return topics


def save_classified_topics(topics):
    speech_reader.save_topics_to_json(topics, 'topics_tag.json')


