# MaryTTS Merlin frontend

This is a starting point to plug marytts with merlin. It is in a really early stage and some filenames are hardcoded.

## Run as the following

```shell
./gradlew process -Plist_filename=tmp/list -Ptxt_dir=tmp/txt -Plab_dir=lab --include-build=/home/slemaguer/work/maintained_tools/src/marytts/system/6.x --stacktrace
```
- list_filename: file containing the list of basenames the user wants to get the lab     [input]
- txt_dir: directory containing the text files                                           [input]
- lab_dir: directory which will contains the output label files                          [output]
