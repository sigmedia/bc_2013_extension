[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Build Status](https://travis-ci.org/marytts/gradle-marytts-kaldi-mfa-plugin.svg?branch=master)](https://travis-ci.org/marytts/gradle-marytts-kaldi-mfa-plugin)

Gradle MaryTTS Kaldi MFA plugin
===============================

This plugin uses the [Kaldi]-based [Montreal Forced Aligner] to phonetically segment audio data based on corresponding text files.
It uses [MaryTTS] to predict the text pronunciation.

Prerequisites
-------------

In your project directory, place the audio and text files under your `build` directory like this:

```
build
├── text
│   ├── utt0001.txt
│   ├── utt0002.txt
│   ├── utt0003.txt
│   ├── utt0004.txt
│   └── utt0005.txt
└── wav
    ├── utt0001.wav
    ├── utt0002.wav
    ├── utt0003.wav
    ├── utt0004.wav
    └── utt0005.wav
```

### Linux note

If you are on a Linux system, ensure that the `libcblas.so.3` file is on the library search path, since it is not bundled with the Linux release of [Montreal Forced Aligner].
For details, see the [installation notes](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/blob/3f548a89c03cabe0c778649d4799b2d3ff1db42f/docs/source/installation.rst#linux).

We hope that this issue is resolved in a future release; until then you can install the missing library by running
```
sudo apt-get install libatlas3-base
```
on Debian-based distributions (such as Ubuntu).

### Windows note

On Windows, an installation of Visual Studio is required.

How to apply this plugin
------------------------

Please see the instructions at <https://plugins.gradle.org/plugin/de.dfki.mary.voicebuilding.marytts-kaldi-mfa>

MFA Tasks
---------

Applying this plugin to a project adds several tasks, which are configured as follows.

### `convertTextToMaryXml`
Converts text files to MaryXML for pronunciation prediction (G2P)
#### Inputs
- `locale`, default: `Locale.US`
- `srcDir`, default: `layout.buildDirectory.dir('text')`
#### Outputs
- `destDir`, default: `layout.buildDirectory.dir('maryxml')`

### `processMaryXml`
Extracts text input files from MaryXML and generates custom dictionary for MFA
#### Inputs
- `srcDir`, default: `convertTextToMaryXml.destDir`
#### Outputs
- `destDir`, default: `layout.buildDirectory.dir('mfaLab')`
- `dictFile`, default: `layout.buildDirectory.file('dict.txt')`

### `prepareForcedAlignment`
Collects audio and text input files and custom dictionary for MFA
#### Inputs
- `wavDir`, default: `layout.buildDirectory.dir('wav')`
- `mfaLabDir`, default: `processMaryXml.destDir`
- `dictFile`, default: `processMaryXml.dictFile`
#### Outputs
- `destDir`, default: `layout.buildDirectory.dir('forcedAlignment')`

### `unpackMFA`
Downloads and unpacks MFA
#### Outputs
- `destinationDir`, default: `layout.buildDirectory.dir('mfa')`

### `runForcedAlignment`
Runs MFA to generate Praat TextGrids (for details on some properties, see the [CLI documentation])
#### Inputs
- `unpackMFA`
- `srcDir`, default: `prepareForcedAlignment.destDir`
- `speakerChars`, default: `0`
- `fast`, defalt: `false`
- `numJobs`, default: `gradle.startParameter.maxWorkerCount`
- `noDict`, default: `false`
- `clean`, default: `false`
- `debug`, default: `false`
- `ignoreExceptions`, default: `false`
#### Outputs
- `modelDir`, default: `layout.buildDirectory.dir('kaldiModels')`
- `destDir`, default: `layout.buildDirectory.dir('TextGrid')`

### `convertTextGridToXLab`
Converts Praat TextGrids to XWaves lab format (with label mapping)
#### Inputs
- `srcDir`, default: `runForcedAlignment.destDir`
- `tierName`, default: `'phones'`
- `labelMapping`, default: `[sil: '_', sp: '_']`
#### Outputs
- `destDir`, default: `layout.buildDirectory.dir('lab')`

To customize the directories configured as input for the forced alignment, you can override them like this in the project's `build.gradle`:

```groovy
convertTextToMaryXml {
    srcDir = file("some/other/text/directory")
}

prepareForcedAlignment {
    wavDir =  file("$buildDir/wav")
    dictFile = file("someDict.txt")
}
```

How to run the forced alignement
--------------------------------

Run
```
./gradlew runForcedAlignment
```
after which the resulting TextGrid files will be under `build/TextGrid`.

### G2P for other languages

To use MaryTTS to predict the pronunciation for languages other than US English, two things must be configured:

1. The `locale` property of the `convertTextToMaryXml` task must be set to the target locale, e.g.,
    ```groovy
    convertTextToMaryXml {
        locale = Locale.GERMAN
    }
    ```
    for German, or
    ```groovy
    convertTextToMaryXml {
        locale = Locale.forLanguageTag("pl-PL")
    }
    ```
    for Polish.
1. The required MaryTTS language component must be added as a dependency to the `marytts` configuration, e.g.,
    ```groovy
    dependencies {
        marytts group: 'de.dfki.mary', name: 'marytts-lang-de', version: '5.2'
    }
    ```
    for German, or
    ```groovy
    repositories {
        maven {
            url 'https://oss.jfrog.org/artifactory/oss-snapshot-local/'
        }
    }
    
    dependencies {
        marytts group: 'de.dfki.mary', name: 'marytts-lang-pl', version: '0.1.0-SNAPSHOT'
    }
    ```
    to resolve a proof-of-concept [language component for Polish] from [OJO].

### Optional post-processing

In order to use the TextGrids for voicebuilding with [MaryTTS] you have to replace the `sil` and `sp` labels with `_` and convert them to `lab` files in Xwaves format.

This can be done simply by running
```
./gradlew convertTextGridToXLab
```
Note that you can also *override* the label mapping:
```groovy
convertTextGridToXLab {
    labelMapping = [sil: 'pau', a: 'ah'] // etc.
}
```

### Using *convertTextGridToXLab* alone

If you want to use `convertTextGridToXLab` alone you may want to override the default TextGrid-directory which is `build/TextGrid/forcedAlignment`:
```
convertTextGridToXLab.tgDir = file("$buildDir/TextGrid")
```

[CLI documentation]: https://montreal-forced-aligner.readthedocs.io/en/v1.0.0/aligning.html#common-options-for-both-aligner-executables
[Kaldi]: http://kaldi-asr.org/
[language component for Polish]: https://github.com/marytts/marytts-lang-pl
[MaryTTS]: http://mary.dfki.de/
[Montreal Forced Aligner]: https://montrealcorpustools.github.io/Montreal-Forced-Aligner/
[OJO]: https://oss.jfrog.org/
[SoX]: http://sox.sourceforge.net/
