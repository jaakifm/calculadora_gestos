import cv2

class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)

        text_x = self.pos[0] + self.width // 2 - 15
        text_y = self.pos[1] + self.height // 2 + 15

        cv2.putText(img, self.value, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN,
                    3, (50, 50, 50), 3)