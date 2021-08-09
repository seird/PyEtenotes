import logging
import pickle
import time
from typing import Any, List

from etebase import (DEFAULT_SERVER_URL, Account, Client, Collection,
                     FetchOptions, random_bytes)

from .__version__ import __title__
from .settings import Settings


logger = logging.getLogger("logger")
settings = Settings(__title__)


class Notebook(object):
    def __init__(self, collection: Collection):
        self.uid = collection.uid
        self.name = collection.meta["name"]
        self.color = collection.meta["color"]
        self.collection = collection


class Note(object):
    def __init__(self, item: Any, notebook: Notebook):
        self.uid = item.uid
        self.name = item.meta["name"]
        self.content = item.content
        self.changed = False
        self.item = item
        self.notebook = notebook


class EtesyncNotes(object):
    def __init__(self):
        self.server_url = None
        self.client = None
        self.etebase = None
        self.authenticated = False
        self.stoken = {"notebook": None, "note": None}

    def authenticate(self, username: str, password: str, server_url: str = None, stay_logged_in: bool = True) -> bool:
        self.server_url = server_url or DEFAULT_SERVER_URL
        self.client = Client(__title__, self.server_url)

        if self.server_url != DEFAULT_SERVER_URL and not Account.is_etebase_server(self.client):
            return False

        try:
            self.etebase = Account.login(self.client, username, password)
            if stay_logged_in:
                # Store the session
                encryption_key = random_bytes(32)
                stored_session = self.etebase.save(encryption_key)
                settings.setValue("session/url", self.server_url)
                settings.setValue("session/key", encryption_key) # Todo (?) Store somewhere else
                settings.setValue("session/sessiondata", stored_session)

            self.authenticated = True
            logger.debug("EtesyncNotes.authenticate: successful.")
        except Exception as e:
            logger.debug("EtesyncNotes.authenticate: failed: " + str(e))

        return self.authenticated

    def restore_session(self, encryption_key: bytes, stored_session: Any, server_url: str):
        self.server_url = server_url
        self.client = Client(__title__, self.server_url)
        self.etebase = Account.restore(self.client, stored_session, encryption_key)

    def cache_save(self, notebooks: List[Notebook], notes: List[Note]):
        cache = {"stoken": self.stoken, "notebooks": [], "notes": []}

        col_mgr = self.etebase.get_collection_manager()
        for notebook in notebooks:
            cache["notebooks"].append(col_mgr.cache_save(notebook.collection))

        for note in notes:
            item_mgr = col_mgr.get_item_manager(note.notebook.collection)
            cache["notes"].append((note.notebook.uid, item_mgr.cache_save(note.item)))

        with open(settings.value("cache/path"), "wb") as f:
            pickle.dump(cache, f)

    def cache_load(self):
        try:
            with open(settings.value("cache/path", type=str), "rb") as f:
                cache = pickle.load(f)
        except FileNotFoundError as e:
            logger.debug(f"EtesyncNotes.cache_load: file not found: {e}")
            return [], []
        except pickle.PickleError as e:
            logger.error(f"EtesyncNotes.cache_load: pickle error: {e}")
            return [], []

        # Retrieve notebooks
        col_mgr = self.etebase.get_collection_manager()
        try:
            notebooks = [Notebook(col_mgr.cache_load(blob)) for blob in cache["notebooks"]]
        except Exception as e:
            logger.warning(f"EtesyncNotes.cache_load: cache_load error: {e}")
            return [], []

        if not notebooks:
            return [], []

        self.stoken = cache["stoken"]

        # Retrieve notes
        notes = []
        for notebook_uid, blob in cache["notes"]:
            notebook = list(filter(lambda nb: notebook_uid == nb.uid, notebooks))
            if not notebook:
                return
            notebook = notebook[0]
            item_mgr = col_mgr.get_item_manager(notebook.collection)
            item = item_mgr.cache_load(blob)
            notes.append(Note(item, notebook))

        return notebooks, notes

    def logout(self):
        self.etebase.logout()
        settings.remove("session/key")
        settings.remove("session/sessiondata")
        settings.remove("notetreewidget/")
        settings.remove("noteentrywidget/")
        settings.remove("newnotedialog/selectednotebook")

    def get_notebooks(self, changes=False) -> List[Notebook]:
        col_mgr = self.etebase.get_collection_manager()
        collections = col_mgr.list("etebase.md.note", FetchOptions().stoken(self.stoken["notebook"] if changes else None))
        self.stoken["notebook"] = collections.stoken
        return [Notebook(collection) for collection in collections.data if not collection.deleted]

    def create_notebook(self, name: str, description: str, color: str) -> Notebook:
        col_mgr = self.etebase.get_collection_manager()

        # Create, encrypt and upload a new collection
        collection = col_mgr.create("etebase.md.note",
            {
                "name": name,
                "description": description,
                "color": color,
            },
            b""  # Empty content
        )
        col_mgr.upload(collection)
        return Notebook(collection)

    def remove_notebook(self, notebook: Notebook):
        col_mgr = self.etebase.get_collection_manager()
        notebook.collection.delete()
        col_mgr.upload(notebook.collection)

    def get_notes(self, notebook: Notebook, changes=False) -> List[Note]:
        col_mgr = self.etebase.get_collection_manager()
        item_mgr = col_mgr.get_item_manager(notebook.collection)
        items = item_mgr.list(FetchOptions().stoken(self.stoken["note"] if changes else None))
        self.stoken["note"] = items.stoken
        return [Note(item, notebook) for item in items.data if not item.deleted]

    def save_notes(self, notes: List[Note], force: bool = False):
        for note in notes:
            self.save_note(note, force=force)

    def save_note(self, note: Note, force: bool = False):
        if not note.changed and not force:
            logger.debug(f"EtesyncNotes.save_note: {note.name} has no new contents. Skipping.")
            return
        note.item.content = note.content
        col_mgr = self.etebase.get_collection_manager()
        item_mgr = col_mgr.get_item_manager(note.notebook.collection)
        item_mgr.batch([note.item])
        note.changed = False
        logger.debug(f"EtesyncNotes.save_note: {note.name} saved.")

    def create_note(self, name: str, notebook: Notebook) -> Note:
        col_mgr = self.etebase.get_collection_manager()
        item_mgr = col_mgr.get_item_manager(notebook.collection)

        item = item_mgr.create(
            {
                "type": "file",
                "name": name,
                "mtime": int(round(time.time() * 1000))
            },
            b""
        )
        item_mgr.batch([item])

        return Note(item, notebook)

    def remove_note(self, note: Note):
        col_mgr = self.etebase.get_collection_manager()
        item_mgr = col_mgr.get_item_manager(note.notebook.collection)
        note.item.delete()
        item_mgr.batch([note.item])
