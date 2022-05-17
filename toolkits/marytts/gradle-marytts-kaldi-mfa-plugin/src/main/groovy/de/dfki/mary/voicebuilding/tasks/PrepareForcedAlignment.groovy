package de.dfki.mary.voicebuilding.tasks

import org.gradle.api.DefaultTask
import org.gradle.api.file.*
import org.gradle.api.tasks.*

class PrepareForcedAlignment extends DefaultTask {

    @InputDirectory
    final DirectoryProperty wavDir = newInputDirectory()

    @InputDirectory
    final DirectoryProperty mfaLabDir = newInputDirectory()

    @InputFile
    final RegularFileProperty dictFile = newInputFile()

    @OutputDirectory
    final DirectoryProperty destDir = newOutputDirectory()

    @TaskAction
    void prepare() {
        project.copy {
            from wavDir, {
                include '*.wav'
            }
            from mfaLabDir, {
                include '*.lab'
            }
            from dictFile
            into destDir
        }
    }
}
