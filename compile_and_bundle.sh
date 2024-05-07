#!/bin/bash
#Usage: ./compile_and_bundle.sh 
#this must run from ~/Desktop/src. 
#results: save file "FCT" on ~/Desktop. save needed distribution files in folder on ~/Desktop/.dist

if [[ $(/usr/bin/id -u) -eq 0 ]]; then
    echo "Cannot run as root on Mac"
    exit
fi

app_name='Data Grapher'
src_py_file="Data_Grapher.py"
distro_dmg_folder='~/Documents/Github/data_grapher/dist'

# app_icon="${app_name}.icns"
app_file="${app_name}.app"
distro_date=$(date +'%Y-%m-%d')
echo "Building app = ${app_file}"

dist_folder="dist/"

#Pyinstaller will put the app here. And all contents will be copy to dmg
distro_app_folder="${dist_folder}app/" 

#Pyinstaller will also make a CLI file here but we will move it to the dist/ folder
cli_app_folder="${distro_app_folder}${app_name}/"
cli_app="${cli_app_folder}${app_name}" 
cli_app_internal_folder="${cli_app_folder}_internal/" 

#Create dmg will then go to distro_app_folder and package into dmg here. 
distro_dmg_filename="${app_name}_distro_${distro_date}.dmg"
distro_dmg="${distro_dmg_folder}${distro_dmg_filename}"

# clean up build files
[ -d "build" ] && rm -rf build
[ -d "build_cythonize" ] && rm -rf build_cythonize

# cleanup files in dist folder. Dont' clean up the folder for easy entering of command from terminal
[ -d "${dist_folder}" ] && rm -rf "${dist_folder}*"
[ -d "${distro_app_folder}" ] && rm -rf "${distro_app_folder}*"

#cleanup cli
[ -d "${dist_folder}_internal" ] && rm -rf "${dist_folder}_internal"
[ -e "${dist_folder}${app_name}" ] && rm -rf "${dist_folder}${app_name}"

# cleanup pyinstaller .spec file
[ -f "${app_name}.spec" ] && rm "${app_name}.spec"

# If the DMG already exists, delete it.
[ -f "${distro_dmg}" ] && rm "${distro_dmg}"

#remove all compiled libraries
rm -f *darwin.so

#remove all compiled python
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# compile
cp ../common/lib_*.py . 
python3 setup.py build_ext --inplace -j 6
rm lib_*.py 

# if windowed means already a single .app. Don't do --onefile again because it will zip up the folder before putting into one app for mac which slows down load
#module regex needed for pandas lambda

pyinstaller \
    --noconfirm \
    --windowed \
    --name "${app_name}" \
    --add-binary="Data_Grapher.cpython-311-darwin.so:." \
    --hidden-import="numpy" \
    --hidden-import="pandas" \
    --hidden-import="PyQt6" \
    --hidden-import="sys" \
    --exclude-module="PyQt5" \
    --distpath="${distro_app_folder}" \
    "${src_py_file}"

#move cli to dist folder
[ -f "${cli_app}" ] && mv "${cli_app}" "${dist_folder}"
[ -d "${cli_app_internal_folder}" ] && mv "${cli_app_internal_folder}" "${dist_folder}"
[ -d "${cli_app_folder}" ] && rmdir "${cli_app_folder}"

#remove build files
rm -f *.so  
rm -f *.spec
rm -rf build/
rm -rf build_cythonize/


create-dmg \
    --volname "${app_name}" \
    --window-pos 200 120 \
    --window-size 300 600 \
    --app-drop-link 425 120 \
    "${distro_dmg}" \
    "${distro_app_folder}"
    #--volicon "Hello World.icns" \



