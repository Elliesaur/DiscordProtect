import os
import random
import string
from shutil import copy2


def id_generator(size=7, chars=string.ascii_uppercase + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


roaming = os.getenv('APPDATA')
local = os.getenv('LOCALAPPDATA')

version = "0.0.300"
insecure_folder = "discord"
# Random string 7 chars long.
secure_folder = id_generator()

bootstrapper_file = "{}/Discord/app-{}/resources/app.asar".format(local, version)
desktop_core_file = "{}/{}/{}/modules/discord_desktop_core/core.asar".format(roaming, insecure_folder, version)

user_data_path = '''var userDataPath = _path2.default.join(userDataRoot, 'discord' + (buildInfo.releaseChannel == 'stable' ? '' : buildInfo.releaseChannel));'''


def backup_file(file):
    # Get file info to use to reconstruct the new path.
    split = os.path.splitext(file)
    file_name_inc_path = split[0]
    file_ext = split[1]

    new_file = file_name_inc_path + '_backup' + file_ext

    # Verify it is copied
    new_file = copy2(file, new_file)
    return os.path.exists(new_file)


def rename(folder_path):
    sec = folder_path.replace(insecure_folder, secure_folder)
    os.rename(folder_path, sec)


def patch_asar(in_file):
    if not backup_file(in_file):
        return False

    with open(in_file, 'rb') as file:
        data = file.read()

    data = data.replace(user_data_path.encode('ansi'),
                        user_data_path.replace(insecure_folder, secure_folder).encode('ansi'))

    with open(in_file, 'wb') as file:
        file.write(data)

    return True


if not patch_asar(bootstrapper_file):
    print('Error patching boostrapper!')
    exit()
print('Patched bootstrapper...')
if not patch_asar(desktop_core_file):
    print('Error patching desktop core!')
    exit()
print('Patched desktop core...')
try:
    rename("{}/{}".format(roaming, insecure_folder))
    print('Discord is now secure. The new folder for discord is', secure_folder)
except PermissionError:
    print('Could not rename folder "{}" to "{}" in "{}".\nPlease manually complete this step.'.format(insecure_folder,
                                                                                                      secure_folder,
                                                                                                      roaming))
