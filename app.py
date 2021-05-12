from dotenv import load_dotenv
load_dotenv()
import os, cv2, datetime, urllib, pyaudio, time, json
from pydub import AudioSegment
from google.cloud import speech_v1 as speech
from flask import Flask, request, abort, render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)
from pyngrok.conf import PyngrokConfig
from pyngrok import ngrok
from pydub.playback import play
from google.oauth2 import service_account
import io

NGROK_TOKEN = os.environ['NGROK_TOKEN']
pyngrok_config = PyngrokConfig(region="jp")
ngrok.set_auth_token(NGROK_TOKEN)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=("key.json")

# Prepare web framework
app = Flask(__name__, static_url_path='/static')
app.config['TESTING'] = True
app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'development'

CH_ACCESS_TOKEN = os.environ['CH_ACCESS_TOKEN']
CH_SECRET = os.environ['CH_SECRET']
line_bot_api = LineBotApi(CH_ACCESS_TOKEN)
handler = WebhookHandler(CH_SECRET)

@app.route('/')
def main():
    ''' Main page rendering '''
    print(request.headers)
    print(request.get_data(as_text=True))
    return render_template('main.html')

@app.route('/webhook', methods=['POST'])
def callback():
    """ Main webhook  """
    # get X-Line-Signature header and body   
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Request body: " + body)
    # handle webhook body and signature
    try:
        handler.handle(body, signature)     
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as err:
        print(err)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    if isinstance(event.source, SourceUser):
        if event.message.text.startswith('#'):
            cmdline = event.message.text[:]
            cmdargs = cmdline.split(' ')
            if cmdargs[1] == 'print':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.source.user_id)
                )
            elif cmdargs[1] == 'cap':
                cap = cv2.VideoCapture(0)
                _, frame = cap.read()
                name = "img_" + str(datetime.datetime.now()).split('.')[0] \
                       .replace(':', '-').replace(' ', '_')+ ".jpg"
                cv2.imwrite(os.path.join(os.path.dirname(__file__), '/static/%s'%(name)), frame)
                new_url = endpoint + '/static/%s'%(name)
                cap.release()
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(new_url, new_url)
                )
            
            elif cmdargs[1] == 'echo':
                text = ' '.join([str(elem) for elem in cmdargs[2:]]) 
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text)
                )
            elif cmdargs[1] == 'flex1':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['share_access'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            elif cmdargs[1] == 'flex2':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['confirmation'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            elif cmdargs[1] == 'flex3':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['remote_access'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="I don't understand.")
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Not Supported.")
            )
    if isinstance(event.source, SourceGroup):
            if event.message.text[:] == 'flex1':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['share_access'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            elif event.message.text[:] == 'flex2':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['confirmation'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            elif event.message.text[:] == 'flex3':
                message = FlexSendMessage(alt_text="hello", contents=json.loads(open("flex.json", 'rb').read().decode('utf8'))['remote_access'])
                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
            else:
                pass
        # print(event.source.text)

@handler.add(MessageEvent, message=AudioMessage)
def message_audio(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    abspath = os.path.join(os.path.dirname(__file__), 'tmp.m4a')
    with open(abspath, 'wb+') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    audio = AudioSegment.from_file(abspath, "m4a")
    wav = abspath.replace("m4a", "wav")
    audio.export(wav, format='wav')
    client = speech.SpeechClient()

    with io.open(wav, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-EN",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=u"Transcript: {}".format(result.alternatives[0].transcript))
        )



if __name__ == '__main__':
    global endpoint
    public_url = ngrok.connect(5001, pyngrok_config=pyngrok_config)
    print(public_url)
    endpoint = public_url.public_url
    endpoint = endpoint.replace('http://', 'https://')
    line_bot_api.set_webhook_endpoint(endpoint + '/webhook')
    app.run(port=5001, use_reloader=False)
