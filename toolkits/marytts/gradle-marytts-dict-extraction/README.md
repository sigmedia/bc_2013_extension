[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

Gradle MaryTTS Dictionary generation plugin
===============================

This plugin uses [MaryTTS] to generate a phonetic dictionary.

Prerequisites
-------------

In your project directory, place the audio and text files under your `build` directory like this:

```
build
├── text
    ├── utt0001.txt
    ├── utt0002.txt
    ├── utt0003.txt
    ├── utt0004.txt
    └── utt0005.txt

```

How to apply this plugin
------------------------

TODO

Plugin Tasks
---------

Applying this plugin to a project adds several tasks, which are configured as follows.

### `generateDictionary`
Extract the dictionary and save the utterances in the JSON format
#### Inputs
- `srcDir`, default: `layout.buildDirectory.dir('text')`
#### Outputs
- `destDir`, default: `layout.buildDirectory.dir('utt_json')`
- `destDir`, default: `layout.buildDirectory.fil('dict.txt')`

[MaryTTS]: http://mary.dfki.de/
