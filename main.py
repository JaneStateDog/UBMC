import UnityPy
import json
import os
import extras.typetree.GetTypeTrees as tt
from PIL import Image
import PySimpleGUI as sg
import zipfile as zp
import subprocess
from UnityPy.files import ObjectReader
import os




sg.theme("DarkTeal10")
title = "Unbeatable Mod Creator"



#Init
ROOT = os.path.dirname(os.path.abspath(__file__))

assetsToUse = ["resources.assets", "resources.assets.resS", "level2", "globalgamemanagers.assets", 
               "globalgamemanagers.assets.resS", "sharedassets12.assets", "sharedassets12.assets.resS"]
'''
difficulties = [
    "Beginner",
    "Easy",
    "Normal",
    "Hard",
    "UNBEATABLE",
    "Trailer",
    "Tutorial"
]'''

masterBankIDs = {"EMPTY DIARY": 0, "EMPTY DIARY DANTE": 1, "FOREVER NOW": 2, "FOREVER WHEN": 3, "Familiar": 4, "Forever Now - DOG_NOISE Remix": 5, 
                 "Mirror": 6, "NOISZ - Done In Love": 7, "NOISZ - True": 8, "OFFSETWIZARD": -1, "PROPERRHYTHM": -1, "PROPERRHYTHM MUST DIE": 11,
                 "Waiting": 12}


#Get config file
layout = [
    [sg.Text("New mod file name: "), sg.InputText(key="name")], 
    [sg.Text("New mod file location: "), sg.InputText(key="location"), sg.FolderBrowse()],
    [sg.Text()],
    [sg.Text("Old mod file location: "), sg.InputText(key="text"), sg.FileBrowse(file_types=(("Mod config", "*.json"),))],
    [sg.Button("Continue")]
]

nameWin = sg.Window(title, layout)

while True:
    event, values = nameWin.read()

    if event == "Continue":

        if values["name"] != "" and values["location"] != "":
            modName = values["name"]
            modLocation = os.path.join(values["location"], modName + ".json")
            
            config = {'BeatmapInfoDisplayMod': True, 'credits': True, 
                      'GameDataFolder': " ",
                      'songs': {},
                      'MusicFiles': {}}

            with open(modLocation, "wt") as file:
                json.dump(config, file, indent=4)
        else:
            modLocation = values["text"]
            modName = os.path.basename(modLocation).replace(".json", "")

            config = json.load(open(modLocation, "rt"))

        nameWin.close()
        break

    elif event == sg.WIN_CLOSED:
        quit()



#Get messages if credits is on
if config["credits"]:

    #Get the edited health message (the thing with our credits in it)
    healthMessage = Image.open("extras\\ourthings\\healthmessage.png")















#UI stuff!
def getSongsToReplace():
    songsToReplace = []
    for song in masterBankIDs:
        if masterBankIDs[song] != -1:
            songsToReplace.append(song)

    output = []
    for song in masterBankIDs:
        if masterBankIDs[song] != -1:

            if song in config["MusicFiles"] and 'nickname' in config['MusicFiles'][song]:
                output.append(f"{config['MusicFiles'][song]['nickname']} ({song})")
            else:
                output.append(song)

    return (songsToReplace, output)

def getSongsToReset():
    songsToReset = []
    for song in config["MusicFiles"]:
        songsToReset.append(song)

    output = []
    for song in songsToReset:
        if song in config["MusicFiles"] and 'nickname' in config['MusicFiles'][song]:
            output.append(f"{config['MusicFiles'][song]['nickname']} ({song})")
        else:
            output.append(song)

    return (songsToReset, output)

maxSize = 28523040
def getSizeText():
    usedSize = 0

    for songLoc in config["MusicFiles"]:
        try:
            usedSize += os.path.getsize(config["MusicFiles"][songLoc]["file"])
        except:
            pass

    if usedSize >= maxSize:
        tempTxt = "(MAXIMUM FILE SIZE REACHED!) "
        isTrue = True
    else:
        tempTxt = ""
        isTrue = False
    tempTxt += f"File size\n{usedSize}\nout of:\n{maxSize}"

    return (tempTxt, isTrue)


layout = [
    [sg.Text()],
    [sg.Text(f"Mod name: {modName}")],
    [sg.Text("Game data folder:"), sg.Input(default_text=config["GameDataFolder"]), sg.FolderBrowse()],
    [sg.Text()],
    [sg.Listbox(getSongsToReplace()[1], key="editSong", select_mode="LISTBOX_SELECT_MODE_SINGLE"), sg.Button("Edit song"), 
        sg.Text(getSizeText()[0], key="size")],
    [sg.Listbox(getSongsToReset()[1], key="resetSong", select_mode="LISTBOX_SELECT_MODE_SINGLE"), sg.Button("Reset song")],
    [sg.Text()],
    [sg.Button("Save")],
    [sg.Text()]
]

mainWin = sg.Window(title, layout, resizable=True, finalize=True)
mainWin.bind('<Configure>', "Configure")




while True:
    event, values = mainWin.read()


    if event == "Edit song":
        if values["editSong"] == []:
            print("There is no song selected")
            continue

        songName = values["editSong"][0]
        i = 0
        for song in getSongsToReplace()[1]:
            if song == values["editSong"][0]:
                songName = getSongsToReplace()[0][i]
                break

            i += 1
        

        try:
            temp = config["MusicFiles"][songName]["nickname"]
        except:
            temp = ""

        songLayout = [
            [sg.Text()],
            [sg.Text("Song nickname: "), sg.InputText(temp, key="nickname")],
            [sg.Text()]
        ]

        try:
            temp = config["MusicFiles"][songName]["file"]
        except:
            temp = ""

        beatmapList = []
        try:
            for dif in config["songs"][songName]:
                beatmapList.append(config["songs"][songName][dif])
        except:
            pass

        songLayout.extend([
            [sg.Text("Song file location:"), sg.Input(temp, key="file"), 
                sg.FileBrowse(file_types=(("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("OGG files", "*.ogg"),))],
            [sg.Text()],
            [sg.Listbox(beatmapList, key="editBeatmap", select_mode="LISTBOX_SELECT_MODE_SINGLE"), 
                sg.Button("Edit beatmap"), sg.Button("Add beatmap"), sg.Button("Delete beatmap")],
            [sg.Text()],
            [sg.Button("Save")],
            [sg.Text()]
        ])



        songWin = sg.Window(title, songLayout, modal=True, resizable=True, finalize=True)
        songWin.bind('<Configure>', "Configure")

        while True:
            newEvent, newValues = songWin.read()


            if newEvent == "Add beatmap":
                layout2 = [
                    [sg.Text("Beatmap location:"), 
                        sg.Input(key="text"), sg.FileBrowse(file_types=(("osu files", "*.osu"),))], 
                    [sg.Button("Add")]
                ]

                beatmapWin = sg.Window(title, layout2, modal=True)

                while True:
                    event2, values2 = beatmapWin.read()

                    if event2 == "Add":
                        beatmapList.append(values2["text"])

                        beatmapWin.close()
                        break

                    elif event2 == sg.WIN_CLOSED:
                        beatmapWin.close()
                        break

            elif newEvent == "Edit beatmap":
                if newValues["editBeatmap"] == []:
                    print("There is no beatmap selected")
                    continue

                layout2 = [
                    [sg.Text("Beatmap location:"), 
                        sg.Input(newValues["editBeatmap"][0], key="text"), sg.FileBrowse(file_types=(("osu files", "*.osu"),))], 
                    [sg.Button("Edit")]
                ]

                beatmapWin = sg.Window(title, layout2, modal=True)

                while True:
                    event2, values2 = beatmapWin.read()

                    if event2 == "Edit":
                        i = 0
                        for bm in beatmapList:
                            if bm == newValues["editBeatmap"][0]:
                                beatmapList[i] = values2["text"]
                            i += 1

                        beatmapWin.close()
                        break

                    elif event2 == sg.WIN_CLOSED:
                        beatmapWin.close()
                        break

            elif newEvent == "Delete beatmap":
                if newValues["editBeatmap"] == []:
                    print("There is no beatmap selected")
                    continue
                
                beatmapList.remove(newValues["editBeatmap"][0])

            elif newEvent == "Save":

                config["MusicFiles"][songName] = {}
                config["MusicFiles"][songName]["file"] = newValues["file"]
                config["MusicFiles"][songName]["nickname"] = newValues["nickname"]

                config["songs"][songName] = {}

                i = 0
                for bm in beatmapList:
                    config["songs"][songName][str(i)] = bm
                    i += 1

                songWin.close()
                break

            elif newEvent == sg.WIN_CLOSED:
                songWin.close()
                break

            songWin["editBeatmap"].update(beatmapList)

            for element in songWin.element_list():
                if type(element) != sg.Input and type(element) != sg.Listbox:
                    continue
                
                if type(element) == sg.Input:
                    element.expand(expand_x=True, expand_y=False, expand_row=False)
                elif type(element) == sg.Listbox:
                    element.expand(expand_x=True, expand_y=True, expand_row=False)

            songWin.Refresh()


    elif event == "Reset song":
        if values["resetSong"] == []:
            print("There is no song selected")
            continue

        songName = values["resetSong"][0]
        i = 0
        for song in getSongsToReset()[1]:
            if song == values["resetSong"][0]:
                songName = getSongsToReset()[0][i]
                break

            i += 1

        doReset = sg.popup_ok_cancel(f"Are you sure you want to reset\nthe song: {songName}")

        if doReset == "OK":

            config["songs"].pop(songName, None)
            config["MusicFiles"].pop(songName, None)

    elif event == "Save":

        if values[0] == "":
            print("There is no game data")
            continue

        if getSizeText()[1]:
            print("Your music files are too large, please remove some or compress them")
            continue

        config["GameDataFolder"] = values[0]

        with open(modLocation, "wt") as file:
            json.dump(config, file, indent=4)

        break

    elif event == sg.WIN_CLOSED:
        quit()


    mainWin["editSong"].update(getSongsToReplace()[1])
    mainWin["size"].update(getSizeText()[0])
    mainWin["resetSong"].update(getSongsToReset()[1])

    for element in mainWin.element_list():
        if type(element) != sg.Listbox:
            continue
        
        element.expand(expand_x=True, expand_y=True, expand_row=True)

    mainWin.Refresh()


mainWin.close()













#Get difficulties
difficulties = []
for song in config["songs"]:
    for dif in config["songs"][song]:
        failed = True
        for name in difficulties:
            if name == dif:
                failed = False
                break
        if failed:
            difficulties.append(dif)












#Get in and out directories along with game data
try:
    os.mkdir("out")
except:
    pass

OUT = f"out\\{modName}"


prefixOut = "UNBEATABLE [white label]_Data"




#Open the zip file for writing
zip = zp.ZipFile(f"{OUT}.rar", "w", compression=zp.ZIP_LZMA) #OH MY GOD THIS COMPRESSION IS AMAZING




#Move our edited code to the output
if config["BeatmapInfoDisplayMod"]:
    with open("extras\\ourthings\\editedcode.dll", "rb") as editedCode:
        zip.writestr(f"{prefixOut}\\Managed\\Assembly-CSharp.dll", editedCode.read())

else:
    with open("user\\in\\Managed\\Assembly-CSharp.dll", "rb") as editedCode:
        zip.writestr(f"{prefixOut}\\Managed\\Assembly-CSharp.dll", editedCode.read())






print("Gettings type trees")

tt.main(["BeatmapIndex", "10940"], config["GameDataFolder"], f"{config['GameDataFolder']}\\Managed", assetsToUse)

ttOut = "extras\\typetree\\out"

songsIndexNodes = json.load(open(f"{ttOut}\\10940Nodes.json", "rt", encoding="utf8"))["WhiteLabelMainMenu"]
songsIndex = json.load(open(f"{ttOut}\\10940.json", "rt", encoding="utf8"))

beatmapIndexNodes = json.load(open(f"{ttOut}\\BeatmapIndexNodes.json", "rt", encoding="utf8"))["BeatmapIndex"]
beatmapIndex = json.load(open(f"{ttOut}\\BeatmapIndex.json", "rt", encoding="utf8"))

print("Done getting type trees")





#Write tracks file for bank editing
songsList = []
for id in masterBankIDs:
    songsList.append("filler.mp3")

hasSongToFill = False
for song in config["MusicFiles"]:
    
    if masterBankIDs[song] != -1 and "file" in config["MusicFiles"][song] and config["MusicFiles"][song]["file"] != "":
        songsList[masterBankIDs[song]] = config["MusicFiles"][song]["file"]
        hasSongToFill = True


try:
    os.mkdir("extras//music")
except:
    pass


if hasSongToFill:
    print("Start editing master bank")

    with open("extras\\music\\00000000.txt", "wt") as tracks:
        for i in songsList:
            tracks.writelines(i + "\n")

    #Copy master bank to in for use with bs.main()
    with open(f"{config['GameDataFolder']}\\StreamingAssets\\Master.bank", "rb") as bank1:
        with open("extras\\music\\Master.bank", "wb") as bank2:
            bank2.write(bank1.read())

    #Copy filler mp3 to in for use with bs.main()
    with open("extras\\ourthings\\filler.mp3", "rb") as filler1:
        with open("extras\\music\\filler.mp3", "wb") as filler2:
            filler2.write(filler1.read())

    #Copy song files to in for use with bs.main()
    for file in config["MusicFiles"]:
        with open(config["MusicFiles"][file]["file"], "rb") as music1:
            with open(f"extras\\music\\{os.path.basename(os.path.normpath(config['MusicFiles'][file]['file']))}", "wb") as music2:
                music2.write(music1.read())



    #Run bank stuff code
    def cmd(string):
        subprocess.run(string, shell=True)

    #Make fsb
    cmd(f'cd extras\\fmod & fsbankcl.exe -format Vorbis -quality 82 -verbosity 5 -ignore_errors -o "{ROOT}\\extras\\music\\00000000.fsb" "{ROOT}\\extras\\music\\00000000.txt"')

    #Use fsb and import it into the bank
    cmd(f'cd extras\\reimport & quickbms.exe -w -r script.bms "{ROOT}\\extras\\music\\Master.bank" "{ROOT}\\extras\\music"')


    with open("extras\\music\\Master.bank", "rb") as file:
        zip.writestr(f"{prefixOut}\\StreamingAssets\\Master.bank", file.read())


    for root, dirs, files in os.walk("extras\\music"):
        for file in files:
            os.remove(os.path.join(root, file))

    print("Finished editing master bank")
else:
    with open(f"{config['GameDataFolder']}\\StreamingAssets\\Master.bank", "rb") as file:
        zip.writestr(f"{prefixOut}\\StreamingAssets\\Master.bank", file.read())








class FakeReader(ObjectReader):
    def __init__(self, reader: ObjectReader):
        self.__dict__.update(reader.__dict__)

def duplicate_obj(obj: ObjectReader, env = None) -> ObjectReader:
    # 1. get serialized file
    sf = obj.assets_file
    # 2. create a "new" object from the existing one
    new = FakeReader(obj)
    # 3. find unused path_id
    path_id = 99999
    for pid in sorted(x.path_id for x in env.objects):
        if pid == path_id:
            path_id += 1
        elif pid > path_id:
            break
    new.path_id = path_id
    # 4. add new obj to the serialized file
    sf.objects[path_id] = new
    return new






for r, d, fs in os.walk(config['GameDataFolder']):
    for f in fs:

        if str(f) not in assetsToUse:
            continue


        print("Going through:", f)
        env = UnityPy.load(os.path.join(r, f))



        #Get text asset template
        textAssTemp = -1
        for obj in env.objects:
            if obj.type == "TextAsset":
                textAssTemp = obj
                break



        for obj in env.objects:
            if obj.type == "MonoBehaviour": #Beatmap index and the song list

                data = obj.read()

                if data.name == "BeatmapIndex":
                    beatmapIndex["difficulties"] = difficulties
                    beatmapIndex["beatmaps"] = []

                    if textAssTemp == -1:
                        continue

                    for song in config["songs"]:
                        for dif in config["songs"][song]:
                            newObj = duplicate_obj(textAssTemp, env)

                            newData = newObj.read()
                            with open(config['songs'][song][dif], "rb") as file:
                                newData.script = file.read()
                            newData.save()

                            beatmapIndex["beatmaps"].append(
                                {
                                    "textAsset": {
                                        "m_FileID": 0,
                                        "m_PathID": newObj.path_id
                                    },
                                    "songName": song,
                                    "difficulty": dif
                                }
                            )

                    obj.save_typetree(beatmapIndex, beatmapIndexNodes)

                elif data.path_id == 10940:

                    if songsIndex["songs"] == []:
                        continue

                    songsIndex["songs"] = []

                    for song in config["songs"]:
                        songsIndex["songs"].append(song)

                    obj.save_typetree(songsIndex, songsIndexNodes)


            elif obj.type == "TextAsset": #Edit beatmaps

                data = obj.read()

                #Put in beatmap file IDs for the songs that are to be used
                '''for beatmap in beatmapIndex["beatmaps"]:
                    if beatmap["textAsset"]["m_PathID"] == obj.path_id:
                        for song in config["songs"]:
                            if song == beatmap["songName"]:
                                for difficulty in config["songs"][song]:
                                    if difficulty == beatmap["difficulty"]:
                                        with open(config['songs'][song][difficulty], "rb") as file:
                                            data.script = file.read()
                                            
                                        data.save()'''

            elif obj.type == "Texture2D": #Edit images (right now is used for credits and a little message from us)

                if config["credits"] == False: #If people are lame and stupid then don't put our messages in
                    continue

                data = obj.read()
                
                if obj.path_id == 4 and data.name == "healthandsafety":

                    data.image = healthMessage
                    data.save()






        #Don't save .resS files because it is unneeded and breaks them
        if ".resS" in f:
            continue


        #Save all the files
        zip.writestr(f"{prefixOut}\\{f}", env.file.save())




zip.close()