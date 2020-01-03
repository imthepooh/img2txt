import telegram
import os
from google.cloud import vision

bot = telegram.Bot(token=os.environ["TOKEN"])

def imgcheck(request):
    if request.method == 'POST':
        update = telegram.Update.de_json(request.get_json(request),bot)
        chat_id = update.message.chat.id
        #message_id = update.message.message_id
        if update.message.text == '/start':
            res_text = '\nHello! Welcome. I am a bot that sends you text within an image sent to me.\nPlease check /help for more details' 
            bot.send_message(chat_id=chat_id,text=res_text)
        elif update.message.text == '/help':
            res_text = '\nPlease send the image containing the text in it as a photo. No special commands required.'
            bot.send_message(chat_id=chat_id,text=res_text)
        else:
            #print(update.message.photo[-1].file_id)
            file_id = update.message.photo[-1].file_id
            res_text = process_gv(bot,file_id)
            bot.send_chat_action(chat_id=chat_id,action='TYPING')
            if len(res_text) > 4096:
                fin_txt = [res_text[i:i+4096] for i in range(0,len(res_text),4096)]
                for text_msg in fin_txt:
                    bot.send_message(chat_id=chat_id,text=text_msg)        
            else:
                bot.send_message(chat_id=chat_id,text=res_text)
        #bot.delete_message(chat_id=chat_id,message_id=message_id)                
    return f'ok'

def process_gv(bot,file_id):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    file_key = bot.get_file(file_id)
    file_key.download('/tmp/sample.jpg')
    with open('/tmp/sample.jpg','rb') as f:
        content = f.read()
    image.content = content
    #image.source.image_uri = file_key.file_path
    #print(image)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    if len(texts) > 0:
        final_text = texts[0].description
    else:
        final_text = 'No text detected'
    return final_text