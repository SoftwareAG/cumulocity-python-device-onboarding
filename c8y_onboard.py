import paho.mqtt.client as mqtt
import sys, os.path, time
import logging, json

class Onboard():
    def __init__(self, device_id):
        self.device_id = device_id
        self.sentMessages = 0
        self.receivedMessages = []
        self.credentialsReceived = False
        self.credentialsFile = "frpresales-credentials.json"
        self.bootstrapUsername = "management/devicebootstrap"
        self.bootstrapPassword = "Fhdt1bb1f"
        self.brokerUrl = "mqtt.cumulocity.com"
        self.credentials = {}
        self.auth = ()

    def dcr_handler(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        print("Received message " + payload)
        if payload.startswith("70,"):
            [tenant, username, password] = payload.split(",")[1:4]
            print("Credentials received! " + tenant +"/" + username + ", " + password)
            self.credentials[self.device_id] = {"tenant": tenant, "username": username, "password": password}
            with open(self.credentialsFile,"w") as cred_file:
                cred_file.write(json.dumps(self.credentials, indent=4, sort_keys=True))
            self.credentialsReceived = True
            print("Credentials successfully written to file!")

    def error_handler(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        print("Error message " + payload)

    def default_message_callback(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        print("Unhandled message received: " + payload)
    
    def publish(self, topic, message, waitForAck = False):
        mid = self.client.publish(topic, message, 2)[1]
        if message:
            print("Publishing message: '" + message + "' with id " + str(mid))
        else:
            print("Publishing message with id " + str(mid))
        if (waitForAck):
            self.sentMessages = self.sentMessages + 1
            while not mid in self.receivedMessages:
                time.sleep(0.25)
            self.receivedMessages.remove(mid)
            self.sentMessages = self.sentMessages - 1
    
    def on_publish(self, client, userdata, mid):
        print("Message published: " + str(mid))
        self.receivedMessages.append(mid)
      
    def on_connect(self, client, userdata, flags, rc):
        print("Connection returned result: " + mqtt.connack_string(rc))
    
    
    def bootstrap(self):
        print("Credentials not found. Bootstrapping device...")
        self.initMqttClient()
        self.client.username_pw_set(self.bootstrapUsername, self.bootstrapPassword)
        self.client.connect(self.brokerUrl, 1883)
        self.client.loop_start()
        self.client.subscribe("s/e")
        self.client.subscribe("s/dcr")
        self.message_callback_add("s/e", self.error_handler)
        self.message_callback_add("s/dcr", self.dcr_handler)
        print("Waiting for device to be registered...")
        cpt = 1
        while not self.credentialsReceived:
            print("Attempt: " + str(cpt))
            self.publish("s/ucr", None, True)
            time.sleep(1.0)
            cpt = cpt + 1
        self.client.disconnect()
        self.connect()
    
    def connect(self, tenant = None, username = None, password = None):
        if (os.path.isfile(self.credentialsFile)):
            with open(self.credentialsFile) as cred_file:
                self.credentials = json.load(cred_file)
        if self.device_id in self.credentials:
            tenant = self.credentials[self.device_id]["tenant"]
            username = self.credentials[self.device_id]["username"]
            password = self.credentials[self.device_id]["password"]
        if tenant and username and password:
            self.credentials[self.device_id] = {"tenant": tenant, "username": username, "password": password}
            with open(self.credentialsFile,"w") as cred_file:
                json.dump(self.credentials, cred_file)
            self.auth = (tenant + "/" + username, password)
            print("File with credentials found. Using them to connect...")
            print("Connecting with: " + tenant +"/" + username + ", " + password)
            self.initMqttClient()
            self.client.username_pw_set(tenant + "/" + username, password)
            self.client.connect(self.brokerUrl, 1883)
            self.client.loop_start()
            self.client.subscribe("s/e")
            self.message_callback_add("s/e", self.error_handler)
            print("Connected!")
        else:
            self.bootstrap()
    
    def initMqttClient(self):
        self.client = mqtt.Client(client_id=self.device_id)
        logger = logging.getLogger(__name__)
        self.client.enable_logger(logger)
        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.client.on_message = self.default_message_callback
        
    def waitForAllMessagesPublished(self):
        while self.sentMessages > 0:
            print("Waiting for all messages to be acknowledged...")
            time.sleep(0.25)
        print("All done!")
        
    def message_callback_add(self, sub, callback):
        self.client.message_callback_add(sub, callback)
        
    def subscribe(self, topic):
        self.client.subscribe(topic, 2)
        
    def getCredentials(self):
        return self.credentials[self.device_id]

    def getAuth(self):
        return self.auth

if __name__ == "__main__":
    device_name = sys.argv[1]
    device_id = sys.argv[2]
    serial = sys.argv[3]


    o = Onboard(device_id);    
    o.connect()
    
    print("Creating the device in Cumulocity...")
    o.publish("s/us", "100," + device_name + ",c8y_Test", True)
    print("Sending additional info...")
    o.publish("s/us", "110," + serial + ",Test,Rev0.1", True)
    o.publish("s/us", "400,registered,Device connected", True)
    o.publish("s/us", '''211,20.4,2019-09-03T08:36:10.432Z
211,20.5,2019-09-03T08:36:11.432Z
211,20.6,2019-09-03T08:36:12.432Z
211,20.7,2019-09-03T08:36:13.432Z
211,20.8,2019-09-03T08:36:14.432Z
211,20.9,2019-09-03T08:36:15.432Z
211,20.10,2019-09-03T08:36:16.432Z''', True)
    o.waitForAllMessagesPublished()
    
