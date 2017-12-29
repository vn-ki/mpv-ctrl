import socket
import json

try :
    from mpris.mpris import MPRIS
    from pydbus import SessionBus
    import pkg_resources
    MPRIS_AVAILABLE = True
except ImportError :
    MPRIS_AVAILABLE = False

class seekMode :
    RELATIVE = 'relative'
    ABSOLUTE = 'absolute'
    ABSOLUTE_PERCENT = 'absolute-percent'
    RELATIVE_PERCENT = 'relative-percent'

class queueMode :
    REPLACE = 'replace'
    APPEND = 'append'
    APPEND_PLAY = 'append-play'

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
            MPRIS.dbus = pkg_resources.resource_string(__name__, "mpris/mpris.xml").decode("utf-8")
            self.mpris.player = self
            bus = SessionBus()
            bus.publish('org.mpris.MediaPlayer2.YouTubePlayer', self.mpris, ("/org/mpris/MediaPlayer2", self.mpris) )

    ## Main Methods

    def status(self) :
        #TODO

        return

    def isPlaying(self) :
        #TODO
        reply = self.getProperty('core-idle')
        return reply['data']

    def filename(self) :
        reply = self.getProperty('filename')
        return reply['data']

    def path(self) :
        reply = self.getProperty('working-directory')
        return reply['data'] + self.filename()

    def setFullscreen(self, b) :
        self.setProperty('fs', b)

    def enableMPRIS(self, mpris_identity = 'mpv') :
        self.mpris = MPRIS(mpris_identity)\
        MPRIS.dbus = pkg_resources.resource_string(__name__, "mpris/mpris.xml").decode("utf-8")
        self.mpris.player = self
        bus = SessionBus()
        bus.publish('org.mpris.MediaPlayer2.YouTubePlayer', self.mpris, ("/org/mpris/MediaPlayer2", self.mpris) )


    ###Playback controls

    def play(self) :
        self.setProperty('pause', False)
        return

    def pause(self) :
        self.setProperty('pause', True)
        return

    def PlayPause(self) :
        status = self.isPlaying()
        self.setProperty('pause', status)
        return not status

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
        return reply['data']

    def seek(self, seconds, seekMode = seekMode.RELATIVE) :
        self.command('seek', seconds, seekMode)

    def revertSeek(self) :
        self.command('revert_seek')

    def setSpeed(self, speed=1.0) :
        self.setProperty('speed', speed)
        return

    def getSpeed(self) :
        reply = self.getProperty('speed')
        return reply['data']

    ###

    ###Volume controls
    def mute(self, b) :
        reply = self.setProperty('mute', b)

    def setVolume(self, volume) :
        reply = self.setProperty('volume', volume)

    def getVolume(self) :
        reply = self.getProperty('volume')
        return reply['data']
    ###

    ###Playlist controls
    def add(self, path, queueMode = queueMode.REPLACE) :
        #TODO Add support for options
        reply = self.command('loadfile', path, queueMode)
        return reply

    def playlistPosition(self) :
        reply = self.getProperty('playlist-pos')
        return reply['data']

    def playlist(self) :
        #Returns playlist
        reply = self.getProperty('playlist')
        return reply['data']

    def playItem(self, itemNo) :

        return

    def remove(self, index='current') :
        reply = self.command('playlist-remove', ItemNo)
        return True

    def move(self, i1, i2) :
        reply = self.command('playlist-move'. i1, i2)
        return True

    def clearPlaylist(self) :
        reply = self.command('playlist-clear')
        return True

    def shufflePlaylist(self) :
        reply = self.command('playlist-shuffle')
        return True

    ###

    ###Metadata

    def getMetadata(self) :
        reply = self.getProperty('metadata')
        return reply['data']

    def getTitle(self) :
        reply = self.getProperty('media-title')
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

        try :
            if reply['error'] != 'success' :
                raise mpvError(reply['error'])
        except KeyError :
            pass

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
        reply = json.loads(reply)
        #print(reply )

        try :
            if reply['error'] != 'success' :
                raise mpvError(reply['error'])
        except KeyError :
            pass

        return reply

    def _setProperty(self, property, arg) :
        cmd = ['set_property']
        cmd.append(property)
        cmd.append(arg)
        reply = self._command(cmd)
        if '"error"' not in reply :
            reply = self._receiveReply()

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
        reply = ''
        while True :
            t = str(self.target.recv(1024), 'utf-8')
            #print(len(t))
            reply += t
            if len(t)<1023 :
                break
        return reply
