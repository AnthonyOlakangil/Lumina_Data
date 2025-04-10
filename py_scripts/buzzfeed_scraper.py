import pandas as pd
import re

def extract_stories():
    # The stories from the conversation
    stories_text = """
1. "I had a high school math teacher who refused to answer questions from the young women in his class because, 'You won't need to know math after you graduate.' He made it clear that it was because he figured we'd all be married and pregnant."

2. "When I was in undergraduate school, I had a meeting with my major advisor at the beginning of my senior year to discuss my grad school applications. He told me that as much as he enjoyed having me in his classes, his specialty was one that he couldn't advise. The reason he gave: It was too dangerous for a woman to travel to the archaeological sites I was studying in his classes."

3. "During the first day of high school physics, my teacher was asking basic questions to get a feel for our general physics knowledge. He called on a few guys and gently corrected them when they were wrong. He called on me, and as I started to answer, he cut me off to tell me to 'use my science words.'"

4. "Whenever I'm talking about my finance job, and I mention my boss, people always assume they're a man."

5. "Back in high school, I was overlooked for leadership positions in band for no reason other than the fact I was the only girl going for them. When I finally got president, I was co-president with a boy who got all the credit for doing none of the work. At the end of the year, he got the most prestigious award despite the fact that I had basically run the band for the year."

6. "The one thing that made me realize I would be discriminated against as a woman was in primary school when teachers would always ask for big strong boys to carry chairs, and I knew I could carry double what they could."

7. "It was a comment that actually came from my male supervisor. As most women did during COVID, I pretty well stopped wearing makeup. Prior to that, I would wear a very light face of makeup to work. On a day I wasn't wearing makeup to the office, my male supervisor said to me, 'You should wear makeup to work again; it would make everybody happier.' I was so disgusted. He made me feel like as a woman, I HAD to wear makeup to work to please everybody else."

8. "My parents only allowed me to walk to the local convenience store with my brother who is five years younger. I also wasn't allowed to get a job or my license during high school, but he was encouraged to do so."

9. "In college, I was at a science fair with a group from my class. I was standing by our poster with a guy from my group. We were going to be discussing the material and answering questions from anyone who was interested. It was mostly me answering the questions, so we just needed two people at the poster. The head of one of the prestigious schools at the university came over to ask some questions. Any time I would answer one, he would turn and ask the exact same question to my partner. He seemed amazed at the answers, the same ones I had just given him. He GRILLED us for a solid 15 minutes, and I was the only one with answers to his questions, but he only seemed to hear the answers when spoken by my male partner."

10. "I'm a disabled veteran and have disabled veteran plates on my car. On more than one occasion, someone approaches me and my husband to thank him for his service and sacrifice. He always corrects them by telling them it's me. Sometimes they'll then thank me, sometimes they'll walk away."

11. "I worked at a camp one summer, and we had a manual truck as our camp vehicle. I knew in theory how to drive a stick, but wanted a chance to actually try it. The camp director let one of the boys on staff drive the vehicle for errands without any instructions (and he was entirely incompetent at it), but wouldn't even let me drive it around the parking lot."

12. "Being excluded from activities my brothers were invited to because I 'wouldn't like it.'"

13. "I worked for a major insurance company selling auto and home insurance. I have a bachelor's degree and have worked for 25 years in various sales and management roles. All of the sales agents were paid a base salary. I thought my salary was fair until I found out that a younger male employee with less experience and no degree made almost $7K more than me. Years later, at the same company, I took on a different role which several people were hired for. During my negotiations, I asked for a salary that was in the range for the position. I did not ask for the capped amount, slightly lower. They told me that they were not paying any of the new hires that amount, and my salary was set at the starting salary."

14. "I applied for a joint mortgage with my husband. During the process of checking our current credit and commitments, we had a follow-up lender asking if Mr. N was planning to upgrade his car within the next year. I was a bit confused; my husband doesn't have a car. I realized that because there's one car between the two of us, the assumption was that it belongs to the man!"

15. "My boyfriend at the time was having trouble sleeping so, like a good girlfriend, I read a bunch of peer-reviewed studies on sleep, how to fall asleep easier, and better your sleep health. I texted him what I learned and included the articles. Still, he complained about not being able to sleep. Fast-forward a week or two later, and he excitedly told me that his sleep schedule was finally on track! I was happy for him and asked how he did it. He told me his friend, a man, gave him advice and it worked. What, exactly, did his friend tell him? Why, only EXACTLY what I told him two weeks prior!"

16. "I worked for a Comcast call center. I was the tech support you called when your cable or cable box wasn't working or you were setting up your new cable box. I don't know how many times I have been asked by male customers to transfer them to a man because they know what they are doing, and we silly women don't know how to do that."

17. "I used to work in retail customer-facing tech support as a repair technician. I was working in the repair room, and someone came in to see if I could take a last-minute customer out front. I let him know the cost of repair for a liquid-damage computer. Dude had the BALLS to look me right in the eye and say, 'I think I'll wait for the technician.'"

18. "In college, I was an engineering student and one of two women in my whole circuit's class. My professor called the girls up to the front of the room and auctioned us off, basically. He made the men compete to have us as lab partners 'because women are more organized and they'll write better reports.' I was LIVID. The other girl and I turned to each other and said, 'We choose each other as partners actually.'"

19. "I worked for an ice cream shop that had a couple of steady employees. Four of us make ice cream cakes. The two men didn't like making the cakes but would if they had to. When the female employee left, I got saddled with cake decorating because, as a woman, it's something I should be good at, according to my boss. I wasn't good at it because I was a woman; I was good at it because I had studied cake decorating alongside my mother when I was growing up because she decorated cakes for 15+ years."

20. "In grade school, boys were saying men were better at everything than women, including cooking because the greatest chefs in the world were men. I felt hopeless, like girls and women couldn't be good at anything."

21. "My manager treated me differently after having a baby. I had more experience, more accounts, and the least amount of mistakes but wasn't even considered for a promotion. Multiple people in the company were SHOCKED that I wasn't even given a chance to apply. After further reflection, I thought it was also a little suspicious that my manager, the director, and VP weren't married or had kids!"

22. "My first year teaching, I was the only female teacher at a new charter school. We were having some sort of gathering, and there was cake that no one had started eating yet. I didn't think much of it until one of the many male teachers handed me a serving knife to cut and serve the cake. They had been waiting the whole time for me to serve the cake because, apparently, that's something only women can do. I promptly put the knife down and excused myself to the restroom. Spoiler: I left after my contract for that year ended."

23. "I have a PhD in chemistry. Just over a year ago, I got hired at a huge pharmaceutical company, and my husband and I were preparing for a major move for the job. An assessor from the moving service my company provided came to determine the amount of insurance we needed for the move. Even though her paperwork was in my (rather feminine) name and she had been in contact with me, she called my husband 'doctor' and asked him if he was excited about his new job. I was in shock, but my husband just pointed at me and said, 'You'll have to ask her, she's the doctor.'"
    """
    
    # Initialize list to store stories
    stories = []
    
    # Split the text into individual stories and process them
    for story in stories_text.strip().split('\n\n'):
        # Skip empty lines
        if not story.strip():
            continue
            
        # Extract story number and text
        match = re.match(r'(\d+)\.\s*"(.+)"', story.strip())
        if match:
            story_num = int(match.group(1))
            story_text = match.group(2)
            
            stories.append({
                'story_number': story_num,
                'story_text': story_text
            })
    
    # Create DataFrame
    df = pd.DataFrame(stories)
    
    # Save to CSV
    df.to_csv('buzzfeed_stories.csv', index=False)
    print(f"Successfully extracted {len(stories)} stories and saved to buzzfeed_stories.csv")

if __name__ == "__main__":
    extract_stories()
