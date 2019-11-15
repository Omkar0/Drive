#import dependencies
from flask import Flask, request, session, make_response,jsonify, send_from_directory, send_file
from flask_restplus import Resource, Api, fields, reqparse
from flask_pymongo import PyMongo
import werkzeug
import os

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


#location to save file folder 
Upload_folderapi='./static/'

app.config['Upload_folder1']= Upload_folderapi
app.config['SESSION_TYPE'] = 'filesystem'


parser = reqparse.RequestParser()
parser.add_argument('filename', type=str, help='Please provide with your fileID')
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', action='append', help='Upload file')
parser.add_argument('email', type=str, help='Please provide with your emailID')


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
            temp = mongo.db.fs.files.find_one({"_id":x})
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


@api.route('/uploadFile')
class my_file_upload(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        tempList = []
        user = mongo.db.users.find_one({"userEid": args["email"]})
        if args['file'] and args['email']==user["userEid"]:
            for files in args['file']:
                try:
                    os.mkdir(app.config['Upload_folder1']+args['email']+'/')
                    files.save(os.path.join(app.config['Upload_folder1']+args['email']+'/', werkzeug.secure_filename(files.filename)))
                except FileExistsError:
                    files.save(os.path.join(app.config['Upload_folder1']+args['email']+'/', werkzeug.secure_filename(files.filename)))

                # temp = mongo.save_file(files.filename, files, base='fs', content_type=None)
                # tempList.append(temp)

        for i in tempList:
            user['rootFiles'].append(i)
            mongo.db.users.save(user)

        return "Done"

@api.route('/downloadFile')
class download_file(Resource):
    api.expect(parser)
    def post(self):
        args = parser.parse_args()
        tempPath = os.path.join(app.config['Upload_folder1']+args['email']+'/',werkzeug.secure_filename(args['filename']))
        directory = os.path.join(app.config['Upload_folder1']+args['email']+'/')
        print(tempPath, type(tempPath))
        abc = send_from_directory(directory=directory, filename=args['filename'])
        response = make_response(abc)
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers["Content-Disposition"] = "attachment; filename={}".format(args['filename'])
        return response


if __name__ == "__main__":
    app.run(debug=True)
