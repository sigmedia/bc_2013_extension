import org.gradle.api.DefaultTask
import org.gradle.api.file.*
import org.gradle.api.tasks.*

class ExtractMFALab extends DefaultTask {

    @InputDirectory
    final DirectoryProperty srcDir = newInputDirectory()

    @OutputDirectory
    final DirectoryProperty destDir = newOutputDirectory()

    @TaskAction
    void convert() {
        def broken = []
        project.fileTree(srcDir).include('*.txt').each { txtFile ->
            // try {
            destDir.file(txtFile.name - '.txt' + '.lab').get().asFile.text = txtFile.text
            // } catch (all) {
            //     project.logger.error "Excluding $txtFile.name"
            //     broken << txtFile.name - '.txt'
            // }
        }
    }
}
