from pywinauto import Application, Desktop
import time

app = Application(backend="uia").connect(title_re=".*ProofTest-Reporting solution.*SILworX.*")
dlg = app.window(title_re=".*ProofTest-Reporting solution.*SILworX.*")
dlg.set_focus()
for c in dlg.descendants(control_type="MenuItem"):
    if c.window_text() == "Extras":
        c.click_input()
        time.sleep(0.6)
        break
for c in dlg.descendants(control_type="MenuItem"):
    if "API certificate" in c.window_text():
        print("click", c.window_text())
        c.click_input()
        time.sleep(5)
        break
for w in Desktop(backend="uia").windows():
    print("W", repr(w.window_text()), w.class_name())
    if w.window_text() and "SILworX" not in w.window_text():
        for d in w.descendants():
            t = d.window_text()
            if t and len(t) < 100:
                print(" ", d.element_info.control_type, repr(t))
