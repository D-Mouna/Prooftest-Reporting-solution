# -*- coding: utf-8 -*-

"""Collects offline and online data from SILworX, a project and a
resource and stores this in a csv-file.

This plug-in works with SILworX V15 or higher. It doesn't work without
SILworX. The core function is started on the context menu of a resource
in an opened SILworX project.

Date:   2024-07-12
Status: RELEASE
Author: Karlheinz Volpp / HIMA / APD
"""

########################################
# Import section
########################################
import os                               # Miscellaneous operating system interfaces
import sys                              # System-specific parameters and functions
from argparse import ArgumentParser     # Parser for command-line options, arguments and sub-commands
from datetime import datetime, timezone # Basic date and time types
import ssl                              # TLS/SSL wrapper for socket objects
import websocket                        # WebSocket client for Python                 !!! pip install websocket-client !!!
import requests                         # HTTP for humans                             !!! pip install requests         !!!
import screeninfo                       # Fetch location and size of physical screens !!! pip install screeninfo       !!!
import json                             # JSON encoder and decoder
import tkinter as tk                    # Python interface to Tcl/Tk
from tkinter import ttk                 # Tk themed widgets
from tkinter import filedialog as fd    # File selection dialogs
import csv                              # CSV file reading and writing

########################################
# Some const variables
########################################
PLUGIN_NAME = 'hima.asset_inventory'
VERSION = '1.2-0'
AUTHOR = 'Application Development (APD)'
VENDOR = 'HIMA Paul Hildebrandt GmbH'
LICENSE = 'Plug-In Feature license and SILworX API license'
TRIGGER_NAME = 'START_SYSTEM_INVENTORY'
LANG_DICT = {
    'menuEntryName':   ('Anlageninventur',
                        'Asset Inventory'),
    'funcQuitInfo':    ('Info: Funktion beendet',
                        'Info: Function terminated'),
    'funcAbortedErr':  ('Fehler: Funktion abgebrochen: ',
                        'Error: Function aborted: '),
    'onMessageErr':    ('Fehler: Unerwarteter Message-Typ empfangen, Message',
                        'Error: Unexpected message type received, Message'),
    'onTriggerErr':    ('Fehler: Unerwarteter Trigger-Name in Plugin',
                        'Error: Unexpected trigger name in plugin'),
    'onErrorErr':      ('Fehler: Interner Fehler aufgetreten, Fehler',
                        'Error: Internal error occured, Error'),
    'apiServerErr':    ('Fehler: Keine Antwort auf API-Anfrage erhalten, URL',
                        'Error: No response received to API request, URL'),
    'apiRequestInfo':  ('Info: API-Anfrage ok, URL',
                        'Info: API request ok, URL'),
    'apiRequestErr':   ('Fehler: Ungültige API-Anfrage ohne Fehlermeldung, URL',
                        'Error: Bad API request without advice, URL'),
    'apiStatusErr':    ('Fehler: Unerwarteter Statuscode für API-Anfrage, URL::Code',
                        'Error: Unexpected status code for API request, URL::Code'),
    'responseTimeInfo':('Antwortzeit:',
                        'Response time:'),
    'sessionIdInfo':   ('Info: SessionId erhalten, ID',
                        'Info: SessionId received, ID'),
    'logDateFormat':   ('%d.%m.%Y',
                        '%Y-%m-%d'),
    'initWaitText':    ('System-Daten aufnehmen, bitte warten...',
                        'Collecting system data, please wait...'),
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
    'loginModeValue':  ('Lesen',
                        'Read'),
    'cancelButtonText':('Abbrechen',
                        'Cancel'),
    'exportWinTitle':  ('Export: Inventardaten als CVS sichern',
                        'Export: Save Inventory Data as CSV'),
    'delimiterLabel':  ('Trennzeichen',
                        'Delimiter'),
    'delimiterText1':  ('Komma',
                        'Comma'),
    'delimiterText2':  ('Semikolon',
                        'Semicolon'),
    'codingLabel':     ('Codierung',
                        'Coding'),
    'exportfileLabel': ('Exportdatei',
                        'Export File'),
    'fileselectTitle': ('Wählen Sie die Zieldatei des Inventar-Exports',
                        'Select Inventory Export Destination File'),
    'csvFiletypeText': ('CSV-Dateien',
                        'CSV files'),
    'allFiletypeText': ('Alle Dateien',
                        'All files'),
    'showerrWinTitle': ('Fehler',
                        'Error'),
    'csvErrorMessage': ('Die CSV-Datei muss die Endung ".csv" haben.',
                        'The CSV file extension must be ".csv".'),
    'pathErrorMessage':('Das System kann den angegebenen Pfad nicht finden.',
                        'The system cannot find the path specified.'),
    'fnErrorMessage':  ('Der angegebene Dateiname ist nicht gültig.',
                        'The specified file name is not valid.'),
    'acsErrorMessage': ('Kein Schreiberlaubnis für dieses Verzeichnis.',
                        'No write permit for this directory.'),
    'askyesnoWinTitle':('Datei überschreiben?',
                        'Overwrite file?'),
    'existingMessage': ('Eine Datei mit diesem Namen existiert bereits.\n'
                        'Soll die existierende Datei überschrieben werden?',
                        'A file with this name already exists.\n'
                        'Do you want to overwrite the existing file?'),
    'fileWrittenInfo': ('Info: CSV-Datei gespeichert, Dateiname',
                        'Info: CSV file saved, Filename'),
    'csvrow1_header':  ('Datum[.]Uhrzeit',
                        'Date[.]Time'),
    'csvrow2_header':  ('Produkt[.]Version[.]Lizenz[.]Gültig bis',
                        'Product name[.]Version[.]License[.]Valid until'),
    'csvrow2_nodata':  ('Datenabfrage nicht erfolgreich, kein Zugriff auf API möglich',
                        'Data query not successful, no API access possible'),
    'csvrow3_header':  ('Projekt[.]Konfiguration[.]Ressource[.]System-ID',
                        'Project[.]Configuration[.]Resource[.]System ID'),
    'csvrow4_header':  ('System: Zustand[.]Status[.]Zeit[.]Betriebsdauer[.]Forcen[.]'
                        'Zykluszeit: Mittlere[.]Minimale[.]Maximale[.]'
                        'Systemfehler: Aktuelle Anzahl[.]Gesamte Anzahl[.]Letztes Auftreten[.]'
                        'Feldfehler: Aktuelle Anzahl[.]Gesamte Anzahl[.]Letztes Auftreten[.].'
                        'Kommunikationsfehler: Aktuelle Anzahl[.]Gesamte Anzahl[.]Letztes Auftreten',
                        'System: State[.]Status[.]Time[.]Period of Operation[.]Forcing[.]'
                        'Cycle Time: Average[.]Minimum[.]Maximum[.]'
                        'System Errors: Current Count[.]Total Number[.]Last Occurence[.]'
                        'Field Errors: Current Count[.]Total Number[.]Last Occurence[.]'
                        'Communication Errors: Current Count[.]Total Number[.]Last Occurence'),
    'csvrow4_nodata':  ('Datenabfrage nicht erfolgreich, keine Online-Verbindung möglich',
                        'Data query not successful, no online connection possible'),
    'csvrow5_header':  ('Modul: SRS[.]Typ[.]Name[.]Betriebssystem[.]Betriebssystem-Lader[.]Urlader[.]'
                        'Hardware-Revision[.]Serien-Nummer[.]Adresse: MAC[.]IP',
                        'Module: SRS[.]Type[.]Name[.]Operating System[.]Operating System Loader[.]Bootloader[.]'
                        'Hardware Revision[.]Serial Number[.]Address: MAC[.]IP'),
    'csvrow5_nodata':  ('Datenabfrage nicht erfolgreich: Lesen der Moduldaten nicht möglich',
                        'Data query not successful: Reading of module data not possible')
}

class Plugin():
    """Communicate with SILworX' plugin interface."""
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
            logfile = os.path.join(logpath, PLUGIN_NAME+'.log')
            sys.stdout = open(logfile, 'a')
        else:
            self.is_development_mode = True
        print(
            f'\n-------------------------------'
            f'\n  {PLUGIN_NAME} V{VERSION}'
            f'\n-------------------------------'
        )

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
            'plugin_vendor': VENDOR,
            'plugin_license': LICENSE,
            'customized_contextmenu_trigger': [
                {
                    'menu_entry_name': LANG_DICT['menuEntryName'][self.language],
                    'node_type': 'resource',
                    'trigger_name': TRIGGER_NAME,
                    'timeout': 10
                }
            ],
            'predefined_trigger': [
                {
                    'trigger_name': 'TRIGGER_SESSION_ID_CHANGED',
                    'timeout': 10
                }
            ]
        }
        ws.send(json.dumps(message))

    def on_message(self, ws, message):
        """Call the responsible message handler.

        Called when SILworX sends a message to the plugin.
        """

        def do_triggeraction(ws, trigger):
            """Do the requested trigger action and acknowledge the receipt of the trigger.

            Called when SILworX triggers an action from the plugin.
            """

            ws.send(json.dumps({'msg_type': 'resume', 'trigger_id': trigger.get('trigger_id')}))
            trigger_name = trigger.get('trigger_name')
            if trigger_name == 'TRIGGER_SESSION_ID_CHANGED':
                self.user_session_id = trigger.get('session_id')
                print_message('INFO', 'sessionIdInfo', f' = {self.user_session_id}')
            elif trigger_name == TRIGGER_NAME:
                if self.is_running_sema == 0:
                    self.is_running_sema = 1
                    self.resource_address = trigger.get('internal_address')
                    run_inventory()
                    self.is_running_sema = 0
            else:
                print_message('ERR', 'onTriggerErr', f' {PLUGIN_NAME}: {trigger_name}')

        # on_message(self, ws, message)
        json_message = json.loads(message)
        msg_type = json_message.get('msg_type')
        if msg_type == 'trigger':
            do_triggeraction(ws, json_message)
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
        if self.is_development_mode and not isinstance(error, websocket.WebSocketConnectionClosedException):
            raise
        sys.exit(1)

    def on_close(self, ws, close_statuscode, close_msg):
        """Exit the plugin.

        Called when connection is closed or, during develop mode, CTRL-C is received.
        """

        print_message('INFO', 'funcQuitInfo')
        sys.exit(0)

class API():
    """Communicate with SILworX' API interface."""
    def __init__(self, args):
        self._certificate = args.certificate
        self._url_fixed_part = f'https://{args.apiaddress}:{args.apiport}/api/v1/'
        self.has_user_management = False
        self.usergroup, self.password = '', ''
        self.csvfilename = ''
        self.csv_rows = []

    def request_api(self, url, params, headers, body=None):
        """Post an API request to SILworX and check the response."""
        def print_responsetime(responsetime):
            s = responsetime.seconds
            ms = int(responsetime.microseconds/1000)
            responseTimeInfo = LANG_DICT['responseTimeInfo'][plugin.language]
            print(f' └► {responseTimeInfo} {s}.{ms} s')

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
            plugin.is_running_sema -= 1
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
            # SILworx internal format (language independent) = yyyy-mm-ddThh:mm:ss.mssZ
            utctime = datetime.strptime(advice.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')
            localtime = convert_to_localtime(utctime)
            ms = localtime.strftime('%f')
            dateFormat = LANG_DICT['logDateFormat'][plugin.language]
            indentation = indent * '    '
            timestamp = localtime.strftime(f'{dateFormat} %H:%M:%S.{ms[:3]}')
            level = advice.get('level').get('text')
            data = advice.get('data').get('text')
            path = advice.get('path')
            if path:
                print(f'{indentation}{timestamp}, {level}: {data}, {path}')
            else:
                print(f'{indentation}{timestamp}, {level}: {data}')
            subadvice = advice.get('advices')
            if subadvice is not None:
                self.print_advices(subadvice, indent+1)

    def read_silworxinfo(self):
        """Call SILworX API with POST <Retrieving SILworX info>.

        This action retrieves information about a SILworX instance.
        """

        def get_silworxinfo_value(info_result, key):
            """Extract value of type key from the info_result."""
            value = info_result.get(key)
            if not value:
                value = info_result.get('license').get(key)
            return value

        # read_silworxinfo(self)
        self.csv_rows.clear()
        timestamp, filename_timestamp = get_currenttimestamp(return_filename=True)
        self.csvfilename = os.path.join(os.getenv('USERPROFILE'), 'Documents\\Inventory_')+filename_timestamp
        # First row: current date and time
        self.csv_rows.append(LANG_DICT['csvrow1_header'][plugin.language])
        date, time = timestamp.split(' ')
        self.csv_rows.append(f'{date}[.]{time}')
        self.csv_rows.append('')
        # Second row: SILworX version and license info
        self.csv_rows.append(LANG_DICT['csvrow2_header'][plugin.language])
        url = self._url_fixed_part+'silworx/info'
        params = {}
        headers = {}
        response = self.request_api(url, params, headers)
        results = response.get('results')
        if results is None:
            self.csv_rows.append(LANG_DICT['csvrow2_nodata'][plugin.language])
        else:
            productname = get_silworxinfo_value(results, 'productname')
            version = get_silworxinfo_value(results, 'version')
            license_info = get_silworxinfo_value(results, 'lic_info')
            license, valid_until = license_info.split(',')
            _, valid_until = valid_until.split(': ')
            self.csv_rows.append(f'{productname}[.]{version}[.]{license}[.]{valid_until[:-1]}')
            self.csv_rows.append('')

    def read_structuretree(self):
        """Call SILworX API with POST <Retrieving structure tree information>.

        This action retrieves the structure tree information of the current project.
        """

        def get_structuretree_nodes(structuretree, nodes, symbol):
            """Extract nodes of type symbol from a structure tree."""
            for node in structuretree:
                if node.get('type_info').get('symbol') == symbol:
                    element = {
                        'name': node.get('display_name'),
                        'address': node.get('internal_address')
                    }
                    nodes.append(element)
                children = node.get('children')
                if children is not None:
                    get_structuretree_nodes(children, nodes, symbol)

        def read_resourceproperties():
            """Call SILworX API with POST <Retrieving all properties for a resource node>.

            This action retrieves all properties for the referenced resource node.
            """

            def get_resourceproperties_value(properties, key):
                """Extract value of type key from the properties."""
                return properties.get(key)

            # read_resourceproperties()
            url = self._url_fixed_part+'node/resource/properties/read'
            params = {'internal_address': plugin.resource_address}
            headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
            response = self.request_api(url, params, headers)
            results = response.get('results')
            id = '' if results is None else str(get_resourceproperties_value(results, 'system_id'))
            return id

        # read_structuretree(self)
        url = self._url_fixed_part+'project/structuretree/info'
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
        # Third row: Some info about the project
        self.csv_rows.append(LANG_DICT['csvrow3_header'][plugin.language])
        if structuretree:
            projects = []
            get_structuretree_nodes(structuretree, projects, 'project')
            projectname = projects[0].get('name')
            _, configuration, resource = plugin.resource_address.split('/')
            usermanagement = []
            get_structuretree_nodes(structuretree, usermanagement, 'user_management')
            self.has_user_management = True if usermanagement else False
            id = read_resourceproperties()
            self.csv_rows.append(f'{projectname}[.]{configuration}[.]{resource}[.]{id}')
            self.csv_rows.append('')

    def do_systemlogin(self):
        """Call SILworX API with POST <Performing a system login>.

        This action performs a system login to a resource.
        """

        url = self._url_fixed_part+'online/system/login'
        params = {
            'internal_address': plugin.resource_address,
            'access_right': 'read'
        }
        headers = {
            'HIMA_SAPI_user_session_id': plugin.user_session_id,
            'HIMA_SAPI_username': self.usergroup,
            'HIMA_SAPI_password': self.password
        }
        response = self.request_api(url, params, headers)
        is_online = True
        advices = response.get('advices')
        for advice in advices:
            if advice.get('level').get('id') == 'error':
                is_online = False
        return is_online

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
        url = self._url_fixed_part+'online/system/info'
        params = {
            'internal_address': plugin.resource_address,
            'service_property_list': 'system_data'
        }
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        service_properties = []
        results = response.get('results')
        if results is not None:
            services = results.get('services',[])
            for service in services:
                if service.get('service') == 'system_data':
                    service_properties = service.get('properties')
        # Fourth row: Some info about the running system
        self.csv_rows.append(LANG_DICT['csvrow4_header'][plugin.language])
        if service_properties:
            system_state = get_systeminfo_property(service_properties, 'system_state')
            system_status = get_systeminfo_property(service_properties, 'system_status')
            utc_system_time = get_systeminfo_property(service_properties, 'system_time')
            system_time = convert_to_localtime(utc_system_time)
            power_on_time = get_systeminfo_property(service_properties, 'power_on_time')
            force_state = get_systeminfo_property(service_properties, 'force_state')
            system_prop = f'{system_state}[.]{system_status}[.]{system_time}[.]{power_on_time}[.]{force_state}'
            cycletime_average = get_systeminfo_property(service_properties, 'cycle_time.cycletime_average')
            cycletime_min = get_systeminfo_property(service_properties, 'cycle_time.cycletime_min')
            cycletime_max = get_systeminfo_property(service_properties, 'cycle_time.cycletime_max')
            cycletime = f'{cycletime_average}[.]{cycletime_min}[.]{cycletime_max}'
            system_err_current = get_systeminfo_property(service_properties, 'system_errors.errors_warnings_no_current')
            system_err_total = get_systeminfo_property(service_properties, 'system_errors.errors_warnings_no_historic')
            utc_system_err_last = get_systeminfo_property(service_properties, 'system_errors.errors_warnings_last_occurrence')
            system_err_last = convert_to_localtime(utc_system_err_last)
            sys_error = f'{system_err_current}[.]{system_err_total}[.]{system_err_last}'
            field_err_current = get_systeminfo_property(service_properties, 'field_errors.errors_warnings_no_current')
            field_err_total = get_systeminfo_property(service_properties, 'field_errors.errors_warnings_no_historic')
            utc_field_err_last = get_systeminfo_property(service_properties, 'field_errors.errors_warnings_last_occurrence')
            field_err_last = convert_to_localtime(utc_field_err_last)
            field_error = f'{field_err_current}[.]{field_err_total}[.]{field_err_last}'
            comm_err_current = get_systeminfo_property(service_properties, 'communication_errors.errors_warnings_no_current')
            comm_err_total = get_systeminfo_property(service_properties, 'communication_errors.errors_warnings_no_historic')
            utc_comm_err_last = get_systeminfo_property(service_properties, 'communication_errors.errors_warnings_last_occurrence')
            comm_err_last = convert_to_localtime(utc_comm_err_last)
            comm_error = f'{comm_err_current}[.]{comm_err_total}[.]{comm_err_last}'
            self.csv_rows.append(f'{system_prop}[.]{cycletime}[.]{sys_error}[.]{field_error}[.]{comm_error}')
        else:
            self.csv_rows.append(LANG_DICT['csvrow4_nodata'][plugin.language])
        self.csv_rows.append('')

    def read_moduleinfo(self):
        """Call SILworX API with POST <Retrieving module information>.

        This action retrieves module information (all modules) from a resource.
        """

        def get_moduleinfo_value(modules, module_item):
            """Extract a module item from module information service response."""
            value = ''
            if module_item in modules:
                value = modules.get(module_item)
                if 'value' in value:
                    value = value.get('value')
            elif module_item in ('os', 'osl', 'bl'):
                operating_systems = modules.get('operating_systems',{})
                for os in operating_systems:
                    if os.get('os_type') == module_item:
                        value = os.get('version').get('value')
            return value

        def sort_srs(md):
            """Sort the module info ascending by rack, slot."""
            srs = md[4:md.find('[')]
            _, rack, slot = srs.split('.')
            return int(rack)*100 + int(slot)

        # read_moduleinfo(self)
        url = self._url_fixed_part+'online/module/info'
        params = {'internal_address': plugin.resource_address}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)
        results = response.get('results')
        modules = [] if results is None else results.get('modules')
        # Fifth row: Some info about each module in system
        self.csv_rows.append(LANG_DICT['csvrow5_header'][plugin.language])
        if modules:
            moduledata = []
            for module in modules:
                srs = get_moduleinfo_value(module, 'srs')
                type = get_moduleinfo_value(module, 'type')
                if type:
                    name = get_moduleinfo_value(module, 'name')
                    os = get_moduleinfo_value(module, 'os')
                    osl = get_moduleinfo_value(module, 'osl')
                    bl = get_moduleinfo_value(module, 'bl')
                    hw_version = get_moduleinfo_value(module, 'hw_version')
                    serial_number = get_moduleinfo_value(module, 'serial_number')
                    mac_adr = get_moduleinfo_value(module, 'mac_adr')
                    ip_adr = get_moduleinfo_value(module, 'ip_adr')
                    md = f'SRS:{srs}[.]{type}[.]{name}[.]V{os}[.]V{osl}[.]V{bl}[.]'
                    md += f'Rev.{hw_version}[.]SN:{serial_number}[.]{mac_adr}[.]{ip_adr}'
                else:
                    md = f'SRS:{srs}[.]{type}[.]{LANG_DICT["csvrow5_nodata"][plugin.language]}'
                moduledata.append(md)
            moduledata.sort(key=sort_srs)
            self.csv_rows.extend(moduledata)
        else:
            api.csv_rows.append(LANG_DICT['csvrow5_nodata'][plugin.language])

    def do_disconnect(self):
        """Call SILworX API with POST <Disconnecting an online session>.

        This action disconnects an online session.
        """

        url = self._url_fixed_part+'online/disconnect'
        params = {'internal_address': plugin.resource_address}
        headers = {'HIMA_SAPI_user_session_id': plugin.user_session_id}
        response = self.request_api(url, params, headers)

class GUI():
    """Functions for the graphical user interface."""
    def __init__(self):
        self._root = tk.Tk()
        self._root.withdraw()
        self.x_pos = None
        self.is_aborted = False
        self._csvfile = ''
        self._delimiter =','
        self._encoding = 'cp1252'

    def position_window(self, window_width, window_height, centered=False):
        """Position a window on the same monitor on which SILworX is running."""
        if self.x_pos is None:
            self.x_pos = self._root.winfo_pointerx()
        monitors = screeninfo.get_monitors()
        monitors.sort(key=lambda monitor: monitor.x)
        screen_width = 0
        for monitor in monitors:
            if self.x_pos >= monitor.x:
                screen_width += monitor.width
        screen_height = self._root.winfo_screenheight()
        center_x = self.x_pos + 100
        if center_x > (screen_width - window_width):
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
        text = (
            f'{LANG_DICT["menuEntryName"][plugin.language]}:\n'
            f'{LANG_DICT["initWaitText"][plugin.language]}'
        )
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
            frame = ttk.Labelframe(parentframe, text=LANG_DICT['loginLabel'][plugin.language])
            frame.grid(column=0, row=0, sticky='ew', padx=10, pady=(10,0))
            label = ttk.Label(frame, text=LANG_DICT['loginGroupText'][plugin.language])
            label.grid(column=0, row=0, sticky='nw', padx=6, pady=(10,0))
            validatecommand = (self._root.register(validate_input), '%P')
            self.usergroup_entry = ttk.Entry(frame, width=22, validate='all', validatecommand=validatecommand)
            self.usergroup_entry.grid(column=1, row=0, sticky='nw', padx=6, pady=(9,0))
            label = ttk.Label(frame, text=LANG_DICT['loginPWText'][plugin.language])
            label.grid(column=0, row=1, sticky='nw', padx=6, pady=10)
            self.password_entry = ttk.Entry(frame, width=22, show='*')
            self.password_entry.grid(column=1, row=1, sticky='nw', padx=6, pady=8)
            label = ttk.Label(frame, text=LANG_DICT['loginAccessText'][plugin.language])
            label.grid(column=0, row=2, sticky='nw', padx=6, pady=(0,10))
            combobox = ttk.Combobox(frame, width=19)
            combobox.delete(0, 'end')
            combobox.insert(0, LANG_DICT['loginModeValue'][plugin.language])
            combobox.state(['disabled'])
            combobox.grid(column=1, row=2, sticky='nw', padx=6, pady=(0,10))

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

        def enter_defaultlogin(event):
            """Default values, entered with <Ctrl><a>."""
            self.usergroup_entry.delete(0, 'end')
            self.usergroup_entry.insert(0, 'Administrator')
            self.password_entry.delete(0, 'end')

        def quit_logindialog(abort_state):
            """Close dialog and event loop and release memory."""
            self.is_aborted = abort_state
            api.usergroup = self.usergroup_entry.get()
            api.password = self.password_entry.get()
            self.logindialog.quit()
            self.logindialog.destroy()
            self.logindialog = None
            del self.logindialog

        def set_focus():
            """Force the input focus to the login widget."""
            self.logindialog.focus_force()
            self.usergroup_entry.focus_set()

        # show_logindialog(self)
        self.logindialog = tk.Toplevel(self._root)
        self.logindialog.title(LANG_DICT['loginTitle'][plugin.language])
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

    def save_csvfile(self):
        """Save the inventory data as a csv file."""
        def show_filedialog(filename):
            """Ask user for delimiter, coding and file name and path."""
            def create_exportentries(parentframe):
                """Create entries for separator, coding and filename."""
                def on_selectclicked():
                    """Invite user to select filename and path using standard Windows save file dialog.

                    Called when user pushes file selection <...> button.
                    """

                    path, file = os.path.split(self._csvfile)
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
                        self._csvfile = file_dialog.replace('/', '\\')
                        self.tk_filename.set(self._csvfile)
                        entry.xview_moveto(1)

                # create_exportentries(parentframe)
                frame = ttk.Labelframe(parentframe, text=LANG_DICT['delimiterLabel'][plugin.language])
                frame.grid(column=0, row=0, sticky='ew', padx=28, pady=(20,0))
                self.tk_delimiter = tk.IntVar()
                radiobutton = ttk.Radiobutton(
                    frame, text=LANG_DICT['delimiterText1'][plugin.language],
                    value=1, variable=self.tk_delimiter
                )
                radiobutton.grid(column=0, row=0, sticky='nw', padx=8, pady=(8,0))
                radiobutton = ttk.Radiobutton(
                    frame, text=LANG_DICT['delimiterText2'][plugin.language],
                    value=2, variable=self.tk_delimiter
                )
                radiobutton.grid(column=0, row=1, sticky='nw', padx=8, pady=(8,5))
                self.tk_delimiter.set(1)
                frame = ttk.LabelFrame(parentframe, text=LANG_DICT['codingLabel'][plugin.language])
                frame.grid(column=0, row=1, sticky='ew', padx=28, pady=(8,0))
                self.tk_coding = tk.IntVar()
                radiobutton = ttk.Radiobutton(frame, text='ANSI (Latin-1)', value=1, variable=self.tk_coding)
                radiobutton.grid(column=0, row=0, sticky='nw', padx=8, pady=(8,0))
                radiobutton = ttk.Radiobutton(frame, text='Unicode (UTF-16)', value=2, variable=self.tk_coding)
                radiobutton.grid(column=0, row=1, sticky='nw', padx=8, pady=(8,5))
                self.tk_coding.set(1)
                frame = ttk.Frame(parentframe)
                frame.grid(column=0, row=2, sticky='ew', padx=28, pady=(10,0))
                label = ttk.Label(frame, text=LANG_DICT['exportfileLabel'][plugin.language])
                label.grid(column=0, row=0, sticky='nw')
                self.tk_filename = tk.StringVar()
                self.tk_filename.set(self._csvfile)
                entry = ttk.Entry(frame, textvariable=self.tk_filename, width=55)
                entry.grid(column=0, row=1, sticky='nw', pady=(4,0))
                entry.xview_moveto(1)
                select_button = ttk.Button(frame, text='...', width=2, command=on_selectclicked)
                select_button.grid(column=1, row=1, sticky='nw', pady=2)

            def create_buttonrow(parentframe):
                """Create ok and cancel button."""
                def on_okclicked():
                    """Check if selected filename has the correct .csv extension etc.
                    and close the dialog if everything is ok.

                    Called when user pushes <OK> button.
                    """

                    def is_file_writable(fnm):
                        """Check if path+file in fnm is writable (i.e., is not rootdir,
                        is no other directory name and has file write permission).
                        """

                        try:
                            with open(fnm, 'w') as _:
                                return True
                        except IOError:
                            return False

                    # on_okclicked()
                    self._csvfile = self.tk_filename.get()
                    path, _ = os.path.split(self._csvfile)
                    _, file_extension = os.path.splitext(self._csvfile)
                    errormessage = ''
                    if any((char in ('*?"<>|')) for char in self._csvfile):
                        errormessage = LANG_DICT['fnErrorMessage'][plugin.language]
                    elif file_extension.lower() != '.csv':
                        errormessage = LANG_DICT['csvErrorMessage'][plugin.language]
                    elif not os.path.exists(path):
                        errormessage = LANG_DICT['pathErrorMessage'][plugin.language]
                    elif os.access(self._csvfile, os.F_OK):
                        if os.path.isdir(self._csvfile):
                            errormessage = LANG_DICT['acsErrorMessage'][plugin.language]
                        else:
                            title = LANG_DICT['askyesnoWinTitle'][plugin.language]
                            message = LANG_DICT['existingMessage'][plugin.language]
                            if tk.messagebox.askyesno(parent=self.export_dialog, title=title, message=message):
                                self.export_dialog.quit()
                    elif not is_file_writable(self._csvfile):
                        errormessage = LANG_DICT['acsErrorMessage'][plugin.language]
                    if errormessage:
                        title = LANG_DICT['showerrWinTitle'][plugin.language]
                        tk.messagebox.showerror(parent=self.export_dialog, title=title, message=errormessage)
                    else:
                        quit_filedialog(False)

                # create_buttonrow(parentframe)
                frame = ttk.Frame(parentframe)
                frame.grid(column=0, row=3, sticky='ew', padx=12, pady=(20,0))
                ok_button = ttk.Button(frame, text='OK', command=on_okclicked)
                ok_button.grid(column=0, row=0, sticky='ew', padx=0, pady=0)
                ok_button.config(width=31)
                cancel_button = ttk.Button(
                    frame, text=LANG_DICT['cancelButtonText'][plugin.language],
                    command=lambda: quit_filedialog(True)
                )
                cancel_button.grid(column=1, row=0, sticky='ew', padx=(5,0), pady=0)
                cancel_button.config(width=31)

            def quit_filedialog(abort_state):
                """Close dialog and event loop and release memory."""
                self.is_aborted = abort_state
                if self.is_aborted:
                    self._csvfile = ''
                self.export_dialog.quit()
                self.export_dialog.destroy()
                self.export_dialog = None
                del self.export_dialog

            # show_filedialog(filename)
            self.export_dialog = tk.Toplevel(self._root)
            self.export_dialog.title(LANG_DICT['exportWinTitle'][plugin.language])
            geometry = self.position_window(420, 310, centered=True)
            self.export_dialog.geometry(geometry)
            self.export_dialog.resizable(False, False)
            self.export_dialog.protocol('WM_DELETE_WINDOW', lambda: quit_filedialog(True))
            self.export_dialog.attributes('-toolwindow', True)
            self.export_dialog.attributes('-topmost', True)
            self.export_dialog.columnconfigure(0, weight=1)
            self._csvfile = filename
            create_exportentries(self.export_dialog)
            create_buttonrow(self.export_dialog)
            self.export_dialog.mainloop()
            self._delimiter = ',' if self.tk_delimiter.get() == 1 else ';'
            self._encoding = 'cp1252' if self.tk_coding.get() == 1 else 'utf-16'

        # save_csvfile(self)
        show_filedialog(api.csvfilename)
        if self._csvfile:
            with open(self._csvfile, 'w', newline='', encoding=self._encoding) as f:
                csvwriter = csv.writer(f, delimiter=self._delimiter, quoting=csv.QUOTE_ALL)
                for packed_row in api.csv_rows:
                    row_wincp = convert_to_windowscodepage(packed_row)
                    row = [item for item in row_wincp.split('[.]')]
                    csvwriter.writerow(row)
            print_message('INFO', 'fileWrittenInfo', f' = {self._csvfile}')
        else:
            print_message('ERR', 'funcAbortedErr', LANG_DICT['menuEntryName'][plugin.language])

def print_message(level, key, additional_info=''):
    """Show message with date and time in SILworX log window."""
    dt = get_currenttimestamp()
    text = LANG_DICT[key][plugin.language]
    print(f'{dt}, {text}{additional_info}')
    if level == 'ERR' and not plugin.is_development_mode:
        print(f'{text}{additional_info}', file=sys.stderr)

def get_currenttimestamp(return_filename=False):
    """Get current date and time in language dependant format."""
    timestamp = datetime.now()
    dateFormat = LANG_DICT['logDateFormat'][plugin.language]
    dt = timestamp.strftime(dateFormat+' %H:%M:%S.')
    ms = timestamp.strftime('%f')
    localtime = dt+ms[:3]
    filename_timestamp = timestamp.strftime('%Y_%m_%d_%H_%M_%S.csv')
    if return_filename:
        return localtime, filename_timestamp
    else:
        return localtime

def convert_to_localtime(utc_dt):
    """Convert a UTC time according to the local time."""
    if type(utc_dt) is str:
        if utc_dt == '---':
            # No time stamp available
            return utc_dt
        else:
            # SILworx internal format (language independent) = yyyy-mm-ddThh:mm:ss.mssZ
            datetime_object = datetime.strptime(utc_dt, '%Y-%m-%dT%H:%M:%S.%fZ')
            localtime = datetime_object.replace(tzinfo=timezone.utc).astimezone(tz=None)
            dateFormat = LANG_DICT['logDateFormat'][plugin.language]
            dt = localtime.strftime(dateFormat+' %H:%M:%S.')
            ms = utc_dt[20:23]
            return dt[:20]+ms
    else:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def convert_to_windowscodepage(s):
    """Convert an url coded string to the current Windows codepage."""
    raw = s.replace('%00', '%')             # quick and dirty: s is UTF16 encoded, but requests.utils.unquote needs UTF8
    return requests.utils.unquote(raw, 'cp1252')

def parse_args():
    """Read command line arguments delivered from SILworX."""
    parser = ArgumentParser()
    parser.add_argument('--tls-certificate', dest='certificate', default=r'C:\ProgramData\SILworX_v15.0.0 R2875\settings\api_cert.pem')
    parser.add_argument('--api-port', dest='apiport', default='51710')
    parser.add_argument('--api-address', dest='apiaddress', default='127.0.0.1')
    parser.add_argument('--plugin-port', dest='pluginport', default='8400')
    parser.add_argument('--language', dest='language', default='de')
    parser.add_argument('--read-secret', dest='readsecret', action='store_true', default=False)
    parser.add_argument('--silworx-version', dest='swxversion', default='15.0.0')
    return parser.parse_args()

def run_inventory():
    """Collect all information from SILworX to generate an inventory"""
    gui.is_aborted = False
    gui.x_pos = None
    api.read_silworxinfo()
    api.read_structuretree()
    if api.has_user_management:
        gui.show_logindialog()
        if gui.is_aborted:
            print_message('ERR', 'funcAbortedErr', LANG_DICT['menuEntryName'][plugin.language])
    else:
        api.usergroup = 'Administrator'
        api.password = ''
    if not gui.is_aborted:
        gui.show_splashscreen()
        if api.do_systemlogin():
            api.read_systeminfo()
            api.read_moduleinfo()
            api.do_disconnect()
        else:
            api.csv_rows.append(LANG_DICT['csvrow4_nodata'][plugin.language])
        gui.quit_splashscreen()
        gui.save_csvfile()

def run_plugin(args):
    """Start WebSocket communication with SILworX."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_3    
    context.load_verify_locations(args.certificate)
    try:
        ws = websocket.WebSocketApp(
            'wss://127.0.0.1:'+args.pluginport,
            on_open=plugin.on_open,
            on_message=plugin.on_message,
            on_error=plugin.on_error,
            on_close=plugin.on_close
        )
    except ConnectionRefusedError as e:
        print_message('ERR', 'onErrorErr', f' = {e}')
        sys.exit(1)
    if ws.run_forever(sslopt={'context': context}):     # Set dispatcher to automatic reconnection
        print_message('ERR', 'onErrorErr', f' = {e}')
        sys.exit(1)

if __name__ == '__main__':
    arguments = parse_args()
    plugin = Plugin(arguments)
    api = API(arguments)
    gui = GUI()
    run_plugin(arguments)
    sys.exit(0)
