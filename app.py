from flask import Flask, render_template, request,jsonify,send_file
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os
import shutil
import pymongo

app=Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html") 

@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="POST":
        return render_template("search.html")

@app.route("/scrap",methods=["GET","POST"])
def scrapping():
    try:
        
        #giving a destination to save images during that running of the project
        save_place="Images"

        #------------------------------------------------------------
        if(os.path.exists(save_place)):
            shutil.rmtree(save_place) #This is to remove any all images after each search so only necessary file images will stay 
        #you can choose to do so as if this not be here than the program will take longer as it search through each images when further progress
         #------------------------------------------------------------
        #but if you dont want this to happen that just comment the above
        
        if(not os.path.exists(save_place)):
            os.mkdir(save_place)

        searchkey=request.form["searcher"].replace(" ","")
        searchlink=f"https://www.google.com/search?sca_esv=ab02dd2696e7e4b9&rlz=1C1CHBD_enIN1092IN1092&q={searchkey}&uds=AMwkrPsm7OC6wr_wb2psDRJUVbCqJ9Vxzbtx8Mq5hb4q6T1dFfvx91hWuM-owgPjuRrmEXvz2S9j6Di6CvWIKjPPmfoCKxAibCjhLqCPXZngh47iSW1RyZNcnRliH7KhpPDK_wFJcYZbwRgR6Ic5K7CTo9pcmwvatcDqxaAfhVHkpZUcGyEMUCZZQyl-IrmLULUOW52pNTTEsvbz8Pw_o36q5bdltrlZqvBETbB8MsYg9aHHaCbYlXYQqwDPod7YqiGDA71PqcAhYBXrswB3GfIfa6_0Z4PhJFcLuspuwxwns4Y9Xm6gaY4&udm=2&prmd=ivsnmbtz&sa=X&ved=2ahUKEwiFmveGu5KFAxXQoGMGHcc9B7wQtKgLegQIDhAB&biw=1366&bih=633&dpr=1"
        #To avoid blocked by google this helps so that it seems that a user is operating
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        surf=requests.get(searchlink,headers=headers)
        soup=bs(surf.content,"html.parser")
        img_box=soup.find_all("img")
        del img_box[0] #deleting the first element of the img_box list as there was no image here which produce error in the rest of program

        img_info=[] #stores the information of image that will be used later and is extracted from the web
        for index,Image in enumerate(img_box):
            img_link=Image["src"]
            img_data=requests.get(img_link).content
            image_dict={"Index":index,"Image_data":img_data}
            file_name=f"{searchkey}_{image_dict['Index']}.jpg"
            with open(os.path.join(save_place+"/",file_name),"wb") as f :
                f.write(img_data)
            img_details={"file_name":file_name,"link":img_link,"binary__img_data":img_data}
            img_info.append(img_details)
        #---------------------------------------------------------------------------------------------
        # # This portion of code is intended to be used  if you want to send thhhet data to your mondo db data bases
        # #mongo section start    
        # uri = "paste your own connection string here else keep this portion commented or it will throw error "
        # # Create a new client and connect to the server
        # client = pymongo.MongoClient(uri)

        # # Send a ping to confirm a successful connection
        # try:
        #     client.admin.command('ping')
        #     logging.info("Pinged your deployment. You successfully connected to MongoDB!")
        #     image_db=client["Images_database"]
        #     data_col=image_db["Images_data"]
        #     data_col.insert_many(img_info)
        # except Exception as e:
        #     logging.info(e)

        # #mongo section end [keep this section commented if you dont have a mongo db to avoid errors]
        #--------------------------------------------------------------------------------------------- 


        #locatig the images saved in the image folder and transferring tham to html template ot show over the web page      
        images_list=os.listdir(save_place+"/")
        paths=[]
        for photo_info in img_info:
            photo_name = photo_info["file_name"]
            for image_file in images_list:
                if photo_name == image_file:
                    image_path = os.path.relpath(os.path.join(save_place, image_file), start=os.getcwd())
                    path_dict = {"file_name": photo_name, "path": image_path,"link":photo_info["link"]}
                    paths.append(path_dict)
                    break  # Exit inner loop once a match is found)
        return render_template("result.html",paths=paths) #here paths are list of dictionaries sent to the html containuing link and data of images to show
        
    except Exception as e:
        logging.info(e)
        return f"failed to perform operation due to {e}"
# using send file function which will send that file which is clicked by the filename path so user is able to download

@app.route("/download/<path:filename>")
def download_file(filename):
    save_place = "Images"
    return send_file(os.path.join(save_place, filename), as_attachment=True)

if __name__ == "__main__":
    print(" * Serving Flask app 'app'")
    print(" * Debug mode: off")
    print(" * Running on http://localhost:5000/")  # Print this line
    app.run(host="0.0.0.0")

