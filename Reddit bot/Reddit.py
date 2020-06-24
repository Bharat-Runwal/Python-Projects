import praw 
import random
import re 
from cred import client_id , client_secret,passw,user_ag,username
import time 
DEBUG_MODE = False  # For Debug: Don't post to reddit, only print
debug_posted = []  # In debug mode, remember links

common_spam_list=['udemy','free','discount','coupon','course','save','money']
reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=passw,
                    user_agent=user_ag)

def find_spammers(query):
    spammers=[]
    for sub in reddit.subreddit('all').search(query,sort="new",limit=50):
        print(sub.title,sub.author,sub.url)
        if sub.author not in spammers:
            spammers.append(sub.author)
    return spammers

if __name__=='__main__':
    # spammers=find_spammers("Udemy")
    # for aut in spammers:
    #     print(str(aut))

    while True:
        current_search=random.choice(["udemy"])
        spam_content=[]
        users={}
        authors= find_spammers(current_search)
        for aut in authors:
            urls=[]
            count_sub=0
            count_trash=0
            try:
                for sub in reddit.redditor(str(aut)).submissions.new():
                    link=sub.url
                    title=sub.title
                    subr=sub.subreddit
                    id_s=sub.id
                    trash = False
                    for reg in common_spam_list:
                        if re.search(reg,title.lower()):
                            trash=True
                            trashy= [id_s,title]
                            if trashy not in urls:
                                urls.append([id_s,title,str(aut)])
                    
                    if trash:
                        count_trash+=1
                    count_sub+=1
                try:
                    score = count_trash/count_sub
                except: score=0.0
                print("User {} trashy score is: {}".format(str(aut), round(score,3)))

                if score >=0.5 and count_sub>1:
                    users[str(aut)]=[score,count_sub]

                    for d in urls:
                        spam_content.append(d)
            
            except Exception as e:
                print(e)
    
    for spam in spam_content:
        s_id=spam[0]
        s_user=spam[2]
        sub=reddit.submission(id=spam[0])
        start_time = sub.created_utc
        already_done=False

        for comment in sub.comments.list():
            text=comment.body
            if "*Beep boop" in text:
                print("the sub is already done")
                already_done=True
            if already_done:
                continue

            if time.time()-start_time <=86400 *10:
                link="http://reddit.com"+sub.permalink
                message = """*Beep boop*
I am a bot that sniffs out spammers, and this smells like spam.
At least {}% out of the {} submissions from /u/{} appear to be for Udemy affiliate links. 
Don't let spam take over Reddit! Throw it out!
*Bee bop*""".format(round(users[s_user][0]*100,2), users[s_user][1], s_user)
                try:
                    if DEBUG_MODE:
                        if link in debug_posted:
                            continue
                        print(f"Would've posted reply to post by {s_user}: {link}")
                        debug_posted.append(link)
                        continue

                    with open("posted_urls.txt","r") as f:
                        if_pos= f.read().split('\n')
                    if link not in if_pos:
                        print(message)
                        sub.reply(message)
                        print("We've posted to {} and now we need to sleep for 12 minutes".format(link))
                        with open("posted_urls.txt","a") as f:
                            f.write(link+'\n')
                        time.sleep(12*60)
                        break
                except Exception as e:
                    print(str(e))
                    time.sleep(12*60)    
        



