def create_robotlist(self,filepath: Union[str, None]):
        #
        """
        begin by reading single frame and generating robot instances for all
        #detected contours
        Args:
            filepath: either FLIR camera or presaved video
        Returns:
            None
        """
        if filepath is None:
            try:
                cam = EasyPySpin.VideoCapture(0)
            except EasyPySpin.EasyPySpinWarning:
                print("EasyPySpin camera not found, using standard camera")
            # cam = cv2.VideoCapture(0)
        else:
            # Use when reading in a video file
            cam = cv2.VideoCapture(filepath)
            
        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


        success,firstframe = cam.read()
        resize_scale = self.camera_params["resize_scale"]
        resize_ratio = (
                self.width * resize_scale // 100,
                self.height * resize_scale // 100,
            )
        firstframe = cv2.resize(firstframe, resize_ratio, interpolation=cv2.INTER_AREA)

        crop_mask = cv2.cvtColor(firstframe, cv2.COLOR_BGR2GRAY)
        crop_mask = cv2.GaussianBlur(crop_mask, (5,5), 0)
        crop_mask = cv2.inRange(crop_mask, self.control_params["lower_thresh"], self.control_params["upper_thresh"])

        contours, _ = cv2.findContours(crop_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        areas = []  
        
        for contour in contours: #treating each contour as a robot
            # remove small elements by calcualting arrea
            area = cv2.contourArea(contour)
            areas.append(area)

        print(areas)
        print(np.mean(np.array(areas)))

        frame = cv2.cvtColor(crop_mask, cv2.COLOR_GRAY2BGR)
        for contour in contours: #treating each contour as a robot
            # remove small elements by calcualting arrea
            area = cv2.contourArea(contour)

            if area > np.mean(np.array(areas))/2:  # and area < 3000:# and area < 2000: #pixels


                x, y, w, h = cv2.boundingRect(contour)
                current_pos = [(x + x + w) / 2, (y + y + h) / 2]

                x,y = current_pos

                x_1 = int(x - self.control_params["bounding_length"] / 2)
                y_1 = int(y - self.control_params["bounding_length"] / 2)
                w = self.control_params["bounding_length"]
                h = self.control_params["bounding_length"]


                #if w > max_width:
                #    max_width = w*self.control_params["area_filter"]
                #if h > max_height:
                #    max_height = h*self.control_params["area_filter"]


                robot = Robot()  # create robot instance
                robot.add_position(current_pos)  # add position of the robot
                robot.add_crop([x_1, y_1, w, h])
                self.robot_list.append(robot)

                # add starting point of trajectory
                self.num_bots += 1
                
                cv2.drawContours(frame, contour, -1, (0, 0, 255), 2)

        #create checkboxes for each robot
        self.robot_window = Frame(master= self.main_window)#Toplevel(self.main_window)
        self.robot_window.grid(row=1,column=4, rowspan=7)
        self.create_robot_checkbox(self.robot_window)
                
        cv2.imwrite("src/imgs/initialmask.png",frame)
        cam.release()
      