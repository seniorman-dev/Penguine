


#DATA STRUCTURE ON HOW PYTHON DICTIONARIES WORK UNDERNEATH THE HOOD
#HASHTABLE
#HASHFUNCTION
#HASHMAP
#HASH SETS
#COLLISION  -> sln (Separate chaining using linked lists or By using Linear probing) to set items and then to look up items


import os
import requests


class HashTableByChaining:
    
    #constructor
    def __init__(self,):
        self.Max = 100
        '''self.array = [
            None 
            for i in range(self.Max)
        ]'''
        # each bucket is a list (chain or linked list)
        self.buckets = [[] for _ in range(self.Max)]  # each bucket is a list (chain)
        
        
    def get_hash(self, key):
        h = 0
        for char in str(key):
            h += ord(char)
        return h % self.Max
    
    
    def setitem(self, key, value):
        h = self.get_hash(key=key)
        bucket = self.buckets[h]
        #if key exists, update it
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        #otherwise append new pair
        bucket.append((key, value))
        
        
    def getitem(self, key,):
        h = self.get_hash(key=key)
        bucket = self.buckets[h]
        for k, v in bucket:
            if k == key:
                return v
        return None
    
    
    def delitem(self, key):
        h = self.get_hash(key=key)
        bucket = self.buckets[h]
        #if key exists, delete it
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return True
            break
        #otherwise return False
        return False
        

'''table = HashTableByChaining()
table.setitem("john", 1000)
table.setitem("jane", 1300)
res = table.getitem("jane")    # collision: both keys map to same index
table.setitem("jane", 16766)
res2 = table.getitem("jane")
print(res) # -> 200 (overwritten), wrong if we wanted both
print(res2)
print(table.buckets)'''


def send_brevo_email(recipient: str, subject: str, content: str, sender: str, sender_name: str = "SenderXX"):
    """Send email via Brevo API"""
    
    #url = "https://api.brevo.com/v3/emailCampaigns"
    # CORRECT ENDPOINT FOR TRANSACTIONAL EMAILS
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "api-key": "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",  #f"{os.getenv("BREVO_API_KEY")}",
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"name": sender_name, "email": sender},
        "to": [{"email": recipient}],
        "subject": subject,
        #"name": content,
        "htmlContent": content
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        print(f"Email sent!: {response.json()}")  #response.json().get('messageId')
        return True
    else:
        print(f"Error: {response.json()}")
        return False

print(f"{send_brevo_email(recipient="coder.jay2001@gmail.com", subject="Hello Cacus!", content="fjfjhacjhcshcj", sender="japhetebelechukwu@gmail.com", sender_name="Japhet Alvin")}")