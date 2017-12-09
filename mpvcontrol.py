import socket
import json


class mpvControl :
    def __init__(self, path) :
        self.target = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
        self.target.connect(path)

    def play() :
        self.target.setProperty('pause', False)
        return
    def pause() :
        self.target.setProperty('pause', True)
        return

    def getDuration() :
        return self.target.getProperty('duration')

    def getProperty(self, property) :
        ''' Process the reply from _getProperty()'''
        #TODO format reply and raise exception on {"error" : "Property not found"}

    def _getProperty(self, property) :
        #TODO Implement a check for valid property
        data = {'command' : []}
        cmd = ['get_property']
        cmd.append(property)
        data['command'] = cmd
        payload = self._parseCommand(data)
        self._executeCommand(payload)
        reply = self._receiveReply()

        return reply

    def setProperty(self, property, arg) :
        ''' Process the reply from _setProperty() '''
        #TODO Raise an exception of error != success

        return reply

    def _setProperty(self, property, arg) :
        data = {'command' : []}
        cmd = ['set_property']
        cmd.append(property)
        cmd.append(arg)
        data['command'] = cmd
        payload = self._parseCommand(data)
        self._executeCommand(payload)
        reply = self._receiveReply()
        return reply

    def _parseCommand(self, command) :
        #Command is dict { 'command' : ['command_name' , 'param1', 'param2', ..]}
        cmd = json.dumps(command)
        cmd = cmd.encode('utf-8') + b'\n'
        return cmd

    def _executeCommand(self, command) :
        self.target.sendall(command)

    def _receiveReply(self) :
        reply = self.target.recv(1024)
        reply = str(reply, 'utf-8')
        return reply
