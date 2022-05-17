package marytts.tasks


import org.gradle.api.DefaultTask
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.tasks.*

// Configuration
import marytts.config.MaryConfiguration
import marytts.config.JSONMaryConfigLoader

// Runtime / Request
import marytts.runutils.Mary
import marytts.runutils.Request

// IO
import marytts.data.Utterance


class GenerateHTSLabels extends DefaultTask {

    @InputDirectory
    final DirectoryProperty srcDir = project.objects.directoryProperty()

    @OutputDirectory
    final DirectoryProperty fullLabDir = project.objects.directoryProperty()

    @OutputDirectory
    final DirectoryProperty monoLabDir = project.objects.directoryProperty()

    final Set<String> vowels = new HashSet<String>(["aa", "ae", "ah", "ao", "aw", "ax", "axr", "ay", "eh", "er", "ey", "ih", "ix", "iy", "ow", "ow", "oy", "uh", "uw", "ux"])

    String addStress(String mono_label, String full_label) {
        if (vowels.contains(mono_label)) {
            def m = full_label =~ /^.*\/B:([01x]+)-([01x]+)-.*/;
            def accent = m[0][1]
            def stress = m[0][2]
            return "${accent}${stress}"
        } else {
            return "";
        }
    }

    @TaskAction
    void convert() {
        // Call Mary
        def dict = [:]
        project.fileTree(srcDir).include('*.json').collect { jsonFile ->
            try {
                // Read the text
                String input_data = jsonFile.text;

                // Read the configuration
                InputStream configuration_stream = this.class.getResourceAsStream("/marytts/labels.json")
                MaryConfiguration conf_object = (new JSONMaryConfigLoader()).loadConfiguration(configuration_stream);
                
                // Call mary && Get the output utterance
                def request = new Request(conf_object, input_data);
                request.process();

                // Save full label
                def full_lab = request.serializeFinaleUtterance();
                fullLabDir.file(jsonFile.name - '.json' + '.lab').get().asFile.withWriter('UTF-8') { out ->
                    out.println full_lab
                }

                // Save mono label
                def mono_lab = []
                full_lab.eachLine { full ->
                    def m = full =~ /^([0-9]*)[ \t]*([0-9]*)[ \t]*[^-]*-([^+]+)[+].*/;
                    def stress = addStress(m[0][3], full)
                    mono_lab.add("${m[0][1]}\t${m[0][2]}\t${m[0][3]}${stress}")
                }
                monoLabDir.file(jsonFile.name - '.json' + '.lab').get().asFile.withWriter('UTF-8') { out ->
                    out.println mono_lab.join("\n")
                }

            } catch (Exception ex) {
                project.logger.error "Excluding $jsonFile.name for label generation: ${ex}"
                throw ex;
                // FIXME: more detail message
            }
        }
    }
}
