# -*- coding: utf-8 -*-

"""
Collects online-diagnostic data from project and stores this in a csv-file.

This plug-in works with SILworX V14 or higher. It doesn't work without
SILworX. The core function is started on the context menu of a resource
in an opened SILworX project.

This plug-in reads diagnostic_data

Date:   2024-01-31
Status: RELEASE
Author: Mustafa Muslem / HIMA
"""

###################################
# Import section
###################################

import os  # Miscellaneous operating system interfaces
import sys  # System-specific parameters and functions
from argparse import ArgumentParser  # Parser for command-line options, arguments and sub-commands
from datetime import datetime, timezone  # Basic date and time types
import websocket  # WebSocket client for Python
import rel  # Registered Event Listener
import requests  # HTTP for humans
import json  # JSON encoder and decoder
import screeninfo  # Fetch location and size of physical screens
import tkinter as tk  # Python interface to Tcl/Tk
from tkinter import ttk  # Tk themed widgets
from tkinter import filedialog as fd  # File selection dialogs
import csv  # CSV file reading and writing

#
from spyder.plugins.findinfiles.widgets import combobox

###################################
# Some const variables
###################################
PLUGIN_NAME = 'read_diagnostic'
VERSION = '1.1-0'
AUTHOR = 'HIMA Paul Hildebrandt GmbH'
TRIGGER_NAME = 'START_Reading_Diagnostic'
LANG_DICT = {
    'menuEntryName': ('Diagnose Auslesen',
                      'Read Diagnostic'),
    'onMessageErr': ('Fehler: Unerwarteter Message-Typ empfangen, Message',
                     'Error: Unexpected message type received, Message'),
    'onTriggerErr': ('Fehler: Unerwarteter Trigger-Name in Plugin',
                     'Error: Unexpected trigger name in plugin'),
    'onErrorErr': ('Fehler: Interner Fehler aufgetreten, Fehler',
                   'Error: Internal error occured, Error'),
    'projOpenedInfo': ('Info: Projekt geöffnet, SessionId',
                       'Info: Project opened, SessionId'),
    'projClosedInfo': ('Info: Projekt geschlossen, SessionId',
                       'Info: Project closed, SessionId'),
    'apiServerErr': ('Fehler: Keine Antwort auf API-Anfrage erhalten, URL',
                     'Error: No response received to API request, URL'),
    'apiRequestInfo': ('Info: API-Anfrage ok, URL',
                       'Info: API request ok, URL'),
    'apiRequestErr': ('Fehler: Ungültige API-Anfrage ohne Fehlermeldung, URL',
                      'Error: Bad API request without advice, URL'),
    'apiStatusErr': ('Fehler: Unerwarteter Statuscode für API-Anfrage, URL::Code',
                     'Error: Unexpected status code for API request, URL::Code'),
    'dateFormat': ('%d.%m.%Y',
                   '%Y-%m-%d'),
    'initWaitText': ('System-Daten aufnehmen, bitte warten...',
                     'Collecting system data, please wait...'),
    'loginTitle': ('System-Login',
                   'System Login'),
    'loginLabel': ('Zugangsdaten',
                   'Access Data'),
    'loginGroupText': ('Benutzergruppe',
                       'User Group'),
    'loginPWText': ('Passwort',
                    'Password'),
    'loginAccessText': ('Zugriffsart',
                        'Access Mode'),
    'loginModeValue': ('Lesen',
                       'Read'),
    'cancelButtonText': ('Abbrechen',
                         'Cancel'),
    'funcAbortedErr': ('Fehler: Funktion abgebrochen: ',
                       'Error: Function aborted: '),
    'exportWinTitle': ('Export: Diagnosedaten als CSV sichern',
                       'Export: Save Diagnostic Data as CSV'),
    'delimiterLabel': ('Trennzeichen',
                       'Delimiter'),
    'delimiterText1': ('Komma',
                       'Comma'),
    'delimiterText2': ('Semikolon',
                       'Semicolon'),
    'codingLabel': ('Codierung',
                    'Coding'),
    'Category':('Kategorie-Auswahl: ', 'Category-Selection: '),
    'exportfileLabel': ('Exportdatei',
                        'Export File'),
    'fileselectTitle': ('Wählen Sie die Zieldatei des Diagnose-Exports',
                        'Select Diagnostic Export Destination File'),
    'csvFiletypeText': ('CSV-Dateien',
                        'CSV files'),
    'allFiletypeText': ('Alle Dateien',
                        'All files'),
    'showerrWinTitle': ('Fehler',
                        'Error'),
    'csvErrorMessage': ('Die CSV-Datei muss die Endung ".csv" haben.',
                        'The CSV file extension must be ".csv".'),
    'pathErrorMessage': ('Das System kann den angegebenen Pfad nicht finden.',
                         'The system cannot find the path specified.'),
    'fnErrorMessage': ('Der angegebene Dateiname ist nicht gültig.',
                       'The specified file name is not valid.'),
    'acsErrorMessage': ('Kein Schreiberlaubnis für dieses Verzeichnis.',
                        'No write permit for this directory.'),
    'askyesnoWinTitle': ('Datei überschreiben?',
                         'Overwrite file?'),
    'existingMessage': ('Eine Datei mit diesem Namen existiert bereits.\n'
                        'Soll die existierende Datei überschrieben werden?',
                        'A file with this name already exists.\n'
                        'Do you want to overwrite the existing file?'),
    'fileWrittenInfo': ('Info: CSV-Datei gespeichert, Dateiname',
                        'Info: CSV file saved, Filename'),
    'noFileSelectInfo': ('Info: Zieldateiauswahl abgebrochen',
                         'Info: Destination file selection aborted'),
    'Fenster':('Fenster zur Auswahl der Module und Kategorien','Window for selecting modules and categories'),

    'optionen': ('Wählen Sie eine Option aus:', 'Choose an option:'),
    'alle_Module':('Diagnose aller Module', 'Diagnosis of all modules'),
    'Einzeln_Modul':('Diagnose des Moduls_','Diagnosis of Module_'),
    'Button_Text':('Ausführen','Execute'),
    'csvrow1_nodata': ('Datenabfrage nicht erfolgreich, kein Zugriff auf API möglich',
                       'Data query not successful, no API access possible'),
    'csvrow2_nodata': ('Datenabfrage nicht erfolgreich, keine Online-Verbindung möglich',
                       'Data query not successful, no online connection possible'),
    'csvrow0_header': ('Diagnosedaten des Moduls:', 'Diagnostic Data of Module:'),
    'csvrow1_header': ('ID[.]Kategorie[.]Zeitstempel[.]Laufzeit[.]Diagnosetext[.]Parameter[.]',
                       'ID[.]Category[.]Timestamp[.]Duration[.]Diagnostic Text[.]Parameter[.]'),
    'csvrow3_nodata': ('Es wurde keine Einträge gefunden',
                       'no entries were found'),
    'csvrow2_header':  ('Datum[.]Uhrzeit',
                        'Date[.]Time'),
    'csvrow3_header':  ('Produkt[.]Version[.]Lizenz[.]Gültig bis',
                        'Product name[.]Version[.]License[.]Valid until'),
    'csvrow4_header':  ('Projekt[.]Konfiguration[.]Ressource[.]System-ID',
                        'Project[.]Configuration[.]Resource[.]System ID'),
}

root = None
class Plugin():
    """
    Communicate with SILworX plugin interface.
    """
    n=0
    m=0
    def __init__(self, args):
        self.language = 0 if args.language == 'de' else 1
        self.user_session_id = ''
        self.resource_address = ''
        self.is_running_sema = 0
        if args.readsecret:
            self.is_development_mode = False
            logpath = os.path.join(os.environ.get('APPDATA'), 'SILworX_Plugins')
            if not os.path.exists(logpath):
                os.makedirs(logpath)
            logfile = os.path.join(logpath, PLUGIN_NAME + '.log')
            sys.stdout = open(logfile, 'a')
            print(f'\n--------------------------'
                  f'\n  {PLUGIN_NAME} V{VERSION}'
                  f'\n--------------------------')
        else:
            self.is_development_mode = True

    def on_open(self, ws):
        """
        Register the plugin in SILworX.
        Called when a WebSocket communication with SILworX is opened.
        """

        secret = '' if self.is_development_mode else sys.stdin.readline()
        register = {
            'msg_type': 'register',
            'plugin_name': PLUGIN_NAME,
            'secret': secret,
            'plugin_version': VERSION,
            'plugin_author': AUTHOR,
            'customized_contextmenu_trigger': [
                {'menu_entry_name': LANG_DICT['menuEntryName'][self.language],
                 'node_type': 'resource',
                 'trigger_name': TRIGGER_NAME
                 },
            ],
            'predefined_trigger': [
                {'trigger_name': 'TRIGGER_SESSION_ID_CHANGED'}
            ]
        }

        ws.send(json.dumps(register))

    def on_message(self, ws, message):
        """
        Call the responsible message handler.
        Called when SILworX sends a message to the plugin.
        """
        def do_trigger_action(ws, trigger):
            """
            Do the requested trigger action and acknowledge the receipt of the trigger.
            Called when SILworX triggers an action from the plugin.
            """
            ws.send(json.dumps({'msg_type': 'resume', 'trigger_id': trigger.get('trigger_id')}))
            trigger_name = trigger.get('trigger_name')
            if trigger_name == 'TRIGGER_SESSION_ID_CHANGED':
                self.user_session_id = trigger.get('session_id')
                key = 'projOpenedInfo' if self.user_session_id else 'projClosedInfo'
                print_message('INFO', key, f' = {self.user_session_id}')
            elif trigger_name == TRIGGER_NAME:
                self.resource_address = trigger.get('internal_address')
                run_diagnostic()
            else:
                print_message('ERR', 'onTriggerErr', f' {PLUGIN_NAME}: {trigger_name}')

        msg = json.loads(message)
        msg_type = msg.get('msg_type')
        if msg_type == 'trigger':
            do_trigger_action(ws, msg)
        elif msg_type == 'advice':
            api.print_advices(msg.get('advices'))
        else:
            print_message('INFO', 'onMessageErr', f' = {message}')

    def on_error(self, ws, error):
        """
        Show the error occured.
        Called if we have an error in Python code (*shouldn't be*) or
        when SILworX closes the WebSocket connection with the plugin.
        """

        if self.is_development_mode and not isinstance(error, websocket.WebSocketConnectionClosedException):
            raise
        else:
            print_message('ERR', 'onErrorErr', f' = {error}')
        sys.exit(1)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Exit the plugin.
        Called when connection is closed or, during develop mode, CTRL-C is received.
        """

        sys.exit(0)


class API():
    """
    Communicate with SILworX API interface.
    """

    def __init__(self, args):
        self.certificate = args.certificate
        self.url_fixed_part = f'https://localhost:{args.apiport}/api/v1/'
        self.has_user_management = False
        self.usergroup, self.password = '', ''
        self.csvfilename = ''
        self.csv_rows = []
        self.category_5 = ''


    def request_api(self, url, params, headers, body=None):
        """
        Post an API request to SILworX and check the response.
        """

        def print_responsetime(responsetime):
            s = responsetime.seconds
            ms = int(responsetime.microseconds / 1000)
            print(f' └► Antwortzeit: {s}.{ms}s')

        data = {} if body is None else json.dumps(body)
        try:
            response = requests.post(url, params=params, headers=headers, data=data, verify=self.certificate)
        except OSError as error:
            print_message('ERR', 'onErrorErr', f' = {error}')
            sys.exit(1)
        appdata = response.json()
        if appdata is None:
            print_message('ERR', 'apiServerErr', f' = {url}')
            sys.exit(1)
        else:
            advices = appdata.get('advices')
            if response.status_code == 200:  # OK, standard response for successful HTTP requests
                if advices:
                    self.print_advices(advices)
                else:
                    print_message('INFO', 'apiRequestInfo', f' = {url}')
            elif response.status_code == 400:  # Bad request, SILworX cannot or will not process the request
                if advices:
                    self.print_advices(advices)
                else:
                    print_message('ERR', 'apiRequestErr', f' = {url}')
            else:  # maybe 202 (Action successful) or 206 (Partial content), but should not occur in this context
                print_message('ERR', 'apiStatusErr', f' = {url}::{response.status_code}')
            if plugin.is_development_mode:
                print_responsetime(response.elapsed)
            return appdata

    def print_advices(self, advices, indent=0):
        """
        Show SILworX advices, even if they are nested.
        """
        for advice in advices:
            ts = datetime.strptime(advice.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')
            timestamp = convert_to_local_time(ts)
            ms = timestamp.strftime('%f')
            dateFormat = LANG_DICT['dateFormat'][plugin.language]
            indentation = indent * '    '
            dt = timestamp.strftime(f'{dateFormat} %H:%M:%S.{ms[:3]}')
            level = advice.get('level').get('text')
            data = advice.get('data').get('text')
            path = advice.get('path')
            if path:
                print(f'{indentation}{dt}, {level}: {data}, {path}')
            else:
                print(f'{indentation}{dt}, {level}: {data}')
            subadvice = advice.get('advices')
            if subadvice is not None:
                self.print_advices(subadvice, indent + 1)

    def read_silworx_info(self):
        """Call SILworX API with POST <Retrieving SILworX info>.

        This action retrieves information about a SILworX instance.
        """

        def get_silworxinfo_value(info_result, key):
            """Extract value of type key from the info_result."""
            value = info_result.get(key)
            if not value:
                value = info_result.get('license').get(key)
            return value

        self.csv_rows.clear()
        timestamp, filename_timestamp = get_current_timestamp(return_filename=True)
        self.csvfilename = os.path.join(os.getenv('USERPROFILE'), 'Documents\\Diagnose_') + filename_timestamp
        # First row: current date and time
        self.csv_rows.append(LANG_DICT['csvrow2_header'][plugin.language])
        date, time = timestamp.split(' ')
        self.csv_rows.append(f'{date}[.]{time}')
        self.csv_rows.append('')
        # Second row: SILworX version and license info
        self.csv_rows.append(LANG_DICT['csvrow3_header'][plugin.language])
        url = self.url_fixed_part + 'silworx/info'
        params = {}
        headers = {}
        response = self.request_api(url, params, headers)
        if response is None:
            self.csv_rows.append(LANG_DICT['csvrow1_nodata'][plugin.language])
        else:
            results = response.get('results')
            if results is None:
                self.csv_rows.append(LANG_DICT['csvrow1_nodata'][plugin.language])
            else:
                productname = get_silworxinfo_value(results, 'productname')
                version = get_silworxinfo_value(results, 'version')
                license_info = get_silworxinfo_value(results, 'lic_info')
                license, valid_until = license_info.split(',')
                _, valid_until = valid_until.split(': ')
                self.csv_rows.append(f'{productname}[.]{version}[.]{license}[.]{valid_until[:-1]}')
                self.csv_rows.append('')

    def read_structure_tree(self):
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

        def read_resource_properties():
            """Call SILworX API with POST <Retrieving all properties for a resource node>.

            This action retrieves all properties for the referenced resource node.
            """

            def get_resourceproperties_value(properties, key):
                """Extract value of type key from the properties."""
                return properties.get(key)

            url = self.url_fixed_part + 'node/resource/properties/read'
            params = {'internal_address': plugin.resource_address}
            headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
            response = self.request_api(url, params, headers)
            id = ''
            if response is not None:
                results = response.get('results')
                if results is not None:
                    id = str(get_resourceproperties_value(results, 'system_id'))
            return id

        url = self.url_fixed_part + 'project/structuretree/info'
        params = {}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        structuretree = []
        if response is not None:
            advices = response.get('advices')
            for advice in advices:
                if advice.get('level').get('id') == 'error':
                    print_message('ERR', 'onErrorErr', f' {advice.get("data").get("text")}')
                    sys.exit(1)
            results = response.get('results')
            if results is not None:
                structuretree = results.get('structure_tree')
        # Third row: Some info about the project
        self.csv_rows.append(LANG_DICT['csvrow4_header'][plugin.language])
        if structuretree:
            projects = []
            get_structuretree_nodes(structuretree, projects, 'project')
            projectname = projects[0].get('name')
            _, configuration, resource = plugin.resource_address.split('/')
            usermanagement = []
            get_structuretree_nodes(structuretree, usermanagement, 'user_management')
            self.has_user_management = True if usermanagement else False
            id = read_resource_properties()
            self.csv_rows.append(f'{projectname}[.]{configuration}[.]{resource}[.]{id}')
            self.csv_rows.append('')

    def read_diagnostic_info(self):

        self.selected_option = None  # Variable zum Speichern der ausgewählten Option
        def get_diagmoduleinfo_value(diag_entries, diag_item):

            value = ''
            if diag_item in diag_entries:
                value = diag_entries.get(diag_item)

            return value

        def get_timestamp(diag_entry):
            return diag_entry.get('timestamp', '')  # Hier Zeitstempel abrufen

        def Anzahl_Module():
            def get_moduleinfo_value(modules, module_item):
                """Extract a module item from module information service response."""
                value = ''
                if module_item in modules:
                    value = modules.get(module_item)
                return value
            url = self.url_fixed_part + 'online/module/info'
            params = {'internal_address': plugin.resource_address}
            headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
            response = self.request_api(url, params, headers)
            modules = []
            if response is not None:
                results = response.get('results')
                if results is not None:
                    modules = results.get('modules')
            if modules:
                for module in modules:
                    srs = get_moduleinfo_value(module, 'srs')
                    n, m = map(int, srs.split('.')[1:])

                    # Aktualisiere max_n und max_m, wenn n oder m größer sind
                    plugin.m = max(plugin.m, n)
                    plugin.n = max(plugin.n, m)

        Anzahl_Module()


        def create_gui():
            global root
            root = None
            if root is None:
                root = tk.Tk()
                root.title(LANG_DICT['Fenster'][plugin.language])
                root.geometry('450x450')
                label_above_combobox = ttk.Label(root, text=LANG_DICT['optionen'][plugin.language])
                label_above_combobox.pack(padx=(0,10), pady=(10, 0))
            options = [LANG_DICT['alle_Module'][plugin.language]]
            for j in range(plugin.m + 1):
                for i in range(plugin.n):
                    option = LANG_DICT['Einzeln_Modul'][plugin.language] + f"100.{j}.{i + 1}"
                    options.append(option)

            combo_frame = ttk.Frame(root)
            combo_frame.pack(pady=5)
            self.combobox = ttk.Combobox(combo_frame, values=options, width=60)
            self.combobox.pack(padx=5, pady=5)

            def on_radiobutton_select(text):
                self.Option=text

            self.tk_category = tk.StringVar()
            childframe = ttk.Labelframe(root, text=LANG_DICT['Category'][plugin.language])
            childframe.pack(padx=(10,10), pady=(10, 0), fill='both')

            def on_radiobutton_select_wrapper(text):
                return lambda: on_radiobutton_select(text)

            radiobutton_texts = ["all", "userinfo", "interninfo","internerr", "usererr", "userwarn"]
            radiobuttons = []
            for index, text in enumerate(radiobutton_texts, start=1):
                radiobutton = ttk.Radiobutton(childframe, text=text, variable=self.tk_category, value=index,
                                              command=on_radiobutton_select_wrapper(text))
                radiobutton.pack(anchor='w', padx=8, pady=(8, 0))
                radiobuttons.append(radiobutton)

            button_frame = ttk.Frame(root)
            button_frame.pack()

            style = ttk.Style()
            execute_button = ttk.Button(button_frame, text=LANG_DICT['Button_Text'][plugin.language], command=on_execute_button)
            execute_button.pack(padx=10, pady=30)

            root.mainloop()

        def on_execute_button():

            if self.combobox.get():  # Überprüfung, ob in der Combobox eine Auswahl getroffen wurde
                self.selected_option = self.combobox.get()  # Der ausgewählte Wert der Combobox wird der Variable zugewiesen

                root.quit()

        create_gui()

        def Alle_Module():
            for j in range(plugin.m + 1):
                for i in range(plugin.n):
                    self.csv_rows.append(LANG_DICT['csvrow0_header'][plugin.language] + f'100.{j}.{i + 1}')
                    url = self.url_fixed_part + 'online/module/diagnostic/info'
                    params = {'internal_address': plugin.resource_address, 'rs': f'{j}.{i + 1}'}
                    headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
                    response = self.request_api(url, params, headers)
                    diagmodules = []
                    if response is not None:
                        results = response.get('results')
                        if results is not None:
                            diagmodules = results.get('diag_entries')
                            self.csv_rows.append(LANG_DICT['csvrow1_header'][plugin.language])
                            diagmoduledata = []
                            if self.Option == 'all':
                                for diagmodule in diagmodules:
                                    unique_id = get_diagmoduleinfo_value(diagmodule, 'unique_id')
                                    category = get_diagmoduleinfo_value(diagmodule, 'category')
                                    timestamp = get_timestamp(diagmodule)  # Hier den Zeitstempel abrufen
                                    duration = get_diagmoduleinfo_value(diagmodule, 'duration')
                                    diag_text = get_diagmoduleinfo_value(diagmodule, 'diag_text')
                                    parameter = get_diagmoduleinfo_value(diagmodule, 'parameter')
                                    md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                    diagmoduledata.append(md)
                                self.csv_rows.extend(diagmoduledata)
                            else:
                                for diagmodule in diagmodules:
                                    unique_id = get_diagmoduleinfo_value(diagmodule, 'unique_id')
                                    category = get_diagmoduleinfo_value(diagmodule, 'category')
                                    timestamp = get_timestamp(diagmodule)  # Hier den Zeitstempel abrufen
                                    duration = get_diagmoduleinfo_value(diagmodule, 'duration')
                                    diag_text = get_diagmoduleinfo_value(diagmodule, 'diag_text')
                                    parameter = get_diagmoduleinfo_value(diagmodule, 'parameter')
                                    result = ""
                                    if self.Option == 'userinfo':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'userinfo':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'interninfo':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'interninfo':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'internerr':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'internerr':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'usererr':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'usererr':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'userwarn':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'userwarn':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                self.csv_rows.extend(diagmoduledata)
                        else:
                            api.csv_rows.append(LANG_DICT['csvrow3_nodata'][plugin.language])
                    else:
                        api.csv_rows.append(LANG_DICT['csvrow3_nodata'][plugin.language])

        for j in range(plugin.m + 1):
            for i in range(plugin.n):
                if self.selected_option == LANG_DICT['Einzeln_Modul'][plugin.language] + f"100.{j}.{i + 1}":
                    self.csv_rows.append(LANG_DICT['csvrow0_header'][plugin.language] + f'100.{j}.{i + 1}')
        url = self.url_fixed_part + 'online/module/diagnostic/info'
        for j in range(plugin.m + 1):
            for i in range(plugin.n):
                if self.selected_option == LANG_DICT['Einzeln_Modul'][plugin.language] + f"100.{j}.{i + 1}":
                    params = {'internal_address': plugin.resource_address, 'rs': f'{j}.{i + 1}'}
                    headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
                    response = self.request_api(url, params, headers)
                    diagmodules = []
                    if response is not None:
                        results = response.get('results')
                        if results is not None:
                            diagmodules = results.get('diag_entries')
                            self.csv_rows.append(LANG_DICT['csvrow1_header'][plugin.language])
                            diagmoduledata = []
                            if self.Option == 'all':
                                for diagmodule in diagmodules:
                                    unique_id = get_diagmoduleinfo_value(diagmodule, 'unique_id')
                                    category = get_diagmoduleinfo_value(diagmodule, 'category')
                                    timestamp = get_timestamp(diagmodule)  # Hier den Zeitstempel abrufen
                                    duration = get_diagmoduleinfo_value(diagmodule, 'duration')
                                    diag_text = get_diagmoduleinfo_value(diagmodule, 'diag_text')
                                    parameter = get_diagmoduleinfo_value(diagmodule, 'parameter')
                                    md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                    diagmoduledata.append(md)
                                self.csv_rows.extend(diagmoduledata)
                            else:
                                for diagmodule in diagmodules:
                                    unique_id = get_diagmoduleinfo_value(diagmodule, 'unique_id')
                                    category = get_diagmoduleinfo_value(diagmodule, 'category')
                                    timestamp = get_timestamp(diagmodule)  # Hier den Zeitstempel abrufen
                                    duration = get_diagmoduleinfo_value(diagmodule, 'duration')
                                    diag_text = get_diagmoduleinfo_value(diagmodule, 'diag_text')
                                    parameter = get_diagmoduleinfo_value(diagmodule, 'parameter')
                                    result = ""
                                    if self.Option == 'userinfo':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'userinfo':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'interninfo':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'interninfo':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'internerr':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'internerr':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'usererr':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'usererr':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                    elif self.Option == 'userwarn':
                                        for Katergorie_5 in category:
                                            result += Katergorie_5
                                            if result == 'userwarn':
                                                md = f'SRS:{unique_id}[.]{category}[.]{timestamp}[.]V{duration}[.]V{diag_text}[.]V{parameter}'
                                                diagmoduledata.append(md)
                                self.csv_rows.extend(diagmoduledata)
                        else:
                            api.csv_rows.append(LANG_DICT['csvrow3_nodata'][plugin.language])
                    else:
                        api.csv_rows.append(LANG_DICT['csvrow3_nodata'][plugin.language])
                    break
                elif self.selected_option == LANG_DICT['alle_Module'][plugin.language]:
                    Alle_Module()
                    break
    def close_window(self):
        global root  # Deklaration der globalen Variable

        if root is not None:  # Überprüfen, ob root initialisiert wurde
            root.destroy()

    def do_system_login(self):
        """
        Call SILworX API with POST <Performing a system login>.
        This action performs a system login to a resource.
        """

        url = self.url_fixed_part + 'online/system/login'
        params = {'internal_address': plugin.resource_address,
                  'access_right': 'read'}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id,
                   'HIMA_SAPI_username': self.usergroup,
                   'HIMA_SAPI_password': self.password}
        response = self.request_api(url, params, headers)
        if response is None:
            is_online = False
        else:
            is_online = True
            advices = response.get('advices')
            for advice in advices:
                if advice.get('level').get('id') == 'error':
                    is_online = False
        return is_online

    def do_disconnect(self):
        """
        Call SILworX API with POST <Disconnecting an online session>.
        This action disconnects an online session.
        """

        url = self.url_fixed_part + 'online/disconnect'
        params = {'internal_address': plugin.resource_address}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)


class GUI():
    """
    Functions for the graphical user interface.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.x_pos = -1
        self.is_aborted = False
        self.csvfile = ''
        self.delimiter = ','
        self.encoding = 'cp1252'

    def position_window(self, window_width, window_height, centered=False):
        """
        Position a window on the same monitor on which SILworX is running.
        """
        if self.x_pos < 0:
            self.x_pos = self.root.winfo_pointerx()
        monitors = screeninfo.get_monitors()
        monitors.sort(key=lambda monitor: monitor.x)
        screen_width = 0
        for monitor in monitors:
            if self.x_pos >= monitor.x:
                screen_width += monitor.width
        screen_height = self.root.winfo_screenheight()
        center_x = self.x_pos + 100
        if center_x > (screen_width - window_width):
            center_x = screen_width - window_width - 14
        if centered:
            center_x = screen_width - monitor.width + int((monitor.width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        return f'{window_width}x{window_height}+{center_x}+{center_y}'

    def show_splashscreen(self):
        """
        Show a 'initializing...' window until all necessary data from SILworX is collected.
        """
        self.splashscreen = tk.Toplevel(self.root)
        geometry = self.position_window(400, 150, centered=True)
        self.splashscreen.geometry(geometry)
        self.splashscreen.wm_overrideredirect(True)
        self.splashscreen.attributes('-topmost', True)
        self.splashscreen.config(cursor='watch')
        frame = ttk.Frame(self.splashscreen)
        frame.place(anchor='c', relx=0.5, rely=0.5)
        text = (f'{LANG_DICT["menuEntryName"][plugin.language]}:\n'
                f'{LANG_DICT["initWaitText"][plugin.language]}')
        tk.Label(frame, text=text, font=('Segoe UI', 12, 'bold'), justify=tk.LEFT).pack()
        self.splashscreen.update()

    def quit_splashscreen(self):
        """
        Close splash screen and release memory.
        """
        self.splashscreen.destroy()
        self.splashscreen = None
        del self.splashscreen

    def show_logindialog(self):
        """
        Ask for username and password for resource login.
        """

        def create_login_entries(parentframe):
            """
            Create entries for user group and password.
            """

            def validate_entry(new_value):
                """
                Check if there is an entry for the (required) username.
                """
                if new_value:
                    result = len(new_value) <= 32
                    self.login_button.config(state='normal')
                else:
                    result = True
                    self.login_button.config(state='disabled')
                return result

            childframe = ttk.Labelframe(parentframe, text=LANG_DICT['loginLabel'][plugin.language])
            childframe.grid(column=0, row=0, sticky='ew', padx=10, pady=(10, 0))
            label = ttk.Label(childframe, text=LANG_DICT['loginGroupText'][plugin.language])
            label.grid(column=0, row=0, sticky='nw', padx=6, pady=(10, 0))
            validatecommand = (self.root.register(validate_entry), '%P')
            self.tk_usergroup = tk.StringVar(value='')
            self.usergroup_entry = ttk.Entry(
                childframe, textvariable=self.tk_usergroup, width=22,
                validate='all', validatecommand=validatecommand
            )
            self.usergroup_entry.grid(column=1, row=0, sticky='nw', padx=6, pady=(9, 0))
            label = ttk.Label(childframe, text=LANG_DICT['loginPWText'][plugin.language])
            label.grid(column=0, row=1, sticky='nw', padx=6, pady=10)
            self.tk_password = tk.StringVar(value='')
            password_entry = ttk.Entry(childframe, textvariable=self.tk_password, width=22, show='*')
            password_entry.grid(column=1, row=1, sticky='nw', padx=6, pady=8)
            label = ttk.Label(childframe, text=LANG_DICT['loginAccessText'][plugin.language])
            label.grid(column=0, row=2, sticky='nw', padx=6, pady=(0, 10))
            access_combobox = ttk.Combobox(childframe, width=19)
            access_combobox.delete(0, 'end')
            access_combobox.insert(0, LANG_DICT['loginModeValue'][plugin.language])
            access_combobox.grid(column=1, row=2, sticky='nw', padx=6, pady=(0, 10))
            access_combobox.config(state='disabled')

        def create_button_row(parentframe):
            """
            Create login and cancel button.
            """
            childframe = ttk.Frame(parentframe)
            childframe.grid(column=0, row=1, sticky='ew', padx=10, pady=15)
            self.login_button = ttk.Button(
                childframe, text='Login',
                width=18, command=lambda: quit_logindialog(False)
            )
            self.login_button.grid(column=0, row=0, sticky='nw', padx=(0, 5))
            self.login_button.config(state='disabled')
            cancel_button = ttk.Button(
                childframe, text=LANG_DICT['cancelButtonText'][plugin.language],
                width=18, command=lambda: quit_logindialog(True)
            )
            cancel_button.grid(column=1, row=0, sticky='nw', padx=(5, 0))

        def quit_logindialog(abort_state):
            """Close dialog and event loop and release memory."""
            self.is_aborted = abort_state
            self.logindialog.quit()
            self.logindialog.destroy()
            self.logindialog = None
            del self.logindialog

        self.logindialog = tk.Toplevel(self.root)
        self.logindialog.title(LANG_DICT['loginTitle'][plugin.language])
        geometry = self.position_window(270, 180, centered=True)
        self.logindialog.geometry(geometry)
        self.logindialog.resizable(False, False)
        self.logindialog.protocol('WM_DELETE_WINDOW', lambda: quit_logindialog(True))
        self.logindialog.attributes('-toolwindow', True)
        self.logindialog.attributes('-topmost', True)
        create_login_entries(self.logindialog)
        create_button_row(self.logindialog)
        self.logindialog.focus_force()
        self.usergroup_entry.focus_set()
        self.root.mainloop()
        api.usergroup = self.tk_usergroup.get()
        api.password = self.tk_password.get()

    def save_csvfile(self):
        """
        Save the diagnostic data as a csv file.
        """

        def show_filedialog(filename):
            """
            Ask user for delimiter, coding and file name and path.
            """

            def create_export_entries(parentframe):
                """
                Create entries for separator, coding and filename.
                """

                def on_select_clicked():
                    """
                    Invite user to select filename and path using standard Windows save file dialog.
                    Called when user pushes file selection <...> button.
                    """

                    path, file = os.path.split(self.csvfile)
                    filetypes = (
                        (LANG_DICT['csvFiletypeText'][plugin.language], '*.csv'),
                        (LANG_DICT['allFiletypeText'][plugin.language], '*.*')
                    )
                    file_dialog = fd.asksaveasfilename(
                        parent=self.export_dialog,
                        title=LANG_DICT['fileselectTitle'][plugin.language],
                        initialdir=path,
                        initialfile=file,
                        filetypes=filetypes,
                        defaultextension='.csv'
                    )
                    if file_dialog:
                        self.csvfile = file_dialog.replace('/', '\\')
                        self.tk_filename.set(self.csvfile)
                        entry.xview_moveto(1)

                childframe = ttk.Labelframe(parentframe, text=LANG_DICT['delimiterLabel'][plugin.language])
                childframe.grid(column=0, row=0, sticky='ew', padx=28, pady=(20, 0))

                self.tk_delimiter = tk.IntVar()
                radiobutton = ttk.Radiobutton(childframe, text=LANG_DICT['delimiterText1'][plugin.language], value=1,
                                              variable=self.tk_delimiter)
                radiobutton.grid(column=0, row=0, sticky='nw', padx=8, pady=(8, 0))

                radiobutton = ttk.Radiobutton(childframe, text=LANG_DICT['delimiterText2'][plugin.language], value=2,
                                              variable=self.tk_delimiter)
                radiobutton.grid(column=0, row=1, sticky='nw', padx=8, pady=(8, 5))

                self.tk_delimiter.set(1)

                childframe = ttk.LabelFrame(parentframe, text=LANG_DICT['codingLabel'][plugin.language])
                childframe.grid(column=0, row=1, sticky='ew', padx=28, pady=(8, 0))

                self.tk_coding = tk.IntVar()
                radiobutton = ttk.Radiobutton(childframe, text='ANSI (Latin-1)', value=1, variable=self.tk_coding)
                radiobutton.grid(column=0, row=0, sticky='nw', padx=8, pady=(8, 0))

                radiobutton = ttk.Radiobutton(childframe, text='Unicode (UTF-16)', value=2, variable=self.tk_coding)
                radiobutton.grid(column=0, row=1, sticky='nw', padx=8, pady=(8, 5))

                self.tk_coding.set(1)


                childframe = ttk.Frame(parentframe)
                childframe.grid(column=0, row=3, sticky='ew', padx=28, pady=(10, 0))

                label = ttk.Label(childframe, text=LANG_DICT['exportfileLabel'][plugin.language])
                label.grid(column=0, row=0, sticky='nw')

                self.tk_filename = tk.StringVar()
                self.tk_filename.set(self.csvfile)
                entry = ttk.Entry(childframe, textvariable=self.tk_filename, width=55)
                entry.grid(column=0, row=1, sticky='nw', pady=(4, 0))
                entry.xview_moveto(1)

                select_button = ttk.Button(childframe, text='...', width=2, command=on_select_clicked)
                select_button.grid(column=1, row=1, sticky='nw', pady=2)


            def create_button_row(parentframe):
                """
                Create ok and cancel button.
                """

                def on_ok_clicked():
                    """
                    Check if selected filename has the correct .csv extension etc.
                    and close the dialog if everything is ok.
                    Called when user pushes <OK> button.
                    """

                    def is_file_writable(fnm):
                        """
                        Check if path+file in fnm is writable (i.e., is not rootdir,
                        is no other directory name and has file write permission).
                        """

                        try:
                            with open(fnm, 'w') as _:
                                return True
                        except IOError:
                            return False

                    self.csvfile = self.tk_filename.get()
                    path, _ = os.path.split(self.csvfile)
                    _, file_extension = os.path.splitext(self.csvfile)
                    errormessage = ''
                    if any((char in ('*?"<>|')) for char in self.csvfile):
                        errormessage = LANG_DICT['fnErrorMessage'][plugin.language]
                    elif file_extension.lower() != '.csv':
                        errormessage = LANG_DICT['csvErrorMessage'][plugin.language]
                    elif not os.path.exists(path):
                        errormessage = LANG_DICT['pathErrorMessage'][plugin.language]
                    elif os.access(self.csvfile, os.F_OK):
                        if os.path.isdir(self.csvfile):
                            errormessage = LANG_DICT['acsErrorMessage'][plugin.language]
                        else:
                            title = LANG_DICT['askyesnoWinTitle'][plugin.language]
                            message = LANG_DICT['existingMessage'][plugin.language]
                            if tk.messagebox.askyesno(parent=self.export_dialog, title=title, message=message):
                                self.export_dialog.quit()
                    elif not is_file_writable(self.csvfile):
                        errormessage = LANG_DICT['acsErrorMessage'][plugin.language]
                    if errormessage:
                        title = LANG_DICT['showerrWinTitle'][plugin.language]
                        tk.messagebox.showerror(parent=self.export_dialog, title=title, message=errormessage)
                    else:
                        quit_filedialog(False)

                childframe = ttk.Frame(parentframe)
                childframe.grid(column=0, row=4, sticky='ew', padx=12, pady=(20, 0))

                ok_button = ttk.Button(childframe, text='OK', command=on_ok_clicked)
                ok_button.grid(column=0, row=0, sticky='ew', padx=0, pady=0)
                ok_button.config(width=31)

                cancel_button = ttk.Button(childframe, text=LANG_DICT['cancelButtonText'][plugin.language],
                                           command=lambda: quit_filedialog(True))
                cancel_button.grid(column=1, row=0, sticky='ew', padx=(5, 0), pady=0)
                cancel_button.config(width=31)

            def quit_filedialog(abort_state):
                """
                Close dialog and event loop and release memory.
                """
                self.is_aborted = abort_state
                if self.is_aborted:
                    self.csvfile = ''
                self.export_dialog.quit()
                self.export_dialog.destroy()
                self.export_dialog = None
                del self.export_dialog

            self.export_dialog = tk.Toplevel(self.root)
            self.export_dialog.title(LANG_DICT['exportWinTitle'][plugin.language])
            geometry = self.position_window(420, 310, centered=True)
            self.export_dialog.geometry(geometry)
            self.export_dialog.resizable(False, False)
            self.export_dialog.protocol('WM_DELETE_WINDOW', lambda: quit_filedialog(True))
            self.export_dialog.attributes('-toolwindow', True)
            self.export_dialog.attributes('-topmost', True)
            self.export_dialog.columnconfigure(0, weight=1)
            self.csvfile = filename
            create_export_entries(self.export_dialog)
            create_button_row(self.export_dialog)
            self.root.mainloop()
            self.delimiter = ',' if self.tk_delimiter.get() == 1 else ';'
            self.encoding = 'cp1252' if self.tk_coding.get() == 1 else 'utf-16'

        show_filedialog(api.csvfilename)
        if self.csvfile:
            with open(self.csvfile, 'w', newline='', encoding=self.encoding) as f:
                csvwriter = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_ALL)
                for packed_row in api.csv_rows:
                    row_wincp = convert_to_windows_codepage(packed_row)
                    row = [item for item in row_wincp.split('[.]')]
                    csvwriter.writerow(row)
            print_message('INFO', 'fileWrittenInfo', f' = {self.csvfile}')
        else:
            print_message('INFO', 'noFileSelectInfo')


def print_message(level, key, additional_info=''):
    """
    Show message with date and time in SILworX log window.
    """
    dt = get_current_timestamp()
    text = LANG_DICT[key][plugin.language]
    print(f'{dt}, {text}{additional_info}')
    if level == 'ERR' and not plugin.is_development_mode:
        print(f'{text}{additional_info}', file=sys.stderr)


def get_current_timestamp(return_filename=False):
    """
    Get current date and time in language dependant format.
    """
    timestamp = datetime.now()
    dateFormat = LANG_DICT['dateFormat'][plugin.language]
    dt = timestamp.strftime(dateFormat + ' %H:%M:%S.')
    ms = timestamp.strftime('%f')
    localtime = dt + ms[:3]
    filename_timestamp = timestamp.strftime('%Y_%m_%d_%H_%M_%S.csv')
    if return_filename:
        return localtime, filename_timestamp
    else:
        return localtime


def convert_to_local_time(utc_dt):
    """
    Convert a UTC time according to the local time.
    """
    if type(utc_dt) is str:
        if utc_dt == '---':
            # No time stamp available
            return utc_dt
        else:
            # SILworx internal format (language independent) = yyyy-mm-ddThh:mm:ss.mssZ
            datetime_object = datetime.strptime(utc_dt, '%Y-%m-%dT%H:%M:%S.%fZ')
            localtime = datetime_object.replace(tzinfo=timezone.utc).astimezone(tz=None)
            dateFormat = LANG_DICT['dateFormat'][plugin.language]
            dt = localtime.strftime(dateFormat + ' %H:%M:%S.')
            ms = utc_dt[20:23]
            return dt[:20] + ms
    else:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convert_to_windows_codepage(s):
    """
    Convert an url coded string to the current Windows codepage.
    """
    raw = s.replace('%00', '%')  # quick and dirty: s is UTF16 encoded, but requests.utils.unquote needs UTF8
    return requests.utils.unquote(raw, 'cp1252')


def parse_args():
    """
    Read command line arguments delivered from SILworX.
    """
    parser = ArgumentParser()
    parser.add_argument('--tls-certificate', dest='certificate', default=r'C:\Users\HIMA\cert.pem')
    parser.add_argument('--api-port', dest='apiport', default='443')
    parser.add_argument('--plugin-port', dest='pluginport', default='8400')
    parser.add_argument('--language', dest='language', default='de')
    parser.add_argument('--read-secret', dest='readsecret', action='store_true', default=False)
    return parser.parse_args()


def run_diagnostic():
    """Collect all information from SILworX to generate a Diagnosis"""
    gui.is_aborted = False
    gui.x_pos = -1
    gui.show_splashscreen()
    if api.has_user_management:
        gui.quit_splashscreen()
        gui.show_logindialog()
        if gui.is_aborted:
            print_message('ERR', 'funcAbortedErr', LANG_DICT['menuEntryName'][plugin.language])
        else:
            gui.show_splashscreen()
    else:
        api.usergroup = 'Administrator'
        api.password = ''
    if not gui.is_aborted:
        if api.do_system_login():
            api.read_silworx_info()
            api.read_structure_tree()
            api.read_diagnostic_info()
            api.do_disconnect()
        else:
            api.csv_rows.append(LANG_DICT['csvrow2_nodata'][plugin.language])
        gui.quit_splashscreen()
    gui.save_csvfile()
    api.close_window()

def run_plugin(port):
    """Start WebSocket communication with SILworX."""
    ws = websocket.WebSocketApp(
        'ws://localhost:' + port,
        on_open=plugin.on_open,
        on_message=plugin.on_message,
        on_error=plugin.on_error,
        on_close=plugin.on_close
    )
    try:
        ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    except ConnectionRefusedError as error:
        print_message('ERR', 'onErrorErr', f' = {error}')
        sys.exit(1)
    rel.signal(2, rel.abort)  # Catch keyboard interrupt SIGINT = CTRL+C
    try:
        rel.dispatch()
    except ConnectionResetError as error:
        print_message('ERR', 'onErrorErr', f' = {error}')
        sys.exit(1)


if __name__ == '__main__':
    arguments = parse_args()
    plugin = Plugin(arguments)
    api = API(arguments)
    gui = GUI()
    run_plugin(arguments.pluginport)

    sys.exit(0)
