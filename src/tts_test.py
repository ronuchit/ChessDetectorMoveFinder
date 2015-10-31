import pyttsx
engine = pyttsx.init()
horizontalPos = None
verticalPos = None
playerColor = None
text = "Move to ay 1"
myVoice = 
engine.say(text)
voices = engine.getProperty('voices')
for voice in voices:
	engine.setProperty('voice', voice.id)
	engine.say(text)
engine.runAndWait()