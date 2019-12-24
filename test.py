"""
    @Time    : 2019/12/24 12:31
    @Author  : Chen Runwen
"""
from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
from evernote.edam.type.ttypes import Note, Notebook

# 这个是沙盒的账号
# dev_token = ""
# client = EvernoteClient(token=dev_token, service_host='sandbox.yinxiang.com')

# 这个是正式账号
prod_token = ""
client = EvernoteClient(token=prod_token, service_host='app.yinxiang.com')

userStore = client.get_user_store()
user = userStore.getUser()
print(user.username)

# --- 加笔记本
# 第一件事，get_note_store
noteStore = client.get_note_store()
notebook = Notebook()
notebook.name = "My Notebook"
notebook = noteStore.createNotebook(notebook)
print(notebook.guid)

# --- 加笔记
noteStore = client.get_note_store()
note = Note()
note.title = "I'm a test note!"
note.content = '<?xml version="1.0" encoding="UTF-8"?>' \
               '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
note.content += '<en-note>Hello, world!</en-note>'
# 如果不附notebookGUID的话会创建到默认笔记本里
note.notebookGuid = notebook.guid
note = noteStore.createNote(note)

# --- 搜索笔记
noteStore = client.get_note_store()
# notebooks = noteStore.listNotebooks()
guid_notebook = '2d083d6b-b84e-4dea-b6de-e4fa42d8fd72'
notebook = noteStore.getNotebook(guid_notebook)  # OneNote迁移 笔记本
guid_notebook_bak = '9a93a8dc-d863-4621-8ab5-c91f4fdf8576'
notebook_bak = noteStore.getNotebook(guid_notebook_bak)  # 迁移备份 笔记本

filter = NoteStore.NoteFilter()
filter.notebookGuid = guid_notebook
spec = NoteStore.NotesMetadataResultSpec()
spec.includeTitle = True
notes = noteStore.findNotesMetadata(filter, 0, 200, spec).notes

note = noteStore.getNote(notes[1].guid, True, True, True, True)
print(note.content)
note_new = noteStore.getNote(notes[0].guid, True, True, True, True)
print(note_new.content)

