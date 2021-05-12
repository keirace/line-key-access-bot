# Line-Key-Access
**Smart door lock.**
**Connect. make your life easier.**
## introduction
owner can order bot to open door and also can authorize friend to open door at anytime
## requirements
python >= 3.4
## installation
**if you already install line bot sdk, uninstall it first**
* clone line bot sdk lastest version from [line-bot-sdk](https://github.com/line/line-bot-sdk-python)
  * Windows
    * run cmd as administator
    * change directory into line bot sdk
    * $ python setup.py install
  * Linux
    * $ change directory into line bot sdk
    * $ sudo python setup.py install
    
* To use speech-to-text, you need [cloud sdk](https://cloud.google.com/sdk/docs/install) installed and download [key](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/keys/create) as key.json to the same directory as app.py
