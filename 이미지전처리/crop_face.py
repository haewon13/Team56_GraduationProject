from googleapiclient import  discovery
from oauth2client.client  import GoogleCredentials
import sys
import io
import base64
from PIL import Image
from PIL import ImageDraw
from genericpath import isfile
import os
from oauth2client.service_account import ServiceAccountCredentials
 
NUM_THREADS = 10
MAX_RESULTS = 1
IMAGE_SIZE = 128, 128
 
class FaceDetector():
    def __init__(self):
        # initialize library
        #credentials = GoogleCredentials.get_application_default()
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        #구글 vision api에서 serviceaccount다운 후 './~~~' 위치에 넣어야 합니다.
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
                        './My Project 80882-59e9035ad9a9.json', scopes=scopes)
        self.service = discovery.build('vision', 'v1', credentials=credentials)
        #print ("Getting vision API client : %s" ,self.service)
 
    #def extract_face(selfself,image_file,output_file):
         
    def detect_face(self,image_file):
        try:
            with io.open(image_file,'rb') as fd:
                image = fd.read()
                batch_request = [{
                        'image':{
                            'content':base64.b64encode(image).decode('utf-8')
                            },
                        'features':[{
                            'type':'FACE_DETECTION',
                            'maxResults':MAX_RESULTS,
                            }]
                        }]
                fd.close()
         
            request = self.service.images().annotate(body={
                            'requests':batch_request, })
            response = request.execute()
            if 'faceAnnotations' not in response['responses'][0]:
                 print('[Error] %s: Cannot find face ' % image_file)
                 return None
                 
            face = response['responses'][0]['faceAnnotations']
            box = face[0]['fdBoundingPoly']['vertices']
            left = box[0]['x']
            top = box[1]['y']
                 
            right = box[2]['x']
            bottom = box[2]['y']
                 
            rect = [left,top,right,bottom]
                 
            print("[Info] %s: Find face from in position %s" % (image_file,rect))
            return rect
        except Exception as e:
            print('[Error] %s: cannot process file : %s' %(image_file,str(e)) )
             
    def rect_face(self,image_file,rect,outputfile):
        try:
            fd = io.open(image_file,'rb')
            image = Image.open(fd)
            draw = ImageDraw.Draw(image)
            draw.rectangle(rect,fill=None,outline="green")
            image.save(outputfile)
            fd.close()
            print('[Info] %s: Mark face with Rect %s and write it to file : %s' %(image_file,rect,outputfile) )
        except Exception as e:
            print('[Error] %s: Rect image writing error : %s' %(image_file,str(e)) )
         
    def crop_face(self,image_file,rect,outputfile):
        try:
            fd = io.open(image_file,'rb')
            image = Image.open(fd)  
            crop = image.crop(rect)
            im = crop.resize(IMAGE_SIZE,Image.ANTIALIAS)
            im.save(outputfile,"JPEG")
            fd.close()
            print('[Info] %s: Crop face %s and write it to file : %s' %(image_file,rect,outputfile) )
        except Exception as e:
            print('[Error] %s: Crop image writing error : %s' %(image_file,str(e)) )
         
    def getfiles(self,src_dir):
        files = []
        for f in os.listdir(src_dir):
            if isfile(os.path.join(src_dir,f)):
                if not f.startswith('.'):
                 files.append(os.path.join(src_dir,f))
 
        return files
     
    def rect_faces_dir(self,src_dir,des_dir):
        if not os.path.exists(des_dir):
            os.makedirs(des_dir)
             
        files = self.getfiles(src_dir)
        for f in files:
            des_file = os.path.join(des_dir,os.path.basename(f))
            rect = self.detect_face(f)
            if rect != None:
                self.rect_face(f, rect, des_file)
                 
    def crop_faces_dir(self,src_dir,des_dir):         
        # training data will be written in $des_dir/training
         
        des_dir_training = os.path.join(des_dir,'training')
         
        if not os.path.exists(des_dir):
            os.makedirs(des_dir)
        if not os.path.exists(des_dir_training):
            os.makedirs(des_dir_training)
         
        path,folder_name = os.path.split(src_dir)
        label = folder_name
         
        # create label file. it will contains file location 
        # and label for each file
        training_file = open('training_file.txt','a')
         
        files = self.getfiles(src_dir)
        for f in files:
            rect = self.detect_face(f)
 
            # replace ',' in file name to '.'
            # because ',' is used for deliminator of image file name and its label
            des_file_name = os.path.basename(f)
            des_file_name = des_file_name.replace(',','_')
             
            if rect != None:
                des_file = os.path.join(des_dir_training,des_file_name)
                self.crop_face(f, rect, des_file )
                training_file.write("%s,%s\n"%(des_file,label))
        
        training_file.close()
         
def main():
    #파일 위치 변경해야해요.
    srcdir = "C:\\Users\\jiki\\Documents\\deeplearning\\crop_src"
    desdir = "C:\\Users\\jiki\\Documents\\deeplearning\\crop_dest"
    
    detector = FaceDetector()
 
    detector.crop_faces_dir(srcdir, desdir)
    #detector.crop_faces_dir(inputfile,outputfile)
    #rect = detector.detect_face(inputfile)
    #detector.rect_image(inputfile, rect, outputfile)
    #detector.crop_face(inputfile, rect, outputfile)
     
if __name__ == "__main__":
    main()
