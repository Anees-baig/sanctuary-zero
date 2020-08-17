import asyncio, websockets, time, json, click, secrets, os, sys
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter

textsess = PromptSession()


class actnlist(object):
    def __init__(self, wbsocket, username, chatroom, servaddr):
        self.username = username
        self.chatroom = chatroom
        self.servaddr = servaddr
        self.wbsocket = wbsocket

    async def chekcomd(self, mesgdict):
        actiword = mesgdict["mesgtext"].split(" ")[0]
        if actiword == "/kick":
            if mesgdict["username"] == self.username:
                return await self.sendkick(mesgdict)
            else:
                return self.recvkick(mesgdict)
        elif actiword == "/stop":
            if mesgdict["username"] == self.username:
                return self.recvstop(mesgdict)
            else:
                return self.sendstop(mesgdict)
        elif actiword == "/purr":
            if mesgdict["username"] == self.username:
                return self.recvpurr(mesgdict)
            else:
                return self.sendpurr(mesgdict)
        elif actiword == "/exit":
            if mesgdict["username"] == self.username:
                return self.sendexit(mesgdict)
            else:
                return self.recvexit(mesgdict)
        else:
            return False

    async def sendkick(self, mesgdict):
        await self.wbsocket.send(json.dumps(mesgdict))
        return True

    def recvkick(self, mesgdict):
        mesgtext = mesgdict["mesgtext"]
        if self.username == mesgtext.split(" ")[1]:
            print("[" + obtntime() + "] " + formusnm(mesgdict["username"]) + " ⮞ You were removed from the chatroom by " + str(mesgdict["username"]))
            #print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>Leaving SNCTRYZERO...</yellow>"))
            sys.exit(0)
        else:
            print("[" + obtntime() + "] " + formusnm(mesgdict["username"]) + " ⮞ " + mesgtext.split(" ")[1] + " was removed from the chatroom by " + mesgdict["username"])
        return True

    def sendstop(self, mesgdict):
        return True

    def recvstop(self, mesgdict):
        return True

    def sendpurr(self, mesgdict):
        return True

    def recvpurr(self, mesgdict):
        return True

    def sendexit(self, mesgdict):
        return True

    def recvexit(self, mesgdict):
        return True


class emtyfind(Validator):
    def validate(self, document):
        text = document.text
        if text.strip() == "":
            raise ValidationError(message="You cannot send an empty message")


async def consumer_handler(actiobjc, websocket, username, chatroom, servaddr):
    async for recvdata in websocket:
        try:
            recvjson = json.loads(recvdata)
            if not await actiobjc.chekcomd(mesgdict=recvjson):
                if recvjson["chatroom"] == chatroom:
                    if recvjson["username"] != username:
                        print("[" + obtntime() + "] " + formusnm(recvjson["username"]) + " ⮞ " + recvjson["mesgtext"])
        except Exception as EXPT:
            pass


async def producer_handler(actiobjc, websocket, username, chatroom, servaddr):
    footelem = HTML("<b><style bg='seagreen'>" + username.strip() + "</style></b>@<b><style bg='seagreen'>" + chatroom + "</style></b> [<b><style bg='seagreen'>Sanctuary ZERO v15082020</style></b> running on <b><style bg='seagreen'>" + servaddr + "</style></b>]")
    complete = WordCompleter(["/kick", "/stop", "/exit", "/purr"])
    while True:
        with patch_stdout():
            mesgtext = await textsess.prompt_async("[" + obtntime() + "] " + formusnm(str(username)) + " ⮞ ", bottom_toolbar=footelem, validator=emtyfind(), completer=complete)
        sendjson = {"username": username.strip(), "chatroom": chatroom, "mesgtext": mesgtext.strip()}
        if not await actiobjc.chekcomd(mesgdict=sendjson):
            await websocket.send(json.dumps(sendjson))


async def hello(servaddr, username, chatroom):
    async with websockets.connect(servaddr) as websocket:
        actiobjc = actnlist(websocket, str(username), str(chatroom), str(servaddr))
        prod = asyncio.get_event_loop().create_task(producer_handler(actiobjc, websocket, str(username), str(chatroom), str(servaddr)))
        cons = asyncio.get_event_loop().create_task(consumer_handler(actiobjc, websocket, str(username), str(chatroom), str(servaddr)))
        sendmesg = json.dumps({"username": "SNCTRYZERO", "chatroom": chatroom, "mesgtext": str(username) + " has joined the chatroom"})
        await websocket.send(sendmesg)
        await prod
        await cons
        asyncio.get_event_loop().run_forever()


def obtntime():
    timestmp = time.localtime()
    timehour = str(timestmp.tm_hour)
    timemint = str(timestmp.tm_min)
    timesecs = str(timestmp.tm_sec)
    if int(timehour) < 10:
        timehour = "0" + timehour
    if int(timemint) < 10:
        timemint = "0" + timemint
    if int(timesecs) < 10:
        timesecs = "0" + timesecs
    timestrg = timehour + ":" + timemint + ":" + timesecs
    return timestrg


def randgene():
    numb = 8
    randstrg = ''.join(secrets.choice("ABCDEF" + "0123456789") for i in range(numb))
    return randstrg


def chekroom(strg):
    if len(strg) != 8:
        return False
    else:
        try:
            geee = int(strg, 16)
            return True
        except ValueError:
            return False


def formusnm(username):
    if len(username) < 10:
        return username + " " * (10 - len(username))
    elif len(username) > 10:
        return username[0:10]
    else:
        return username


@click.command()
@click.option("-u", "--username", "username", help="Enter the username that you would identify yourself with", required=True)
@click.option("-c", "--chatroom", "chatroom", help="Enter the chatroom identity you would want to enter in")
@click.option("-s", "--servaddr", "servaddr", help="Enter the server address you would want to connect to", required=True)
@click.version_option(version="16082020", prog_name="SNCTRYZERO Client by t0xic0der")
def mainfunc(username, chatroom, servaddr):
    try:
        os.system("clear")
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <b><seagreen>Starting Sanctuary ZERO v15082020 up...</seagreen></b>"))
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <lightgreen>Connected to " + servaddr + " successfully</lightgreen>"))
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <lightgreen>Session started at " + str(time.ctime()) + "</lightgreen>"))
        if chatroom is None:
            print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>Welcome " + username + "! You have joined a newly created chatroom</yellow>"))
            chatroom = randgene()
        elif chekroom(chatroom):
            print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>Welcome " + username + "! You have joined the specified chatroom</yellow>"))
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <lightgreen>Chatroom identity [" + chatroom.upper() + "] - Share to add members</lightgreen>"))
        asyncio.get_event_loop().run_until_complete(hello(servaddr, username, chatroom))
    except KeyboardInterrupt as EXPT:
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>Leaving SNCTRYZERO...</yellow>"))
        sys.exit()
    except OSError as EXPT:
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>A connection to the server could not be established</yellow>"))
        sys.exit()
    except websockets.exceptions.ConnectionClosedError as EXPT:
        print_formatted_text(HTML("[" + obtntime() + "] " + "SNCTRYZERO ⮞ <yellow>A connection to the server was lost</yellow>"))
        sys.exit()


if __name__ == "__main__":
    mainfunc()
