import collections
from collections import Counter
from collections import defaultdict
from operator import itemgetter
import pandas as pd
import spacy
import pandas as pd
from collections import Counter
from app.irsystem.models.BingImageSearchv7 import image_search


nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

# Taking into consideration only nouns so as to identify the topics.
def only_nouns(texts):
    output = []
    doc = nlp(texts)
    for token in doc:
        if token.pos_ == "NOUN":
            output.append(token.lemma_)
    return output

def get_top_n_related(topic, n, politicians={}):
    if n:
        n=int(n)
    else:
        n=5
    debate_data = pd.read_csv('app/data/debate_transcripts_v5.csv')
    final_data = []
    if not politicians and not topic:
        return
    if not politicians:
        related_data = debate_data       
    else:
        politicians = set([p.strip() for p in politicians.split(",")])
        related_data = debate_data.loc[debate_data.speaker.isin(politicians)]
    if topic:        
        new_dict=defaultdict(dict)
        # Base form of the topic, with no inflectional suffixes.
        input_topic = topic.lower()
        topics = set(only_nouns(input_topic))
        for index, row in related_data.iterrows():
            word_dict = dict(Counter(str(row['speech_nouns']).split(" ")))
            topic_intersect = topics.intersection(word_dict.keys())
            if topic_intersect:
                for item in topic_intersect:
                    new_dict[item][index] = word_dict[item]
        for tp in new_dict.keys():
            od = sorted(new_dict[tp].items(), key=itemgetter(1), reverse=True)
            i=0
            for k, v in od: 
                trans_info = debate_data.loc[k]
                obj = {"score": v, "debate_date": trans_info['debate_date'], "speaker":trans_info['speaker'], "speech":trans_info['speech'], "link": trans_info["transcript_link"], "image":image_search(trans_info['speaker'])}
                final_data.append(obj)
                i+=1
                if i==n:
                    return final_data   
    else:
        new_dict=defaultdict(int)
        i=0
        # print("No topic !!!")
        for index, row in related_data.iterrows():
            obj = {"score": index, "debate_date": row['debate_date'], "speaker":row['speaker'], "speech":row['speech'], "link": row["transcript_link"], "image":image_search(trans_info['speaker'])}
            final_data.append(obj)
            i+=1
            if i==n:
                return final_data
