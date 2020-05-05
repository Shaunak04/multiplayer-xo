import asyncio
import json
import websockets


BOARD = {
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
    "7": "",
    "8": "",
    "9": "",
}
X_POS = set()
O_POS = set()
GAMEOVER = False
flag = 0
##Checking
#0 incomplete
#1 x wins
#2 o wins
#3 tie
def check_game():
    global flag
    l = list(BOARD.values())
    if l[1]==l[4] and l[4]==l[7]:
        x=l[1]
        if x=="X":
            #X WON THE GAME
            flag=1
        if x=="O":
            #O WON THE GAME
            flag=2
    elif l[0]==l[1] and l[1]==l[2] or l[0]==l[4] and l[4]==l[8]:
        x=l[0]
        if x=="X":
            flag=1
        #X WON
        if x=='O':
            flag=2
        #Y won
    elif l[3]==l[4] and l[4]==l[5] or l[0]==l[3] and l[3]==l[6]:
        x=l[3]
        if x=="X":
        #X won
            flag=1
        if x=="O":
        #O won
            flag=2
    elif l[6]==l[7] and l[7]==l[8] or l[2]==l[4] and l[4]==l[6]  :
        x=l[6]
        if x=="X":
        #X won
            flag=1
        if x=="O":
            #O WON THE GAME
            flag=2
    elif l[2]==l[5] and l[5]==l[8] :
        x=l[2]
        if x=="X":
        #X won
            flag=1
        if x=="O":
            #O WON THE GAME
            flag=2
    else:
        tie = True
        for p in l:
            if p == '':
                tie = False
                break
        if tie:
            flag = 3

    return flag

# Players connected
PLAYERS = set()
player_map = dict()
O_SET = False
X_SET = False

def board_state():
    global GAMEOVER
    global flag
    global BOARD
    return json.dumps({"type": "state", "gameover": GAMEOVER, "board": BOARD, "winner": flag})

def player_count():
    global PLAYERS
    return json.dumps({"type": "playercount", "count": len(PLAYERS)})

async def notify_players():
    if PLAYERS:
        message = player_count()
        await asyncio.wait([user.send(message) for user in PLAYERS])

async def notify_board_state():
    if PLAYERS:
        message = board_state()
        await asyncio.wait([user.send(message) for user in PLAYERS])

async def register_player(websocket):
    global O_SET
    global X_SET
    global PLAYERS
    global player_map
    # if O_SET and X_SET:
    #     return

    PLAYERS.add(websocket)
    if not O_SET:
        await websocket.send(json.dumps({"type": "player", "player": "O"}))
        player_map[websocket] = "O"
        O_SET = True
    elif not X_SET:
        await websocket.send(json.dumps({"type": "player", "player": "X"}))
        player_map[websocket] = "X"
        X_SET = True

    await notify_players()
async def unregister_player(websocket):
    global O_SET
    global X_SET
    global PLAYERS
    global player_map
    if player_map[websockets] == "O":
        player_map[websockets] = None
        O_SET = False
    elif player_map[websockets] == "X":
        player_map[websockets] = None
        X_SET = False
    PLAYERS.remove(websockets)

    await notify_players()

async def counter(websocket, path):
    global GAMEOVER
    await register_player(websocket)
    try:
        # send board state here
        async for message in websocket:
            data = json.loads(message)
            # notify board state after every reply
            if data["action"] == "set cell":
                BOARD[str(data["pos"])] = data["player"]
                if check_game() != 0:
                    GAMEOVER = True
                    print("Game Over")
                if check_game() == 1:
                    print("X won")
                elif check_game() == 2:
                    print("O won")
                elif check_game() == 3:
                    print("TIE")
                print(BOARD)

                await notify_board_state()
            elif data["action"] == "restart":
                pass
            else:
                print("Unknown message" + message)
                break
    except:
        print("Cannot add more than 2 players at a time...")
        return
    finally:
        await unregister_player(websocket)

start_server = websockets.serve(counter, "localhost", 80)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()