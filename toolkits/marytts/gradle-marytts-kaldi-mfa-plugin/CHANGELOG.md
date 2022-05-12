Gradle MaryTTS Kaldi MFA Plugin
===============================

[Unreleased]
------------

### Changed

- [all changes since v0.3.6]

[v0.3.6] (2018-10-19)
---------------------

### Added

- support for languages other than US English

### Changed

- [all changes since v0.3.5]

[v0.3.5] (2018-10-01)
---------------------

### Added

- exposed MFA command line options as wrapper task properties

### Changed

- CI testing on multiple Mac OSX versions (10.10-10.13)
- [all changes since v0.3.4]

[v0.3.4] (2018-09-18)
---------------------

### Changed

- resolve MFA from source archive, not Ivy repo
- unpack MFA directly under `build/mfa`
- convert to lower case for utterance tokens, generated dictionary
- build with Gradle v4.10.1
- [all changes since v0.3.3]

[v0.3.3] (2018-09-15)
---------------------

### Added

- CI testing on Mac OSX

### Changed

- build with Gradle v4.10
- improve documentation
- [all changes since v0.3.2]

### Fixed

- trim potential whitespace from XML text nodes when generating dictionary

[v0.3.2] (2018-04-22)
---------------------

### Changed

- merge tasks for MaryXML processing; input text and custom dictionary are now generated from a single task, `processMaryXml`
- [all changes since v0.3.1]

### Fixed

- strip trailing dots (e.g., from abbreviations) from tokens; previously, these caused `<unk>` words in the aligned words, and missing segments

[v0.3.1] (2018-04-18)
---------------------

### Changed

- build with Gradle v4.7
- always run MFA multi-threaded; no need to add `--parallel` option
- [all changes since v0.3.0]

[v0.3.0] (2018-02-16)
---------------------

### Changed

- build with Gradle v4.5.1
- upgrade some dependencies
- download (and cache) MFA as dependency
- use Gradle Provider API to manage task configuration and dependencies
- [all changes since v0.2.0]

[v0.2.0] (2017-11-10)
---------------------

### Changed

- updated jtgt to v5.3
- removed dependency in `convertTextGridToXlab.groovy`
    - this task can now also be used for other TextGrids
- updated jtgt to stable release
- updated the documentation
- added `labelMapping`
- adding missing package name
- generalized paths in Groovy task
- no requirement for Docker anymore
    - we directly use the binaries from MFA v1.0.0 now
    - check for OS to see which binary to download
- [all changes since v0.1.0]

[v0.1.0] (2017-07-14)
---------------------

### Initial release

- Forced Alignment based on a [Kaldi MFA Docker image](https://hub.docker.com/r/psibre/kaldi-mfa/)

[Unreleased]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/tree/master
[all changes since v0.3.6]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.6...HEAD
[v0.3.6]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.6
[all changes since v0.3.5]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.5...v0.3.6
[v0.3.5]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.5
[all changes since v0.3.4]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.4...v0.3.5
[v0.3.4]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.4
[all changes since v0.3.3]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.3...v0.3.4
[v0.3.3]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.3
[all changes since v0.3.2]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.2...v0.3.3
[v0.3.2]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.2
[all changes since v0.3.1]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.1...v0.3.2
[v0.3.1]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.1
[all changes since v0.3.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.3.0
[all changes since v0.2.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.2.0
[all changes since v0.1.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/marytts/gradle-marytts-kaldi-mfa-plugin/releases/tag/v0.1.0
