def handle_joystick(self, arduino: ArduinoHandler):
        #state buttons for acoustic button logic
        button_state = 0
        last_state = 0
        counter = 0
        switch_state = 0

        # Instantiate the controller
        joy = Joystick() 
        self.text_box.insert(END, "XBOX Connected\n")
        self.text_box.see("end")
    
        #initialize actions
        typ = 4
        input1 = 0
        input2 = 0
        input3 = 0
        
        while not joy.Back():

            #A Button Function --> Acoustic Module Toggle
            button_state = joy.A()
            if button_state != last_state:
                if button_state == True:
                    counter +=1
            last_state = button_state
            if counter %2 != 0 and switch_state !=0:
                switch_state = 0
                self.AcousticModule.start(ACOUSTIC_PARAMS["acoustic_freq"])
                print("acoustic: on")
            elif counter %2 == 0 and switch_state !=1:
                switch_state = 1
                self.AcousticModule.stop()
                print("acoustic: off")

            #Left Joystick Function --> Orient
            elif not joy.leftX() == 0 or not joy.leftY() == 0:
                Bxl = round(joy.leftX(),2)
                Byl = round(joy.leftY(),2)
                typ = 2
                input1 = Bxl
                input2 = Byl
                self.text_box.insert(END, "Left Joy\n")
                self.text_box.see("end")

            #Right Joystick Function --> Roll
            elif not joy.rightX() == 0 or not joy.rightY() == 0:
                Bxr = round(joy.rightX(),2)
                Byr = round(joy.rightY(),2)
                    
                angle = np.arctan2(Bxr,Byr)
                freq = CONTROL_PARAMS["rolling_frequency"]
                gamma = CONTROL_PARAMS["gamma"]
                typ = 1
                input1 = angle
                input2 = freq
                input3 = gamma
                self.text_box.insert(END, "Right Joy\n")
                self.text_box.see("end")
            
            #Right Trigger Function --> Positive Z
            elif joy.rightTrigger() > 0:
                typ = 2
                input3 = joy.rightTrigger()
                self.text_box.insert(END, "Right Trig\n")
                self.text_box.see("end")

            #Left Trigger Function --> Negative Z
            elif joy.leftTrigger() > 0:
                typ = 2
                input3 = -joy.leftTrigger()
                self.text_box.insert(END, "Left Trig\n")
                self.text_box.see("end")
        
            else:
                typ = 4
                input1 = 0
                input2 = 0
                input3 = 0
                self.text_box.insert(END, "Zeroed\n")
                self.text_box.see("end")

            #send command
            if arduino.conn is not None:
                arduino.send(typ,input1,input2,input3)
            
            #add delay and update window
            self.main_window.update()
            
        self.text_box.insert(END, "XBOX Disconnected\n")
        self.text_box.see("end")
        joy.close()
        arduino.send(4,0,0,0)
        self.AcousticModule.stop()