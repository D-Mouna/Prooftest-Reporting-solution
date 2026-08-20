# -*- coding: utf-8 -*-

"""Starts the recording of process values of local variables and
displays the selected variables in a oscilloscope-like graphic.

This plug-in works with SILworX V14 or higher. It doesn't work without
SILworX. The core function is started on the context menu of a program
in an opened SILworX project.

Date:   2023-11-15
Status: RELEASE
Author: Karlheinz Volpp / HIMA
"""

########################################
# Import section
########################################
import os                               # Miscellaneous operating system interfaces
import sys                              # System-specific parameters and functions
from argparse import ArgumentParser     # Parser for command-line options, arguments and sub-commands
import datetime                         # Basic date and time types
import math                             # Mathematical functions
import websocket                        # WebSocket client for Python (-> pip install websocket-client)
import rel                              # Registered Event Listener (-> pip install rel)
import requests                         # HTTP for humans (-> pip install requests)
import json                             # JSON encoder and decoder
import struct                           # Interpret bytes as packed binary data
import threading                        # Thread-based parallelism
import screeninfo                       # Fetch location and size of physical screens (-> pip install screeninfo)
import tkinter as tk                    # Python interface to Tcl/Tk
from tkinter import ttk                 # Tk themed widgets
from tkinter import messagebox          # Tkinter message prompts
import matplotlib as mpl                # Visualization with Python (-> pip install matplotlib)
import matplotlib.pyplot as plt         # Make matplotlib work like MATLAB
from matplotlib.lines import Line2D     # 2D lines with support for a variety of line styles, markers, colors, etc.
import matplotlib.dates as mdates       # Matplotlib date plotting capabilities
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk   # Use tkinter backend

########################################
# Some const variables
########################################
PLUGIN_NAME = 'o-scope'
VERSION = '1.0-0'
AUTHOR = 'HIMA Paul Hildebrandt GmbH'
TRIGGER_NAME = 'START_OSCILLOSCOPE'
LANG_DICT = {
    'menuEntryName':   ('Oszilloskop',
                        'Oscilloscope'),
    'onMessageErr':    ('Fehler: Unerwarteter Message-Typ empfangen, Message',
                        'Error: Unexpected message type received, Message'),
    'onTriggerErr':    ('Fehler: Unerwarteter Trigger-Name in Plugin',
                        'Error: Unexpected trigger name in plugin'),
    'onErrorErr':      ('Fehler: Interner Fehler aufgetreten, Fehler',
                        'Error: Internal error occured, Error'),
    'projOpenedInfo':  ('Info: Projekt geöffnet, Session-Id',
                        'Info: Project opened, Session ID'),
    'projClosedInfo':  ('Info: Projekt geschlossen, Session-Id',
                        'Info: Project closed, Session ID'),
    'responseTime':    ('Antwortzeit:',
                        'Response time:'),
    'apiServerErr':    ('Fehler: Keine Antwort auf API-Anfrage erhalten, URL',
                        'Error: No response received to API request, URL'),
    'apiRequestInfo':  ('Info: API-Anfrage ok, URL',
                        'Info: API request ok, URL'),
    'apiRequestErr':   ('Fehler: Ungültige API-Anfrage ohne Fehlermeldung, URL',
                        'Error: Bad API request without advice, URL'),
    'apiStatusErr':    ('Fehler: Unerwarteter Statuscode in API-Anfrage, URL::Code',
                        'Error: Unexpected status code in API request, URL::Code'),
    'logDateFormat':   ('%d.%m.%Y',
                        '%Y-%m-%d'),
    'initWaitText':    ('Initialisierung, bitte warten...',
                        'Initialising, please wait...'),
    'loginTitle':      ('System-Login',
                        'System Login'),
    'loginLabel':      ('Zugangsdaten',
                        'Access Data'),
    'loginGroupText':  ('Benutzergruppe',
                        'User Group'),
    'loginPWText':     ('Passwort',
                        'Password'),
    'loginAccessText': ('Zugriffsart',
                        'Access Mode'),
    'loginModeValue0': ('Administrator',
                        'Administrator'),
    'loginModeValue1': ('Lesen',
                        'Read'),
    'loginModeValue2': ('Lesen + Schreiben',
                        'Read and Write'),
    'loginModeValue3': ('Lesen + Bediener',
                        'Read and Operator'),
    'loginModeValue4': ('MultiForcen',
                        'MultiForcing'),
    'cancelButtonText':('Abbrechen',
                        'Cancel'),
    'funcAbortedErr':  ('Fehler: Funktion abgebrochen: ',
                        'Error: Function aborted: '),
    'varDatatypeErr':  ('Fehler: Unerwarteter Datentyp bei lokaler Variable, Name::Typ'
                        'Error: Unexpected data type for local variable, Name::Type'),
    'offsetFormatYMD': ('%d. %b %Y',
                        '%Y %b %d'),
    'offsetFormatYM':  ('%b %Y',
                        '%Y %b'),
    'offsetFormatMD':  ('%d. %b',
                        '%b %d'),
    'startButtonText': ('Starten',
                        'Start'),
    'pauseButtonText': ('Anhalten',
                        'Pause'),
    'resumeButtonText':('Fortsetzen',
                        'Resume'),
    'stopButtonText':  ('Beenden',
                        'Stop'),
    'chartTimeLabel':  ('Zeitdauer Diagramm',
                        'Chart Time Length'),
    'listboxHeader0':  ('Name',
                        'Name'),
    'listboxHeader1':  ('Datentyp',
                        'Data Type'),
    'maxSelectTitle':  ('Hinweis',
                        'Notice'),
    'maxSelectText':   ('Maximal zehn Variablen selektierbar!',
                        'Maximum ten variables selectable!'),
    'winClosedInfo':   ('Info: Fenster geschlossen: ',
                        'Info: Window closed: ')
}

"""
MatPlotLib Toolbar:
************* Tooltips *************
tooltip.home:   ('Zurück zur ursprüngliche Ansicht',
                 'Reset original view'),
tooltip.pan:    ('Achsen verschieben mit linker Maustaste, Zoomen mit rechter Maustaste',
                 'Pan axes with left mouse button, zoom with right mouse button'),
tooltip.zoom:   ('In Rechteck zoomen',
                 'Zoom to rectangle'),
tooltip.save:   ('Abbildung speichern',
                 'Save picture')

************* Keymaps *************
keymap.home:    h, r, home  # home or reset mnemonic
keymap.pan:     p           # pan/zoom mnemonic
keymap.zoom:    o           # zoom-to-rect mnemonic
keymap.save:    s, ctrl+s   # saving current figure

************* Modifier keys *************
Constrain pan/zoom to x axis: hold x when panning/zooming with mouse
Constrain pan/zoom to y axis: hold y when panning/zooming with mouse
Preserve aspect ratio: hold ctrl when panning/zooming with mouse
"""

class Plugin():
    """Communicate with SILworX' plugin interface."""
    def __init__(self, args):
        self.language = 0 if args.language == 'de' else 1
        self.user_session_id = ''
        self.resource_address = ''
        self.program_address = ''
        self.program_name = ''
        self.is_running_sema = 0
        if args.readsecret:
            self.is_development_mode = False
            logpath = os.path.join(os.environ.get('APPDATA'), 'SILworX_Plugins')
            if not os.path.exists(logpath):
                os.makedirs(logpath)
            logfile = os.path.join(logpath, PLUGIN_NAME+'.log')
            sys.stdout = open(logfile, 'a')
            print(f'\n----------------------'
                  f'\n    {PLUGIN_NAME} V{VERSION}'
                  f'\n----------------------')
        else:
            self.is_development_mode = True

    def on_open(self, ws):
        """Register the plugin in SILworX.

        Called when a WebSocket communication with SILworX is opened.
        """

        secret = '' if self.is_development_mode else sys.stdin.readline()
        message = {
            'msg_type': 'register',
            'plugin_name': PLUGIN_NAME,
            'secret': secret,
            'plugin_version': VERSION,
            'plugin_author': AUTHOR,
            'customized_contextmenu_trigger': [
                {'menu_entry_name': LANG_DICT['menuEntryName'][self.language],
                 'node_type': 'program',
                 'trigger_name': TRIGGER_NAME,
                 'timeout': 10}
            ],
            'predefined_trigger': [
                {'trigger_name': 'TRIGGER_SESSION_ID_CHANGED',
                 'timeout': 10}
            ]
        }
        ws.send(json.dumps(message))

    def on_message(self, ws, message):
        """Call the responsible message handler.

        Called when SILworX sends a message to the plugin.
        """

        def do_trigger_action(ws, trigger):
            """Do the requested trigger action and acknowledge the receipt of the trigger.

            Called when SILworX triggers an action from the plugin.
            """

            ws.send(json.dumps({'msg_type': 'resume', 'trigger_id': trigger.get('trigger_id')}))
            trigger_name = trigger.get('trigger_name')
            if trigger_name == 'TRIGGER_SESSION_ID_CHANGED':
                self.user_session_id = trigger.get('session_id')
                key = 'projOpenedInfo' if self.user_session_id else 'projClosedInfo'
                print_message('INFO', key, f' = {self.user_session_id}')
            elif trigger_name == TRIGGER_NAME:
                if self.is_running_sema == 0:
                    self.is_running_sema = 1
                    self.program_address = trigger.get('internal_address')
                    _, configuration, resource, program = self.program_address.split('/')
                    self.program_name = convert_to_windows_codepage(program)
                    self.resource_address = f'/{configuration}/{resource}'
                    run_oscope()
                    self.is_running_sema = 0
            else:
                print_message('ERR', 'onTriggerErr', f' {PLUGIN_NAME}: {trigger_name}')

        # on_message(self, ws, message)
        json_message = json.loads(message)
        msg_type = json_message.get('msg_type')
        if msg_type == 'trigger':
            do_trigger_action(ws, json_message)
        elif msg_type == 'advice':
            api.print_advices(json_message.get('advices'))
        else:
            print_message('INFO', 'onMessageErr', f' = {message}')

    def on_error(self, ws, error):
        """Show the error occured.

        Called if we have an error in Python code (*shouldn't be*) or
        when SILworX closes the WebSocket connection with the plugin.
        """

        print_message('ERR', 'onErrorErr', f' = {error}')
        if (
            self.is_development_mode
            and not isinstance(error, websocket.WebSocketConnectionClosedException)
        ):
            raise
        sys.exit(1)

    def on_close(self, ws, close_status_code, close_msg):
        """Exit the plugin.

        Called when connection is closed or, during develop mode, CTRL-C is received.
        """

        sys.exit(0)

class API():
    """Communicate with SILworX' API interface."""
    def __init__(self, args):
        self._certificate = args.certificate
        self._url_fixed_part = f'https://localhost:{args.apiport}/api/v1/'
        self.program_path = ''
        self.usergroup, self.password, self.accessmode = '', '', ''
        self.cycle_time = None
        self.is_online = False
        self.local_force_data = []

    def request_api(self, url, params, headers, body=None):
        """Post an API request to SILworX and check the response."""
        def print_responsetime(responsetime):
            """Show the responsetime of the API call (only during debugging)."""
            s = responsetime.seconds
            ms = int(responsetime.microseconds/1000)
            responseTime = LANG_DICT['responseTime'][plugin.language]
            print(f' └► {responseTime} {s}.{ms}s')

        # request_api(self, url, params, headers, body=None)
        plugin.is_running_sema += 1
        data = {} if body is None else json.dumps(body)
        try:
            response = requests.post(url, params=params, headers=headers, data=data, verify=self._certificate)
        except OSError as e:
            print_message('ERR', 'onErrorErr', f' = {e}')
            sys.exit(1)
        plugin.is_running_sema -= 1
        if response is None:
            print_message('ERR', 'apiServerErr', f' = {url}')
            sys.exit(1)
        else:
            appdata = response.json()
            advices = appdata.get('advices')
            if response.status_code == 200:      # OK, standard response for successful HTTP requests
                if advices:
                    self.print_advices(advices)
                else:
                    print_message('INFO', 'apiRequestInfo', f' = {url}')
            elif response.status_code == 400:    # Bad request, SILworX cannot or will not process the request
                if advices:
                    self.print_advices(advices)
                    text = advices[0].get('data').get('text').lower()
                    if (
                        text.__contains__('session')
                        and text.__contains__('id')
                        and (text.__contains__('not valid') or text.__contains__('nicht gültig'))
                    ):
                        graph.stop_timer(wait_for_termination=False)
                        if gui.is_displayed:
                            gui.quit_mainwindow()
                        sys.exit(1)
                else:
                    print_message('ERR', 'apiRequestErr', f' = {url}')
            else:       # maybe 202 (Action successful) or 206 (Partial content), but should not occur in this context
                print_message('ERR', 'apiStatusErr', f' = {url}::{response.status_code}')
            if plugin.is_development_mode:
                print_responsetime(response.elapsed)
            return appdata

    def print_advices(self, advices, indent=0):
        """Show SILworX advices, even if they are nested."""
        for advice in advices:
            timestamp_utc = datetime.datetime.strptime(advice.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')
            timestamp_dt = timestamp_utc.replace(tzinfo=datetime.UTC).astimezone(tz=None)
            ms = timestamp_dt.strftime('%f')
            dateFormat = LANG_DICT['logDateFormat'][plugin.language]
            indentation = indent * '    '
            localtime = timestamp_dt.strftime(f'{dateFormat} %H:%M:%S.{ms[:3]}')
            level = advice.get('level').get('text')
            data = advice.get('data').get('text')
            path = advice.get('path')
            if path:
                print(f'{indentation}{localtime}, {level}: {data}, {path}')
            else:
                print(f'{indentation}{localtime}, {level}: {data}')
            subadvice = advice.get('advices')
            if subadvice is not None:
                self.print_advices(subadvice, indent+1)

    def read_structuretree(self):
        """Call SILworX API with POST <Retrieving structure tree information>.

        This action retrieves the structure tree information of the current project.
        """

        def get_structuretree_nodes(structuretree, nodes, symbol):
            """Extract nodes of type symbol from a structure tree."""
            for node in structuretree:
                if node.get('type_info').get('symbol') == symbol:
                    element = {'name': node.get('display_name'),
                               'address': node.get('internal_address')}
                    nodes.append(element)
                children = node.get('children')
                if children is not None:
                    get_structuretree_nodes(children, nodes, symbol)

        # read_structuretree(self)
        url = self._url_fixed_part + 'project/structuretree/info'
        params = {}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        advices = response.get('advices')
        for advice in advices:
            if advice.get('level').get('id') == 'error':
                print_message('ERR', 'onErrorErr', f' {advice.get("data").get("text")}')
                sys.exit(1)
        results = response.get('results')
        structuretree = [] if results is None else results.get('structure_tree')
        self.program_path = ''
        if structuretree:
            projects = []
            get_structuretree_nodes(structuretree, projects, 'project')
            project_name = projects[0].get('name')
            self.program_path = convert_to_windows_codepage(f'{project_name}{plugin.program_address}')

    def do_systemlogin(self):
        """Call SILworX API with POST <Performing a system login>.

        This action performs a system login to a resource.
        """

        url = self._url_fixed_part + 'online/system/login'
        params = {'internal_address': plugin.resource_address,
                  'access_right': self.accessmode}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id,
                   'HIMA_SAPI_username': self.usergroup,
                   'HIMA_SAPI_password': self.password}
        response = self.request_api(url, params, headers)
        self.is_online = True
        advices = response.get('advices')
        for advice in advices:
            if advice.get('level').get('id') == 'error':
                self.is_online = False

    def read_systeminfo(self):
        """Call SILworX API with POST <Retrieving system information from a resource>.

        This action retrieves system information from a resource.
        """

        def get_systeminfo_property(properties, prop_name):
            """Extract a property with prop_name from system information service response."""
            for property in properties:
                if property.get('prop_name') == prop_name:
                    return property.get('property').get('value')

        # read_systeminfo(self)
        url = self._url_fixed_part + 'online/system/info'
        params = {'internal_address': plugin.resource_address,
                  'service_property_list': 'system_data'}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        cycletime = None
        results = response.get('results')
        if results is not None:
            services = results.get('services',[])
            for service in services:
                if service.get('service') == 'system_data':
                    service_properties = service.get('properties')
                    cycletime = get_systeminfo_property(service_properties, 'cycle_time.cycletime_average')
        if cycletime is None:
            self.is_online = False
        else:
            self.cycle_time = 2*max(15, int(cycletime))

    def read_localforcedata(self, varpaths=None):
        """Call SILworX API with POST <Retrieving local force data>.

        This action retrieves force data (local variables) from a program.
        """
        if varpaths is None:
            varpaths = []
        url = self._url_fixed_part + 'online/forcing/local/read'
        params = {'internal_address': plugin.resource_address,
                  'program': plugin.program_name,
                  'varpaths': varpaths}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        results = response.get('results')
        self.local_force_data = [] if results is None else results.get('local_force_data')
        if not self.local_force_data:
            self.is_online = False

    def start_localforcedata_recording(self, output_file):
        """Call SILworX API with POST <Starting the recording of process values of local variables>.

        This action starts the recording of process values of local variables.
        The retrievable variables are limited to the specified program.
        Multiple recordings may run in parallel.
        """

        try:
            os.remove(output_file)
        except FileNotFoundError as e:
            pass
        url = self._url_fixed_part + 'online/forcing/local/recording/start'
        params = {'output_file_path': output_file,
                  'interval': graph.recordinginterval_ms,
                  'internal_address': plugin.resource_address,
                  'program': plugin.program_name,
                  'varpaths': graph.varpaths}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        advices = response.get('advices')
        for advice in advices:
            if advice.get('level').get('id') == 'error':
                self.is_online = False
        return response

    def get_forcedatarecording_layout(self, response):
        """Extract the arrangement of the values in the local force data recording dump file."""
        results = response.get('results')
        allocation = []
        if results is not None:
            keys = list(results.keys())
            layout = results.get(keys[0])
            formatstring = '>xxxx'
            for memory_block in layout:
                variables = memory_block.get('variables')
                for variable in variables:
                    datatype = variable.get('datatype')
                    varpath = variable.get('path')
                    if datatype in ('BOOL', 'BYTE', 'USINT'):
                        formatstring += 'B'
                    elif datatype == 'SINT':
                        formatstring += 'b'
                    elif datatype in ('WORD', 'UINT'):
                        formatstring += 'H'
                    elif datatype == 'INT':
                        formatstring += 'h'
                    elif datatype in ('DWORD', 'UDINT'):
                        formatstring += 'I'
                    elif datatype == 'DINT':
                        formatstring += 'i'
                    elif datatype in ('LWORD', 'ULINT'):
                        formatstring += 'Q'
                    elif datatype in ('LINT', 'TIME'):
                        formatstring += 'q'
                    elif datatype == 'REAL':
                        formatstring += 'f'
                    elif datatype == 'LREAL':
                        formatstring += 'd'
                    else:
                        print_message('ERR', 'varDatatypeErr', datatype)
                        sys.exit(1)
                    for index, path in enumerate(graph.varpaths):
                        if path == varpath:
                            element = {'is_time': datatype == 'TIME',
                                       'sortindex': index}
                            allocation.append(element)
                            break
            allocation.append(formatstring)
        return allocation

    def stop_localforcedata_recording(self, output_file, allocation=None):
        """Call SILworX API with POST <Stopping the recording of process values of local variables>.

        This action stops the recording of process values of local variables.
        """

        def get_forcedatarecording_time(response):
            """Extract the start time of the recording from the response."""
            advices = response.get('advices')
            for advice in advices:
                if advice.get('level').get('id') == 'info':
                    timestamp_utc = datetime.datetime.strptime(advice.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')
                    utcoffset_dt = datetime.datetime.now(datetime.UTC).astimezone().utcoffset()
                    return timestamp_utc + utcoffset_dt

        def read_dumpfile(filename, allocation):
            """Extract the variable values from the local force data recording dump file."""
            try:
                with open(filename, 'rb') as f:
                    bytestream = f.read()
            except FileNotFoundError as e:
                print_message('ERR', 'funcAbortedErr', e)
                sys.exit(1)
            return list(struct.iter_unpack(allocation[-1], bytestream))

        # stop_localforcedata_recording(self, output_file, allocation=None)
        url = self._url_fixed_part + 'online/forcing/local/recording/stop'
        params = {'output_file_path': output_file}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        advices = response.get('advices')
        for advice in advices:
            if advice.get('level').get('id') == 'error':
                self.is_online = False
        if self.is_online and allocation is not None:
            graph.chunk_endtime_dt = get_forcedatarecording_time(response)
            chunklist = read_dumpfile(output_file, allocation)
            graph.update_trend(chunklist)

    def do_disconnect(self):
        """Call SILworX API with POST <Disconnecting an online session>.

        This action disconnects an online session.
        """

        url = self._url_fixed_part + 'online/disconnect'
        params = {'internal_address': plugin.resource_address}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        self.is_online = False

class GUI():
    """Functions for the graphical user interface."""
    def __init__(self):
        self._root = tk.Tk()
        self._root.withdraw()
        self._x_pos = None
        self.is_aborted = False
        self.treeview_enabled = True
        self.trend_not_paused = True
        self.is_displayed = False
        self.selected_vars = []
        self._checkbox_unchecked_enabled_img = tk.PhotoImage(
            data=(b'iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOww'
                  b'AADsMBx2+oZAAAABtJREFUKFNjKCAOgNT9JwRG1WEHA6yOMCgoAABSnailSKbZSwAAAABJRU5ErkJggg==')
        )
        self._checkbox_checked_enabled_img = tk.PhotoImage(
            data=(b'iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8'
                  b'YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACFSURBVChTjY/REcQQFEVTigpUoAKF+Pahgm1ABSpQTwpR'
                  b'QXLWs2wyJnI+zLscd9j8O77esWLh7RWGJ6+UYoxRSuWcnzznHNLEizHSIXNKSaQQAnF4ZHattai8SSRi'
                  b'vfXnUd7PtNYMrL1+eCCVHfmpcPGgq9S3rcrdg0+lhR8Tb0rz1nh/Asy8WmkTBSarAAAAAElFTkSuQmCC')
        )
        self._checkbox_unchecked_disabled_img = tk.PhotoImage(
            data=(b'iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZ'
                  b'cwAADsMAAA7DAcdvqGQAAAAdSURBVChTY1i7aSsxCKTuPyEwqg47GGB1hNGmrQCmSM1lJcm1TQAAAABJRU5ErkJggg==')
        )
        self._checkbox_checked_disabled_img = tk.PhotoImage(
            data=(b'iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8Y'
                  b'QUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADESURBVChTY1y7aSsDMQCo7j8hAFTDBFWODXz89AmIIGyc6n'
                  b'7//n389Nm9B488fPwEyMWp7uyFS9++fYdykNVdv3kbaAaEfefe/WcvXgIZ8rIyQARkQNUBdV+/dfvQsZN'
                  b'ApUA3Xbp6HSjIz8dnbKAHUQBVJyIsBCSBKoBKgQjIZmVltbMyB0uCAFQd3HygUojtQEVApWBJEEC4D2gF'
                  b'RCmEDbQUwoYAhDogAEqrKCkCEVwDHKCoAwI9bU0ggnKQAHHxy8AAAHQibkZ9qcKDAAAAAElFTkSuQmCC')
        )

    def position_window(self, window_width, window_height, centered=False):
        """Position a window on the same monitor on which SILworX is running."""
        if self._x_pos is None:
            self._x_pos = self._root.winfo_pointerx()
        monitors = screeninfo.get_monitors()
        monitors.sort(key=lambda monitor: monitor.x)
        screen_width = 0
        for monitor in monitors:
            if self._x_pos >= monitor.x:
                screen_width += monitor.width
        screen_height = self._root.winfo_screenheight()
        center_x = self._x_pos + 200
        if center_x > screen_width - window_width:
            center_x = screen_width - window_width - 14
        if centered:
            center_x = screen_width - monitor.width + int((monitor.width - window_width)/2)
        center_y = int((screen_height - window_height)/2)
        return f'{window_width}x{window_height}+{center_x}+{center_y}'

    def show_splashscreen(self):
        """Show a 'initializing...' window until all necessary data from SILworX is collected."""
        self.splashscreen = tk.Toplevel(self._root)
        geometry = self.position_window(300, 100, centered=True)
        self.splashscreen.geometry(geometry)
        self.splashscreen.wm_overrideredirect(True)
        self.splashscreen.attributes('-topmost', True)
        self.splashscreen.config(cursor='watch')
        frame = ttk.Frame(self.splashscreen)
        frame.place(anchor='c', relx=0.5, rely=0.5)
        text = (f'{LANG_DICT["menuEntryName"][plugin.language]}:\n'
                f'{LANG_DICT["initWaitText"][plugin.language]}')
        tk.Label(frame, text=text, font=('Segoe UI', 10, 'bold'), justify=tk.LEFT).pack()
        self.splashscreen.update()

    def quit_splashscreen(self):
        """Close splash screen and release memory."""
        self.splashscreen.destroy()
        self.splashscreen = None
        del self.splashscreen

    def show_logindialog(self):
        """Ask for user name and password for resource login."""
        def create_loginmask(parentframe):
            """Create entries for user group and password."""
            def validate_input(inputstring):
                """Check if there is an entry for the (required) user name."""
                if inputstring:
                    is_valid = len(inputstring) <= 32
                    self.login_button.config(state='normal')
                else:
                    is_valid = True
                    self.login_button.config(state='disabled')
                return is_valid

            # create_loginmask(parentframe)
            labelframe = ttk.Labelframe(parentframe, text=LANG_DICT['loginLabel'][plugin.language])
            labelframe.grid(column=0, row=0, sticky='ew', padx=10, pady=(10,0))
            label = ttk.Label(labelframe, text=LANG_DICT['loginGroupText'][plugin.language])
            label.grid(column=0, row=0, sticky='nw', padx=6, pady=(10,0))
            validatecommand = (self._root.register(validate_input), '%P')
            self.usergroup_entry = ttk.Entry(
                labelframe, width=22, validate='all', validatecommand=validatecommand
            )
            self.usergroup_entry.grid(column=1, row=0, sticky='nw', padx=6, pady=(9,0))
            label = ttk.Label(labelframe, text=LANG_DICT['loginPWText'][plugin.language])
            label.grid(column=0, row=1, sticky='nw', padx=6, pady=10)
            self.password_entry = ttk.Entry(labelframe, width=22, show='*')
            self.password_entry.grid(column=1, row=1, sticky='nw', padx=6, pady=8)
            label = ttk.Label(labelframe, text=LANG_DICT['loginAccessText'][plugin.language])
            label.grid(column=0, row=2, sticky='nw', padx=6, pady=(0,10))
            combobox_values = []
            for index in range(5):
                loginModeValue = 'loginModeValue' + str(index)
                combobox_values.append(LANG_DICT[loginModeValue][plugin.language])
            self.combobox = ttk.Combobox(labelframe, values=combobox_values, width=19)
            self.combobox.delete(0, 'end')
            self.combobox.insert(0, combobox_values[1])
            self.combobox.state(['readonly'])
            self.combobox.grid(column=1, row=2, sticky='nw', padx=6, pady=(0,10))

        def enter_defaultlogin(event):
            """Default values, entered with <Ctrl><a>."""
            self.usergroup_entry.delete(0, 'end')
            self.usergroup_entry.insert(0, 'Administrator')
            self.password_entry.delete(0, 'end')
            self.combobox.set(LANG_DICT['loginModeValue0'][plugin.language])

        def quit_logindialog(abort_state):
            """Close dialog and event loop and release memory."""
            self.is_aborted = abort_state
            api.usergroup = self.usergroup_entry.get()
            api.password = self.password_entry.get()
            access_rights = ('admin', 'read', 'write', 'operator', 'multiforce')
            api.accessmode = access_rights[self.combobox.current()]
            self.logindialog.quit()
            self.logindialog.destroy()
            self.logindialog = None
            del self.logindialog

        def create_buttonrow(parentframe):
            """Create login and cancel button."""
            frame = ttk.Frame(parentframe)
            frame.grid(column=0, row=1, sticky='ew', padx=10, pady=15)
            self.login_button = ttk.Button(
                frame, text='Login',
                width=18, command=lambda: quit_logindialog(False)
            )
            self.login_button.grid(column=0, row=0, sticky='nw', padx=(0,5))
            self.login_button.config(state='disabled')
            cancel_button = ttk.Button(
                frame, text=LANG_DICT['cancelButtonText'][plugin.language],
                width=18, command=lambda: quit_logindialog(True)
            )
            cancel_button.grid(column=1, row=0, sticky='nw', padx=(5,0))

        def set_focus():
            """Force the input focus to the login widget."""
            self.logindialog.focus_force()
            self.usergroup_entry.focus_set()

        # show_logindialog(self)
        self.is_aborted = False
        self.logindialog = tk.Toplevel(self._root)
        self.logindialog.title(LANG_DICT['loginTitle'][plugin.language])
        self._x_pos = None
        geometry = self.position_window(270, 180, centered=True)
        self.logindialog.geometry(geometry)
        self.logindialog.resizable(False, False)
        self.logindialog.protocol('WM_DELETE_WINDOW', lambda: quit_logindialog(True))
        self.logindialog.attributes('-toolwindow', True)
        self.logindialog.attributes('-topmost', True)
        self.logindialog.bind('<Control-A>', enter_defaultlogin)
        self.logindialog.bind('<Control-a>', enter_defaultlogin)
        create_loginmask(self.logindialog)
        create_buttonrow(self.logindialog)
        self.logindialog.after(50, lambda: set_focus())
        self.logindialog.mainloop()

    def quit_mainwindow(self):
        """Close window and event loop and release memory."""
        if self.is_displayed:
            self.is_aborted = True
            self.is_displayed = False
            self.mainwindow.quit()
            self.mainwindow.withdraw()
            if api.is_online:
                graph.stop_timer()
            self.mainwindow = None
            del self.mainwindow

    def show_mainwindow(self):
        """Show the main user interface window."""
        def create_menubar(parentframe):
            """Create start, stop and pause button."""
            def on_startbutton_clicked():
                """Start recording of process variables."""
                self.treeview_enabled = False
                self.time_h_entry.config(state='disabled')
                self.time_min_entry.config(state='disabled')
                self.time_s_entry.config(state='disabled')
                self.treeview.state(['disabled'])
                self.start_button.config(state='disabled')
                self.trend_not_paused = True
                self.pause_button.config(state='normal')
                self.stop_button.config(state='normal')
                self.mainwindow.update_idletasks()
                api.do_systemlogin()
                if api.is_online:
                    self.mainwindow.after(0, graph.start_trend)

            def on_pausebutton_clicked():
                """Pause/resume updating the graph."""
                if self.trend_not_paused:
                    self.pause_button.config(text=LANG_DICT['resumeButtonText'][plugin.language])
                else:
                    self.pause_button.config(text=LANG_DICT['pauseButtonText'][plugin.language])
                    graph.axis_float.set_xlim(graph.tdata[0], graph.tdata[0]+graph.time_length_dt)
                    graph.axis_float.set_ylim(graph.y_min, graph.y_max)
                    for index, vars in enumerate(self.selected_vars):
                        line = vars[3]
                        line.set_data(graph.tdata, graph.ydata[index])
                    graph.canvas.draw()
                self.trend_not_paused = not self.trend_not_paused

            def on_stopbutton_clicked():
                """Stop recording of process variables."""
                self.treeview_enabled = True
                self.time_h_entry.config(state='normal')
                self.time_min_entry.config(state='normal')
                self.time_s_entry.config(state='normal')
                self.treeview.state(['!disabled'])
                self.start_button.config(state='normal')
                if not self.trend_not_paused:
                    self.trend_not_paused = True
                    self.pause_button.config(text=LANG_DICT['pauseButtonText'][plugin.language])
                self.pause_button.config(state='disabled')
                self.stop_button.config(state='disabled')
                graph.stop_timer()

            # create_menubar(parentframe)
            frame = ttk.Frame(parentframe, padding='5')
            frame.grid(column=0, row=0, sticky='nw', padx=5, pady=5)
            self.start_button = ttk.Button(frame, command=on_startbutton_clicked, width=20)
            self.start_button.config(text=LANG_DICT['startButtonText'][plugin.language], state='disabled')
            self.start_button.grid(column=0, row=0)
            self.pause_button = ttk.Button(frame, command=on_pausebutton_clicked, width=20)
            self.pause_button.config(text=LANG_DICT['pauseButtonText'][plugin.language], state='disabled')
            self.pause_button.grid(column=1, row=0, padx=10)
            self.stop_button = ttk.Button(frame, command=on_stopbutton_clicked, width=20)
            self.stop_button.config(text=LANG_DICT['stopButtonText'][plugin.language], state='disabled')
            self.stop_button.grid(column=2, row=0)
            separator = ttk.Separator(parentframe, orient=tk.HORIZONTAL)
            separator.grid(column=0, row=1, sticky='ew', padx=10)

        def create_configurationarea(parentframe):
            """Show all local variables in a treeview."""
            def create_timeselection_frame(parentframe):
                """Create h:m:s entries to choose time span of the graph."""
                def validate_input(inputstring, reason, widget):
                    """Validate the h:m:s entries, max value is 05:59:59."""
                    is_valid = False
                    if reason == 'key':
                        if not inputstring:
                            is_valid = True
                        elif inputstring.isnumeric():
                            is_valid = int(inputstring) <= 99 and len(inputstring) <= 2
                    elif reason == 'focusout':
                        if '!entry3' in widget:
                            entry = self.time_s_entry
                            max_value = 59
                        elif '!entry2' in widget:
                            entry = self.time_min_entry
                            max_value = 59
                        elif '!entry' in widget:
                            entry = self.time_h_entry
                            max_value = 5
                        if not inputstring:
                            entry.delete(0,'end')
                            entry.insert(0,'00')
                        else:
                            number = min(int(inputstring), max_value)
                            value = '0' + str(number) if number < 10 else str(number)
                            entry.delete(0,'end')
                            entry.insert(0,value)
                        check_startbuttonrelease()
                        is_valid = True
                    return is_valid

                # create_timeselection_frame(parentframe)
                labelframe = ttk.Labelframe(parentframe, text=LANG_DICT['chartTimeLabel'][plugin.language])
                labelframe.grid(column=0, row=0, sticky='nw', padx=25, pady=10)
                validatecommand = (self._root.register(validate_input), '%P', '%V', '%W')
                self.time_h_entry = ttk.Entry(labelframe, width=3, validate='all', validatecommand=validatecommand)
                self.time_h_entry.grid(column=0, row=0, padx=(10,0), pady=(5,10))
                self.time_h_entry.insert(0,'00')
                label = ttk.Label(labelframe, text='h')
                label.grid(column=1, row=0, padx=3, pady=5)
                self.time_min_entry = ttk.Entry(labelframe, width=3, validate='all', validatecommand=validatecommand)
                self.time_min_entry.grid(column=2, row=0, padx=(10,0), pady=(5,10))
                self.time_min_entry.insert(0,'01')
                label = ttk.Label(labelframe, text='min')
                label.grid(column=3, row=0, padx=3, pady=5)
                self.time_s_entry = ttk.Entry(labelframe, width=3, validate='all', validatecommand=validatecommand)
                self.time_s_entry.grid(column=4, row=0, padx=(10,0), pady=(5,10))
                self.time_s_entry.insert(0,'00')
                label = ttk.Label(labelframe, text='s')
                label.grid(column=5, row=0, padx=(3,10), pady=5)

            def check_startbuttonrelease():
                """Check if start button can be enabled."""
                time_length_s = self.get_time_length()
                if (
                    self.selected_vars
                    and time_length_s >= 10         # Minimum 10 seconds
                    and time_length_s <= 21600      # Maximum 6 hours
                ):
                    self.start_button.config(state='normal')
                else:
                    self.start_button.config(state='disabled')

            def create_treeview(frame):
                """Create treeview to choose variables to display in graph."""
                def on_keypressed_up(event):
                    """Select the next visible entry above, independant of level."""
                    if self.treeview_enabled:
                        widget = event.widget
                        cur_iid = widget.selection()
                        prev_iid = widget.prev(cur_iid)
                        while True:
                            children = widget.get_children(prev_iid)
                            if children and widget.item(prev_iid, 'open'):
                                prev_iid = children[-1]
                            else:
                                break
                        if not prev_iid:
                            prev_iid = widget.parent(cur_iid)
                        if prev_iid:
                            widget.selection_set(prev_iid)
                            widget.focus(prev_iid)
                            widget.see(prev_iid)

                def on_keypressed_down(event):
                    """Select the next visible entry below, independant of level."""
                    if self.treeview_enabled:
                        widget = event.widget
                        cur_iid = widget.selection()
                        next_iid = widget.next(cur_iid)
                        children = widget.get_children(cur_iid)
                        if children and widget.item(cur_iid, 'open'):
                            next_iid = children[0]
                        elif not next_iid:
                            while True:
                                prev_iid = widget.parent(cur_iid)
                                if prev_iid:
                                    next_iid = widget.next(prev_iid)
                                    if next_iid:
                                        break
                                    else:
                                        cur_iid = prev_iid
                                else:
                                    break
                        if next_iid:
                            widget.selection_set(next_iid)
                            widget.focus(next_iid)
                            widget.see(next_iid)

                def on_keypressed_left(event):
                    """Close current entry or select the next parent entry on top or left side."""
                    if self.treeview_enabled:
                        widget = event.widget
                        iid = widget.selection()
                        children = widget.get_children(iid)
                        if children and widget.item(iid, 'open'):
                            widget.item(iid, open=False)
                        else:
                            iid = widget.parent(iid)
                        if iid:
                            widget.selection_set(iid)
                            widget.focus(iid)
                            widget.see(iid)
                        return 'break'

                def on_keypressed_right(event):
                    """Open current entry or select the next child entry below or on right side."""
                    if self.treeview_enabled:
                        widget = event.widget
                        cur_iid = widget.selection()
                        children = widget.get_children(cur_iid)
                        if children:
                            if widget.item(cur_iid, 'open'):
                                cur_iid = children[0]
                            else:
                                widget.item(cur_iid, open=True)
                            widget.selection_set(cur_iid)
                            widget.focus(cur_iid)
                            widget.see(cur_iid)

                def on_keypressed_ctrl_home(event):
                    """Open current entry or select the next child entry below or on right side."""
                    if self.treeview_enabled:
                        widget = event.widget
                        children = widget.get_children('')
                        root_iid = children[0]
                        widget.selection_set(root_iid)
                        widget.focus(root_iid)
                        widget.see(root_iid)

                def on_keypressed_ctrl_end(event):
                    """Open current entry or select the next child entry below or on right side."""
                    if self.treeview_enabled:
                        widget = event.widget
                        children = widget.get_children('')
                        last_iid = children[-1]
                        while True:
                            children = widget.get_children(last_iid)
                            if children:
                                last_iid = children[-1]
                            else:
                                break
                        if last_iid:
                            widget.selection_set(last_iid)
                            widget.focus(last_iid)
                            widget.see(last_iid)

                def on_keypressed(event):
                    """Depending on pressed key do actions:

                    <Blank> = Toggle selection state,
                    <+> = Open current entry,
                    <-> = Close current entry,
                    <other key> = Search for next entry starting with pressed key.
                    """

                    if self.treeview_enabled:
                        widget = event.widget
                        cur_iid = widget.selection()
                        if event.char == ' ':
                            toggle_checkedstate(cur_iid)
                            check_startbuttonrelease()
                        elif event.char == '+':
                            children = widget.get_children(cur_iid)
                            if children:
                                widget.item(cur_iid, open=True)
                        elif event.char == '-':
                            children = widget.get_children(cur_iid)
                            if children:
                                widget.item(cur_iid, open=False)
                        elif event.char:
                            searchtext = '  ' + event.char.lower()
                            parent_iid = widget.parent(cur_iid)
                            if parent_iid:
                                children = widget.get_children(parent_iid)
                                found_iid, char_found = None, False
                                for child in children:
                                    if child == cur_iid[0]:
                                        char_found = False
                                    elif (
                                        widget.item(child, 'text').lower().__contains__(searchtext)
                                        and not char_found
                                    ):
                                        found_iid = child
                                        char_found = True
                                if found_iid:
                                    widget.selection_set(found_iid)
                                    widget.focus(found_iid)
                                    widget.see(found_iid)

                def on_treeview_clicked(event):
                    """Change picture for checkbox if checkbox is clicked."""
                    if self.treeview_enabled:
                        widget = event.widget
                        iid = widget.identify_row(event.y)
                        if iid:
                            widget.selection_set(iid)
                            widget.focus(iid)
                            widget.see(iid)
                            if 'image' in widget.identify('element', event.x, event.y):
                                toggle_checkedstate(iid)
                                check_startbuttonrelease()

                def on_treeview_doubleclicked(event):
                    """Change picture for checkbox if row is double-clicked."""
                    if self.treeview_enabled:
                        widget = event.widget
                        iid = widget.identify_row(event.y)
                        if iid:
                            widget.selection_set(iid)
                            widget.focus(iid)
                            widget.see(iid)
                            toggle_checkedstate(iid)
                            check_startbuttonrelease()

                def toggle_checkedstate(iid):
                    """Change pictures and tags recursively for checkbox."""
                    def search_next_color():
                        """Search circular for the next available color."""
                        maxlen = len(graph.color_scheme)
                        for index in range(graph.next_color, 2*maxlen):
                            i = index % maxlen
                            if not graph.color_scheme[i][1]:
                                return i

                    def add_checkmarks(iid):
                        """Mark all upstream checkboxes in variable tree as checked."""
                        parent = self.treeview.parent(iid)
                        while parent:
                            values = list(self.treeview.item(parent, 'values'))
                            values[2] = str(int(values[2]) + 1)
                            self.treeview.item(parent, image=self._checkbox_checked_disabled_img, values=values)
                            parent = self.treeview.parent(parent)

                    def remove_checkmarks(iid):
                        """Mark all upstream checkboxes in variable tree as unchecked."""
                        parent = self.treeview.parent(iid)
                        while parent:
                            values = list(self.treeview.item(parent, 'values'))
                            checkmark_counter = int(values[2]) - 1
                            values[2] = str(checkmark_counter)
                            if checkmark_counter > 0:
                                self.treeview.item(parent, values=values)
                            else:
                                self.treeview.item(parent, image=self._checkbox_unchecked_disabled_img, values=values)
                            parent = self.treeview.parent(parent)

                    # toggle_checkedstate(iid)
                    tags = self.treeview.item(iid, 'tags')
                    if 'selected' in tags:
                        values = list(self.treeview.item(iid, 'values'))
                        del self.selected_vars[graph.remove_entry(values)]
                        values[2] = str(int(values[2]) - 1)
                        self.treeview.item(
                            iid, image=self._checkbox_unchecked_enabled_img, values=values, tags=('unselected', )
                        )
                        remove_checkmarks(iid)
                    elif 'unselected' in tags:
                        if len(self.selected_vars) < len(graph.color_scheme):
                            graph.next_color = search_next_color()
                            values = list(self.treeview.item(iid, 'values'))
                            self.selected_vars.append(graph.add_entry(values))
                            values[2] = str(int(values[2]) + 1)
                            self.treeview.item(
                                iid, image=self._checkbox_checked_enabled_img, values=values, tags=('selected', )
                            )
                            add_checkmarks(iid)
                        else:
                            title = LANG_DICT['maxSelectTitle'][plugin.language]
                            message = LANG_DICT['maxSelectText'][plugin.language]
                            messagebox.showinfo(parent=self.mainwindow, title=title, message=message)

                def insert_variables():
                    """Add local variables to the treeview."""
                    def get_local_variables(local_force_data, path=None):
                        """Extract local variable names of the program from the force data list."""
                        if path is None:
                            path = ''
                            suffix = ''
                            varpath = ''
                        property_names = local_force_data.keys()
                        for property_name in property_names:
                            property = local_force_data.get(property_name)
                            datatype = property.get('datatype')
                            instances = property.get('instances')
                            if self.iid:
                                if not path:
                                    varpath = property_name
                                elif property_name[0] != '[':
                                    varpath = f'{path}.{property_name}'
                                else:
                                    varpath = f'{path}{property_name}'
                            values = (datatype, varpath, '0')
                            if instances is None:
                                if property.get('process_value') is None or (property_name != 'ENO'):
                                    id = self.treeview.insert(
                                        parent=self.iid, index='end', text='  '+property_name,
                                        image=self._checkbox_unchecked_enabled_img, values=values, tag=('unselected')
                                    )
                            else:
                                id = self.treeview.insert(
                                    parent=self.iid, index='end', text='  '+property_name,
                                    image=self._checkbox_unchecked_disabled_img, values=values, tag=('unselectable')
                                )
                                if path:
                                    suffix = '.' + property_name if property_name[0] != '[' else property_name
                                    path += suffix
                                elif self.iid:
                                    suffix = property_name
                                    path = property_name
                                old_id = self.iid
                                self.iid = id
                                get_local_variables(instances, path)
                                self.iid = old_id
                                path = path.removesuffix(suffix)

                    # insert_variables()
                    self.iid = ''
                    get_local_variables(api.local_force_data)
                    self.treeview.tag_configure('unselectable', background='#f0f0f0')
                    self.selected_vars = []
                    self.treeview_enabled = True

                # create_treeview(frame)
                header0 = LANG_DICT['listboxHeader0'][plugin.language]
                header1 = LANG_DICT['listboxHeader1'][plugin.language]
                #self.treeview = ttk.Treeview(frame, column=(header1), selectmode='none')
                self.treeview = ttk.Treeview(frame, column=(header1, ), selectmode='none')
                self.treeview.heading('#0', text=header0)
                self.treeview.column('#0', stretch=tk.NO, width=240)
                self.treeview.heading('#1', text=header1)
                self.treeview.column('#1', stretch=tk.YES, width=120)
                self.treeview.grid(column=0, row=1, sticky='nsew')
                vertical_scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.treeview.yview)
                vertical_scrollbar.grid(column=1, row=1, sticky='ns')
                horizontal_scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=self.treeview.xview)
                horizontal_scrollbar.grid(column=0, row=2, sticky='ew')
                self.treeview.config(
                    yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set
                )
                self.treeview.bind('<ButtonRelease-1>', on_treeview_clicked)
                self.treeview.bind('<Double-1>', on_treeview_doubleclicked)
                self.treeview.bind('<Up>', on_keypressed_up)
                self.treeview.bind('<Down>', on_keypressed_down)
                self.treeview.bind('<Left>', on_keypressed_left)
                self.treeview.bind('<Right>', on_keypressed_right)
                self.treeview.bind('<Control-Home>', on_keypressed_ctrl_home)
                self.treeview.bind('<Control-End>', on_keypressed_ctrl_end)
                self.treeview.bind('<Key>', on_keypressed)
                insert_variables()

            # create_configurationarea(parentframe)
            frame = ttk.Frame(parentframe)
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
            create_timeselection_frame(frame)
            create_treeview(frame)
            separator = tk.Frame(frame, bg='#d5dfe5', width=1)
            separator.grid(column=2, row=0, rowspan=3, sticky='ns', padx=(3,0))
            separator = tk.Frame(frame, bg='white', width=1)
            separator.grid(column=3, row=0, rowspan=3, sticky='ns')
            return frame

        def move_sashpos(event):
            """Move the sash on doubleclick."""
            position = self.panedwindow.sashpos(0)
            if position < 25 or position > 450:
                self.panedwindow.sashpos(0, 360)
            else:
                self.panedwindow.sashpos(0, 0)

        def set_focus():
            """Force the input focus to the treeview."""
            self.mainwindow.focus_force()
            self.panedwindow.sashpos(0, 360)
            self.treeview.focus_set()
            children = self.treeview.get_children('')
            root_iid = children[0]
            self.treeview.selection_set(root_iid)
            self.treeview.focus(root_iid)
            self.treeview.item(root_iid, open=True)

        # show_mainwindow(self)
        self.mainwindow = tk.Toplevel(self._root)
        title = (f'{LANG_DICT["menuEntryName"][plugin.language]} - {api.program_path}')
        self.mainwindow.title(title)
        geometry = self.position_window(1370, 790)
        self.mainwindow.geometry(geometry)
        self.mainwindow.protocol('WM_DELETE_WINDOW', self.quit_mainwindow)
        self.mainwindow.attributes('-topmost', True)
        self.mainwindow.columnconfigure(0, weight=1)
        self.mainwindow.rowconfigure(2, weight=1)
        create_menubar(self.mainwindow)
        frame = ttk.Frame(self.mainwindow)
        frame.grid(column=0, row=2, sticky='nsew', padx=5, pady=(0,5))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        style = ttk.Style()
        style.configure('my.TPanedwindow', background='#d5dfe5')
        self.panedwindow = ttk.Panedwindow(frame, orient=tk.HORIZONTAL, style='my.TPanedwindow')
        self.panedwindow.grid(column=0, row=0, sticky='nsew')
        self.panedwindow.columnconfigure(0, weight=1)
        self.panedwindow.rowconfigure(0, weight=1)
        self.panedwindow.add(create_configurationarea(self.panedwindow))
        self.panedwindow.add(graph.create_drawingarea(self.panedwindow))
        self.panedwindow.bind('<Double-1>', move_sashpos)
        self.mainwindow.minsize(800, 400)
        self.mainwindow.update_idletasks()
        self.mainwindow.after(50, lambda: set_focus())
        self.is_displayed = True
        self.mainwindow.mainloop()

    def get_time_length(self):
        """Calculate the time span in seconds of the graph."""
        hours = int(self.time_h_entry.get())
        minutes = int(self.time_min_entry.get()) + 60 * hours
        seconds = int(self.time_s_entry.get()) + 60 * minutes
        return seconds

class Graph():
    def __init__(self):
        mpl.rcParams['keymap.yscale'] = ''      # Remove toggle scaling of y-axes ('log'/'linear'), key = l
        mpl.rcParams['keymap.xscale'] = ''      # Remove toggle scaling of x-axes ('log'/'linear'), key = L, k
        mpl.rcParams['keymap.back'] = ''        # Remove forward navigation, key = left, c, backspace, MouseButton.BACK
        mpl.rcParams['keymap.forward'] = ''     # Remove backward navigation, key = right, v, MouseButton.FORWARD
        mpl.rcParams['keymap.grid'] = ''        # Remove switching on/off major grids in current axes, key = g
        mpl.rcParams['keymap.grid_minor'] = ''  # Remove switching on/off minor grids in current axes, key = G
        self.axis_float, self.axis_bool = None, None
        self.float_count, self.bool_count = 0, 0
        self.y_min, self.y_max = 0.0, 1.0
        self.recordinginterval_ms = 0
        self.recordinginterval_dt = None
        self.asynctimerinterval_s = 0
        self.frames_to_shift = 0
        self.time_length_dt = None
        dumppath = os.path.join(os.environ.get('TEMP'), 'SILworX_Plugins')
        if not os.path.exists(dumppath):
            os.makedirs(dumppath)
        self.dumpfileA = os.path.join(dumppath, PLUGIN_NAME+'_recording_A.dump')
        self.dumpfileB = os.path.join(dumppath, PLUGIN_NAME+'_recording_B.dump')
        self.recordingA, self.recordingB = False, False
        self.allocation = []
        self.timer = None
        self.event = threading.Event()
        self.tdata, self.ydata = [], []
        self.next_color = 0
        self.color_scheme = [
            ['#1f77b4', False],     # tab:blue
            ['#ff7f0e', False],     # tab:orange
            ['#2ca02c', False],     # tab:green
            ['#d62728', False],     # tab:red
            ['#bcbd22', False],     # tab:olive
            ['#17becf', False],     # tab:cyan
            ['#e377c2', False],     # tab:pink
            ['#8c5648', False],     # tab:brown
            ['#9467bd', False],     # tab:purple
            ['#7f7f7f', False]      # tab:gray
        ]

    def start_trend(self):
        """Start recording of process variables."""
        def record_async_localforcedata():
            """Return varpaths from selcted variables."""
            if self.event.is_set():
                if api.is_online:
                    api.do_disconnect()
            if self.recordingA:
                if not self.event.is_set():
                    self.recordingB = True
                    api.start_localforcedata_recording(self.dumpfileB)
                self.recordingA = False
                api.stop_localforcedata_recording(self.dumpfileA, self.allocation)
            elif self.recordingB:
                if not self.event.is_set():
                    self.recordingA = True
                    api.start_localforcedata_recording(self.dumpfileA)
                self.recordingB = False
                api.stop_localforcedata_recording(self.dumpfileB, self.allocation)
            else:
                self.recordingA = True
                response = api.start_localforcedata_recording(self.dumpfileA)
                self.allocation = api.get_forcedatarecording_layout(response)
            if not api.is_online:
                self.event.set()
            if self.event.is_set():
                if api.is_online:
                    api.do_disconnect()
            else:
                self.timer = threading.Timer(self.asynctimerinterval_s, record_async_localforcedata)
                self.timer.daemon = True
                self.timer.start()

        # start_trend(self)
        self.varpaths = [var[0] for var in gui.selected_vars]
        self.recordingA = False
        self.recordingB = False
        self.event.clear()
        self.tdata = [datetime.datetime.now()]
        time_length_s = gui.get_time_length()
        self.time_length_dt = datetime.timedelta(seconds=time_length_s)
        self.axis_float.set_xlim(self.tdata[0], self.tdata[0]+self.time_length_dt)
        self.ydata = [[0] for _ in range(len(gui.selected_vars))]
        self.y_min = 0.0
        self.y_max = 1.0
        self.zero_offset = 0.1
        self.axis_float.set_ylim(self.y_min, self.y_max)
        self.canvas.draw()
        self.recordinginterval_ms = max(api.cycle_time, math.ceil(time_length_s/20))
        self.recordinginterval_dt = datetime.timedelta(milliseconds=self.recordinginterval_ms)
        self.asynctimerinterval_s = max(3, math.ceil(self.recordinginterval_ms/500))
        x_length_to_shift = max(time_length_s/10, 1.05*self.asynctimerinterval_s)
        self.frames_to_shift = max(1, math.ceil(x_length_to_shift/(self.recordinginterval_ms/1000)))
        record_async_localforcedata()

    def stop_timer(self, wait_for_termination=True):
        self.event.set()
        if self.timer:
            self.timer.cancel()
        if api.is_online and wait_for_termination:
            if self.recordingA:
                self.recordingA = False
                api.stop_localforcedata_recording(self.dumpfileA)
            if self.recordingB:
                self.recordingB = False
                api.stop_localforcedata_recording(self.dumpfileB)
            api.do_disconnect()
        if self.timer:
            if wait_for_termination:
                self.timer.join()
            self.timer = None

    def create_drawingarea(self, parentframe):
        """Create canvas for graph."""
        def create_trend(parentframe):
            """Create figure, axis and toolbar for graph."""
            def format_xaxis(start_time, offset):
                """Show date and time in optimized format on x-axis."""
                locator = mdates.AutoDateLocator(minticks=10, maxticks=20)
                formatter = mdates.ConciseDateFormatter(locator)
                formatter.formats = ['%y', '%b', '%d', '%H:%M', '%H:%M', '%S.%f', ]
                formatter.zero_formats = [''] + formatter.formats[:-1]
                formatter.zero_formats[3] = LANG_DICT['offsetFormatMD'][plugin.language]
                fmtYearMonth = LANG_DICT['offsetFormatYM'][plugin.language]
                fmtYearMonthDay = LANG_DICT['offsetFormatYMD'][plugin.language]
                formatter.offset_formats = [
                    '', '%Y', fmtYearMonth, fmtYearMonthDay, fmtYearMonthDay, fmtYearMonthDay+' %H:%M',
                ]
                self.axis_float.xaxis.set_major_locator(locator)
                self.axis_float.xaxis.set_major_formatter(formatter)
                self.axis_float.set_xlim(start_time, start_time+offset)

            # create_trend(parentframe)
            plt.cla()
            self.figure = plt.figure(layout='constrained')
            self.axis_float = self.figure.add_subplot()
            self.axis_float.grid()
            self.canvas = FigureCanvasTkAgg(self.figure, master=parentframe)
            format_xaxis(
                datetime.datetime.now(), datetime.timedelta(seconds=gui.get_time_length())
            )
            self.canvas.draw()
            toolbar = NavigationToolbar2Tk(self.canvas, parentframe, pack_toolbar=False)
            toolbar.update_idletasks()
            toolbar.pack(side=tk.TOP, fill=tk.X)
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            toolbar.children['!button2'].pack_forget()
            toolbar.children['!button3'].pack_forget()
            toolbar.children['!button4'].pack_forget()

        # create_drawingarea(self, parentframe)
        frame = ttk.Frame(parentframe)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        for color in self.color_scheme:
            color[1] = False
        self.next_color = 0
        self.float_count, self.bool_count = 0, 0
        create_trend(frame)
        return frame

    def update_trend(self, chunklist):
        chunk_starttime_dt = self.chunk_endtime_dt - len(chunklist) * self.recordinginterval_dt
        new_tdata = []
        new_ydata = [[] for _ in gui.selected_vars]
        for chunk in chunklist:
            if chunk_starttime_dt > self.tdata[-1]:
                new_tdata.append(chunk_starttime_dt)
                for var_index in range(len(gui.selected_vars)):
                    for alloc_index in range(len(self.allocation) - 1):
                        element = self.allocation[alloc_index]
                        if element.get('sortindex') == var_index:
                            new_value = chunk[alloc_index]
                            if element.get('is_time'):
                                new_value /= 1000.0
                            new_ydata[var_index].append(new_value)
                            if new_value <= self.y_min:
                                self.y_min = 1.1 * new_value if new_value < 0.0 else -self.zero_offset
                                if gui.trend_not_paused:
                                    self.axis_float.set_ylim(self.y_min, self.y_max)
                            elif new_value >= self.y_max:
                                self.y_max = 1.1 * new_value
                                self.zero_offset = self.y_max - new_value
                                if gui.trend_not_paused:
                                    self.axis_float.set_ylim(self.y_min, self.y_max)
                            break
            chunk_starttime_dt += self.recordinginterval_dt
        move_data = False
        self.tdata += new_tdata
        if self.tdata[-1] >= self.tdata[0] + self.time_length_dt:
            self.tdata = self.tdata[self.frames_to_shift:]
            if gui.trend_not_paused:
                self.axis_float.set_xlim(self.tdata[0], self.tdata[0]+self.time_length_dt)
            move_data = True
        for index, vars in enumerate(gui.selected_vars):
            self.ydata[index] += new_ydata[index]
            if move_data:
                self.ydata[index] = self.ydata[index][self.frames_to_shift:]
            if gui.trend_not_paused:
                line = vars[3]
                line.set_data(self.tdata, self.ydata[index])
        if gui.trend_not_paused:
            self.canvas.draw()

    def add_entry(self, values):
        """Add item to selected_vars and lock used color."""
        datatype, varpath = values[0], values[1]
        color = self.color_scheme[self.next_color][0]
        self.color_scheme[self.next_color][1] = True
        if varpath[0] == '_':
            varpath = ' ' + varpath
        line = Line2D([], [], drawstyle='steps', label=varpath, color=color, linewidth=1.5)
        if datatype == 'BOOL':
            self.bool_count += 1
            if self.axis_bool is None:
                self.axis_bool = self.axis_float.twinx()
                self.axis_bool.set_ylim(-0.03, 1.03)
                self.axis_bool.set_yticks([0, 1], ['FALSE', 'TRUE'])
            self.axis_bool.add_line(line)
            self.axis_bool.legend(
                loc='lower right', bbox_to_anchor=(1.06, 1),
                fontsize='small', fancybox=True, shadow=True
            )
        else:
            self.float_count += 1
            self.axis_float.add_line(line)
            self.axis_float.legend(
                loc='upper left', bbox_to_anchor=(-0.04, -0.03),
                fontsize='small', fancybox=True, shadow=True
            )
        self.canvas.draw()
        row = [varpath, datatype, color, line]
        return row

    def remove_entry(self, values):
        """Delete item from selected_vars and release used color."""
        def delete_entries(legend, varpath):
            """Delete legend, line and release color."""
            if legend is not None:
                legend.remove()
                del legend
            for var_index, var in enumerate(gui.selected_vars):
                if var[0] == varpath:
                    for color_index, color in enumerate(self.color_scheme):
                        if color[0] == var[2]:
                            self.color_scheme[color_index][1] = False
                            break
                    line = var[3]
                    line.remove()
                    del line
                    return var_index

        # remove_entry(values)
        if values[0] == 'BOOL':
            self.bool_count -= 1
            var_index = delete_entries(self.axis_bool.get_legend(), values[1])
            if self.bool_count > 0:
                self.axis_bool.legend(
                    loc='lower right', bbox_to_anchor=(1.06, 1),
                    fontsize='small', fancybox=True, shadow=True
                )
            else:
                self.axis_bool.remove()
                self.axis_bool = None
        else:
            self.float_count -= 1
            var_index = delete_entries(self.axis_float.get_legend(), values[1])
            if self.float_count > 0:
                self.axis_float.legend(
                    loc='upper left', bbox_to_anchor=(-0.04, -0.03),
                    fontsize='small', fancybox=True, shadow=True
                )
        self.canvas.draw()
        return var_index

def print_message(level, key, additional_info=''):
    """Show message with date and time in SILworX log window."""
    timestamp_dt = datetime.datetime.now()
    dateFormat = LANG_DICT['logDateFormat'][plugin.language]
    dt = timestamp_dt.strftime(dateFormat+' %H:%M:%S.')
    ms = timestamp_dt.strftime('%f')
    timestamp_ms = dt + ms[:3]
    text = LANG_DICT[key][plugin.language]
    print(f'{timestamp_ms}, {text}{additional_info}')
    if level == 'ERR' and not plugin.is_development_mode:
        print(f'{text}{additional_info}', file=sys.stderr)

def convert_to_windows_codepage(s):
    """Convert an url coded string to the current Windows codepage."""
    raw = s.replace('%00', '%')     # quick and dirty: s is UTF16 encoded, but requests.utils.unquote needs UTF8
    return requests.utils.unquote(raw, 'cp1252')

def parse_args():
    """Read command line arguments delivered from SILworX."""
    parser = ArgumentParser()
    parser.add_argument('--tls-certificate',
                        dest='certificate',
                        default=r'C:\Plugins\Certificates\api_cert.pem')
    parser.add_argument('--api-port',
                        dest='apiport',
                        default='443')
    parser.add_argument('--plugin-port',
                        dest='pluginport',
                        default='8400')
    parser.add_argument('--language',
                        dest='language',
                        default='de')
    parser.add_argument('--read-secret',
                        dest='readsecret',
                        action='store_true',
                        default=False)
    return parser.parse_args()

def run_oscope():
    """Collect all information from SILworX to display an oscilloscope-like graph"""
    api.read_structuretree()
    gui.show_logindialog()
    if gui.is_aborted:
        print_message('ERR', 'funcAbortedErr', LANG_DICT['menuEntryName'][plugin.language])
        sys.stdout.flush()
    else:
        gui.show_splashscreen()
        api.do_systemlogin()
        if api.is_online:
            api.read_systeminfo()
            api.read_localforcedata()
            if api.is_online:
                api.do_disconnect()
                gui.quit_splashscreen()
                sys.stdout.flush()
                gui.show_mainwindow()
                print_message('INFO', 'winClosedInfo', LANG_DICT['menuEntryName'][plugin.language])
                sys.stdout.flush()
            else:
                gui.quit_splashscreen()
        else:
            gui.quit_splashscreen()
        sys.stdout.flush()

def run_plugin(port):
    """Start WebSocket communication with SILworX."""
    ws = websocket.WebSocketApp(
        'ws://localhost:'+port,
        on_open=plugin.on_open,
        on_message=plugin.on_message,
        on_error=plugin.on_error,
        on_close=plugin.on_close
    )
    try:
        ws.run_forever(dispatcher=rel, reconnect=1)     # Set dispatcher to automatic reconnection
    except ConnectionRefusedError as e:
        print_message('ERR', 'onErrorErr', f' = {e}')
        sys.exit(1)
    rel.signal(2, rel.abort)                            # Catch keyboard interrupt SIGINT = CTRL+C
    try:
        rel.dispatch()
    except ConnectionResetError as e:
        print_message('ERR', 'onErrorErr', f' = {e}')
        sys.exit(1)

if __name__ == '__main__':
    arguments = parse_args()
    plugin = Plugin(arguments)
    api = API(arguments)
    gui = GUI()
    graph = Graph()
    run_plugin(arguments.pluginport)
    sys.exit(0)
