from pywinauto import Desktop



def list_ui_elements():

    windows = Desktop(
        backend="uia"
    ).windows()

    result = []

    for w in windows:

        try:

            title = w.window_text()

            rect = w.rectangle()

            result.append({

                "title": title,

                "x": rect.left,

                "y": rect.top,

                "w": rect.width(),

                "h": rect.height()
            })

        except:
            pass

    return result

def click_ui_element(
    title
):

    windows = Desktop(
        backend="uia"
    ).windows()

    for w in windows:

        try:

            if title.lower() in (
                w.window_text().lower()
            ):

                w.set_focus()

                return True

        except:
            pass

    return False

def get_active_window():

    try:

        window = Desktop(
            backend="uia"
        ).get_active()

        return {

            "title": window.window_text()
        }

    except:

        return None    