import psutil


def get_running_processes():

    result = []

    for p in psutil.process_iter([

        "pid",
        "name"
    ]):

        try:

            result.append({

                "pid": p.info["pid"],

                "name": p.info["name"]
            })

        except:
            pass

    return result