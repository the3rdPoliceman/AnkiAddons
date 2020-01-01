from PyQt5 import QtWidgets
from anki.importing import TextImporter
from aqt import mw
from aqt.qt import *
from os import listdir
from shutil import copyfile


def export_spanish():
    config = mw.addonManager.getConfig(__name__)
    file_path = config['export_file_path']
    deck_names = config['decks-to-export']
    states = config['states-to-export']

    file_content_as_string = u" "
    for deckName in deck_names:
        card_ids = set([])
        note_ids = set([])

        for state in states:
            card_ids = mw.col.findCards("\"deck:" + deckName + "\" " + state)
            for cardId in card_ids:
                note_ids.add(mw.col.getCard(cardId).nid)

        for noteId in note_ids:
            note = mw.col.getNote(noteId)
            file_content_as_string += note.fields[2]
            file_content_as_string += "\n"

    file_content_as_string = file_content_as_string.encode('utf-8').strip()
    file = open(file_path, "wb")
    file.write(file_content_as_string)
    file.close()


def import_spanish():
    config = mw.addonManager.getConfig(__name__)
    base_directory = QtWidgets.QFileDialog.getExistingDirectory(mw, 'Select base directory')
    lesson_file = base_directory + "/lesson-file.tsv"
    lesson_media_directory = base_directory + "/media/"
    lesson_media_files = [f for f in listdir(lesson_media_directory)]

    anki_media_directory = config['anki-media-directory']
    for lesson_media_file in lesson_media_files:
        copyfile(lesson_media_directory + lesson_media_file, anki_media_directory + lesson_media_file)

    import_deck_name = config['import-to-deck']
    import_model_name = config['import-model']

    import_deck_id = mw.col.decks.id(import_deck_name)
    mw.col.decks.select(import_deck_id)
    import_model = mw.col.models.byName(import_model_name)
    import_deck = mw.col.decks.get(import_deck_id)
    import_deck['mid'] = import_model['id']
    mw.col.decks.save(import_deck)
    import_model['did'] = import_deck_id

    ti = TextImporter(mw.col, lesson_file)
    ti.initMapping()
    ti.run()


# create a new menu item
exportAction = QAction("Export Spanish", mw)
exportAction.triggered.connect(export_spanish)
mw.form.menuTools.addAction(exportAction)

importAction = QAction("Import Spanish", mw)
importAction.triggered.connect(import_spanish)
mw.form.menuTools.addAction(importAction)
