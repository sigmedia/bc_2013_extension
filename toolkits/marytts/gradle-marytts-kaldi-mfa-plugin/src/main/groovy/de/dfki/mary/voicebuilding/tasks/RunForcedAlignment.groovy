package de.dfki.mary.voicebuilding.tasks

import org.gradle.api.DefaultTask
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.*
import org.gradle.internal.os.OperatingSystem

class RunForcedAlignment extends DefaultTask {

    @InputDirectory
    final DirectoryProperty srcDir = newInputDirectory()

    @Input
    Property<Integer> speakerChars = project.objects.property(Integer)

    @Input
    Property<Boolean> fast = project.objects.property(Boolean)

    @Input
    Property<Integer> numJobs = project.objects.property(Integer)

    @Input
    Property<Boolean> noDict = project.objects.property(Boolean)

    @Input
    Property<Boolean> clean = project.objects.property(Boolean)

    @Input
    Property<Boolean> debug = project.objects.property(Boolean)

    @Input
    Property<Boolean> ignoreExceptions = project.objects.property(Boolean)

    @OutputDirectory
    final DirectoryProperty modelDir = newOutputDirectory()

    @OutputDirectory
    final DirectoryProperty destDir = newOutputDirectory()

    @TaskAction
    void run() {
        def outputModelPath = modelDir.get().asFile
        def corpusDirectory = srcDir.get().asFile
        def dictionaryPath = srcDir.file('dict.txt').get().asFile
        def outputDirectory = destDir.get().asFile
        project.exec {
            commandLine = OperatingSystem.current().isWindows() ?
                    ['cmd', '/c', 'bin\\mfa_train_and_align.exe'] :
                    ['lib/train_and_align']
            if (speakerChars.get() > 0) {
                commandLine += ['--speaker_characters', speakerChars.get()]
            }
            if (fast.get()) {
                commandLine += ['--fast']
            }
            if (clean.get()) {
                commandLine += ['--clean']
            }
            if (debug.get()) {
                commandLine += ['--debug']
            }
            if (ignoreExceptions.get()) {
                commandLine += ['--ignore_exceptions']
            }
            commandLine += [
                    '--output_model_path', outputModelPath,
                    '--temp_directory', temporaryDir,
                    '--num_jobs', numJobs.get(),
                    '--verbose',
                    corpusDirectory]
            if (noDict.get()) {
                commandLine += ['--no_dict']
            } else {
                commandLine += [dictionaryPath]
            }
            commandLine += [outputDirectory]
            workingDir "$project.buildDir/mfa"
        }
    }
}
