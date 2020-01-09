from PyQt5 import QtWidgets
from anki.importing import TextImporter
from aqt import mw
from aqt.qt import *
from os import listdir
from shutil import copyfile


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


def export_spanish():
    config = mw.addonManager.getConfig(__name__)
    file_path = config['export-file-path']
    decks_details = config['decks-export-details']

    file_content_as_string = u" "
    for decks_detail in decks_details:
        deck_name = decks_detail["deck"]
        states_to_export = decks_detail["states-to-export"]
        spanish_field_index = decks_detail["field-index-containing-spanish"]
        note_ids = set([])

        for state in states_to_export:
            search_query = "\"deck:" + deck_name + "\" " + state
            sys.stderr.write(search_query + "\n")
            card_ids = mw.col.findCards(search_query)
            for card_id in card_ids:
                note_ids.add(mw.col.getCard(card_id).nid)

        for noteId in note_ids:
            note = mw.col.getNote(noteId)
            file_content_as_string += note.fields[spanish_field_index]
            file_content_as_string += "\n"

    # write file
    file_content_as_string = file_content_as_string.encode('utf-8').strip()
    file = open(file_path, "wb")
    file.write(file_content_as_string)
    file.close()

    # move cards to target deck(s)
    for decks_detail in decks_details:
        deck_name = decks_detail["deck"]
        states_to_export = decks_detail["states-to-export"]
        target_deck = decks_detail["target-deck-after-exporting"]

        target_deck_id = mw.col.decks.id(target_deck)
        sys.stderr.write("id:" + str(target_deck_id))
        sys.stderr.write(target_deck)
        for state in states_to_export:
            card_ids = mw.col.findCards("\"deck:" + deck_name + "\" " + state)
            for card_id in card_ids:
                card = mw.col.getCard(card_id)
                sys.stderr.write("writing card " + str(card_id) + " to " + str(target_deck_id))
                card.did = target_deck_id
                card.flush()


# create menu items
importAction = QAction("Import Spanish", mw)
importAction.triggered.connect(import_spanish)
mw.form.menuTools.addAction(importAction)

exportAction = QAction("Export Spanish", mw)
exportAction.triggered.connect(export_spanish)
mw.form.menuTools.addAction(exportAction)
