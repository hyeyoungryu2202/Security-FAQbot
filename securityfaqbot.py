
# coding: utf-8

# # Security Aid Chatbot (BoaanBot)

# In[1]:


#Import pandas to read excel file
import pandas as pd
#Read the excel file that has the faq and answers regarding startup security aid programs
boaanbot_excel = pd.read_excel('/Users/angieryu2202/Desktop/securityaidchatbot/startupsecurityaid.xlsx')
#Assign the data in the questions column to security_aid_questions
security_aid_excel_questions = boaanbot_excel['questions']
#Assign the data in the answers column to security_aid_answers
security_aid_excel_answers = boaanbot_excel['answers']


# In[2]:


#Inside the list security_aid_questions, add the data from security_aid_questions
security_aid_questions = []
for security_aid_excel_question in security_aid_excel_questions:
    security_aid_questions.append(security_aid_excel_question.lower())


# In[3]:


#Inside the list security_aid_answers, add the data from security_aid_answers
security_aid_answers = []
for security_aid_excel_answer in security_aid_excel_answers:
    security_aid_answers.append(security_aid_excel_answer)


# In[4]:


#Import the necessary modules
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

update_id = None
#List to store the unanswered questions so that the administrator could check which questions were unanswered
unanswered_questions=[]

def main(security_aid_questions):
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    
    mytoken = '624780285:AAFb8NRL_AyNIorAxDBbTzIE2Bkq1S6Ew3s' #your token
    bot = telegram.Bot(mytoken)   

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot, security_aid_questions)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1

def echo(bot, security_aid_questions):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        
        # print (update.message.text)
        
        if update.message:
            check_for_faq(update, security_aid_questions)
        
def check_for_faq(update, security_aid_questions):
    question = update.message.text
    #List to store the index values
    value_indexes = []
    #List to store the related questions
    related_questions = []
    hi_words = ["hey", "hi", "sup", "hello", "yo", "/start"]
    bye_words = ["bye", "adios", "goodbye", "byebye", "end"]
    #Tokenize the questions in security_aid_questions
    tokenized_models = [word_tokenize(i) for i in security_aid_questions]
    stopset = set(stopwords.words('english'))
    #List to store the tokenized_models after it has been removed of stop words
    clean_models1 = []
    #Remove the stopwords from tokenized_models
    for m in tokenized_models:
        stop_m = [i for i in m if str(i).lower() not in stopset]
        clean_models1.append(stop_m)
    #List to store the items in clean_models1 after the lists inside the clean_models1 has been joined by " "
    exList = []
    #Join the lists inside clean_models by " "
    for item in clean_models1:
        c = " ".join(item)
        exList.append(c)
    #If question is in security_aid_questions, return the corresponding answer
    if question.lower() in security_aid_questions:
        question_number = security_aid_questions.index(question.lower())
        update.message.reply_text(security_aid_answers[question_number])
    #If what the user has inputted is in bye_words, reply with "Bye! Hope you have a pleasant day:)"    
    elif question.lower() in bye_words:
        update.message.reply_text("Bye! Hope you have a pleasant day:)")
    #If what the user's input is in hi_words, greet the user and give the users the list of questions he or she can choose from
    elif question.lower() in hi_words:
        Quest = "Hi! How would you like to improve your startup's security? You can choose a question from the list below: " + "\n"
        for quest in security_aid_questions:
            Quest += "-" + quest + "\n"
        update.message.reply_text(Quest)
    #If the user wants to see the unanswered questions, type in unanswered questions, and the chatbot will return the list of unanswered questions
    elif question.lower() == "unanswered questions":
        update.message.reply_text(unanswered_questions)
    #If the question is not in security_aid_questions, find and return top five related questions and an apologetic message for not being able to answer the question
    else:
        #Add the qustion to the unanswered_question list for the administrator to find out what questions were unanswered
        unanswered_questions.append(question.lower())
        #Tokenize the question
        tokenized_question = word_tokenize(question)
        stopset = set(stopwords.words('english'))
        #Remove the stopwords
        clean_question1 = [k for k in tokenized_question if str(k).lower() not in stopset]
        #Join the clean_question1 by " "
        clean_question = " ".join(clean_question1)
        #Add the clean_question to exList
        exList.append(clean_question)
        vec = CountVectorizer()
        #Vectorize exList
        data = vec.fit_transform(exList)
        #Calculate the cosine similarity between the vectorized data and itself
        cos_sim = cosine_similarity(data, data)
        #Since the user's question was added to the end of the list, the last cosine similarity array is what we would need to see to find the top five related questions
        a = np.array(cos_sim[-1])
        #Change a into list
        myList = a.tolist()
        #Find the top two related questions after excluding itself which would have the highest cosine similarity
        values = sorted(myList, reverse=True)[1:3]
        #Find the index number of the top five related questions and append them to the list value_indexes
        for value in values:
            if value in myList:
                value_index = myList.index(value)
                value_indexes.append(value_index)
        
        ans = ""
        #Find the corresponding top two related questions
        for index_number in value_indexes:
            related_question = security_aid_questions[index_number]
            ans += related_question + "\n"
        #Return the top five related questions to the user
        update.message.reply_text("Related Questions: " + "\n" + ans)
        #Delete the last item which was the user's input in exList for the aforementioned code to be able to run again properly
        exList = exList[:-1]
        #Clear the related_questions list
        related_questions = related_questions.clear()
        #Clear the value_indexes list
        value_indexes = value_indexes.clear()
        #Return the apologetic message to the user
        update.message.reply_text("I am sorry that I cannot answer your question now, but I can answer you next time. I hope the questions listed above assist you in the mean time.")

if __name__ == '__main__':
    main(security_aid_questions)

