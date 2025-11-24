


#DATA STRUCTURE ON HOW PYTHON DICTIONARIES WORK UNDERNEATH THE HOOD
#HASHTABLE
#HASHFUNCTION
#HASHMAP
#HASH SETS
#COLLISION  -> sln (Separate chaining using linked lists or By using Linear probing) to set items and then to look up items


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
        

table = HashTableByChaining()
table.setitem("john", 1000)
table.setitem("jane", 1300)
res = table.getitem("jane")    # collision: both keys map to same index
table.setitem("jane", 16766)
res2 = table.getitem("jane")
print(res) # -> 200 (overwritten), wrong if we wanted both
print(res2)
print(table.buckets)