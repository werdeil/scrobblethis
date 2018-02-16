#
# Copyright 2009 Amr Hassan <amr.hassan@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import hashlib
import pylast
import st.common

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

# scrobblethis
API_KEY    = 'b1f2c888bff831d32b7c2598226eaf0f'
API_SECRET = '3d5bbb9bf2a7ad3e175af8a414c2ea5f'
# Registered to werdeil

class Account(object):
    def __init__(self, name, server, username, password, password_hash, submit_url, client_version):

        self.name = name
        self.username = username
        self.server = server

        if not password_hash:
            password_hash = hashlib.md5(password).hexdigest()

        if server == "lastfm":
            self.network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username = username, password_hash = password_hash)
        elif server == "librefm":
            self.network = pylast.LibreFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username = username, password_hash = password_hash)
        elif server == "custom":
            self.network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username = username, password_hash = password_hash)
            self.network.submission_server = submit_url

        self.cache = []

    def add_to_scrobble_cache(self, track):
        self.cache.append([track.artist, track.title, track.timestamp, pylast.SCROBBLE_SOURCE_USER,
                           pylast.SCROBBLE_MODE_PLAYED, track.duration, track.album, track.position,
                           track.musicbrainz])

    def scrobble(self):
        self.network.scrobble_many(self.cache)

    def __repr__(self):
        return self.name

def get_accounts():
    c = configparser.ConfigParser(defaults={"password": "", "md5_password_hash": "", "submit_url": ""})

    accounts_config_path = st.common.get_config_path("accounts.config")

    l = []
    if os.path.exists(accounts_config_path):
        c.read(accounts_config_path)

        for name in c.sections():
            l.append(Account(name = name,
                             server = c.get(name, "server"),
                             username = c.get(name, "username"),
                             password = c.get(name, "password"),
                             password_hash = c.get(name, "md5_password_hash"),
                             submit_url = c.get(name, "submit_url"),
                             client_version = st.common.version
                            ))

    return l

def write_default_accounts():
    text = """# Enable one or more of these accounts
# 
# You can either provide your passwords or your md5 hash. To get a md5 of a string type this into a shell:
# python -c "import getpass, hashlib; print(hashlib.md5(getpass.getpass().encode('utf-8')).hexdigest())"
# 
#
#A sample Last.fm account. Uncomment this section to use it.
#[MyLastfmAccount]
#type = lastfm
#username = 
#password = 
#md5_password_hash = 
#
#A sample Libre.fm account. Uncomment this section to use it.
#[MyLibrefmAccount]
#type = librefm
#username = 
#password = 
#md5_password_hash = 
#
#A sample custom account account
#[MyCustomAccount]
#type = custom
#submit_url = 
#username = 
#password = 
#md5_password_hash = """


    path = st.common.get_config_path("accounts.config")

    if os.path.exists(path):
        return

    def make_dir(path):
        first_level = os.path.dirname(path)
        if not os.path.exists(os.path.dirname(first_level)):
            make_dir(os.path.dirname(first_level))

        os.mkdir(first_level)

    make_dir(path)

    fp = open(path, "w")
    fp.write(text)
    fp.close()
