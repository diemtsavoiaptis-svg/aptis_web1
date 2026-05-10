from pathlib import Path

Path("auto_save_part2_gioi_voice_info_12_topics.py").write_text(r'''
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Part2Topic, Part2Voice

TOPIC_MAP = {
    1: "Topic Protect the environment",
    2: "Topic Protect the environment 2",
    3: "Topic Online shopping",
    4: "Topic Listening to music",
    5: "Topic Outdoor activities",
    6: "Topic The place to run",
    7: "Topic Do exercise",
    8: "Topic The internet",
    9: "Topic The Art",
    10: "Topic Travel to work.",
    11: "Topic Studying.",
    12: "Topic Studying phiên bản 2.",
}

RAW_DATA = r"""
topic 1
Person A: I find the act of giving away old or secondhand items a bit hypocritical. Why do people give away their old things, only to go out and buy the same item but brand new? Not only does this fail to protect the environment, but it also causes double the harm. Personally, I have a way of protecting the environment by not releasing harmful chemicals into it. I do this by not purchasing chemical cleaning solutions. Instead, I make use of natural products like lemons to create my own floor-cleaning solutions.

Person B: I often don't have time to think about how to reuse my belongings or clothes, but I don't want to throw them away because that would be wasteful. So, I think a better way is to donate them to charity organizations or give them to others. Many people are in need of these things, and giving away my old items also makes me feel happier because I'm helping others.

Person C: A good way to protect the environment is by not using plastic bags or by bringing reusable bags when going to the market, which helps reduce the disposal of plastic bags, a material that is difficult to decompose. However, I'm a very busy person and rarely have time to prepare my own bags when going shopping, and I usually drive to buy groceries quickly instead of walking. I guess I can't protect the environment by not driving. But I have a principle of only buying eco-friendly products, so I think I’m still contributing in a small way to protecting the Earth.

Person D: I see that too many people are wasting food containers, as they often throw them away after use, such as glass jars or plastic bottles. I can reuse them to store food and neatly organize them in my refrigerator. Reusing these containers is a very easy way to protect the environment that anyone can do.

topic 2
A: I usually shop online to reduce the need to drive to the supermarket, which produces harmful emissions for the environment. Additionally, I can avoid using plastic bags for groceries when shopping in person. By simply sitting at home and clicking a few buttons, I can buy everything I want without emitting harmful gases from a car.

B: I used to drive to work for a long period, but then I realized that the excessive use of personal cars contributes significantly to environmental pollution. Therefore, I chose to ride a bicycle to work, which benefits both the environment and my health.

C: I'm not that into environmental protection and usually just do what’s convenient for me. But my electric bill last month shocked me because it was so expensive, and I realized that I needed to save money. So from now on, I’ll have to manage my electricity use more efficiently.

D: I think a lot of people overemphasize protecting the environment by cutting down on personal vehicles, avoiding plastic bags, planting a lot of trees, and so on. But I personally believe we should focus on protecting the environment through small daily actions we often overlook. For example, turning off the water while brushing our teeth or washing our hands. If everyone saves a little water like that, it would add up to a huge amount saved globally.

topic 3
A: "I used to be the person who didn’t like shopping online, but ever since I experienced home delivery, I no longer shop in stores. When I shop online, the delivery person brings the package right to my door, even up to my floor, and knocks on my apartment door, so I don’t even need to step outside. I really enjoy this convenience."

B: "Shopping online has helped me save quite a bit of money. After a few months of online shopping, I was able to save enough to buy a new bicycle. But don't get me wrong, I haven't been eating any less or cutting back on the groceries I buy. It's just that online shopping allows me to compare prices and choose the store with the best deal."

C: "I’m a pretty busy person, and I often don’t have enough time because of my hectic work schedule. That’s why I always shop online to save time. This way, I don’t need to go to the store in person, and someone will deliver the items directly to me. Additionally, online shopping is very convenient because, with just a few clicks, I can buy everything I want without having to go from one store to another."

D: "I don't shop online because it's cheaper or because of the fast shipping. I shop online because, when browsing online stores, I have a wide range of choices. For the same item, there are many different types and brands for me to choose from and compare, which allows me to pick the one I like the most."

topic 4
A: "I see a lot of people listen to music right when they wake up to help them feel alert. But if I listen to music as soon as I wake up, it gives me a headache all day and makes it hard for me to focus on anything. So, I just listen to music to relax when I’m feeling comfortable, not for any other reason."

B: "I usually listen to a pop or rock song as soon as I get out of bed in the morning because it helps me wake up instantly. If I don't listen to music at that moment, I don't know when I'll be able to get up and go to work."

C: "My brothers and friends often say that I have a beautiful voice, so I often sing when I meet them. I usually play music on the TV and hold the remote control, pretending it's a microphone so I can sing."

D: "I have a habit of listening to music while studying; it helps me stay motivated and alert while doing my assignments. If I don't play music, I could fall asleep at any moment, and I'll study in a discouraged mood."

topic 5
A: "My hometown is in the countryside, and we have a very large and beautiful farm. I’ve been learning to ride horses since I was a child, and it’s still my hobby to this day. Whenever I want to relax or enjoy the scenery, I ride my horse along the farm and across the meadows."

B: "My husband and I often wake up early and go to a nearby forest for exercise. We usually go jogging in the early morning to stay healthy, and we really enjoy the fresh air and natural scenery in the forest."

C: "I used to love mountain biking, enjoying the thrill of riding down steep slopes. It was really an amazing and adventurous feeling. However, after an injury from a fall, I became haunted by the fear of crashing and now I'm scared of this sport. But I still love the mountains, so I’ve decided to just go hiking every weekend instead."

D: "My father often encourages me to ride horses because it’s a sport he enjoys. But I’m very afraid of this animal and never want to learn how to ride, even though there’s a riding school near my house. Instead, I prefer mountain biking with my friends to conquer high peaks."

topic 6
A: "My friends often invite me to go jogging on the street, but I find it too dangerous. There’s a lot of traffic, which can be dangerous for people jogging on the street. So, I bought a one-year gym membership and go there to exercise every day."

B: "I see many people wake up early to go jogging and exercise to stay healthy. As for me, I usually walk along the beach simply to relax because there’s a beautiful beach near my house. Every morning, I spend time walking on the white sand; it really helps a lot with my mental well-being."

C: "I usually wake up early in the morning to exercise, and I choose to jog on the street because of its convenience. I just need to step out of the house, and I can start exercising. However, I have to go jogging early to avoid cyclists. My friends go to the gym to exercise a lot, but I find something artificial about the whole thing."

D: "Near my house, there’s a stadium where many people go to exercise. I often run on the track there, and it makes me feel like I’m running more professionally. My personality is quite competitive, so I also time myself and race with my friends there."

topic 7
A: "My friends often advise me to exercise to maintain a good physique and health. However, I am very busy with a tight work schedule. Even if I weren’t busy, I still wouldn’t like to exercise. I feel uncomfortable as soon as I put on workout clothes. I don’t think exercise is something that suits me."

B: "I know that working out every day is good for my health and helps me get in shape. But what I've found is that exercising actually boosts my productivity a lot and really helps me focus better. So, I always try to squeeze in some exercise before heading to work—it definitely makes me more productive."

C: "We’ve all heard about the many benefits of exercising, and I know about them too. My friends often invite me to work out, but after I exercise, I end up feeling extremely exhausted and spend the rest of the day just lying around to recover."

D: "I often go to the gym to work out, but what really motivates me to workout is catching up with my friends there, not just for improving my health. Plus, it’s a great way to meet and make new friends. For me, exercising is just another chance to socialize"

topic 8
A: "I am a big fan of newly released movies, but the cost of going to the cinema is too high. I'm just a student, so I can't afford to go to the cinema regularly to indulge in my hobby. Therefore, I think the internet is great because it allows me to watch movies for free at home. I save both the time of going to the cinema and a considerable amount of money."

B: "In today's digital age, the internet helps us access social media to stay constantly connected with friends. Especially since I have relatives mainly living abroad or in distant cities, the internet has been a great help for my family to stay in touch. We often video call each other to share daily stories."

C: "The internet is a great resource for research, finding materials, and useful information for studying. My friends and I often go to each other's houses to do homework together. Instead of spending hours trying to figure out how to do our homework, we quickly go online and find the answers."

D: "I see that people often use the internet to watch movies, read newspapers, quickly update the news, and so on. But I usually use the internet to find directions and public transport to my friends' and relatives' houses. I'm a forgetful person, and I often forget the way, even if I've been there a hundred times. So the internet helps me a lot in not getting lost and easily find nearby public transport."

topic 9
A: "I personally don't like and don't have a talent for fine arts, especially painting. But I see it as a great way to engage in social charity activities. I'm passionate about teaching children how to draw because I love kids. I'm also part of a volunteer organization that specializes in teaching art to poor children, which makes me very happy."

B: "I think drawing with my children is a great way to understand them better. No matter how busy my work is, I always make time to sit and draw with my kids. This helps us bond more and gives me the chance to talk with them more."

C: "I've loved literature, art, and drawing since I was a child. Now, I'm a writer and a comic book creator. In my stories, I occasionally include some illustrations to make the book more vivid and lively."

D: "I'm currently taking a drawing course and I really want to be serious about it. When practicing drawing, I prefer not to draw with friends, even though they often invite me to join them. I want to focus entirely on my work."

topic 10
A: "I'm concerned about the Earth and the environment, so I always look for ways to use public transportation, like buses or trains, to reduce harmful emissions. I can't walk to work because it's too far from my home, but I always walk to the local market when I need to buy groceries."

B: "I had to take driving lessons to be able to drive to work. My mother works along the same route, so we often drive to work together. Occasionally, she takes over the driving, and I'm happy because driving together gives us more time to chat."

C: "I used to use my car a lot to get to work. But since I moved closer to the company, I always go there on foot. I have a friend who cycles for 20 minutes every day to work—can you imagine? She must be super fit!"

D: "I often choose to walk to work to save on gas money and to keep in shape. I usually walk to the company with a close friend. Sometimes we feel really tired but still push ourselves to walk all the way. There are times when we see a bus stop and have to resist the urge to hop on the bus."

topic 11
A: "I can study in different places, like coffee shops, libraries, or parks. For me, the location isn't that important because I have good concentration skills."

B: "I can't study in very noisy places because I can't focus on my homework. If I study in a café, I end up not getting anything done. So, I usually study in places such as my room in my house or in my office."

C: "I prefer listening to music while studying. I usually play motivational songs to help keep me alert, especially when studying in the morning. Music is like a cup of coffee, keeping me awake and motivated in my studies."

D: "I often can't focus on studying during the day; I feel tired and sleepy when I have to wake up early and study. So, I usually study at night when everyone in the house is asleep. The quiet atmosphere at night allows me to focus the best and be the most productive."

topic 12
A: "I don't like studying in very quiet places such as at home or in the library because I get sleepy easily and might even fall asleep while studying. There's a coffee shop near my house, and I often go there to study because the presence of other people makes me feel more motivated. I find that I achieve higher productivity and efficiency in my studies when I'm there."

B: "I notice that most people prefer doing their homework in the classroom, but for me, those chairs are way too hard and leave me sore all day. I prefer sitting under the trees in the park to study—it's cool, and the air is fresh. There's a famous coffee shop across from where I sit, and they serve really good coffee."

C: "The distance from my house to school is 20 km, and it usually takes me an hour to get there. So, when I'm on the train, I use the time to do homework and review the lessons for the day. Some people say that studying like this can be distracting, but I find it very effective for me."

D: "I don't like studying in very crowded places because I can't focus well. I usually sit on the sofa in the living room to study. My parents often travel for work, so my house is very quiet."
"""

def extract_topic_blocks(raw):
    raw = re.sub(r"(?i)\btopic\s*(\d+)([A-D])\s*:", r"topic \1 \2:", raw)
    matches = list(re.finditer(r"(?i)\btopic\s+(\d+)\s*:?", raw))
    blocks = {}
    for i, m in enumerate(matches):
        topic_no = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        blocks[topic_no] = raw[start:end].strip()
    return blocks

def extract_persons(block):
    pattern = re.compile(r"(?is)(?:Person\s*)?([A-D])\s*:\s*")
    matches = list(pattern.finditer(block))
    persons = {}
    for i, m in enumerate(matches):
        label = m.group(1).upper()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        text = block[start:end].strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if text:
            persons[label] = text
    return persons

def format_voice_info(persons):
    return "\n\n".join(
        f"Person {label}: {persons[label]}"
        for label in ["A", "B", "C", "D"]
        if persons.get(label)
    ).strip()

blocks = extract_topic_blocks(RAW_DATA)

updated = 0
for topic_no, title in TOPIC_MAP.items():
    topic, _ = Part2Topic.objects.get_or_create(
        version="gioi",
        title=title,
        defaults={"description": "Chủ đề Mày giỏi"}
    )

    persons = extract_persons(blocks.get(topic_no, ""))
    voice_info = format_voice_info(persons)

    if voice_info:
        topic.voice_info = voice_info
        if hasattr(topic, "voice_info_locked"):
            topic.voice_info_locked = True
        topic.save()
        updated += 1

    for i in range(1, 5):
        voice, _ = Part2Voice.objects.get_or_create(
            topic=topic,
            order=i,
            defaults={"question_text": f"Person {i}"}
        )
        voice.question_text = f"Person {i}"
        voice.audio_url = topic.audio_url
        voice.save()

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    print(f"Topic {topic_no}: {title} | Person đọc được: {len(persons)}/4 | voice_info: {len(voice_info)} ký tự")

print("")
print(f"DA_LUU_THONG_TIN_VOICE_CHO_{updated}_TOPIC")
''', encoding="utf-8")

print("DA_TAO_SCRIPT_AUTO_SAVE_VOICE_INFO")
