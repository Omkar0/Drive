#import dependencies
from flask import Flask, request, session, make_response,jsonify
from flask_restplus import Resource, Api, fields, reqparse
from flask_pymongo import PyMongo
import datetime
import json

#instantiate app
app = Flask(__name__)

#instatiate api-object
api = Api(app)
email = api.model('email', {
    "email" : fields.String()
})

#connect to database
app.config['MONGO_DNAME'] = 'drive'
app.config['MONGO_URI'] = 'mongodb+srv://vivek:vivek123@storage-r0mya.mongodb.net/drive'

#connect PyMongo to app
mongo = PyMongo(app)



@api.route('/getFile')
class GetFiles(Resource):
    @api.expect(email)
    def post(self):
        data = api.payload
        #Query user details using emailID
        files = mongo.db.users.find_one({"userEid": data["email"]})
        #inistialise dictionary for json response
        rootFolder = {}
        rootFiles = {}
        rootF = {}
        #to access folder obj to get details
        for i in files['rootFolder']:
            dictt ={ }  #file details
            tlist =[ ]  #folder list with file details
            for j in files['rootFolder'][i]:
                temp = mongo.db.fs.files.find_one({"_id":j})
                dictt = {
                            "fileId":str(temp['_id']),
                            "fileName":temp['filename'],
                            "contentType":temp['contentType'],
                            "uploadDate":temp['uploadDate']
                            }
                tlist.append(dictt)
            rootFolder[i] = tlist
        
        fileList = []
        for x in files['rootFiles']:
            print(x)
            temp = mongo.db.fs.files.find_one({"_id":x})
            print(temp)
            dictf = {
                        "fileId":str(temp['_id']),
                        "fileName":temp['filename'],
                        "contentType":temp['contentType'],
                        "uploadDate":temp['uploadDate']
                        }
            fileList.append(dictf)
        rootFiles["rootFile"] = fileList

        rootF['rootFolder'] = rootFolder


        return jsonify(rootF, rootFiles)






if __name__ == "__main__":
    app.run(debug=True, port=3131)