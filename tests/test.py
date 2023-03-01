import keyboard
print(keyboard.read_key())
'''while True:
   
    print(keyboard.read_key())
    if keyboard.read_key() == "a":
        break'''



def delete_bots(self,k):
    #delete single bots
    for bot_id in range(self.num_bots):
        if k == ord(str(bot_id+1)):
                del self.robot_list[bot_id]
                self.num_bots -= 1