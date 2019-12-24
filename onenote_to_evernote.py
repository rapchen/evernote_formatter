"""
    把OneNote同步到印象笔记的笔记格式改成便于编辑的格式
    @Time    : 2019/12/24 17:22
    @Author  : Chen Runwen
"""
from typing import Optional, Any

from bs4 import BeautifulSoup, Tag

from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
from evernote.edam.type.ttypes import Note


def clean_content(content: str) -> str:
    """将XML格式的笔记进行清理，改成便于编辑的格式"""
    content = content.replace('\n', '')
    soup = BeautifulSoup(content, features="html.parser")
    root: Tag = soup.find('en-note')
    root['style'] = 'font-family:Consolas,"Microsoft YaHei"; font-size:11.0pt'

    # 去除OneNote笔记的头（包括标题和创建时间）
    tag: Tag = root.find(style="margin:0in;font-size:10.0pt;color:gray")
    if tag is None:
        tag = root.find('span', text='年').parent
    if tag.parent.previous_sibling is not None:
        tag.parent.previous_sibling.extract()
    tag.parent.extract()
    # 去除OneNote笔记的尾
    tag = root.find_all('p', text='已使用 Microsoft OneNote 2016 创建。')[-1]
    tag.parent.extract()

    # 去除所有仅包含着一个div的div（这是OneNote里的文本框，没有意义）
    div: Tag
    for div in root.find_all('div'):
        if len(div.contents) == 0:
            div.extract()
        elif len(div.contents) == 1 and div.contents[0].name == 'div':
            div.replace_with_children()

    return soup.prettify()


# 这个是正式账号
prod_token = "S=s24:U=5e7bea:E=16f5249169f:C=16f2e3c9198:P=1cd:A=en-devtoken:V=2:H=d7c679940fec0f8d7673a964fe4eb5b6"
client = EvernoteClient(token=prod_token, service_host='app.yinxiang.com')

# 获取笔记本
noteStore = client.get_note_store()
# notebooks = noteStore.listNotebooks()
guid_notebook = '2d083d6b-b84e-4dea-b6de-e4fa42d8fd72'
notebook = noteStore.getNotebook(guid_notebook)  # OneNote迁移 笔记本
guid_notebook_bak = '9a93a8dc-d863-4621-8ab5-c91f4fdf8576'
notebook_bak = noteStore.getNotebook(guid_notebook_bak)  # 迁移备份 笔记本

# 查找笔记
filter = NoteStore.NoteFilter()
filter.notebookGuid = guid_notebook_bak  # TODO 之后改回去
spec = NoteStore.NotesMetadataResultSpec()
spec.includeTitle = True
notes = noteStore.findNotesMetadata(filter, 0, 200, spec).notes
for noteMeta in notes:
    # 先备份一下
    noteStore.copyNote(noteMeta.guid, guid_notebook_bak)
    # 开始改内容
    note = noteStore.getNote(noteMeta.guid, True, True, True, True)
    content = note.content
    new_content = clean_content(content)
    # 更新笔记
    new_note = Note()
    new_note.guid = note.guid
    new_note.title = note.title
    new_note.content = new_content
    noteStore.updateNote(new_note)


