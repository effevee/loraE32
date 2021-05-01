import urequests

class influxdbPutData:
    
    def __init__(self,host,port,db,naamMeetpunt,naamTag,naamField,debug=False):
        self.naam = str(naamMeetpunt).replace(" ","_")
        self.tag = str(naamTag).replace(" ","_")
        self.field = str(naamField).replace(" ","_")
        self.host = host
        self.port = port
        self.db = db
        self.data = ""
        self.debug = debug
    
    def makeDataStringFieldisNumber(self,tagVal,fieldVal,timeStamp=0):
        try:
            tagVal=tagVal.replace(" ","_")
            if len(self.data)>0:
                self.data+="\n"
            self.data += self.naam + "," + self.tag+"="+str(tagVal)+" "+self.field+"="+str(fieldVal)
            if timeStamp != 0:
                self.data += " "+str(timeStamp)
            return True
        except Exception as E:
            if self.debug == True:
                print(E)
            return False
    
    def makeDataStringNodeFieldValue(self, node, tagVal, fieldVal, timeStamp=0):
        try:
            tagVal=tagVal.replace(" ","_")
            self.naam = node.replace(" ","_")
            if len(self.data)>0:
                self.data+="\n"
            self.data += self.naam + "," + self.tag+"="+str(tagVal)+" "+self.field+"="+str(fieldVal)
            if timeStamp != 0:
                self.data += " " + str(timeStamp)
            if self.debug:
                print(self.data)
            return True
        except Exception as E:
            if self.debug == True:
                print(E)
            return False

    def writeToInfluxdb(self):
        
        try:
            url = "http://"+self.host+":"+str(self.port)+"/write?db="+self.db
            if self.debug:
                print(url)
            res=urequests.request("POST",url,self.data)
            self.data=""
            if res.status_code == 400 or res.status_code == 401 or res.status_code == 404 or res.status_code == 413 or res.status_code == 500:
                if self.debug:
                    print("Probleem schrijven naar influxdb")
                    print(res.reason)
                    res.close()
                    return False
            else:
                print(res.status_code)
                res.close()
                return True
                
        except Exception as E:
            if self.debug:
                print(E)
            res.close()
            return False