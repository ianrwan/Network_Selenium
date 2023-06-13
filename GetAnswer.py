import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException

class WebRobot():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    
    completed = 0
    answer = []

    def __init__(self, myAccount, myPassword):
        self.__account = myAccount
        self.__password = myPassword
        self._function = RobotFunction()

    def __logIn(self, suburl):
        self.driver.get("https://fishcoding.ntcu.edu.tw/"+suburl)
        try:
            self.driver.find_element(By.NAME, "email").send_keys(self.__account)
            self.driver.find_element(By.NAME, "password").send_keys(self.__password)
        except NoSuchElementException as msg:
            print(msg)
        self._function.submitClick('//button[@class = "btn" and @type = "submit"]')

    def switch(self, suburl):
        if suburl == '/login':
            self.__logIn(suburl)
        elif suburl == '/home':
            self.__goHome()
        elif suburl == '/explore':
            self.__goStage()

    def __goHome(self):
        percentData = self._function.gettext('//div[@class = "progress"]')
        self.completed = int(self._function.getPercentData(percentData))
        try:
            # self.driver.find_element(By.XPATH,'//a[@id="explore"]').click() 
            # it can't pass
            self.driver.find_element(By.ID, 'explore').click()
        except Exception:
            print(self.driver.current_url)
    
    def __goStage(self):
        allStage = None
        try:
            allStage = self.driver.find_elements(By.XPATH, '//div[@class = "chapter"]/parent::div')
        except NoSuchElementException as msg:
            print(msg)

        i = 0
        while(allStage[i].get_attribute("class").find("lock") == -1 and i < 9 ):
            i += 1
        print("Go to stage {}".format(i))
        allStage[i-1].click()
        self._function.submitClick('//a[@class = "go"]')

class CollectAnswer(WebRobot):
    def __init__(self, myAccount, myPassword):
        super().__init__(myAccount, myPassword)
            
    def __findAnswer(self):
        allAnswer = None
        try:
            allAnswer = self.driver.find_elements(By.XPATH, '//div[@class = "option"]')
        except NoSuchElementException as msg:
            print(msg)
        
        resultDetect = ""
        i = 0
        while(resultDetect != "答對囉!"):
            try:
                allAnswer[i].click()
            except ElementClickInterceptedException:
                self.driver.execute_script("window.scrollTo(0, 0);")
                allAnswer[i].click()
            self._function.submitClick('//div[@class = "submit"]')
            i += 1

            time.sleep(1)
            resultDetect = self._function.gettext('//div[@class = "notyf-announcer"]')
            print(resultDetect," ",i)

            if( resultDetect == "答錯囉!"):
                self._function.timeDectect('//div[@class = "clock"]')# 該網頁有部分 bug，強制解除
                self._function.submitClick('//div[@class = "cancel"]')
        return str(i)

    def goFirst(self):
        self.driver.get("https://fishcoding.ntcu.edu.tw/topic/1")
        time.slee
        page = self.driver.find_elements(By.XPATH, '//ul[@class = "pagination"]/li')
        if( page[0].get_attribute("class") == "inactive"):
            page[0].click()

    def runWholeStage(self):
        correct = ""
        for i in range(0, 6):
            correct += self.__findAnswer()
        self.answer.append(correct)

    def runWholeWeb(self):
        for i in range(0,9):
            print("Go to stage ", i+1)
            self.driver.get("https://fishcoding.ntcu.edu.tw/topic/"+str(i+1))

            time.sleep(1)
            page = self.driver.find_elements(By.XPATH, '//ul[@class = "pagination"]//li')
            if( page[0].get_attribute("class") == "inactive"):
                page[0].click()
            self.runWholeStage()
            print(self.answer)
    
    def outputData(self):
        self._function.fileOutput(self.answer.copy())

class QuickAnswer(WebRobot):
    def __init__(self, myAccount, myPassword):
        super().__init__(myAccount, myPassword)

    def inputData(self):
        self.answer = self._function.fileInput().copy()
    
    def __findAnswer(self, stageNum, exerciseNum):
        allAnswer = None
        answerStr = ""
        try:
            allAnswer = self.driver.find_elements(By.XPATH, '//div[@class = "option"]')
        except NoSuchElementException as msg:
            print(msg)
        answerStr = self.answer[stageNum-1]
        try:
            allAnswer[int(answerStr[exerciseNum-1])-1].click()
        except ElementClickInterceptedException:
                self.driver.execute_script("window.scrollTo(0, 0);")
                allAnswer[self.answer[stageNum][exerciseNum]-1].click()
        
        time.sleep(0.5)
        self._function.submitClick('//div[@class = "submit"]')

    def runWholeStage(self, stageNum):
        for i in range(0, 6):
            self.__findAnswer(stageNum, i+1)
    
    def runWholeWeb(self):
        stageNum = 0
        for i in range(0,9):
            print("Go to stage ", i+1)
            self.driver.get("https://fishcoding.ntcu.edu.tw/topic/"+str(i+1))
            stageNum = i+1

            time.sleep(1)
            page = self.driver.find_elements(By.XPATH, '//ul[@class = "pagination"]//li')
            if( page[0].get_attribute("class") == "inactive"):
                page[0].click()
            self.runWholeStage(stageNum) 

class RobotFunction():
    def __init__(self):
        self.__driver = WebRobot.driver
        
    def submitClick(self, directory):
        try:
            self.__driver.find_element(By.XPATH, directory).click()
        except NoSuchElementException as msg:
            print(msg)
        except ElementClickInterceptedException:
            self.submitClick(directory) 
        except ElementNotInteractableException:
            temp = self.__driver.find_element(By.XPATH, directory)
            action = webdriver.common.action_chains.ActionChains(self.__driver)
            action.move_to_element_with_offset(temp, 100, 150).click().perform()

    def gettext(self, directory):
        try:
            return self.__driver.find_element(By.XPATH, directory).text
        except NoSuchElementException as msg:
            print(msg)
    
    def getPercentData(self, str):
        percentPosition = str.find("%")
        storePercent = ''
        for i in range(3, 0, -1):
            if(str[percentPosition-i].isdigit()):
                storePercent += str[percentPosition-i]
        return storePercent
    
    def timeDectect(self, directory):
        try:
            self.__driver.find_element(By.XPATH, directory)
            print("waiting time")
            time.sleep(21)
            print("time up")
        except NoSuchElementException:
            print("no clock")
            return
    
    def fileInput(self):
        newFile = FileHandling()
        newFile.inputData()
        return newFile.answer
    
    def fileOutput(self, array):
        newFile = FileHandling()
        newFile.outputData(array)

class FileHandling():
    answer = []
    def __init__(self):
        pass

    def inputData(self):
        self.__file = open('answer.txt')
        for i in self.__file:
            self.answer.append(i)
        self.__file.close()
    
    def outputData(self, data):
        self.__file = open('answer.txt', 'w')
        for i in data:
            self.__file.write(i+"\n")
        self.__file.close()
    
class Admin():
    def __init__(self, myAccount, myPassword):
        self.__account = myAccount
        self.__password = myPassword

    def adminCollect(self):
        me = CollectAnswer(self.__account, self.__password)
        me.switch('/login')
        me.switch('/home')
        me.runWholeWeb()
        me.outputData()
        print("finish")

    def adminQuick(self):
        me = QuickAnswer(self.__account, self.__password)
        me.switch('/login')
        me.switch('/home')
        me.inputData()
        me.runWholeWeb()
        print("finish")

me = Admin("adt110112@gm.ntcu.edu.tw", "adt110112")
me.adminCollect()
print("finish")


# notyf__toast notyf__toast--dismissible notyf__toast--lower notyf__toast--error

