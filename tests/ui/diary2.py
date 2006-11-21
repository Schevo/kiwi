... -*- Mode: doctest -*-
... run: examples/framework/diary/diary2.py

>>> from kiwi.ui.test.runner import runner
>>> runner.start()
>>> Diary = runner.waitopen("Diary")
>>> Diary.add.clicked()
>>> Diary.title.set_text("Untitled")
>>> Diary.ObjectList.select_paths(['0'])
>>> Diary.title.set_text("First")
>>> Diary.add.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Untitled")
>>> Diary.ObjectList.select_paths(['1'])
>>> Diary.title.set_text("Second")
>>> Diary.period.clicked()
>>> Diary.afternoon.clicked()
>>> Diary.add.clicked()
>>> Diary.afternoon.clicked()
>>> Diary.period.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Untitled")
>>> Diary.ObjectList.select_paths(['2'])
>>> Diary.title.set_text("Third")
>>> Diary.period.clicked()
>>> Diary.evening.clicked()
>>> Diary.evening.clicked()
>>> Diary.afternoon.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Second")
>>> Diary.ObjectList.select_paths(['1'])
>>> Diary.afternoon.clicked()
>>> Diary.period.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("First")
>>> Diary.ObjectList.select_paths(['0'])
>>> Diary.period.clicked()
>>> Diary.afternoon.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Second")
>>> Diary.ObjectList.select_paths(['1'])
>>> Diary.afternoon.clicked()
>>> Diary.evening.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Third")
>>> Diary.ObjectList.select_paths(['2'])
>>> Diary.remove.clicked()
>>> Diary.ObjectList.select_paths([])
>>> Diary.evening.clicked()
>>> Diary.afternoon.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("Second")
>>> Diary.ObjectList.select_paths(['1'])
>>> Diary.remove.clicked()
>>> Diary.ObjectList.select_paths([])
>>> Diary.afternoon.clicked()
>>> Diary.period.clicked()
>>> Diary.title.set_text("")
>>> Diary.title.set_text("First")
>>> Diary.ObjectList.select_paths(['0'])
>>> Diary.remove.clicked()
>>> Diary.ObjectList.select_paths([])
>>> Diary.title.set_text("")
>>> Diary.title.set_text("")
>>> Diary.delete()
>>> runner.quit()

