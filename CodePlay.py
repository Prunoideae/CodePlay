
import os
import sys
import json
import glob
import ctypes
import urllib
import requests
import keyboard
import threading
import pygame.mixer
import importlib.util
from time import sleep
from pathlib import Path
import importlib.machinery

playlist=[]
offset=0
volume=100.0

def load_music(music_item):
	if music_item[1] == 0:
		pygame.mixer.music.load(music_item[0])
	else:
		pygame.mixer.music.load(os.path.dirname(os.path.abspath(__file__)) + "\\NetEaseCache\\" + music_item[0] + ".mp3")	
def play_music(music_item):
	pygame.mixer.music.play()
	if music_item[1] == 0:
		print ("Now playing:" + Path(music_item[0]).stem())
	else:
		print ("Now playing:" + music_item[2])		
def resume_music():
	if hasattr(codeplay, "custom_resume"):
		codeplay.custom_resume()
	else:
		pygame.mixer.music.unpause()
def pause_music():
	if hasattr(codeplay, "custom_pause"):
		codeplay.custom_pause()
	else:
		pygame.mixer.music.pause()	
def next_music():
	global offset
	if hasattr(codeplay, "custom_next"):
		offset = codeplay.custom_next()
	else:
		offset=1
def prev_music():
	global offset
	if hasattr(codeplay, "custom_prev"):
		offset = codeplay.custom_prev()
	else: 
		offset=-1
def volume_up():
	global volume
	if hasattr(codeplay, "custom_vup"):
		volume = codeplay.custom_vup(volume)
	else:
		volume=volume+10.0
	pygame.mixer.music.set_volume(volume/100)
	
def volume_down():
	global volume
	if hasattr(codeplay, "custom_vdown"):
		volume = codeplay.custom_vdown(volume)
	else:
		volume=volume-10.0
	pygame.mixer.music.set_volume(volume/100)
	
def init():
	os.system("cls")
	if hasattr(codeplay, "init"):
		codeplay.init()
	
	#output some info for playlist
	if hasattr(codeplay, "title"):
		print ("Playlist - " + codeplay.title)
	if hasattr(codeplay, "description"): 
		print (codeplay.description)
	
	#initialize the playlist
	#all from netease
	if hasattr(codeplay, "playlist"):
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))):
			fo = open(os.path.dirname(os.path.abspath(__file__)) + '\\NetEaseCache\\SongInfo.json')
			fjs=fo.read()
			fo.close()
		else:
			fjs="{data:{}}"
			
		songinfo=json.loads(fjs)
		for i in range(0, len(codeplay.playlist)):
			if codeplay.playlist[i][1] == 1:
				if not codeplay.playlist[i][0] in songinfo["data"]:
					r=requests.get("https://api.imjad.cn/cloudmusic/?type=detail&id=" + codeplay.playlist[i][0])
					ddecoded = json.loads(r.text)
					songinfo["data"][codeplay.playlist[i][0]] = ddecoded["songs"][0]["name"]
					
				if not glob.glob(os.path.dirname(os.path.abspath(__file__)) + "\\NetEaseCache\\" + codeplay.playlist[i][0] + ".*"):
					print ("Song " + ddecoded["songs"][0]["name"] + " not found, starting download...")
					r=requests.get("https://api.imjad.cn/cloudmusic/?type=song&id=" + codeplay.playlist[i][0])
					decoded = json.loads(r.text)
					r=requests.get(decoded["data"][0]["url"],allow_redirects=True)
					open(os.path.dirname(os.path.abspath(__file__)) + '\\NetEaseCache\\' + codeplay.playlist[i][0] + '.mp3','wb').write(r.content)
				toadd = codeplay.playlist[i]
				toadd.append(songinfo["data"][codeplay.playlist[i][0]])
				playlist.append(toadd)
			else:
				playlist.append(codeplay.playlist[i])
		fo = open(os.path.dirname(os.path.abspath(__file__)) + '\\NetEaseCache\\SongInfo.json','w')
		fo.write(json.dumps(songinfo))
		fo.close()
		
	#register hotkeys
	if hasattr(codeplay, "resumekey"):
		keyboard.add_hotkey(codeplay.resumekey, resume_music)
	else:
		keyboard.add_hotkey("ctrl+shift+r", resume_music)

	if hasattr(codeplay, "pausekey"):
		keyboard.add_hotkey(codeplay.pausekey, pause_music)
	else:
		keyboard.add_hotkey("ctrl+shift+p", pause_music)

	if hasattr(codeplay, "nextkey"):
		keyboard.add_hotkey(codeplay.nextkey, next_music)
	else:
		keyboard.add_hotkey("ctrl+shift+x", next_music)

	if hasattr(codeplay, "prevkey"):
		keyboard.add_hotkey(codeplay.prevkey, prev_music)
	else:
		keyboard.add_hotkey("ctrl+shift+b", prev_music)

	if hasattr(codeplay, "vupkey"):
		keyboard.add_hotkey(codeplay.vupkey, volume_up)
	else:
		keyboard.add_hotkey("ctrl+shift+up", volume_up)
		
	if hasattr(codeplay, "vdownkey"):
		keyboard.add_hotkey(codeplay.vdownkey, volume_down)
	else:
		keyboard.add_hotkey("ctrl+shift+down", volume_down)
	
	#start song playing
	load_music(playlist[0])
	
	for t in threads:
		t.setDaemon(True)
		t.start()

def music_loop():
	global offset
	nowplaying=-1
	while True:
		if hasattr(codeplay, "playlist") == False:
			mitem = codeplay.custom_list(offset)
			offset = 0
			load_music(mitem)
			play_music(mitem)
		else:
			nowplaying = nowplaying +1
			
			if nowplaying >= len(playlist):
				nowplaying = nowplaying % len(playlist)
				
			load_music(playlist[nowplaying])
			play_music(playlist[nowplaying])
				
		while True:
			sleep(0.1)
			
			#play next song if music stoped
			if pygame.mixer.music.get_busy() != 1:
				break
				
			#move pointer and play next song
			if offset!=0:
				if hasattr(codeplay, "playlist") == True:
					nowplaying = nowplaying + offset - 1
					offset = 0
					if nowplaying == -2 :
						nowplaying = len(playlist) - 2
				break

def event_loop():
	while True:
		sleep(0.1)
	
LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * LF_FACESIZE)]

font = CONSOLE_FONT_INFOEX()
font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
font.nFont = 14
font.dwFontSize.X = 0
font.dwFontSize.Y = 14
font.FontFamily = 54
font.FontWeight = 400
font.FaceName = "Consolas"

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
ctypes.windll.kernel32.SetCurrentConsoleFontEx(
	handle, ctypes.c_long(False), ctypes.pointer(font))
	
threads = []
t1 = threading.Thread(target=music_loop)
threads.append(t1)

if __name__ == "__main__":
	if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "\\NetEaseCache\\"):
		os.makedirs(os.path.dirname(os.path.abspath(__file__)) + "\\NetEaseCache\\")
		
	if len(sys.argv) > 1:
		pygame.mixer.init()
		print (sys.argv[1])
		spec = importlib.util.spec_from_loader("module.name", importlib.machinery.SourceFileLoader("module.name", sys.argv[1]))
		codeplay = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(codeplay)
		
		init()
		event_loop()
	else:
		print ("Argument number mismatch!")
		
