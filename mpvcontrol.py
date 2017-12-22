import socket
import json
try :
    from mpris.MPRIS import MPRIS
except ImportError :
    MPRIS_AVAILABLE = False

class seekMode :
    RELATIVE = 'relative'
    ABSOLUTE = 'absolute'
    ABSOLUTE_PERCENT = 'absolute-percent'
    RELATIVE_PERCENT = 'relative-percent'

class mpvError(Exception) :
    pass

class mpvControl :
    def __init__(self, path, mpris_enabled=False, mpris_identity = 'mpv') :
        self.target = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
        self.target.connect(path)
        if not MPRIS_AVAILABLE :
            mpris_enabled = False

        if mpris_enabled:
            self.mpris = MPRIS(mpris_identity)
    ## Main Methods

    def status(self) :
        #TODO

        return

    def isPlaying(self) :
        #TODO
        return

    def filename(self) :
        reply = self.getProperty('filename')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']

    def path(self) :
        reply = self.getProperty('working-directory')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data'] + self.filename()

    def setFullscreen(self, b) :
        self.setProperty('fs', b)

    ###Playback controls

    def play(self) :
        self.setProperty('pause', False)
        return

    def pause(self) :
        self.setProperty('pause', True)
        return

    def PlayPause(self) :
        return

    def next(self, force=False) :
        if force == False :
            reply = self.command('playlist_next', 'weak')
        else :
            reply = self.command('playlist_next', 'force')

        return reply

    def previous(self, force=False) :
        if force == False :
            reply = self.command('playlist_prev', 'weak')
        else :
            reply = self.command('playlist_prev', 'force')

        return reply

    def getDuration(self) :
        reply = self.getProperty('duration')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']

    def seek(self, seconds, seekMode = seekMode.RELATIVE) :
        self.command('seek', seconds, seekMode)

    def revertSeek(self) :
        self.command('revert_seek')

    def setSpeed(self, speed) :

        return

    def getSpeed(self) :
        reply = self.getProperty('speed')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']

    ###

    ###Volume controls
    def mute(self, b) :
        reply = self.setProperty('mute', b)

    def setVolume(self, volume) :
        reply = self.setProperty('volume', volume)

    def getVolume(self) :
        reply = self.getProperty('volume')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']
    ###

    ###Playlist controls
    def add(self, path) :

        return

    def enqueue(self, path) :

        return

    def playlist(self) :
        #Returns playlist

        return

    def playItem(self, itemNo) :

        return

    def remove(self, ItemNo) :

        return

    def repeat(self, b) :
        #Turn on off repeat

        return

    def clearPlaylist(self) :

        return
    #SHuffle?

    ###

    ###Metadata

    def getMetadata(self) :
        reply = self.getProperty('metadata')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']

    def getTitle(self) :
        reply = self.getProperty('media-title')
        if reply['error'] != 'success' :
            raise mpvError(reply['error'])
        return reply['data']

    def setTitle(self, title) :

        return
    ###
    ##

    ## getProperty and setProperty

    def command(self, *args) :
        reply = self._command(list(args))
        return reply

    def _command(self, command) :
        data = {'command' : []}
        data['command'] = command
        payload = self._parseCommand(data)
        self._executeCommand(payload)
        reply = self._receiveReply()
        return reply

    def getProperty(self, property) :
        ''' Process the reply from _getProperty()'''
        #TODO format reply and raise exception on {"error" : "Property not found"}
        reply = self._getProperty(property)

        reply = json.loads(reply)

        return reply


    def _getProperty(self, property) :
        #TODO Implement a check for valid property
        cmd = ['get_property']
        cmd.append(property)
        reply = self._command(cmd)
        if '"data"' not in reply :
            reply = self._receiveReply()
        return reply

    def setProperty(self, property, arg) :
        ''' Process the reply from _setProperty() '''
        #TODO Raise an exception of error != success
        reply = self._setProperty(property, arg)
        return reply

    def _setProperty(self, property, arg) :
        cmd = ['set_property']
        cmd.append(property)
        cmd.append(arg)
        reply = self._command(cmd)

        return reply

    ## Methods for parsing commands and sending them to the socket

    def _parseCommand(self, command) :
        #Command is dict { 'command' : ['command_name' , 'param1', 'param2', ..]}
        cmd = json.dumps(command)
        cmd = cmd.encode('utf-8') + b'\n'
        return cmd

    def _executeCommand(self, command) :
        try :
            self.target.sendall(command)
        except BrokenPipeError:
            raise mpvError("No host running on the given socket")

    def _receiveReply(self) :
        reply = self.target.recv(1024)
        reply = str(reply, 'utf-8')
        return reply
