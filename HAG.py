import numpy
import cv2
import api
import pyautogui
import pygetwindow
# from PIL import imageGrab
import time
import random
import sys


TIME_TOLERANCE = (0, 0.1)

WINDOW_TITLE = "炉石传说"
WINDOW_SIZE = (700, 500)
WINDOW_POSITION = (10, 10)
DISPLAY_RESOLUTION = (1920, 1080)
# All positions below are relative position.
COMPT_MODE_BUTTON_POSITION = (350, 175)
BRAWL_MODE_BUTTON_POSITION = (350, 240)
START_GAME_BUTTON_POSITION = (538, 412)
START_BRAWL_BUTTON_POSITION = (593, 382)
END_TURN_BUTTON_POSITION = (600, 244)
CASUAL_MODE_BUTTON_POSITION = (491, 108)
SOMEWHERE_POSITION = (673, 45)
DECK_1_BUTTON_POSITION = (149, 161)
X_BETWEEN_DECK = 100
Y_BETWEEN_DECK = 90
NEXT_DECK_PAGE_BUTTON_POSITION = (422, 256)
PREV_DECK_PAGE_BUTTON_POSITION = (67, 256)
FINISH_SHUFFLE_BUTTON_POSITION = (350, 398)
HERO_POWER_BUTTON_POSITION = (437, 395)
SHUFFLE_IDENTIFY_REGION = (316, 377, 75, 41)
RESULT_IDENTIFY_REGION = (308, 280, 85, 55)
SEARCHING_IDENTIFY_REGION = (246, 97, 214, 49)
ERROR_01_IDENTIFY_REGION = (311, 210, 73, 19)
ERROR_02_IDENTIFY_REGION = (272, 222, 144, 70)
ERROR_03_IDENTIFY_REGION = (317, 126, 69, 33)
END_TURN_BUTTON_REGION = (567, 229, 62, 29)
SETTING_BUTTON_POSITION = (671, 479)
SURRENDER_BUTTON_POSITION = (350, 198)
ERROR_01_BUTTON_POSITION = (347, 306)
ERROR_03_BUTTON_POSITION = (285, 378)
GAME_LAUNCHER_POSITION = (290, 1043)
GAME_LAUNCHER_BUTTON_POSITION = (213, 969)

origin = pygetwindow.Point(10, 10)
win = 0
lose = 0
reconnect = 0
#LOG_MUTE_LEVEL = -1
pyautogui.FAILSAFE = False

# -------- Utils -------- #
def sleep(sec):
    time.sleep(sec + random.uniform(TIME_TOLERANCE[0], TIME_TOLERANCE[1]))
def logPrint(level=0, *args):
    if level > LOG_MUTE_LEVEL:
        print(time.asctime(), ':', *args)
def pause(sec):
    logPrint(2, 'Info: Script paused for', sec, 'seconds.')
    sleep(sec)
    logPrint(2, 'Info: Script resumed.')
def toRelPosition(absX, absY):
    return absX - origin.x, absY - origin.y
def toAbsPosition(relX, relY):
    return relX + origin.x, relY + origin.y
def toAbsBox(relBox):
    # return coordinates of upper-left point and lower-right point.
    return relBox[0] + origin.x, relBox[1] + origin.y, relBox[2], relBox[3]
def getMouseAbsPosition():
    return pyautogui.position().x, pyautogui.position().y
def getMouseRelPosition():
    temp = getMouseAbsPosition()
    return toRelPosition(temp[0], temp[1])
def getGameWindow(timeout=5):
    window = pygetwindow.getWindowsWithTitle(WINDOW_TITLE)
    while len(window) != 1:
        timeout -= 1
        if timeout < 0:
            return None
        if len(window) == 0:
            logPrint(4, "Error: Cannot locate the game window. Try relocation in 5 seconds.")
        if len(window) > 1:
            logPrint(4, "Error: Multiple game programs detected. Try relocation in 5 seconds.")
        sleep(5)
        window = pygetwindow.getWindowsWithTitle(WINDOW_TITLE)
    window = window[0]
    logPrint(1, "Game window is captured successfully.")
    window.resizeTo(WINDOW_SIZE[0], WINDOW_SIZE[1])
    window.activate()
    window.moveTo(WINDOW_POSITION[0], WINDOW_POSITION[1])
    return window.topleft
def click(position):
    x = pyautogui.position().x
    y = pyautogui.position().y
    pyautogui.click(toAbsPosition(position[0], position[1]))
    sleep(0.1)
    pyautogui.moveTo(x, y)
def clickComptMode():
    click(COMPT_MODE_BUTTON_POSITION)
def clickBrawlMode():
    click(BRAWL_MODE_BUTTON_POSITION)
def clickOnNextPage():
    click(NEXT_DECK_PAGE_BUTTON_POSITION)
def clickStartGame():
    click(START_GAME_BUTTON_POSITION)
def clickStartBrawl():
    click(START_BRAWL_BUTTON_POSITION)
def clickOnPreviousPage():
    click(PREV_DECK_PAGE_BUTTON_POSITION)
def clickEndTurn():
    click(END_TURN_BUTTON_POSITION)
def clickHeroPower():
    click(HERO_POWER_BUTTON_POSITION)
def clickOnDeck(num):
    deck = num
    if deck > 9:
        clickOnNextPage()
        deck -= 9
    else:
        clickOnPreviousPage()
    sleep(0.5)
    click((DECK_1_BUTTON_POSITION[0] + (deck - 1) % 3 * X_BETWEEN_DECK, \
           DECK_1_BUTTON_POSITION[1] + (deck - 1) // 3 * Y_BETWEEN_DECK))
def clickCasualMode(): # outdated
    click(CASUAL_MODE_BUTTON_POSITION)
def clickFinishShuffling():
    click(FINISH_SHUFFLE_BUTTON_POSITION)
def clickSomewhere():
    click(SOMEWHERE_POSITION)
def clickSetting():
    click(SETTING_BUTTON_POSITION)
def clickSurrender():
    clickSetting()
    click(SURRENDER_BUTTON_POSITION)
def clickDismissError01():
    click(ERROR_01_BUTTON_POSITION)
def clickDismissError03():
    click(ERROR_03_BUTTON_POSITION)
    sleep(0.5)
    click((ERROR_03_BUTTON_POSITION[0] + 30, \
           ERROR_03_BUTTON_POSITION[1]))
def clickLaunchGame_01():
    click(GAME_LAUNCHER_POSITION)
def clickLaunchGame_02():
    click(GAME_LAUNCHER_BUTTON_POSITION)
def findPngOnScreen(pngName, box, sim):
    if pyautogui.locateOnScreen(pngName + '.png', region=box, confidence=sim):
        return True
    else:
        return False
def isDefeat():
    return findPngOnScreen('images/defeat', toAbsBox(RESULT_IDENTIFY_REGION), 0.5)
def isWin():
    return findPngOnScreen('images/win', toAbsBox(RESULT_IDENTIFY_REGION), 0.5)
def isEndOfGame():
    return isWin() or isDefeat()
def isError01():
    return findPngOnScreen('images/error_01', toAbsBox(ERROR_01_IDENTIFY_REGION), 0.8)
def isError02():
    return findPngOnScreen('images/error_02', toAbsBox(ERROR_02_IDENTIFY_REGION), 0.8)
def isError03():
    return findPngOnScreen('images/error_03', toAbsBox(ERROR_03_IDENTIFY_REGION), 0.8)
def isShuffling():
    return findPngOnScreen('images/shuffling', toAbsBox(SHUFFLE_IDENTIFY_REGION), 0.8)
def isSearching():
    return findPngOnScreen('images/searching', toAbsBox(SEARCHING_IDENTIFY_REGION), 0.8)
def shouldEndTurn():
    return findPngOnScreen('images/shouldEndTurn', toAbsBox(END_TURN_BUTTON_REGION), 0.9)
def shouldPlay():
    return findPngOnScreen('images/shouldPlay', toAbsBox(END_TURN_BUTTON_REGION), 0.5)
def notMyTurn():
    return findPngOnScreen('images/notMyTurn', toAbsBox(END_TURN_BUTTON_REGION), 0.5)
def isPlaying():
    return (not isEndOfGame()) and (shouldPlay() or shouldEndTurn() or notMyTurn())
# ---- In-Game Operations ---- #
def endTurn():
    # call iff game is in progress! #
    if shouldEndTurn() or shouldPlay():
        clickEndTurn()
    elif notMyTurn():
        return
    elif isEndOfGame():
        return
    else:
        sleep(1)
        endTurn()
def useHeroPower():
    clickHeroPower()
# -------- Strategies -------- #
def strategy_ComptHunter():
    useHeroPower()
    endTurn()
def strategy_UsePower():
    useHeroPower()
def strategy_AFK():
    #endTurn()
    return
def strategy_ShootThenGiveUp():
    clickHeroPower()
    clickSurrender()
def strategy_IGiveUp():
    clickSurrender()
# -------- Commands -------- #
def init(timeout=5):
    logPrint(1, "Script initializing...")
    global origin
    origin = getGameWindow(timeout)
    if origin == None:
        origin = pygetwindow.Point(10, 10)
        return
    logPrint(1, "Game window captured.")
    time.sleep(1)
    return True
def autoMatch(deck, strategy):
    def autoReconnect():
        sleep(15)
        logPrint(3, "Info: Script re-initializing... [Beta]")
        global reconnect
        reconnect += 1
        pyautogui.moveTo(290, 1080, duration=0.5)
        sleep(1)
        logPrint(3, "Info: Script re-initializing... [1/2]")
        clickLaunchGame_01()
        sleep(20)
        logPrint(3, "Info: Script re-initializing... [2/2]")
        clickLaunchGame_02()
        sleep(10)
        while not init():
            logPrint(3, "Info: Cannot capture game window. Wait.")
            sleep(5)
        sleep(50)
        clickSomewhere()
        sleep(3)
        clickSomewhere()
        sleep(3)
        clickDismissError01()
        sleep(5)
        autoMatch(deck, strategy)

    if not init():
        global reconnect
        if not reconnect:
            reconnect -= 1
            autoReconnect()
    # todo: check main menu.
    # logPrint(1, "Selecting competitive-casual mode...") # outdated
    clickComptMode()
    sleep(4)
    clickOnDeck(deck)
    sleep(1)
    # clickCasualMode() # outdated
    logPrint(1, "Initialization done.")
    if grind(strategy, 999999) == 'E-02':
        autoReconnect()
    logPrint(5, "Fatal: [E-05] Script has touched the end.")
    return

def autoBrawl(deck, strategy):
    # beta
    init()
    clickBrawlMode()
    sleep(1)
    clickStartBrawl()
    if deck: clickOnDeck(deck)
    else: ""
    brawlGrind(strategy, 999999)
def brawlGrind(strategy, num):
    # beta
    for cycle in range(0, num):
        while not isSearching():
            clickStartBrawl()
        sleep(2)
        while isSearching():
            logPrint('matching...')
            time.sleep(5)
        while not isShuffling():
            clickStartBrawl()
            time.sleep(5)
        startPlay(strategy)
def grind(strategy, num):
    for cycle in range(0, num):
        clickOnDeck(DECK)
        sleep(1)
        clickStartGame()
        logPrint(1, "Searching for a worthy opponent...")
        sleep(1)
        while not isSearching():
            if isError01():
                logPrint(4, 'Error: [E-01] Cannot start game, probably because of a connection error. Try restart searching.')
                clickDismissError01()
                sleep(1)
                continue
            elif isError03():
                logPrint(4, 'Error: [E-03] Connection Error. Reconnecting...')
                clickDismissError03()
                sleep(1)
                continue
            else:
                logPrint(1, 'Searching interrupted. Restart searching...')
                clickOnDeck(DECK)
                sleep(1)
                clickStartGame()
                sleep(2)
        sleep(1)
        while isSearching():
            logPrint(1, 'Searching...')
            sleep(10)
        logPrint(2, 'Search ends.')
        sleep(5)
        if isError01():
            logPrint(4, 'Error: [E-01] Cannot start game, probably because of a connection error. Try restart searching.')
            clickDismissError01()
            sleep(1)
            continue
        if isError02():
            logPrint(5, 'Fatal: [E-02] Disconnected. Game crashed.')
            clickSomewhere()
            sleep(5)
            logPrint(2, 'Script terminated.')
            return 'E-02'
        elif isError03():
            logPrint(4, 'Error: [E-03] Connection Error. Try reconnection.')
            clickDismissError03()
            sleep(1)
            continue
        logPrint(2, 'Found a worthy opponent. Game will start soon.')
        if startPlay(strategy) == 'E-02':
            return 'E-02'
def startPlay(strategy):
    global win, lose
    def checkEndOfGame():
        if isEndOfGame():
            global win, lose
            result = '?'
            checkCounter = 0
            checkLimit = 5
            while result == '?' and checkCounter < checkLimit:
                if isDefeat():
                    lose += 1
                    result = 'LOSE.'
                elif isWin():
                    win += 1
                    result = 'WIN.'
                checkCounter += 1
            logPrint(2, 'Game ends with a', result)
            logPrint(2, 'Current record: WIN:', win, 'LOSE:', lose, 'Reconnect:', reconnect)
            clickSomewhere()
            return True
        logPrint(3, 'Warning: Fail to check the end of game.')
        return False
    if isEndOfGame():
        "Early Game End."
        logPrint(3, 'Warning: Early Game End detected, possibly due to an instant surrender from the opponent.')
        if checkEndOfGame():
            return
    while not isShuffling():
        "Wait for screen to update."
        logPrint(2, 'Info: Waiting for hand confirmation panel...')
        sleep(10)
        if isEndOfGame():
            logPrint(2, 'Info: This game ends before hand confirmation.')
            if checkEndOfGame():
                return
    while isShuffling():
        # TODO: shuffling strategy not implemented.
        clickFinishShuffling()
        logPrint(2, 'Hand confirmed.')
        sleep(1)
    logPrint(2, 'Game started.')
    clickCount = 0
    clickLimit = 40

    #15
    hasClicked = False
    while not isEndOfGame():
        "Now game start. Keep updating."
        if notMyTurn():
            "Disabled"
            logPrint(0, 'Game in progress. Opponent\'s turn.')
            hasClicked = False
            sleep(3)
        elif shouldEndTurn():
            "Disabled"
            logPrint(0, 'Game in progress. Player\'s turn. AFKing.')
            hasClicked = True
            # clickEndTurn()
            sleep(6)
        elif shouldPlay():
            if not hasClicked:
                logPrint(0, 'Game in progress. Player\'s turn. Using strategy.')
                strategy()
                hasClicked = True
                clickCount += 1
                sleep(10)
            else:
                logPrint(0, 'Game in progress. Player\'s turn. Opt-AFKing.')
                sleep(1)
                if clickCount >= clickLimit:
                    logPrint(2, "Info: Reached idle-maximum. Surrendered.")
                    clickSurrender()
                    sleep(8)
        else:
            logPrint(0, 'Cannot determine game stage. Game still in progress.')
            if isError02():
                logPrint(5, 'Fatal: [E-02] Disconnected. Game crashed.')
                clickSomewhere()
                sleep(5)
                logPrint(2, 'Script terminated.')
                return 'E-02'
            sleep(3)
    endCheckTimer = 0
    endCheckLimit = 5
    while isEndOfGame():
        if checkEndOfGame():
            logPrint(2, 'Game normally ends.')
            return
        endCheckTimer += 1
        sleep(3)
        if endCheckTimer >= endCheckLimit:
            logPrint(4, "Error: [E-04] Game End-check failed. Game abnormally ends.")
            return
def trackMouse(limit, game='off'):
    i = 0
    if not game is 'off':
        init()
    while True:
        print(getMouseRelPosition())
        time.sleep(1)
        i += 1
        if i > limit:
            break
def test(func):
    i = 0
    init()
    while True:
        print(func())
        time.sleep(1)
        i += 1
        if i > 9999:
            break
# ----------- PARAM ---------- #
LOG_MUTE_LEVEL = 0
DECK = 1
# ----------- Main ----------- #


win = 0
lose = 0
gold = 10110
xp = 453 / 1500
stage = 155
dust = 10180 + 4100
level = 4939/5224/5368
# ------------------ #
gold2 = 1620
level2 = 0/1/6883
# ---------------------------- #
if len(sys.argv) > 1 and int(sys.argv[1]):
    DECK = int(sys.argv[1])
autoMatch(DECK, strategy_AFK) #SFW
#autoMatch(8, strategy_AFK)
#test(shouldEndTurn)
#trackMouse(9999)
